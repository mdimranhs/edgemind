from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "EdgeMind"
    debug: bool = False

    @field_validator("debug", mode="before")
    @classmethod
    def _parse_debug(cls, v: object) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            val = v.strip().lower()
            if val in ("release", "prod", "production", "false", "0", "no", ""):
                return False
            if val in ("debug", "dev", "development", "true", "1", "yes"):
                return True
        return bool(v)

    host: str = "0.0.0.0"
    port: int = 8000


    hf_model: str = "Qwen/Qwen3-8B"
    hf_token: str = ""

    llm_provider: Literal["local", "hf_api", "mock"] = "hf_api"
    memory_backend: Literal["none", "sqlite"] = "none"


    web_search_enabled: bool = True
    rag_local_files_only: bool = False

    # Guardrails, Context, and Resource Limits
    max_history_messages: int = Field(default=8, ge=1, le=64)
    max_message_chars: int = Field(default=2000, ge=1, le=100_000)
    max_generation_tokens: int = Field(default=1024, ge=1, le=8192)
    max_prompt_tokens: int = Field(default=4096, ge=1, le=128_000)
    max_retrieved_chunks: int = Field(default=3, ge=1, le=20)
    hf_request_timeout: float = Field(default=30.0, gt=0, le=300)
    max_concurrent_requests: int = Field(default=4, ge=1, le=100)
    cors_allowed_origins: str = "*"
    rate_limit_per_minute: int = Field(default=30, ge=1, le=10_000)


settings = Settings()
