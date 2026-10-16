import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

BUSINESS_DB = DATA_DIR / "business.db"  # data users ask about
APP_DB = DATA_DIR / "app.db"  # history, logs, feedback, good queries

# "gemini" (free tier) or "anthropic" (Claude, paid)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
DEFAULT_MODELS = {"gemini": "gemini-3.8-flash", "anthropic": "claude-opus-5-5"}
MODEL = os.getenv("LLM_MODEL", DEFAULT_MODELS[LLM_PROVIDER])

# USD per 1M tokens (input, output). Gemini free tier costs nothing.
PRICES = {"gemini": (0.0, 0.0), "anthropic": (4.00, 20.00)}
PRICE_INPUT_PER_M = float(os.getenv("PRICE_INPUT_PER_M", PRICES[LLM_PROVIDER][0]))
PRICE_OUTPUT_PER_M = float(os.getenv("PRICE_OUTPUT_PER_M", PRICES[LLM_PROVIDER][1]))

ROW_LIMIT = 1000
QUERY_TIMEOUT_SECONDS = 10
MAX_FIX_RETRIES = 2
CACHE_TTL_SECONDS = 600
RATE_LIMIT_PER_MINUTE = 30

BASE_TABLES = ["customers", "products", "orders", "order_items"]
