"""应用配置：从 .env 读取（AI辅助制作，本人核对）。"""
from pathlib import Path

from pydantic_settings import BaseSettings

_BACKEND_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # DeepSeek
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    # 图像生成模式：local | remote | api
    image_gen_mode: str = "api"
    # local 模式下自训徽派 LoRA 权重路径，支持多个用英文逗号分隔（如建筑+水墨叠加）
    image_gen_lora_path: str = ""
    remote_image_service_url: str = ""
    cloud_image_api_key: str = ""
    cloud_image_api_url: str = ""

    # CORS
    cors_origins: str = "http://localhost:5173"

    class Config:
        # 相对 __file__ 的绝对路径，保证任何启动目录都能读到 backend/.env
        env_file = str(_BACKEND_ROOT / ".env")
        env_file_encoding = "utf-8"

    @property
    def image_gen_lora_paths(self) -> list[str]:
        """把逗号分隔的 LoRA 路径解析为列表（建筑+水墨可叠加多个）。"""
        return [p.strip() for p in self.image_gen_lora_path.split(",") if p.strip()]


settings = Settings()
