import io
import json
import re
import sqlite3

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.config import BASE_DIR, BUSINESS_DB, BASE_TABLES
from app.db import app_db
from app.services import pipeline, retriever, runner

router = APIRouter()
REPORT = BASE_DIR / "eval" / "report.json"


class FeedbackRequest(BaseModel):
    message_id: int
    rating: int = Field(ge=-1, le=1)


@router.get("/history")
def history():
    return app_db.history()


@router.get("/stats")
def stats():
    return app_db.stats()


@router.post("/feedback")
def feedback(body: FeedbackRequest):
    app_db.save_feedback(body.message_id, body.rating)
    return {"ok": True}


@router.get("/schema")
def schema():
    out = []
    for name in sorted(runner.table_names()):
        cols = runner.run(f'SELECT * FROM "{name}" LIMIT 0')["columns"]
        count = runner.run(f'SELECT COUNT(*) FROM "{name}"')["rows"][0][0]
        doc = retriever.SCHEMA_DOCS.get(name, {})
        out.append({"name": name, "columns": cols, "rows": count,
                    "description": doc.get("description", "Uploaded CSV table"),
                    "uploaded": name not in BASE_TABLES})
    return out


@router.get("/glossary")
def glossary():
    return [{"term": k, "meaning": v} for k, v in retriever.GLOSSARY.items()]


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(400, "Please upload a .csv file.")
    raw = await file.read()
    if len(raw) > 10 * 1024 * 1024:
        raise HTTPException(400, "File is larger than 10 MB.")
    try:
        df = pd.read_csv(io.BytesIO(raw))
    except Exception as e:
        raise HTTPException(400, f"Could not read CSV: {e}") from e
    if df.empty:
        raise HTTPException(400, "The CSV file has no rows.")

    clean = lambda s: re.sub(r"[^a-z0-9_]+", "_", str(s).strip().lower()).strip("_") or "col"
    name = "csv_" + clean(file.filename.rsplit(".", 1)[0])[:40]
    df.columns = [clean(c) for c in df.columns]

    with sqlite3.connect(BUSINESS_DB) as con:
        df.to_sql(name, con, if_exists="replace", index=False)

    cols = "\n".join(f"  - {c}: {str(t)} column" for c, t in df.dtypes.items())
    app_db.add_uploaded_table(name, f"Table {name}: uploaded from {file.filename}.\n{cols}")
    pipeline.clear_cache()
    return {"table": name, "rows": len(df), "columns": list(df.columns)}


@router.get("/eval/report")
def eval_report():
    if not REPORT.exists():
        raise HTTPException(404, "No evaluation report yet. Run: python -m eval.run_eval")
    return json.loads(REPORT.read_text(encoding="utf-8"))
