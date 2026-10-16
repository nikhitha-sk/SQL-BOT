"""Runs one question through every step: cache, RAG, prompt, LLM, validate, run, auto-fix, chart, save."""
import time

from app.config import CACHE_TTL_SECONDS, MAX_FIX_RETRIES
from app.db import app_db
from app.services import charts, llm, prompt, retriever, runner
from app.services.validator import UnsafeSQLError, validate

_cache: dict[str, tuple[float, dict]] = {}


def clear_cache() -> None:
    _cache.clear()


def _cache_key(question: str, memory: list[dict]) -> str:
    last_sql = memory[-1]["sql"] if memory else ""
    return " ".join(question.lower().split()) + "|" + last_sql


def ask(question: str, session_id: str) -> dict:
    started = time.monotonic()
    memory = app_db.chat_memory(session_id)
    key = _cache_key(question, memory)

    hit = _cache.get(key)
    if hit and time.monotonic() - hit[0] < CACHE_TTL_SECONDS:
        answer = {**hit[1], "cached": True, "usage": llm.new_usage()}
    else:
        answer = answer_question(question, memory)
        if answer["status"] == "ok":
            _cache[key] = (time.monotonic(), answer)

    answer["time_ms"] = int((time.monotonic() - started) * 1000)
    answer["id"] = app_db.save_message(
        session_id, question, answer["sql"] if answer["status"] == "ok" else None,
        answer["chart"]["type"], answer["explanation"], len(answer["rows"]))
    app_db.save_log(answer["id"], question, answer["sql"], answer["status"] == "ok",
                    answer["error"], answer["attempts"], answer["usage"], answer["time_ms"])
    return answer


def answer_question(question: str, memory: list[dict], explain: bool = True, rag: bool = True) -> dict:
    """Core text-to-SQL loop. rag=False is the basic prompt (all tables, no glossary or examples)."""
    usage = llm.new_usage()
    answer = {"question": question, "status": "error", "sql": None, "columns": [], "rows": [],
              "chart": {"type": "table"}, "explanation": "", "error": None, "attempts": 0,
              "usage": usage, "cached": False}

    context = retriever.retrieve(question)
    if not rag:
        context = {"tables": [d for d in retriever.build_docs() if d["kind"] == "table"],
                   "glossary": [], "examples": []}
    answer["context"] = {k: [d["key"] for d in v] for k, v in context.items()}
    allowed = runner.table_names()
    error = None

    try:
        for _ in range(1 + MAX_FIX_RETRIES):
            answer["attempts"] += 1
            out = llm.generate_sql(prompt.build(question, context, memory, error), usage)
            if not out["sql"].strip():
                answer["status"] = "blocked"
                answer["error"] = out["reason"] or "I could not answer that from the data."
                return answer
            try:
                answer["sql"] = validate(out["sql"], allowed)
            except UnsafeSQLError as e:
                answer["sql"] = out["sql"]
                answer["status"] = "blocked"
                answer["error"] = str(e)
                return answer
            try:
                result = runner.run(answer["sql"])
                break
            except runner.QueryError as e:
                error = {"sql": answer["sql"], "message": str(e)}
                answer["error"] = str(e)
        else:
            return answer

        answer.update(result, status="ok", error=None)
        answer["chart"] = charts.pick_chart(result["columns"], result["rows"], question)
        try:
            if explain:
                answer["explanation"] = llm.explain(question, result["columns"], result["rows"], usage)
        except llm.LLMError:
            answer["explanation"] = f"The query returned {len(result['rows'])} row(s)."
    except llm.LLMError as e:
        answer["error"] = str(e)
    return answer
