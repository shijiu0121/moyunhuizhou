"""图像生成模式切换接口：GET 查当前模式，POST 切换 local / remote / api。"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..image_gen import GEN_MODES, current_gen_mode, set_gen_mode

router = APIRouter(tags=["genmode"])


class ModeSwitch(BaseModel):
    mode: str


@router.get("/gen-mode")
async def get_mode():
    return {"mode": current_gen_mode(), "modes": GEN_MODES}


@router.post("/gen-mode")
async def post_mode(req: ModeSwitch):
    try:
        mode = set_gen_mode(req.mode)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"mode": mode, "modes": GEN_MODES}
