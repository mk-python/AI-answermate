import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    MAX_REQUEST_SIZE = int(os.getenv("MAX_REQUEST_SIZE", "16000000"))
    MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE", "5000000"))
    MAX_IMAGE_SIDE = int(os.getenv("MAX_IMAGE_SIDE", "2000"))
    RATE_LIMIT_COUNT = int(os.getenv("RATE_LIMIT_COUNT", "60"))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    APP_ENV = os.getenv("APP_ENV", "development")
    PORT = int(os.getenv("PORT", "5000"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    MAX_CONTENT_LENGTH = MAX_REQUEST_SIZE
