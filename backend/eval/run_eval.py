"""Runs the 40 test questions and writes an accuracy report.

Usage (from the backend folder):
    python -m eval.run_eval              # full app: RAG + glossary + examples
    python -m eval.run_eval --mode basic # basic prompt: all tables, no glossary/examples
    python -m eval.run_eval --limit 5    # quick run on the first 5 questions
"""
import argparse
import json
import time
from pathlib import Path

from app.config import BUSINESS_DB
from app.db import app_db, seed
from app.services import pipeline, runner

HERE = Path(__file__).parent
REPORT = HERE / "report.json"


def _norm(value):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return round(float(value), 2)
    return str(value).strip().lower()


def same_result(gold: dict, got: dict) -> bool:
    """Every gold column must appear in the result with the same values (column order and extra columns are ignored)."""
    if len(gold["rows"]) != len(got["rows"]):
        return False
    columns = lambda res: [sorted(map(_norm, col), key=str) for col in zip(*res["rows"])]
    remaining = columns(got)
    for col in columns(gold):
        if col not in remaining:
            return False
        remaining.remove(col)
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["rag", "basic"], default="rag")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    if not BUSINESS_DB.exists():
        seed.seed()
    app_db.init()
    questions = json.loads((HERE / "questions.json").read_text(encoding="utf-8"))[: args.limit]

    cases = []
    for i, q in enumerate(questions, 1):
        started = time.monotonic()
        answer = pipeline.answer_question(q["question"], [], explain=False, rag=args.mode == "rag")
        gold = runner.run(q["sql"])
        passed = answer["status"] == "ok" and same_result(gold, answer)
        cases.append({
            "question": q["question"], "level": q["level"], "passed": passed,
            "expected_sql": q["sql"], "generated_sql": answer["sql"], "error": answer["error"],
            "time_ms": int((time.monotonic() - started) * 1000), "cost_usd": answer["usage"]["cost_usd"],
        })
        print(f"[{i:2}/{len(questions)}] {'PASS' if passed else 'FAIL'}  {q['question']}")

    n = len(cases)
    summary = {
        "mode": args.mode,
        "run_at": time.strftime("%Y-%m-%d %H:%M"),
        "total": n,
        "passed": sum(c["passed"] for c in cases),
        "accuracy": round(100 * sum(c["passed"] for c in cases) / n, 1),
        "avg_time_ms": int(sum(c["time_ms"] for c in cases) / n),
        "avg_cost_usd": round(sum(c["cost_usd"] for c in cases) / n, 5),
        "by_level": {
            lvl: round(100 * sum(c["passed"] for c in cases if c["level"] == lvl)
                       / max(1, sum(c["level"] == lvl for c in cases)), 1)
            for lvl in ("easy", "medium", "hard")
        },
        "cases": cases,
    }

    report = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else {}
    report[args.mode] = summary
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nAccuracy ({args.mode}): {summary['accuracy']}%  "
          f"avg time {summary['avg_time_ms']} ms  avg cost ${summary['avg_cost_usd']}")
    print(f"Report saved to {REPORT}")


if __name__ == "__main__":
    main()
