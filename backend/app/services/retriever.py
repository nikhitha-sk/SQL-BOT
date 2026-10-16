"""RAG context retriever.

Finds the table docs, glossary terms and approved past queries that best match
a question. Uses a small TF-IDF search in pure Python, so no vector database is
needed to run the project.
"""
import math
import re
from collections import Counter

from app.db import app_db

SCHEMA_DOCS = {
    "customers": {
        "description": "People who buy from the store. Use for customer counts, cities, states and signups.",
        "columns": {
            "customer_id": "unique customer id",
            "name": "customer full name",
            "city": "city where the customer lives, e.g. Bengaluru, Mumbai",
            "state": "Indian state, e.g. Karnataka, Maharashtra, Tamil Nadu",
            "signup_date": "date the customer joined (YYYY-MM-DD)",
        },
    },
    "products": {
        "description": "Items the store sells, with category and list price in rupees.",
        "columns": {
            "product_id": "unique product id",
            "name": "product name",
            "category": "Electronics, Clothing, Home, Sports, Stationery or Accessories",
            "price": "list price in INR",
        },
    },
    "orders": {
        "description": "One row per order. Use for sales, revenue, order counts and dates.",
        "columns": {
            "order_id": "unique order id",
            "customer_id": "who placed the order (customers.customer_id)",
            "order_date": "date of the order (YYYY-MM-DD)",
            "status": "delivered, shipped, cancelled or returned",
            "total_amount": "order value in INR",
        },
    },
    "order_items": {
        "description": "Products inside each order. Use for units sold and sales per product or category.",
        "columns": {
            "order_id": "the order (orders.order_id)",
            "product_id": "the product (products.product_id)",
            "quantity": "units bought",
            "unit_price": "price per unit in INR at time of order",
        },
    },
}

GLOSSARY = {
    "revenue": "SUM(orders.total_amount) for orders where status IN ('delivered','shipped'). Cancelled and returned orders are not revenue.",
    "sales": "Same as revenue unless the user asks for units. Units sold = SUM(order_items.quantity).",
    "active customer": "A customer with at least one order in the last 90 days.",
    "new customer": "A customer whose signup_date is in the given period.",
    "average order value": "AOV = revenue / number of non-cancelled, non-returned orders.",
    "best selling product": "Product with the highest SUM(order_items.quantity) on delivered or shipped orders.",
    "cancellation rate": "Cancelled orders / all orders, as a percentage.",
    "last month": "The full previous calendar month relative to today's date.",
    "this year": "From January 1 of the current year until today.",
    "region": "Means customers.state unless the user says city.",
}


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", text.lower().replace("_", " "))
    return [w[:-1] if len(w) > 3 and w.endswith("s") else w for w in words]


def _table_doc(name: str, info: dict) -> str:
    cols = "\n".join(f"  - {c}: {d}" for c, d in info["columns"].items())
    return f"Table {name}: {info['description']}\n{cols}"


def build_docs() -> list[dict]:
    docs = [{"kind": "table", "key": n, "text": _table_doc(n, i)} for n, i in SCHEMA_DOCS.items()]
    for t in app_db.uploaded_tables():
        docs.append({"kind": "table", "key": t["name"], "text": t["description"]})
    docs += [{"kind": "glossary", "key": k, "text": f"{k}: {v}"} for k, v in GLOSSARY.items()]
    docs += [{"kind": "example", "key": q["question"], "text": f"Q: {q['question']}\nSQL: {q['sql']}"}
             for q in app_db.good_queries()]
    return docs


def retrieve(question: str, tables_k: int = 4, glossary_k: int = 3, examples_k: int = 3) -> dict:
    docs = build_docs()
    tokenized = [Counter(tokenize(d["text"] + " " + d["key"])) for d in docs]
    df = Counter(w for t in tokenized for w in t)
    n = len(docs)
    query = set(tokenize(question))

    def score(tokens: Counter) -> float:
        return sum((1 + math.log(tokens[w])) * math.log(1 + n / df[w]) for w in query if w in tokens)

    ranked = sorted(zip(docs, map(score, tokenized)), key=lambda x: -x[1])
    pick = lambda kind, k, need_hit: [d for d, s in ranked if d["kind"] == kind and (s > 0 or not need_hit)][:k]
    return {
        "tables": pick("table", tables_k, False),
        "glossary": pick("glossary", glossary_k, True),
        "examples": pick("example", examples_k, True),
    }
