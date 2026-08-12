"""图像生成引擎工厂：根据配置选择 local / remote / api 模式。"""
from ..config import settings
from .engine import ImageEngine


def get_engine() -> ImageEngine:
    """按 .env 的 IMAGE_GEN_MODE 返回对应引擎实例（懒初始化）。"""
    mode = settings.image_gen_mode
    if mode == "local":
        from .local_sd import LocalSDEngine
        return LocalSDEngine()
    if mode == "remote":
        from .remote_api import RemoteImageClient
        return RemoteImageClient(settings.remote_image_service_url)
    from .remote_api import CloudImageAPI
    return CloudImageAPI(settings.cloud_image_api_url, settings.cloud_image_api_key)
