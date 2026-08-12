"""RAG 问答：检索知识库 + DeepSeek 生成回答（先查资料再回答）。"""
import logging

import httpx

from ..config import settings
from .vectorstore import VectorStore

logger = logging.getLogger(__name__)


class RagAgent:
    def __init__(self):
        self.vs = VectorStore()

    def ensure_index(self):
        """确保知识库已构建。"""
        from .knowledge import build_chunks
        self.vs.build_index(build_chunks())

    def _call_deepseek(self, messages: list[dict]) -> str:
        """调用 DeepSeek（OpenAI 兼容接口）。"""
        url = f"{settings.deepseek_base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.deepseek_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.deepseek_model,
            "messages": messages,
            "temperature": 0.4,
        }
        resp = httpx.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def ask(self, question: str) -> dict:
        """问答主流程：检索 → 拼 prompt → 大模型回答 → 返回带来源的回答。"""
        self.ensure_index()
        retrieved = self.vs.search(question, top_k=5)

        context = "\n\n".join(f"[资料{i+1}]{r['text']}" for i, r in enumerate(retrieved))
        system = (
            "你是'墨蕴徽州'平台的徽文化讲解官，请依据提供的徽文化资料回答问题。"
            "回答要准确、通俗、有文化韵味；如果资料不足以回答，请如实说明，不要编造。"
            "回答末尾用[来源]标注用到了哪几条资料。"
        )
        user = f"资料：\n{context}\n\n问题：{question}"
        answer = self._call_deepseek([
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ])
        return {"answer": answer, "sources": [r["text"] for r in retrieved]}
