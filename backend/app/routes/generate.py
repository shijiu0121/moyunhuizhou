"""AI 徽画工坊：文生图 / 图生图接口。"""
from fastapi import APIRouter
from fastapi.responses import Response
from pydantic import BaseModel

from ..image_gen import get_engine

router = APIRouter(tags=["generate"])


class GenerateRequest(BaseModel):
    prompt: str
    negative_prompt: str | None = None
    width: int = 1024
    height: int = 1024
    seed: int | None = 42


@router.post("/generate")
async def generate(req: GenerateRequest):
    """根据提示词生成图片，返回 PNG。"""
    engine = get_engine()
    img_bytes = engine.generate(
        prompt=req.prompt,
        negative_prompt=req.negative_prompt,
        width=req.width,
        height=req.height,
        seed=req.seed,
    )
    return Response(content=img_bytes, media_type="image/png")
