"""徽史问答官：RAG 知识库问答接口。"""
from fastapi import APIRouter
from pydantic import BaseModel

from ..rag.retriever import RagAgent
from ..rag.graph import build_knowledge_graph

router = APIRouter(tags=["ask"])

_agent: RagAgent | None = None


def _get_agent() -> RagAgent:
    global _agent
    if _agent is None:
        _agent = RagAgent()
    return _agent


class AskRequest(BaseModel):
    question: str


@router.get("/ask/knowledge-graph")
def knowledge_graph():
    """读取问答知识库生成图谱，不触发向量索引或模型推理。"""
    return build_knowledge_graph()


@router.post("/ask")
async def ask(req: AskRequest):
    """输入问题，返回带来源的徽文化回答。"""
    result = _get_agent().ask(req.question)
    return result
