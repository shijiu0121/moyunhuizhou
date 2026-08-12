"""远程生图服务客户端 + 云 API 备胎。

- RemoteImageClient : GPU 在远程机器时，通过 HTTP 调用远程生图服务（远程跑 local_sd）
- CloudImageAPI     : 调用云生图 API（备胎，材料中如实标注）
"""
import httpx

from .engine import ImageEngine


class RemoteImageClient(ImageEngine):
    """调用远程机器上运行的生图服务（该服务内部使用 LocalSDEngine）。"""

    def __init__(self, service_url: str):
        self.service_url = service_url.rstrip("/")

    def generate(self, prompt: str, **kwargs) -> bytes:
        resp = httpx.post(
            f"{self.service_url}/generate",
            json={"prompt": prompt, **kwargs},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.content


class CloudImageAPI(ImageEngine):
    """云生图 API 备胎。需在 .env 配置 CLOUD_IMAGE_API_URL / KEY。"""

    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key

    def generate(self, prompt: str, **kwargs) -> bytes:
        # TODO: 根据所选云服务（通义万相/即梦等）适配请求格式
        headers = {"Authorization": f"Bearer {self.api_key}"}
        resp = httpx.post(self.api_url, json={"prompt": prompt, **kwargs},
                          headers=headers, timeout=120)
        resp.raise_for_status()
        return resp.content
