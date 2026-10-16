"""LLM client (Gemini or Claude): writes SQL and explains results. Tracks tokens and cost."""
import json

from app.config import LLM_PROVIDER, MODEL, PRICE_INPUT_PER_M, PRICE_OUTPUT_PER_M
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


def new_usage() -> dict:
    return {"input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0}


def _add_usage(usage: dict, input_tokens: int, output_tokens: int) -> None:
    usage["input_tokens"] += input_tokens or 0
    usage["output_tokens"] += output_tokens or 0
    usage["cost_usd"] = round(
        usage["input_tokens"] / 1e6 * PRICE_INPUT_PER_M + usage["output_tokens"] / 1e6 * PRICE_OUTPUT_PER_M, 6)


def _call_gemini(system: str, user: str, usage: dict, schema: dict | None) -> str:
    import httpx
    from google import genai
    from google.genai import errors, types

    global _client
    try:
        if _client is None:
            # Reads GEMINI_API_KEY (or GOOGLE_API_KEY). Retries with backoff on free-tier rate limits.
            _client = genai.Client(http_options=types.HttpOptions(
                retry_options=types.HttpRetryOptions(attempts=4, initial_delay=2, http_status_codes=[429, 500, 503])))
        resp = _client.models.generate_content(
            model=MODEL,
            contents=user,
            config=types.GenerateContentConfig(
                system_instruction=system,
                response_mime_type="application/json" if schema else None,
                response_json_schema=schema,
            ),
        )
    except ValueError as e:
        raise LLMError("Gemini API key is missing. Set GEMINI_API_KEY.") from e
    except errors.ClientError as e:
        if e.code == 429:
            raise LLMError("Gemini free-tier limit reached. Wait a minute (or until tomorrow) and try again.") from e
        if e.code in (400, 401, 403) and "key" in str(e).lower():
            raise LLMError("Gemini API key is invalid. Check GEMINI_API_KEY.") from e
        raise LLMError(f"Gemini API error ({e.code}).") from e
    except errors.APIError as e:
        raise LLMError(f"Gemini API error ({e.code}).") from e
    except httpx.TransportError as e:
        raise LLMError("Could not reach the Gemini API.") from e

    meta = resp.usage_metadata
    if meta:
        _add_usage(usage, meta.prompt_token_count,
                   (meta.candidates_token_count or 0) + (meta.thoughts_token_count or 0))
    if not resp.text:
        raise LLMError("Gemini returned an empty answer.")
    return resp.text


def _call_claude(system: str, user: str, usage: dict, effort: str, schema: dict | None) -> str:
    import anthropic

    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    output_config = {"effort": effort}
    if schema:
        output_config["format"] = {"type": "json_schema", "schema": schema}
    try:
        resp = _client.beta.messages.create(
            model=MODEL,
            max_tokens=16000,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            system=system,
            messages=[{"role": "user", "content": user}],
            output_config=output_config,
        )
    except (anthropic.AuthenticationError, TypeError) as e:
        # TypeError: the SDK found no credentials at all
        raise LLMError("LLM API key is missing or invalid. Set ANTHROPIC_API_KEY.") from e
    except anthropic.RateLimitError as e:
        raise LLMError("LLM rate limit reached. Please try again in a moment.") from e
    except anthropic.APIStatusError as e:
        raise LLMError(f"LLM API error ({e.status_code}).") from e
    except anthropic.APIConnectionError as e:
        raise LLMError("Could not reach the LLM API.") from e

    _add_usage(usage, resp.usage.input_tokens, resp.usage.output_tokens)
    if resp.stop_reason == "refusal":
        raise LLMError("The model declined this request.")
    return next((b.text for b in resp.content if b.type == "text"), "")


def _call(system: str, user: str, usage: dict, effort: str, schema: dict | None = None) -> str:
    if LLM_PROVIDER == "anthropic":
        return _call_claude(system, user, usage, effort, schema)
    return _call_gemini(system, user, usage, schema)


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
