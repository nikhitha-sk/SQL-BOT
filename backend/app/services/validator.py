"""SQL safety checks with SQLGlot: one read-only SELECT on allowed tables, with a LIMIT."""
import sqlglot
from sqlglot import exp

from app.config import ROW_LIMIT

BLOCKED = (exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Create, exp.Alter,
           exp.Command, exp.Pragma, exp.Attach, exp.Detach, exp.Merge, exp.TruncateTable)


class UnsafeSQLError(ValueError):
    pass


def validate(sql: str, allowed_tables: set[str]) -> str:
    """Return a safe version of the SQL, or raise UnsafeSQLError."""
    try:
        statements = [s for s in sqlglot.parse(sql, read="sqlite") if s is not None]
    except sqlglot.errors.ParseError as e:
        raise UnsafeSQLError(f"Could not parse SQL: {e}") from e

    if len(statements) != 1:
        raise UnsafeSQLError("Only one SQL statement is allowed.")
    tree = statements[0]

    if not isinstance(tree, exp.Query) or any(tree.find_all(*BLOCKED)):
        raise UnsafeSQLError("Only read queries (SELECT) are allowed.")

    cte_names = {cte.alias_or_name.lower() for cte in tree.find_all(exp.CTE)}
    used = {t.name.lower() for t in tree.find_all(exp.Table)} - cte_names
    allowed = {t.lower() for t in allowed_tables}
    blocked = used - allowed
    if blocked:
        raise UnsafeSQLError(f"Table not allowed: {', '.join(sorted(blocked))}")

    limit = tree.args.get("limit")
    if limit is None:
        tree = tree.limit(ROW_LIMIT)
    else:
        try:
            if int(limit.expression.name) > ROW_LIMIT:
                tree = tree.limit(ROW_LIMIT)
        except (AttributeError, ValueError):
            tree = tree.limit(ROW_LIMIT)

    return tree.sql(dialect="sqlite")
