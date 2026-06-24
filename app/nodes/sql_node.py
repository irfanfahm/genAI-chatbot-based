import re
import pandas as pd
import duckdb
from app.llm.client import llm

DB_PATH = "app/database/analytics.duckdb"

def clean_sql(sql: str) -> str:
    # hapus ```sql dan ```
    sql = re.sub(r"```sql", "", sql)
    sql = re.sub(r"```", "", sql)

    return sql.strip()

def sql_node(state):

    question = state.get("question", "")

    prompt = f"""
    You are a senior data analyst.

    You have 3 tables:

    1. sales(
        order_id,
        customer_id,
        product_id,
        quantity,
        revenue,
        discount,
        date
    )

    2. customers(
        customer_id,
        name,
        segment,
        city,
        join_date
    )

    3. products(
        product_id,
        product_name,
        category,
        price
    )

    Rules:
    - Use DuckDB SQL
    - You can JOIN tables
    - Always return valid SQL only

    Question:
    {question}
    """

    sql = llm(prompt)

    # 🔥 CLEAN OUTPUT
    sql = clean_sql(sql)

    conn = duckdb.connect(DB_PATH)

    try:
        df = conn.execute(sql).fetchdf()
    except Exception as e:
        df = pd.DataFrame()
    # df = conn.execute(sql).fetchdf()

    return {
    **state,
    "sql": sql,
    "data": df.to_dict(orient="records")
    }