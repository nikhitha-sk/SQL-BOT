"""Picks a chart type from the shape of the result."""
import re

SHARE_WORDS = {"share", "percent", "percentage", "proportion", "distribution", "split", "breakdown", "pie"}
DATE_RE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")
DATE_NAMES = ("date", "month", "year", "day", "week", "period", "quarter")


def column_kind(name: str, values: list) -> str:
    vals = [v for v in values if v is not None]
    if not vals:
        return "text"
    if all(isinstance(v, str) and DATE_RE.match(v) for v in vals):
        return "date"
    if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in vals):
        if any(w in name.lower() for w in ("year", "month")) and all(isinstance(v, int) for v in vals):
            return "date"
        return "number"
    return "text"


def pick_chart(columns: list[str], rows: list[list], question: str = "") -> dict:
    if not rows:
        return {"type": "table"}
    kinds = [column_kind(c, [r[i] for r in rows]) for i, c in enumerate(columns)]

    if len(rows) == 1 and len(columns) == 1 and kinds[0] == "number":
        return {"type": "number", "label": columns[0]}

    if len(columns) == 2:
        x, y = 0, 1
        if kinds[0] == "number" and kinds[1] in ("date", "text"):
            x, y = 1, 0
        pair = {kinds[x], kinds[y]}
        if kinds[y] == "number" and kinds[x] == "date":
            return {"type": "line", "x": columns[x], "y": columns[y]}
        if kinds[y] == "number" and kinds[x] == "text":
            words = set(re.findall(r"[a-z]+", question.lower()))
            if len(rows) <= 5 and words & SHARE_WORDS:
                return {"type": "pie", "x": columns[x], "y": columns[y]}
            return {"type": "bar", "x": columns[x], "y": columns[y]}
        if pair == {"number"}:
            return {"type": "scatter", "x": columns[0], "y": columns[1]}

    return {"type": "table"}
