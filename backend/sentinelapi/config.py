from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    allow_private_targets: bool = os.getenv("SENTINELAPI_ALLOW_PRIVATE_TARGETS", "true").lower() == "true"
    max_response_bytes: int = int(os.getenv("SENTINELAPI_MAX_RESPONSE_BYTES", "1048576"))
    request_timeout: float = float(os.getenv("SENTINELAPI_REQUEST_TIMEOUT", "5"))
    max_workers: int = min(int(os.getenv("SENTINELAPI_MAX_WORKERS", "8")), 16)
    ai_provider: str = os.getenv("AI_PROVIDER", "groq").lower()
    groq_api_key: str | None = os.getenv("GROQ_API_KEY")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    groq_timeout: float = float(os.getenv("GROQ_TIMEOUT", "20"))
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    gemini_timeout: float = float(os.getenv("GEMINI_TIMEOUT", "20"))
    cors_origins: tuple[str, ...] = tuple(
        item.strip() for item in os.getenv("SENTINELAPI_CORS_ORIGINS", "*").split(",") if item.strip()
    )


settings = Settings()
