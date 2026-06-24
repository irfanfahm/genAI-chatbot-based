import streamlit as st
import pandas as pd
import plotly.express as px

from app.graph.graph import app

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="AI Data Analyst Copilot", layout="wide")

st.title("🧠 AI Data Analyst Copilot")

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    sales = pd.read_csv("data/sales.csv")
    customers = pd.read_csv("data/customers.csv")
    products = pd.read_csv("data/products.csv")
    return sales, customers, products

sales, customers, products = load_data()

# =========================
# SIDEBAR KPI
# =========================
st.sidebar.header("📊 KPI Summary")

total_revenue = sales["revenue"].sum()
total_orders = len(sales)
avg_order = sales["revenue"].mean()

st.sidebar.metric("Total Revenue", f"{total_revenue:,.0f}")
st.sidebar.metric("Total Orders", total_orders)
st.sidebar.metric("Avg Order Value", f"{avg_order:,.0f}")

# =========================
# VISUAL SUMMARY
# =========================
st.subheader("📈 Revenue by Product Category")

merged = sales.merge(products, on="product_id")

cat_rev = merged.groupby("category")["revenue"].sum().reset_index()

fig1 = px.bar(cat_rev, x="category", y="revenue", title="Revenue by Category")
st.plotly_chart(fig1, use_container_width=True)

# =========================
# CUSTOMER SEGMENT ANALYSIS
# =========================
st.subheader("👥 Revenue by Customer Segment")

merged2 = sales.merge(customers, on="customer_id")

seg_rev = merged2.groupby("segment")["revenue"].sum().reset_index()

fig2 = px.pie(seg_rev, names="segment", values="revenue")
st.plotly_chart(fig2, use_container_width=True)

# =========================
# CHAT AI ANALYST
# =========================
st.subheader("💬 Ask AI Data Analyst")

question = st.text_input("Ask your business question:")

if st.button("Analyze"):

    if question:

        with st.spinner("Analyzing data..."):

            result = app.invoke({
                "question": question
            })

            st.markdown("### 🧠 AI Answer")
            st.write(result.get("final_answer", "No answer"))

    else:
        st.warning("Please enter a question")