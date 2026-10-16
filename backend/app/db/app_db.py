"""App database: chat history, query logs, feedback and good queries."""
import sqlite3
from contextlib import closing

from app.config import APP_DB

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, question TEXT, sql TEXT,
    chart TEXT, explanation TEXT, row_count INTEGER, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS query_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT, message_id INTEGER, question TEXT, sql TEXT,
    success INTEGER, error TEXT, attempts INTEGER, input_tokens INTEGER, output_tokens INTEGER,
    cost_usd REAL, time_ms INTEGER, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT, message_id INTEGER, rating INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS good_queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT UNIQUE, sql TEXT);
CREATE TABLE IF NOT EXISTS uploaded_tables (
    name TEXT PRIMARY KEY, description TEXT);
"""


def connect() -> sqlite3.Connection:
    con = sqlite3.connect(APP_DB)
    con.row_factory = sqlite3.Row
    return con


def init() -> None:
    with closing(connect()) as con:
        con.executescript(SCHEMA)


def _rows(sql: str, params=()) -> list[dict]:
    with closing(connect()) as con:
        return [dict(r) for r in con.execute(sql, params).fetchall()]


def _write(sql: str, params=()) -> int:
    with closing(connect()) as con, con:
        return con.execute(sql, params).lastrowid


def save_message(session_id, question, sql, chart, explanation, row_count) -> int:
    return _write(
        "INSERT INTO messages (session_id, question, sql, chart, explanation, row_count) "
        "VALUES (?,?,?,?,?,?)", (session_id, question, sql, chart, explanation, row_count))


def save_log(message_id, question, sql, success, error, attempts, usage, time_ms) -> None:
    _write(
        "INSERT INTO query_logs (message_id, question, sql, success, error, attempts, "
        "input_tokens, output_tokens, cost_usd, time_ms) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (message_id, question, sql, int(success), error, attempts, usage["input_tokens"],
         usage["output_tokens"], usage["cost_usd"], time_ms))


def chat_memory(session_id: str, limit: int = 3) -> list[dict]:
    """Last few successful question + SQL pairs of this chat, oldest first."""
    rows = _rows("SELECT question, sql FROM messages WHERE session_id=? AND sql IS NOT NULL "
                 "ORDER BY id DESC LIMIT ?", (session_id, limit))
    return list(reversed(rows))


def history(limit: int = 100) -> list[dict]:
    return _rows(
        "SELECT m.id, m.session_id, m.question, m.sql, m.chart, m.row_count, m.created_at, "
        "l.success, l.time_ms, l.cost_usd, l.input_tokens, l.output_tokens, "
        "(SELECT rating FROM feedback f WHERE f.message_id=m.id ORDER BY f.id DESC LIMIT 1) AS rating "
        "FROM messages m LEFT JOIN query_logs l ON l.message_id=m.id ORDER BY m.id DESC LIMIT ?",
        (limit,))


def stats() -> dict:
    row = _rows("SELECT COUNT(*) AS questions, COALESCE(AVG(success),0) AS success_rate, "
                "COALESCE(AVG(time_ms),0) AS avg_time_ms, COALESCE(SUM(cost_usd),0) AS total_cost_usd "
                "FROM query_logs")[0]
    row["good_queries"] = _rows("SELECT COUNT(*) AS n FROM good_queries")[0]["n"]
    return row


def save_feedback(message_id: int, rating: int) -> None:
    _write("INSERT INTO feedback (message_id, rating) VALUES (?,?)", (message_id, rating))
    msg = _rows("SELECT question, sql FROM messages WHERE id=?", (message_id,))
    if rating > 0 and msg and msg[0]["sql"]:
        _write("INSERT OR REPLACE INTO good_queries (question, sql) VALUES (?,?)",
               (msg[0]["question"], msg[0]["sql"]))


def good_queries() -> list[dict]:
    return _rows("SELECT question, sql FROM good_queries")


def add_uploaded_table(name: str, description: str) -> None:
    _write("INSERT OR REPLACE INTO uploaded_tables (name, description) VALUES (?,?)",
           (name, description))


def uploaded_tables() -> list[dict]:
    return _rows("SELECT name, description FROM uploaded_tables")
