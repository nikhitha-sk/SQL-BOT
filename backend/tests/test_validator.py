import pytest

from app.services.validator import UnsafeSQLError, validate

TABLES = {"customers", "orders", "products", "order_items"}


def test_select_gets_limit():
    assert validate("SELECT name FROM customers", TABLES).endswith("LIMIT 1000")


def test_keeps_small_limit():
    assert validate("SELECT name FROM customers LIMIT 5", TABLES).endswith("LIMIT 5")


def test_caps_big_limit():
    assert validate("SELECT name FROM customers LIMIT 99999", TABLES).endswith("LIMIT 1000")


def test_cte_is_allowed():
    sql = "WITH t AS (SELECT state FROM customers) SELECT state, COUNT(*) FROM t GROUP BY state"
    assert "LIMIT 1000" in validate(sql, TABLES)


@pytest.mark.parametrize("sql", [
    "DELETE FROM orders",
    "DROP TABLE customers",
    "UPDATE orders SET status = 'x'",
    "INSERT INTO products VALUES (1, 'a', 'b', 1)",
    "ALTER TABLE orders ADD COLUMN x INT",
    "PRAGMA table_info(orders)",
    "SELECT 1; DROP TABLE orders",
])
def test_blocks_unsafe(sql):
    with pytest.raises(UnsafeSQLError):
        validate(sql, TABLES)


def test_blocks_unknown_table():
    with pytest.raises(UnsafeSQLError, match="not allowed"):
        validate("SELECT * FROM sqlite_master", TABLES)
