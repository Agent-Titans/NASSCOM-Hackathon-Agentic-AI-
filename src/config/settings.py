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
    # Comma-separated generate models tried on HTTP 429/503 after primary fails
    gemini_model_fallbacks: str = "gemini-2.5-flash-lite"
    gemini_model_embed: str = "gemini-embedding-001"
    # Chroma vectors: local (ONNX MiniLM, fast/offline) | gemini (LLD, API)
    rag_embedding_backend: str = "local"
    local_embedding_model: str = "all-MiniLM-L6-v2"  # Chroma DefaultEmbeddingFunction

    sqlite_database_url: str = f"sqlite:///{ROOT_DIR / 'data' / 'app.db'}"
    chroma_persist_dir: str = str(ROOT_DIR / "data" / "chroma")
    embedding_cache_path: Path = ROOT_DIR / "data" / "embedding_cache.json"

    c_total_hand1: float = 0.75
    c_total_hand2: float = 0.60
    # strict_lld = LLD-canonical Supervisor; demo = optional playbook overrides
    supervisor_mode: str = "strict_lld"
    rag_top_k: int = 8
    rag_sim_high: float = 0.70  # Hand 1 eligible when other gates pass
    rag_sim_medium: float = 0.55  # below → low_grounding; Hand 2/3 only
    # When false, Chroma/corpus stay empty until ingest/bootstrap scripts run
    rag_auto_seed: bool = True
    # synthetic = 1k JSON corpus only (+ KB seeds); legacy = demo+enterprise; both = all
    rag_corpus_mode: str = "synthetic"
    synthetic_corpus_path: Path = ROOT_DIR / "data" / "synthetic" / "tickets_1000.json"

    resolution_rewrite_enabled: bool = False
    resolution_rewrite_timeout_sec: int = 8
    resolution_rewrite_skip_after_sec: float = 6.0
    # Max corpus/user candidates rescored with Gemini embeddings per ticket
    retrieval_semantic_candidate_cap: int = 16
    # Skip corpus embedding when Chroma/keyword match is already strong (≥ rag_sim_high).
    # Resolved user tickets always get semantic rescoring regardless of this flag.
    retrieval_skip_semantic_when_strong: bool = True
    # Auto-assign unowned Hand 2/3 tickets after this many minutes
    auto_assign_grace_minutes: int = 10

    # Email notifications (off by default — enable when SMTP configured)
    email_notifications_enabled: bool = False
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    sender_email: str = ""

    routing_rules_path: Path = ROOT_DIR / "config" / "routing_rules.json"

    # Gemini classifies first. When True, only "Security incident:" prefix short-circuits.
    classifier_keyword_short_circuit: bool = True
    gemini_classify_max_output_tokens: int = 512
    gemini_http_retries: int = 2
    classifier_keyword_min_score: float = 0.95
    classifier_keyword_min_gap: float = 0.5


@lru_cache
def get_settings() -> Settings:
    return Settings()
