"""知识库构建：把徽文化资料切块成可检索的 chunk。

数据来源：docs/数据来源清单.md 记录的公开资料。
每条知识建议包含：主题分类 / 标题 / 正文 / 来源。
"""
import json
from pathlib import Path

# 知识库原始资料目录：backend/app/data/
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_knowledge_texts() -> list[str]:
    """读取 data/ 下的知识条目（JSON Lines 或纯文本），返回文本列表。"""
    texts = []
    for f in sorted(DATA_DIR.glob("*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                item = json.loads(line)
                texts.append(item.get("text", ""))
            except json.JSONDecodeError:
                continue
    for f in sorted(DATA_DIR.glob("*.txt")):
        texts.append(f.read_text(encoding="utf-8"))
    return [t for t in texts if t.strip()]


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
