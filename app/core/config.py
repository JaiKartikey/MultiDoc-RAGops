# ---create out config file----
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    # ------Gemini API settings------
    gemini_api_key: str
    gemini_api_base_url:str

    # ---LLM settings------
    llm_model: str = "gemini-3.5-flash"
    embedding_model: str = "gemini-embedding-001"

    # ---chunking settings---
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k : int = 5

    # adding storage----------
    storage_dir:str = "storage"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra = "ignore"
    )

import sys
from pydantic import ValidationError

try:
    settings = Settings()
except ValidationError as e:
    print("CRITICAL ERROR: Missing required configuration variables.")
    print("Please ensure GEMINI_API_KEY and GEMINI_API_BASE_URL are set in the environment or .env file.")
    print(f"Details:\n{e}")
    sys.exit(1)