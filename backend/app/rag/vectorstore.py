"""向量库：用 bge-m3（本地 CPU 可跑）做 embedding，存进 ChromaDB。

DeepSeek 不提供 embedding 接口，故本地向量化（免费、隐私、CPU 即可）。
首次运行会下载 bge-m3 模型（约 2GB），需联网一次。
"""
import logging

logger = logging.getLogger(__name__)

# 知识库持久化目录
import os
from pathlib import Path

VECTOR_DIR = Path(__file__).resolve().parent.parent / "data" / "vector_store"

# embedding 模型本地目录：放在项目内（与知识库 data 同目录），便于整体拷贝/移交时带上模型，队友无需重下
# 使用中文专用 embedding 模型，检索质量优于多语言模型，且体积小、下载稳定
MODEL_DIR = Path(__file__).resolve().parent.parent / "data" / "models" / "bge-base-zh-v1.5"


class VectorStore:
    def __init__(self, collection_name: str = "huizhou_kb"):
        self.collection_name = collection_name
        self._model = None
        self._collection = None

    def _get_model(self):
        """懒加载 bge-m3 embedding 模型（本地 CPU，从项目内目录加载）。"""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            if not (MODEL_DIR / "config.json").exists():
                raise FileNotFoundError(
                    f"未找到 bge-m3 模型，请先把模型文件放到 {MODEL_DIR}（需包含 config.json、pytorch_model.bin 等）"
                )
            logger.info("加载本地 embedding 模型 %s ...", MODEL_DIR)
            self._model = SentenceTransformer(str(MODEL_DIR))
        return self._model

    def _get_collection(self):
        """懒加载 ChromaDB 集合。"""
        if self._collection is None:
            import chromadb
            os.makedirs(VECTOR_DIR, exist_ok=True)
            client = chromadb.PersistentClient(path=str(VECTOR_DIR))
            self._collection = client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def build_index(self, chunks: list[str]):
        """把切块后的知识写入向量库。"""
        model = self._get_model()
        collection = self._get_collection()
        if collection.count() > 0:
            logger.info("知识库已存在 %d 条，跳过构建。", collection.count())
            return
        logger.info("构建知识库，共 %d 个 chunk ...", len(chunks))
        vectors = model.encode(chunks, normalize_embeddings=True).tolist()
        collection.add(
            ids=[f"chunk_{i}" for i in range(len(chunks))],
            embeddings=vectors,
            documents=chunks,
        )
        logger.info("知识库构建完成：%d 条。", len(chunks))

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """检索与问题最相关的知识块。"""
        model = self._get_model()
        collection = self._get_collection()
        q_vec = model.encode([query], normalize_embeddings=True).tolist()[0]
        res = collection.query(query_embeddings=[q_vec], n_results=top_k)
        docs = res.get("documents", [[]])[0]
        return [{"text": d} for d in docs]
