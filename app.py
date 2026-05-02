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
# CUSTOM CSS (PREMIUM UI)
# ===============================
st.markdown("""
<style>
.main {
    background-color: #0E1117;
}
h1, h2, h3 {
    color: #FFFFFF;
}
.card {
    background: #1c1f26;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}
.metric {
    font-size: 28px;
    font-weight: bold;
}
.subtext {
    color: #9aa0a6;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# STYLE
# ===============================
plt.style.use('dark_background')
sns.set_style("darkgrid")
sns.set_palette("coolwarm")

# ===============================
# LOAD DATA
# ===============================
file_path = os.path.join("data", "SuperStoreOrders.csv")
df = pd.read_csv(file_path, encoding='latin1')

# ===============================
# CLEAN DATA
# ===============================
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

df['order_date'] = pd.to_datetime(df['order_date'], dayfirst=True, errors='coerce')
df['sales'] = pd.to_numeric(df['sales'], errors='coerce')
df['profit'] = pd.to_numeric(df['profit'], errors='coerce')

df['year'] = df['order_date'].dt.year
df['month'] = df['order_date'].dt.month

# ===============================
# HEADER
# ===============================
st.markdown("## 📊 Business Intelligence Dashboard")
st.markdown("### Real-time insights for smarter decisions")

st.markdown("---")

# ===============================
# SIDEBAR FILTERS
# ===============================
st.sidebar.header("🔍 Filters")

years = sorted(df['year'].dropna().unique())

year = st.sidebar.selectbox("Select Year", ["All"] + list(years))
region = st.sidebar.selectbox("Select Region", ["All"] + list(df['region'].dropna().unique()))

# ===============================
# APPLY FILTERS
# ===============================
filtered_df = df.copy()

if year != "All":
    filtered_df = filtered_df[filtered_df['year'] == year]

if region != "All":
    filtered_df = filtered_df[filtered_df['region'] == region]

# ===============================
# KPIs
# ===============================
total_sales = round(filtered_df['sales'].sum(), 2)
total_profit = round(filtered_df['profit'].sum(), 2)
total_orders = filtered_df.shape[0]

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="card">
        <div class="subtext">Total Sales</div>
        <div class="metric">${total_sales}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card">
        <div class="subtext">Total Profit</div>
        <div class="metric">${total_profit}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card">
        <div class="subtext">Total Orders</div>
        <div class="metric">{total_orders}</div>
    </div>
    """, unsafe_allow_html=True)

# ===============================
# 🧠 SMART INSIGHTS
# ===============================
st.markdown("## 🧠 Key Insights")

if not filtered_df.empty:

    monthly_sales = filtered_df.groupby('month')['sales'].sum()
    best_month = monthly_sales.idxmax()
    worst_month = monthly_sales.idxmin()

    region_profit = filtered_df.groupby('region')['profit'].sum()
    best_region = region_profit.idxmax()
    worst_region = region_profit.idxmin()

    corr = filtered_df[['discount', 'profit']].corr().iloc[0,1]
    total_profit_val = filtered_df['profit'].sum()

    st.markdown(f"""
    <div class="card">
    <b>Business Summary</b><br><br>

    📈 Peak Sales Month: {best_month}<br>
    📉 Weak Month: {worst_month}<br><br>

    💰 Best Region: {best_region}<br>
    ⚠️ Weak Region: {worst_region}<br><br>

    📊 Discount vs Profit Correlation: {round(corr,2)}<br>
    {"High discounts are reducing profit 💸" if corr < 0 else "Discount strategy is stable 👍"}<br><br>

    {"🟢 Overall business is profitable" if total_profit_val > 0 else "🔴 Business is in loss"}
    </div>
    """, unsafe_allow_html=True)

st.markdown("## 📈 Performance Overview")

# ===============================
# LAYOUT
# ===============================
left, right = st.columns(2)

# Sales Trend
with left:
    st.subheader("Sales Trend")
    sales_trend = filtered_df.groupby('month')['sales'].sum()

    fig1, ax1 = plt.subplots()
    sns.lineplot(x=sales_trend.index, y=sales_trend.values, marker='o', linewidth=3, ax=ax1)

    st.pyplot(fig1)

# Profit by Region
with right:
    st.subheader("Profit by Region")
    region_profit = filtered_df.groupby('region')['profit'].sum()

    fig2, ax2 = plt.subplots()
    sns.barplot(x=region_profit.index, y=region_profit.values, palette="viridis", ax=ax2)

    plt.xticks(rotation=45)
    st.pyplot(fig2)

# ===============================
# SECOND ROW
# ===============================
left2, right2 = st.columns(2)

# Scatter
with left2:
    st.subheader("Discount vs Profit")

    fig3, ax3 = plt.subplots()
    sns.scatterplot(
        x=filtered_df['discount'],
        y=filtered_df['profit'],
        hue=filtered_df['region'],
        palette="coolwarm",
        ax=ax3
    )

    st.pyplot(fig3)

# Top Products
with right2:
    st.subheader("Top Products")

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
st.caption("🚀 Built by Mayank | Data Analyst Portfolio Project")
