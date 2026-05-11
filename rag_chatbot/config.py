from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings


load_dotenv()


class Settings(BaseSettings):
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_chat_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_CHAT_MODEL")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        alias="OPENAI_EMBEDDING_MODEL",
    )

    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    qdrant_collection: str = Field(
        default="ai_chatbot_docs",
        alias="QDRANT_COLLECTION",
    )
    qdrant_vector_size: int = Field(default=1536, alias="QDRANT_VECTOR_SIZE")

    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8080, alias="APP_PORT")

    chunk_size: int = Field(default=800, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=120, alias="CHUNK_OVERLAP")
    top_k: int = Field(default=5, alias="TOP_K")
    min_score: float = Field(default=0.25, alias="MIN_SCORE")
    max_context_chars: int = Field(default=12000, alias="MAX_CONTEXT_CHARS")
    llm_temperature: float = Field(default=0.2, alias="LLM_TEMPERATURE")

    data_dir: Path = Path("data/docs")


@lru_cache
def get_settings() -> Settings:
    return Settings()
