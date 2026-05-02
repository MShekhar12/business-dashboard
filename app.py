import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="Business Dashboard", layout="wide")

# ===============================
# LOAD DATA
# ===============================
file_path = os.path.join("data", "SuperStoreOrders.csv")
df = pd.read_csv(file_path, encoding='latin1')

# ===============================
# CLEAN DATA
# ===============================
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Convert types
df['order_date'] = pd.to_datetime(df['order_date'], dayfirst=True, errors='coerce')
df['sales'] = pd.to_numeric(df['sales'], errors='coerce')
df['profit'] = pd.to_numeric(df['profit'], errors='coerce')

# Extract date parts
df['year'] = df['order_date'].dt.year
df['month'] = df['order_date'].dt.month

# ===============================
# STYLE
# ===============================
sns.set_style("darkgrid")

# ===============================
# TITLE
# ===============================
st.title("📊 Smart Business Dashboard")
st.markdown("### Real-time business insights 💡")

st.markdown("---")

# ===============================
# SIDEBAR FILTERS
# ===============================
st.sidebar.header("🔍 Filters")

year = st.sidebar.selectbox(
    "Select Year",
    sorted(df['year'].dropna().unique())
)

region = st.sidebar.selectbox(
    "Select Region",
    ["All"] + list(df['region'].dropna().unique())
)

# Apply filters
filtered_df = df[df['year'] == year]

if region != "All":
    filtered_df = filtered_df[filtered_df['region'] == region]

# ===============================
# KPIs
# ===============================
total_sales = round(filtered_df['sales'].sum(), 2)
total_profit = round(filtered_df['profit'].sum(), 2)
total_orders = filtered_df.shape[0]

col1, col2, col3 = st.columns(3)

col1.metric("💰 Total Sales", f"${total_sales}")
col2.metric("📈 Total Profit", f"${total_profit}")
col3.metric("🧾 Total Orders", total_orders)

st.markdown("---")

# ===============================
# SALES OVER TIME
# ===============================
st.subheader("📅 Sales Trend")

sales_trend = filtered_df.groupby('month')['sales'].sum()

fig1, ax1 = plt.subplots()
sns.lineplot(x=sales_trend.index, y=sales_trend.values, marker='o', ax=ax1)

ax1.set_xlabel("Month")
ax1.set_ylabel("Sales")

st.pyplot(fig1)

# ===============================
# PROFIT BY REGION
# ===============================
st.subheader("🌍 Profit by Region")

region_profit = filtered_df.groupby('region')['profit'].sum()

fig2, ax2 = plt.subplots()
sns.barplot(x=region_profit.index, y=region_profit.values, ax=ax2)

plt.xticks(rotation=45)

st.pyplot(fig2)

# ===============================
# DISCOUNT VS PROFIT
# ===============================
st.subheader("💸 Discount vs Profit")

fig3, ax3 = plt.subplots()
sns.scatterplot(x=filtered_df['discount'], y=filtered_df['profit'], ax=ax3)

st.pyplot(fig3)

# ===============================
# TOP PRODUCTS
# ===============================
st.subheader("🏆 Top 5 Products")

top_products = (
    filtered_df.groupby('product_name')['sales']
    .sum()
    .sort_values(ascending=False)
    .head(5)
)

st.dataframe(top_products)

# ===============================
# FOOTER
# ===============================
st.markdown("---")
st.caption("Built with ❤️ using Streamlit | Data Analyst Portfolio Project")
