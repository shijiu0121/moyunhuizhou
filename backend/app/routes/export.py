"""文创印务局：把生成的图合成文创成品（明信片/海报/书签）并导出。"""
from fastapi import APIRouter
from fastapi.responses import Response
from pydantic import BaseModel

from ..export.composer import compose_bookmark, compose_postcard, compose_poster
from ..image_gen import get_engine

router = APIRouter(tags=["export"])


class ExportRequest(BaseModel):
    prompt: str
    title: str = "墨蕴徽州"
    subtitle: str = ""
    template: str = "postcard"  # postcard | poster | bookmark
    seed: int | None = None


@router.post("/export")
async def export_product(req: ExportRequest):
    """生图并套模板，导出一张文创成品 PNG。

    相同 seed + 相同描述 → 同一幅画；切换模板/改版式即可复用同画重排。
    """
    engine = get_engine()
    img_bytes = engine.generate(
        prompt=req.prompt,
        width=1024,
        height=1024,
        seed=req.seed if req.seed is not None else 42,
    )
    if req.template == "poster":
        out = compose_poster(img_bytes, title=req.title, subtitle=req.subtitle)
    elif req.template == "bookmark":
        out = compose_bookmark(img_bytes, title=req.title, subtitle=req.subtitle)
    else:
        out = compose_postcard(img_bytes, title=req.title, subtitle=req.subtitle)
    return Response(content=out, media_type="image/png")
