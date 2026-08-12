"""图像生成引擎抽象接口（可插拔设计，应对远程 GPU / 云 API 切换）。

三种模式：
- local  : 本机/同一进程有 GPU，直接用本地 SDXL + 徽派LoRA（自研亮点）
- remote : GPU 在远程机器，通过 HTTP 调用远程生图服务
- api    : 云生图 API（明确标注的备胎）

对外统一暴露 generate() 方法，上层路由不需要关心底层实现。
"""
from abc import ABC, abstractmethod


class ImageEngine(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> bytes:
        """输入提示词，返回生成的图片字节流。"""
        raise NotImplementedError
