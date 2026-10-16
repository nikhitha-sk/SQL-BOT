import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

BUSINESS_DB = DATA_DIR / "business.db"  # data users ask about
APP_DB = DATA_DIR / "app.db"  # history, logs, feedback, good queries

MODEL = os.getenv("LLM_MODEL", "claude-opus-5-5")
PRICE_INPUT_PER_M = 4.00  # USD per 1M input tokens (Claude Opus 5.5)
PRICE_OUTPUT_PER_M = 20.00  # USD per 1M output tokens

ROW_LIMIT = 1000
QUERY_TIMEOUT_SECONDS = 10
MAX_FIX_RETRIES = 2
CACHE_TTL_SECONDS = 600
RATE_LIMIT_PER_MINUTE = 30

BASE_TABLES = ["customers", "products", "orders", "order_items"]
