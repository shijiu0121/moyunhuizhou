"""知识库构建：把徽文化资料切块成可检索的 chunk。

原始资料目录：backend/app/data/。
每条知识建议包含：主题分类 / 标题 / 正文 / 来源。
"""
import json
from pathlib import Path

# 知识库原始资料目录：backend/app/data/
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_knowledge_entries() -> list[dict]:
    """读取原始条目，保留标题、文件来源与全文，供问答和图谱共用。"""
    entries = []
    for f in sorted(DATA_DIR.glob("*.jsonl")):
        for number, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
                entries.append({
                    "title": item.get("title") or f"{f.stem} · {number}",
                    "source": f"{f.name}:{number}",
                    "text": item.get("text", ""),
                })
            except json.JSONDecodeError:
                continue
    for f in sorted(DATA_DIR.glob("*.txt")):
        entries.append({"title": f.stem, "source": f.name, "text": f.read_text(encoding="utf-8")})
    return [entry for entry in entries if entry["text"].strip()]


def load_knowledge_texts() -> list[str]:
    """保持问答原有的文本顺序与内容，供向量切块使用。"""
    return [entry["text"] for entry in load_knowledge_entries()]


def chunk_text(text: str, chunk_size: int = 200, overlap: int = 50) -> list[str]:
    """简单按字符切块，保留重叠，避免上下文断裂。"""
    if len(text) <= chunk_size:
        return [text] if text.strip() else []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def build_chunks() -> list[str]:
    """加载全部知识文本并切块。"""
    chunks = []
    for t in load_knowledge_texts():
        chunks.extend(chunk_text(t))
    return chunks
