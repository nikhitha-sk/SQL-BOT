"""Runs SQL on a read-only connection with a timeout."""
import sqlite3
import time

from app.config import BUSINESS_DB, QUERY_TIMEOUT_SECONDS


class QueryError(RuntimeError):
    pass


def run(sql: str, timeout: float = QUERY_TIMEOUT_SECONDS) -> dict:
    # mode=ro: the database itself refuses writes, even if a bad query gets through.
    con = sqlite3.connect(f"file:{BUSINESS_DB.as_posix()}?mode=ro", uri=True)
    deadline = time.monotonic() + timeout
    con.set_progress_handler(lambda: 1 if time.monotonic() > deadline else 0, 10_000)
    try:
        cur = con.execute(sql)
        columns = [d[0] for d in cur.description or []]
        rows = [list(r) for r in cur.fetchall()]
    except sqlite3.OperationalError as e:
        if "interrupted" in str(e):
            raise QueryError(f"Query stopped after {timeout:g} seconds.") from e
        raise QueryError(str(e)) from e
    except sqlite3.Error as e:
        raise QueryError(str(e)) from e
    finally:
        con.close()
    return {"columns": columns, "rows": rows}


def table_names() -> set[str]:
    con = sqlite3.connect(f"file:{BUSINESS_DB.as_posix()}?mode=ro", uri=True)
    try:
        return {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    finally:
        con.close()


def sample_rows(table: str, n: int = 2) -> dict:
    return run(f'SELECT * FROM "{table}" LIMIT {n}')
