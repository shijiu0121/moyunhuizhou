"""应用配置：从 .env 读取（AI辅助制作，本人核对）。"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # DeepSeek
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    # 图像生成模式：local | remote | api
    image_gen_mode: str = "api"
    remote_image_service_url: str = ""
    cloud_image_api_key: str = ""
    cloud_image_api_url: str = ""

    # CORS
    cors_origins: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
