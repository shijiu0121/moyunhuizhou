"""运行：在 backend/ 执行 python -m unittest discover -s tests -v。"""
import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

from app.rag.graph import build_knowledge_graph
from app.rag.knowledge import build_chunks, load_knowledge_entries, load_knowledge_texts


class KnowledgeGraphTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.data_patch = patch("app.rag.knowledge.DATA_DIR", self.directory)
        self.data_patch.start()
        self.addCleanup(self.data_patch.stop)

    def write(self, name, text):
        (self.directory / name).write_text(text, encoding="utf-8")

    def test_reader_preserves_rag_content_order_and_chunk_overlap(self):
        self.write("b.txt", " 天井与马头墙\n")
        long_text = "徽" * 230
        self.write("a.txt", long_text)
        self.write("empty.txt", " \n")
        self.write("a.jsonl", '\n' + json.dumps({"title": "徽商读本", "text": "徽商  祠堂\n"}) + '\ninvalid\n{}\n')
        self.assertEqual(load_knowledge_texts(), ["徽商  祠堂\n", long_text, " 天井与马头墙\n"])
        self.assertEqual(build_chunks(), ["徽商  祠堂\n", "徽" * 200, "徽" * 80, " 天井与马头墙\n"])
        self.assertEqual(load_knowledge_entries()[0]["source"], "a.jsonl:2")

    def test_empty_library_has_no_invented_nodes(self):
        graph = build_knowledge_graph()
        self.assertEqual(graph["nodes"], [])
        self.assertEqual(graph["links"], [])
        self.assertEqual(graph["stats"], {"articles": 0, "topics": 0, "relations": 0})

    def test_relation_evidence_and_graph_integrity(self):
        texts = {
            "徽派建筑.txt": "天井与马头墙；徽商、祠堂。",
            "徽商故事.txt": "徽商修建祠堂，与天井、马头墙相伴。",
            "徽州宅居.txt": "天井、马头墙、祠堂。",
            "民俗风情.txt": "徽商，祠堂，天井。",
            "孤立资料.txt": "没有目录关键词的新资料仍应可读。",
        }
        for name, text in texts.items():
            self.write(name, text)
        graph = build_knowledge_graph()
        nodes = {n["id"]: n for n in graph["nodes"]}
        self.assertEqual(len(nodes), len(graph["nodes"]))
        self.assertEqual(graph["stats"]["articles"], len(texts))
        self.assertEqual(sum(t["count"] for t in graph["topics"]), len(texts))
        degree = Counter()
        seen = set()
        for link in graph["links"]:
            self.assertIn(link["source"], nodes)
            self.assertIn(link["target"], nodes)
            pair = frozenset((link["source"], link["target"]))
            self.assertNotIn(pair, seen)
            seen.add(pair)
            if link["kind"] == "related":
                self.assertGreaterEqual(len(link["keywords"]), 2)
                for node_id in (link["source"], link["target"]):
                    degree[node_id] += 1
                    for word in link["keywords"]:
                        self.assertIn(word, nodes[node_id]["text"])
        self.assertTrue(degree)
        self.assertLessEqual(max(degree.values()), 2)
        for node in nodes.values():
            if node["kind"] == "article":
                self.assertEqual(node["text"], texts[node["source"]])
                self.assertTrue(any(l["kind"] == "contains" and l["target"] == node["id"] for l in graph["links"]))

    def test_ids_survive_new_files_and_read_live_content(self):
        self.write("徽墨.txt", "徽墨原文")
        first = next(n for n in build_knowledge_graph()["nodes"] if n["kind"] == "article")
        self.write("a.txt", "新增文件")
        self.write("徽墨.txt", "修订后的徽墨原文")
        second = next(n for n in build_knowledge_graph()["nodes"] if n["id"] == first["id"])
        self.assertEqual(second["text"], "修订后的徽墨原文")

    def test_jsonl_duplicate_titles_keep_distinct_sources(self):
        self.write("资料.jsonl", '\n'.join(json.dumps({"title": "徽墨", "text": "徽墨"}) for _ in range(2)))
        articles = [n for n in build_knowledge_graph()["nodes"] if n["kind"] == "article"]
        self.assertEqual(len(articles), 2)
        self.assertNotEqual(articles[0]["id"], articles[1]["id"])


class KnowledgeGraphApiTests(unittest.TestCase):
    def test_graph_endpoint_does_not_invoke_rag_or_import_models(self):
        from fastapi.testclient import TestClient
        from app.main import app
        before = set(sys.modules)
        with patch("app.routes.ask._get_agent", side_effect=AssertionError("图谱不应启动 RAG")):
            response = TestClient(app).get("/api/ask/knowledge-graph")
        self.assertEqual(response.status_code, 200)
        graph = response.json()
        self.assertEqual(graph["stats"]["articles"], len(load_knowledge_entries()))
        added = {name.split('.')[0] for name in set(sys.modules) - before}
        self.assertFalse(added & {"torch", "sentence_transformers", "chromadb", "diffusers"})

    def test_original_ask_contract_is_preserved(self):
        from fastapi.testclient import TestClient
        from app.main import app
        with patch("app.routes.ask._get_agent") as get_agent:
            get_agent.return_value.ask.return_value = {"answer": "测试回答", "sources": ["测试原文"]}
            response = TestClient(app).post("/api/ask", json={"question": "徽墨是什么？"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"answer": "测试回答", "sources": ["测试原文"]})
        get_agent.return_value.ask.assert_called_once_with("徽墨是什么？")


if __name__ == "__main__":
    unittest.main()
