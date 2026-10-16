"""Claude client: writes SQL and explains results. Tracks tokens and cost."""
import json

import anthropic

from app.config import MODEL, PRICE_INPUT_PER_M, PRICE_OUTPUT_PER_M
from app.services.prompt import SYSTEM

SQL_SCHEMA = {
    "type": "object",
    "properties": {"sql": {"type": "string"}, "reason": {"type": "string"}},
    "required": ["sql", "reason"],
    "additionalProperties": False,
}

_client = None


class LLMError(RuntimeError):
    pass


def client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


def new_usage() -> dict:
    return {"input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0}


def _call(system: str, user: str, usage: dict, effort: str, schema: dict | None = None) -> str:
    output_config = {"effort": effort}
    if schema:
        output_config["format"] = {"type": "json_schema", "schema": schema}
    try:
        resp = client().beta.messages.create(
            model=MODEL,
            max_tokens=16000,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            system=system,
            messages=[{"role": "user", "content": user}],
            output_config=output_config,
        )
    except anthropic.AuthenticationError as e:
        raise LLMError("LLM API key is missing or invalid. Set ANTHROPIC_API_KEY.") from e
    except anthropic.RateLimitError as e:
        raise LLMError("LLM rate limit reached. Please try again in a moment.") from e
    except anthropic.APIStatusError as e:
        raise LLMError(f"LLM API error ({e.status_code}).") from e
    except anthropic.APIConnectionError as e:
        raise LLMError("Could not reach the LLM API.") from e

    usage["input_tokens"] += resp.usage.input_tokens
    usage["output_tokens"] += resp.usage.output_tokens
    usage["cost_usd"] = round(
        usage["input_tokens"] / 1e6 * PRICE_INPUT_PER_M + usage["output_tokens"] / 1e6 * PRICE_OUTPUT_PER_M, 6)

    if resp.stop_reason == "refusal":
        raise LLMError("The model declined this request.")
    return next((b.text for b in resp.content if b.type == "text"), "")


def generate_sql(prompt: str, usage: dict) -> dict:
    """Returns {"sql": str, "reason": str}. Empty sql means the model will not answer."""
    text = _call(SYSTEM, prompt, usage, effort="medium", schema=SQL_SCHEMA)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise LLMError("The model returned an invalid answer.") from e


def explain(question: str, columns: list, rows: list, usage: dict) -> str:
    preview = json.dumps({"columns": columns, "rows": rows[:20], "total_rows": len(rows)}, default=str)
    return _call(
        "You explain query results to business users in one or two short, plain English sentences. "
        "Mention the key numbers. Money is in Indian rupees (₹). No markdown.",
        f"Question: {question}\nResult: {preview}",
        usage,
        effort="low",
    ).strip()
