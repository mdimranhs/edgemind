from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "EdgeMind"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    hf_model: str = "Qwen/Qwen2.5-1.5B-Instruct"
    hf_token: str = ""

    llm_provider: str = "local"

    web_search_enabled: bool = True
    rag_local_files_only: bool = False


settings = Settings()
