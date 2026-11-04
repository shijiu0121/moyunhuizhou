"""本地 SDXL + 徽派 LoRA 图像生成（自研亮点）。

运行条件：需要 CUDA GPU + diffusers + torch（见 requirements.txt 中被注释的部分）。
此模块在有 GPU 的机器上运行；无 GPU 的开发机使用 remote 或 api 模式。

加载两枚自训徽派 LoRA（建筑 + 水墨）并可叠加：
- 每个权重已「烧入」验证好的基准强度（建筑 0.3 / 水墨 0.5）
- adapter_weights 再乘一个系数控制配比，见 _STYLE_ADAPTER_WEIGHTS
- 出图默认带负向提示词，压制 SDXL 偏好的人像 / 现代内景等失败形态
"""
import logging
from pathlib import Path

from .engine import ImageEngine

logger = logging.getLogger(__name__)

# 后端项目根目录（backend/），用于把相对路径的 LoRA 权重解析成绝对路径，
# 保证无论从哪个目录启动 uvicorn 都能找到权重。
_BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent


def _resolve_path(p: str) -> str:
    """相对路径按 backend/ 根目录解析，绝对路径原样返回。"""
    path = Path(p)
    return str(path if path.is_absolute() else _BACKEND_ROOT / path)

# 队友交付文档里的「最关键的出图技巧」：压制人像 / 现代元素 / 室内。
# 前端未传 negative_prompt 时使用此默认值。
DEFAULT_NEGATIVE_PROMPT = (
    "people, person, portrait, 人物, 人像, "
    "modern interior, modern, 现代, 现代客厅"
)

# 风格 → 两个 LoRA 的 adapter_weights（对应 lora_paths 的顺序：[建筑, 水墨]）
# 每个权重已烧入基准强度，这里乘系数。参考交付文档「叠加配比调整」表。
_STYLE_ADAPTER_WEIGHTS = {
    "ink": [0.4, 1.2],       # 水墨优先：墨色重、留白多
    "photo": [1.2, 0.4],     # 写实建筑优先：马头墙/白墙更明显
    "balanced": [1.2, 1.2],  # 默认平衡：建筑清晰 + 水墨感
}


class LocalSDEngine(ImageEngine):
    def __init__(self, model_id: str = "/root/autodl-tmp/sdxl-base",
                 lora_paths: list[str] | None = None, device: str = "cuda"):
        """model_id: SDXL 基础模型；lora_paths: 自训徽派 LoRA 权重路径列表（可多枚叠加）。"""
        self.model_id = model_id
        self.lora_paths = [_resolve_path(p) for p in lora_paths] if lora_paths else []
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

        if self.lora_paths:
            adapter_names = []
            for i, p in enumerate(self.lora_paths):
                name = Path(p).stem  # 如 lora_building_03 → 用文件名当 adapter 名
                logger.info("加载徽派 LoRA[%d]: %s (adapter=%s)", i, p, name)
                self._pipe.load_lora_weights(p, adapter_name=name)
                adapter_names.append(name)
            # 默认用平衡配比；具体某次生成时按 style 动态调整
            self._adapter_names = adapter_names
            self.set_style("balanced")
        else:
            logger.warning("未配置 LoRA 路径（IMAGE_GEN_LORA_PATH），生成将不带徽派风格")

    def set_style(self, style: str):
        """按风格调整两枚 LoRA 的叠加配比。style: ink | photo | balanced。"""
        weights = _STYLE_ADAPTER_WEIGHTS.get(style, _STYLE_ADAPTER_WEIGHTS["balanced"])
        if len(self._adapter_names) == 1:
            weights = [weights[0]]
        logger.info("LoRA 配比 %s -> %s", self._adapter_names, weights)
        self._pipe.set_adapters(self._adapter_names, adapter_weights=weights)

    def generate(self, prompt: str, negative_prompt: str = None,
                 width: int = 1024, height: int = 1024, seed: int = 42,
                 style: str = "balanced") -> bytes:
        self._load()
        import torch
        if seed is not None:
            torch.manual_seed(seed)
        if style in _STYLE_ADAPTER_WEIGHTS:
            self.set_style(style)
        negative_prompt = negative_prompt or DEFAULT_NEGATIVE_PROMPT
        pipe = self._pipe  # 局部引用，避免模式切换释放引擎时本次调用受影响
        result = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_inference_steps=30,
            guidance_scale=7.5,
        ).images[0]
        from io import BytesIO
        buf = BytesIO()
        result.save(buf, format="PNG")
        return buf.getvalue()
