"""
21st Academy AI Assistant — Backend Configuration
All settings are read from environment variables (.env) so the same code
can run in dev (SQLite + local Ollama) and prod (Postgres + remote Ollama)
without any code changes.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


class Settings:
    # --- App ---
    APP_NAME: str = "21st Academy AI Assistant"
    ENV: str = os.getenv("ENV", "development")  # development | production
    DEBUG: bool = ENV != "production"

    # --- Database ---
    # SQLite by default. Set DATABASE_URL to a postgres:// URL in prod
    # and nothing else in the codebase needs to change.
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'database' / 'app.db'}"
    )

    # --- Ollama ---
    # Point this at your Linux server later (e.g. http://10.0.0.5:11434)
    # without touching the frontend at all.
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_CHAT_MODEL: str = os.getenv("OLLAMA_CHAT_MODEL", "llama3")
    OLLAMA_EMBED_MODEL: str = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "60"))
    OLLAMA_MAX_RETRIES: int = int(os.getenv("OLLAMA_MAX_RETRIES", "2"))

    # --- Auth ---
    JWT_SECRET: str = os.getenv("JWT_SECRET", "CHANGE_ME_IN_PRODUCTION_32CHARS_MIN")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "720"))  # 12h

    # Bootstrap admin (used once, on first startup, if no admin exists)
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@21stacademy.in")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "ChangeMe123!")

    # --- CORS ---
    # Comma-separated list of origins allowed to call this API.
    # Add every domain the widget is embedded on.
    ALLOWED_ORIGINS: list = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5500,http://127.0.0.1:5500,https://21stacademy.in,https://www.21stacademy.in,https://21st-academy-ai-chatbot-gcg7.vercel.app",
)

    # --- Rate limiting ---
    RATE_LIMIT_CHAT: str = os.getenv("RATE_LIMIT_CHAT", "20/minute")
    RATE_LIMIT_UPLOAD: str = os.getenv("RATE_LIMIT_UPLOAD", "5/minute")
    RATE_LIMIT_LOGIN: str = os.getenv("RATE_LIMIT_LOGIN", "10/minute")

    # --- Uploads / RAG ---
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    VECTOR_DB_DIR: Path = BASE_DIR / "vector_db"
    MAX_UPLOAD_MB: int = int(os.getenv("MAX_UPLOAD_MB", "20"))
    ALLOWED_UPLOAD_EXT = {".pdf", ".docx", ".txt", ".csv", ".xlsx", ".xls", ".pptx", ".ppt"}
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "800"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "120"))
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "4"))

    # --- System prompt (business context, ported from the old chatbot.js) ---
    SYSTEM_PROMPT: str = """You are the friendly and professional AI assistant for 21st Academy and our Career Mapping Workshop.
Your job is to answer visitor questions warmly and professionally using the dynamic course catalogue and workshop details provided in the system context.

Strict Rules:
1. Ground your answers strictly on the "AVAILABLE ACADEMY COURSES", "WORKSHOP DETAILS", and "RELEVANT REFERENCE MATERIAL" provided in the prompt context.
2. If the user asks about a course, syllabus topic, fee, duration, location, date, or other details that are NOT present in the provided context (or if you do not know the answer), you must respond EXACTLY with:
   "I don't have that information yet. Please contact 21st Academy."
3. Do NOT make up, approximate, or hallucinate any facts, dates, durations, pricing, projects, or placement statistics.
4. If a user asks about general concepts or courses not offered (and not listed in context), redirect them politely to our registered courses.
5. Keep your responses short (2-4 sentences max). Recommend relevant courses if a user shares their interests (e.g., if interested in AI, recommend Python, Machine Learning, Deep Learning, Generative AI, and Agentic AI with expected salaries and durations as listed in our database)."""


settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
