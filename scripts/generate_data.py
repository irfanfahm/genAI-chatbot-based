import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()
np.random.seed(42)
random.seed(42)

# =========================
# CONFIG
# =========================
NUM_CUSTOMERS = 500
NUM_PRODUCTS = 50
NUM_SALES = 10000

# =========================
# 1. CUSTOMERS
# =========================
segments = ["Enterprise", "SMB", "Startup"]

customers = []
for i in range(1, NUM_CUSTOMERS + 1):
    customers.append({
        "customer_id": i,
        "name": fake.name(),
        "segment": random.choice(segments),
        "city": fake.city(),
        "join_date": fake.date_between(start_date="-3y", end_date="-1y")
    })

df_customers = pd.DataFrame(customers)

# =========================
# 2. PRODUCTS
# =========================
categories = ["Electronics", "Furniture", "Office", "Software"]

products_master = [
    ("Laptop Pro 14", "Electronics", 18000000),
    ("Laptop Air 13", "Electronics", 12000000),
    ("Mechanical Keyboard", "Electronics", 850000),
    ("Wireless Mouse", "Electronics", 350000),
    ("27 Inch Monitor", "Electronics", 3200000),
    ("Office Chair", "Furniture", 2500000),
    ("Standing Desk", "Furniture", 4500000),
    ("Meeting Table", "Furniture", 3500000),
    ("CRM Software", "Software", 5000000),
    ("Analytics Dashboard", "Software", 7000000),
    ("Project Management Suite", "Software", 4500000),
    ("Business Intelligence Platform", "Software", 9000000),
    ("Cloud Storage Package", "Software", 1200000),
    ("Printer LaserJet", "Office", 2800000),
    ("Scanner Pro", "Office", 1800000),
    ("Document Management System", "Software", 6500000),
    ("Accounting Software", "Software", 5500000),
    ("HR Management System", "Software", 6000000),
    ("Network Switch", "Electronics", 2200000),
    ("Business Laptop Elite", "Electronics", 21000000)
]

products = []

for idx, (name, category, price) in enumerate(products_master, start=1):
    products.append({
        "product_id": idx,
        "product_name": name,
        "category": category,
        "price": price
    })

df_products = pd.DataFrame(products)

NUM_PRODUCTS = len(df_products)

# products = []
# for i in range(1, NUM_PRODUCTS + 1):
#     products.append({
#         "product_id": i,
#         "product_name": fake.word().capitalize(),
#         "category": random.choice(categories),
#         "price": random.randint(100000, 20000000)
#     })

# df_products = pd.DataFrame(products)

# =========================
# 3. SALES (FACT TABLE)
# =========================
sales = []

start_date = datetime(2023, 1, 1)

for i in range(1, NUM_SALES + 1):

    customer = random.randint(1, NUM_CUSTOMERS)
    product = random.choice(df_products["product_id"].tolist())

    product_price = df_products.loc[df_products["product_id"] == product, "price"].values[0]

    date = start_date + timedelta(days=random.randint(0, 700))

    quantity = random.randint(1, 5)

    # add noise + discount simulation
    discount = random.choice([0, 0.05, 0.1, 0.15])

    revenue = int(product_price * quantity * (1 - discount))

    sales.append({
        "order_id": i,
        "customer_id": customer,
        "product_id": product,
        "quantity": quantity,
        "revenue": revenue,
        "discount": discount,
        "date": date.date()
    })

df_sales = pd.DataFrame(sales)

# =========================
# SAVE CSV
# =========================
df_customers.to_csv("data/customers.csv", index=False)
df_products.to_csv("data/products.csv", index=False)
df_sales.to_csv("data/sales.csv", index=False)

print("✅ Synthetic dataset generated!")
print("Customers:", len(df_customers))
print("Products:", len(df_products))
print("Sales:", len(df_sales))