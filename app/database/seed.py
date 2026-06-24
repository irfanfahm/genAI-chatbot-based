import duckdb
import pandas as pd

DB_PATH = "app/database/analytics.duckdb"

def seed():

    conn = duckdb.connect(DB_PATH)

    customers = pd.read_csv("data/customers.csv")
    products = pd.read_csv("data/products.csv")
    sales = pd.read_csv("data/sales.csv")

    conn.execute("CREATE OR REPLACE TABLE customers AS SELECT * FROM customers")
    conn.execute("CREATE OR REPLACE TABLE products AS SELECT * FROM products")
    conn.execute("CREATE OR REPLACE TABLE sales AS SELECT * FROM sales")

    conn.register("customers_view", customers)
    conn.register("products_view", products)
    conn.register("sales_view", sales)

    conn.execute("CREATE OR REPLACE TABLE customers AS SELECT * FROM customers_view")
    conn.execute("CREATE OR REPLACE TABLE products AS SELECT * FROM products_view")
    conn.execute("CREATE OR REPLACE TABLE sales AS SELECT * FROM sales_view")

    print("✅ Database seeded with relational BI data!")

if __name__ == "__main__":
    seed()