from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI-First HCP CRM"
    app_env: str = "development"
    debug: bool = True

    database_url: str

    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-120b"

    frontend_origin: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()