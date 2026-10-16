"""Creates the sample business database (an Indian e-commerce store)."""
import random
import sqlite3
from datetime import date, timedelta

from app.config import BUSINESS_DB

CITIES = [
    ("Bengaluru", "Karnataka"), ("Mysuru", "Karnataka"), ("Mangaluru", "Karnataka"),
    ("Mumbai", "Maharashtra"), ("Pune", "Maharashtra"), ("Chennai", "Tamil Nadu"),
    ("Coimbatore", "Tamil Nadu"), ("Hyderabad", "Telangana"), ("Delhi", "Delhi"),
    ("Kolkata", "West Bengal"), ("Ahmedabad", "Gujarat"), ("Kochi", "Kerala"),
]
FIRST = ["Aarav", "Diya", "Rohan", "Ananya", "Vikram", "Meera", "Arjun", "Kavya", "Rahul",
         "Sneha", "Karthik", "Pooja", "Nikhil", "Isha", "Aditya", "Riya", "Sanjay", "Neha"]
LAST = ["Sharma", "Rao", "Iyer", "Patel", "Reddy", "Nair", "Gupta", "Shetty", "Das", "Kumar"]
PRODUCTS = [
    ("Wireless Mouse", "Electronics", 799), ("Bluetooth Speaker", "Electronics", 2499),
    ("Smart Watch", "Electronics", 4999), ("USB-C Charger", "Electronics", 1199),
    ("Noise Cancelling Headphones", "Electronics", 7999), ("Cotton T-Shirt", "Clothing", 499),
    ("Denim Jeans", "Clothing", 1599), ("Running Shoes", "Clothing", 3299),
    ("Rain Jacket", "Clothing", 2199), ("Coffee Mug", "Home", 349), ("Bedsheet Set", "Home", 1299),
    ("Table Lamp", "Home", 1899), ("Non-stick Pan", "Home", 1499), ("Yoga Mat", "Sports", 899),
    ("Cricket Bat", "Sports", 2999), ("Football", "Sports", 699), ("Notebook Pack", "Stationery", 249),
    ("Gel Pen Set", "Stationery", 199), ("Backpack", "Accessories", 1799),
    ("Sunglasses", "Accessories", 1299),
]
STATUSES = ["delivered"] * 8 + ["shipped", "cancelled", "returned"]

SCHEMA = """
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY, name TEXT, city TEXT, state TEXT, signup_date DATE);
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL);
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY, customer_id INTEGER REFERENCES customers(customer_id),
    order_date DATE, status TEXT, total_amount REAL);
CREATE TABLE order_items (
    order_id INTEGER REFERENCES orders(order_id), product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER, unit_price REAL);
"""


def seed(path=BUSINESS_DB, today: date | None = None) -> None:
    rnd = random.Random(42)
    today = today or date.today()
    start = date(today.year - 1, 1, 1)
    days = (today - start).days

    if path.exists():
        path.unlink()
    con = sqlite3.connect(path)
    con.executescript(SCHEMA)

    for i in range(1, 201):
        city, state = rnd.choice(CITIES)
        signup = start + timedelta(days=rnd.randint(0, days))
        con.execute("INSERT INTO customers VALUES (?,?,?,?,?)",
                    (i, f"{rnd.choice(FIRST)} {rnd.choice(LAST)}", city, state, signup.isoformat()))

    for i, (name, cat, price) in enumerate(PRODUCTS, 1):
        con.execute("INSERT INTO products VALUES (?,?,?,?)", (i, name, cat, price))

    for order_id in range(1, 2001):
        customer = rnd.randint(1, 200)
        order_date = start + timedelta(days=rnd.randint(0, days))
        total = 0.0
        for product_id in rnd.sample(range(1, len(PRODUCTS) + 1), rnd.randint(1, 3)):
            qty = rnd.randint(1, 4)
            price = PRODUCTS[product_id - 1][2]
            total += qty * price
            con.execute("INSERT INTO order_items VALUES (?,?,?,?)", (order_id, product_id, qty, price))
        con.execute("INSERT INTO orders VALUES (?,?,?,?,?)",
                    (order_id, customer, order_date.isoformat(), rnd.choice(STATUSES), total))

    con.commit()
    con.close()


if __name__ == "__main__":
    seed()
    print(f"Sample data written to {BUSINESS_DB}")
