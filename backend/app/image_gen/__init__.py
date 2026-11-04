"""图像生成引擎工厂：根据配置选择 local / remote / api 模式，支持运行时切换。

- 引擎按模式缓存复用（避免 local 每次请求重载 SDXL）
- set_gen_mode 更新内存（立即生效）+ 写回 .env（持久化，重启保留）
- 注意：内存切换仅在单进程 uvicorn 下可靠；多 worker 需靠 .env + 重启
"""
import gc
import os
import threading
from pathlib import Path

from ..config import settings
from .engine import ImageEngine

GEN_MODES = ["local", "remote", "api"]
_engines: dict[str, ImageEngine] = {}
_lock = threading.Lock()


def _create(mode: str) -> ImageEngine:
    if mode == "local":
        from .local_sd import LocalSDEngine
        return LocalSDEngine(lora_paths=settings.image_gen_lora_paths or None)
    if mode == "remote":
        from .remote_api import RemoteImageClient
        return RemoteImageClient(settings.remote_image_service_url)
    from .remote_api import CloudImageAPI
    return CloudImageAPI(settings.cloud_image_api_url, settings.cloud_image_api_key)


def get_engine() -> ImageEngine:
    """返回当前模式的引擎（缓存复用；首次创建时懒加载模型）。"""
    mode = settings.image_gen_mode
    eng = _engines.get(mode)
    if eng is not None:
        return eng
    with _lock:
        if mode not in _engines:
            _engines[mode] = _create(mode)
        return _engines[mode]


def current_gen_mode() -> str:
    return settings.image_gen_mode


def set_gen_mode(mode: str) -> str:
    """切换当前模式：校验 + 更新内存（立即生效）+ 写回 .env（持久化）。"""
    if mode not in GEN_MODES:
        raise ValueError(f"未知模式: {mode}（可选 {GEN_MODES}）")
    if mode == "api" and not settings.cloud_image_api_key:
        raise ValueError("云端模式未配置 CLOUD_IMAGE_API_KEY")
    if mode == "remote" and not settings.remote_image_service_url:
        raise ValueError("远程模式未配置 REMOTE_IMAGE_SERVICE_URL")
    if mode == settings.image_gen_mode:
        return settings.image_gen_mode
    with _lock:
        old = settings.image_gen_mode
        if old in _engines:
            _release(_engines.pop(old))
        settings.image_gen_mode = mode
    _persist_env(mode)
    return mode


def _release(engine) -> None:
    """释放引擎持有的模型，尽量回收显存。"""
    if getattr(engine, "_pipe", None) is not None:
        engine._pipe = None
    gc.collect()
    try:
        import torch
        torch.cuda.empty_cache()
    except Exception:
        pass


def _persist_env(mode: str) -> None:
    """把 IMAGE_GEN_MODE 写回 backend/.env（原子替换，保留其他行）。"""
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    if not env_path.exists():
        return
    lines = env_path.read_text(encoding="utf-8").splitlines()
    hit = False
    for i, ln in enumerate(lines):
        if ln.strip().startswith("IMAGE_GEN_MODE="):
            lines[i] = f"IMAGE_GEN_MODE={mode}"
            hit = True
    if not hit:
        lines.append(f"IMAGE_GEN_MODE={mode}")
    tmp = env_path.with_suffix(".env.tmp")
    tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.replace(tmp, env_path)
