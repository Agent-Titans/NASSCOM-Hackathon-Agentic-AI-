from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    google_api_key: str = ""
    gemini_model_classify: str = "gemini-2.5-flash"
    gemini_model_resolve: str = "gemini-2.5-flash"
    gemini_model_embed: str = "gemini-embedding-001"

    sqlite_database_url: str = f"sqlite:///{ROOT_DIR / 'data' / 'app.db'}"
    chroma_persist_dir: str = str(ROOT_DIR / "data" / "chroma")

    c_total_hand1: float = 0.80
    c_total_hand2: float = 0.60
    rag_top_k: int = 8

    routing_rules_path: Path = ROOT_DIR / "config" / "routing_rules.json"


@lru_cache
def get_settings() -> Settings:
    return Settings()
