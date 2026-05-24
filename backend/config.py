from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # ~700MB download — much faster than Phi-2 (~10GB). See README for alternatives.
    model_name: str = "HuggingFaceTB/SmolLM2-360M-Instruct"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    use_slm: bool = True
    chroma_persist_dir: str = str(Path(__file__).parent / "data" / "chroma_db")
    upload_dir: str = str(Path(__file__).parent / "data" / "uploads")
    host: str = "0.0.0.0"
    port: int = 8000
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k_results: int = 5
    max_new_tokens: int = 256
    slm_max_input_chars: int = 3000
    rbi_rss_feeds: list[str] = [
        "https://www.rbi.org.in/pressreleases_rss.xml",
        "https://www.rbi.org.in/notifications_rss.xml",
    ]
    rbi_sync_max_items: int = 15
    rbi_sync_state_file: str = str(Path(__file__).parent / "data" / "rbi_sync_state.json")
    rbi_sync_keywords: list[str] | None = None

    model_config = {"env_file": ".env", "protected_namespaces": ("settings_",)}


settings = Settings()
