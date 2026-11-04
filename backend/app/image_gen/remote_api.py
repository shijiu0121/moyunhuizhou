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
    """智谱 GLM-Image 云生图 API（备胎：无 LoRA，忽略负向/seed/style，带 AI 水印）。"""

    # glm-image 推荐尺寸枚举，用于把前端非标尺寸映射到合格尺寸
    _ENUM = [
        "1280x1280", "1568x1056", "1056x1568",
        "1472x1088", "1088x1472", "1728x960", "960x1728",
    ]

    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url or "https://open.bigmodel.cn/api/paas/v4/images/generations"
        self.api_key = api_key
        self.model = "glm-image"

    @staticmethod
    def _map_size(w: int, h: int) -> str:
        """智谱自定义尺寸须满足：1024~2048、32 整数倍、像素 ≤2^22；否则映射到最接近的枚举。"""
        if (w % 32 == 0 and h % 32 == 0 and 1024 <= min(w, h)
                and max(w, h) <= 2048 and w * h <= 2 ** 22):
            return f"{w}x{h}"
        ratio = w / h
        best, best_d = None, float("inf")
        for s in CloudImageAPI._ENUM:
            sw, sh = map(int, s.split("x"))
            d = abs(sw / sh - ratio)
            if d < best_d:
                best_d, best = d, s
        return best

    def generate(self, prompt: str, width=1280, height=1280, **kwargs) -> bytes:
        # kwargs 里的 negative_prompt / seed / style 在云 API 下无意义，直接忽略
        size = self._map_size(int(width), int(height))
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": self.model,
            "prompt": prompt,
            "size": size,
            "watermark_enabled": True,  # 显式带 AI 水印
        }
        with httpx.Client(timeout=180) as client:
            r = client.post(self.api_url, json=payload, headers=headers)
            r.raise_for_status()
            img_url = r.json()["data"][0]["url"]
            img = client.get(img_url, timeout=180)
            img.raise_for_status()
            return img.content
