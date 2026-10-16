from app.services.charts import pick_chart


def test_number_card():
    assert pick_chart(["revenue"], [[12345.5]])["type"] == "number"


def test_line_for_dates():
    rows = [["2025-01", 10], ["2025-02", 20]]
    assert pick_chart(["month", "revenue"], rows)["type"] == "line"


def test_bar_for_categories():
    rows = [[f"p{i}", i] for i in range(8)]
    assert pick_chart(["product", "units"], rows)["type"] == "bar"


def test_pie_for_share():
    rows = [["Electronics", 50], ["Home", 30], ["Sports", 20]]
    assert pick_chart(["category", "revenue"], rows, "share of revenue by category")["type"] == "pie"


def test_scatter_for_two_numbers():
    assert pick_chart(["price", "units"], [[1, 2], [3, 4]])["type"] == "scatter"


def test_table_otherwise():
    assert pick_chart(["a", "b", "c"], [["x", "y", 1]])["type"] == "table"
