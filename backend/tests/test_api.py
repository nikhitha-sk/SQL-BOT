"""API tests with a fake LLM, so no API key is needed."""
from app.services import llm, pipeline


def fake_llm(monkeypatch, answers):
    answers = list(answers)

    def generate_sql(prompt, usage):
        usage["input_tokens"] += 100
        return answers.pop(0)

    monkeypatch.setattr(llm, "generate_sql", generate_sql)
    monkeypatch.setattr(llm, "explain", lambda *a: "Test explanation.")
    pipeline.clear_cache()


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_schema_lists_tables(client):
    names = {t["name"] for t in client.get("/api/schema").json()}
    assert {"customers", "products", "orders", "order_items"} <= names


def test_chat_returns_chart_and_rows(client, monkeypatch):
    fake_llm(monkeypatch, [{"sql": "SELECT category, COUNT(*) AS n FROM products GROUP BY category", "reason": ""}])
    res = client.post("/api/chat", json={"question": "products per category", "session_id": "t1"}).json()
    assert res["status"] == "ok"
    assert res["chart"]["type"] == "bar"
    assert res["sql"].endswith("LIMIT 1000")
    assert res["explanation"] == "Test explanation."


def test_auto_fix_retries_bad_sql(client, monkeypatch):
    fake_llm(monkeypatch, [
        {"sql": "SELECT wrong_column FROM products", "reason": ""},
        {"sql": "SELECT COUNT(*) AS total FROM products", "reason": ""},
    ])
    res = client.post("/api/chat", json={"question": "how many products", "session_id": "t2"}).json()
    assert res["status"] == "ok"
    assert res["attempts"] == 2
    assert res["chart"]["type"] == "number"


def test_delete_is_blocked(client, monkeypatch):
    fake_llm(monkeypatch, [{"sql": "DELETE FROM orders", "reason": ""}])
    res = client.post("/api/chat", json={"question": "delete all orders", "session_id": "t3"}).json()
    assert res["status"] == "blocked"
    assert "Only read queries" in res["error"]


def test_feedback_saves_good_query(client, monkeypatch):
    fake_llm(monkeypatch, [{"sql": "SELECT COUNT(*) AS customers FROM customers", "reason": ""}])
    res = client.post("/api/chat", json={"question": "count customers", "session_id": "t4"}).json()
    client.post("/api/feedback", json={"message_id": res["id"], "rating": 1})
    assert client.get("/api/stats").json()["good_queries"] >= 1


def test_csv_upload(client):
    csv = b"employee,department,salary\nAsha,HR,50000\nRavi,IT,70000\n"
    res = client.post("/api/upload", files={"file": ("staff.csv", csv, "text/csv")}).json()
    assert res == {"table": "csv_staff", "rows": 2, "columns": ["employee", "department", "salary"]}
