"""本地 SDXL + 徽派 LoRA 图像生成（自研亮点）。

运行条件：需要 CUDA GPU + diffusers + torch（见 requirements.txt 中被注释的部分）。
此模块在有 GPU 的机器上运行；无 GPU 的开发机使用 remote 或 api 模式。

注意：这是"演示所见即本地模型所产"的核心，训练徽派 LoRA 后加载其权重。
"""
import logging

from .engine import ImageEngine

logger = logging.getLogger(__name__)


class LocalSDEngine(ImageEngine):
    def __init__(self, model_id: str = "stabilityai/stable-diffusion-xl-base-1.0",
                 lora_path: str = None, device: str = "cuda"):
        """model_id: SDXL 基础模型；lora_path: 自训徽派 LoRA 权重路径。"""
        self.model_id = model_id
        self.lora_path = lora_path
        self.device = device
        self._pipe = None

    def _load(self):
        """懒加载：首次生成时才加载模型，避免启动慢。"""
        if self._pipe is not None:
            return
        from diffusers import AutoPipelineForText2Image
        import torch
        logger.info("加载 SDXL 模型: %s (device=%s)", self.model_id, self.device)
        self._pipe = AutoPipelineForText2Image.from_pretrained(
            self.model_id, torch_dtype=torch.float16, variant="fp16"
        ).to(self.device)
        if self.lora_path:
            logger.info("加载徽派 LoRA: %s", self.lora_path)
            self._pipe.load_lora_weights(self.lora_path)

    def generate(self, prompt: str, negative_prompt: str = None,
                 width: int = 1024, height: int = 1024, seed: int = 42) -> bytes:
        self._load()
        import torch
        if seed is not None:
            torch.manual_seed(seed)
        result = self._pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_inference_steps=30,
        ).images[0]
        from io import BytesIO
        buf = BytesIO()
        result.save(buf, format="PNG")
        return buf.getvalue()
