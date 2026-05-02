import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
import time

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="Business Dashboard", layout="wide")

# ===============================
# FIXED CSS (IMPORTANT)
# ===============================
st.markdown("""
<style>
/* Font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Background */
.main {
    background-color: #0F172A;
}

/* Cards */
.card {
    background: #1E293B;
    padding: 22px;
    border-radius: 14px;
    box-shadow: 0 6px 24px rgba(0,0,0,0.35);
}

/* KPI */
.metric {
    font-size: 30px;
    font-weight: 700;
    color: #E2E8F0;
}

.subtext {
    color: #94A3B8;
    font-size: 13px;
}

/* Headings */
h1, h2, h3 {
    color: #E2E8F0;
}

/* Hide Streamlit UI */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ===============================
# STYLE
# ===============================
plt.style.use('dark_background')
sns.set_palette(["#14B8A6", "#38BDF8", "#6366F1"])

# ===============================
# LOADING
# ===============================
with st.spinner("Analyzing business data..."):
    time.sleep(1)

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

# Convert month number → name (fix ugly 11.0 issue)
df['month_name'] = df['order_date'].dt.strftime('%b')

# ===============================
# SIDEBAR
# ===============================
st.sidebar.header("Filters")

years = sorted(df['year'].dropna().unique())
year = st.sidebar.selectbox("Select Year", ["All"] + list(years))
region = st.sidebar.selectbox("Select Region", ["All"] + list(df['region'].dropna().unique()))

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

def color_metric(value):
    return "#14B8A6" if value > 0 else "#EF4444"

col1, col2, col3 = st.columns(3)

col1.markdown(f"""
<div class='card'>
<div class='subtext'>Total Sales</div>
<div class='metric'>${total_sales:,.0f}</div>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class='card'>
<div class='subtext'>Total Profit</div>
<div class='metric' style='color:{color_metric(total_profit)};'>${total_profit:,.0f}</div>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class='card'>
<div class='subtext'>Total Orders</div>
<div class='metric'>{total_orders:,}</div>
</div>
""", unsafe_allow_html=True)

# ===============================
# INSIGHTS
# ===============================
monthly_sales = filtered_df.groupby('month_name')['sales'].sum()
best_month = monthly_sales.idxmax()
worst_month = monthly_sales.idxmin()

region_profit = filtered_df.groupby('region')['profit'].sum()
best_region = region_profit.idxmax()
worst_region = region_profit.idxmin()

corr = filtered_df[['discount', 'profit']].corr().iloc[0,1]

# ===============================
# EXECUTIVE SUMMARY
# ===============================
st.markdown("## Executive Summary")

summary = f"""
In {year if year!='All' else 'all years'}, the business generated ${total_sales:,.0f} in sales 
and ${total_profit:,.0f} in profit.

The strongest region is {best_region}, while {worst_region} requires attention.

Sales peaked in {best_month}, indicating demand patterns.

Discount vs profit correlation is {round(corr,2)}, suggesting 
{'discounting is reducing profitability' if corr < 0 else 'discounting remains stable'}.
"""

st.markdown(f"<div class='card'>{summary}</div>", unsafe_allow_html=True)

# ===============================
# TABS
# ===============================
tab1, tab2, tab3 = st.tabs(["Overview", "Trends", "Forecast"])

# ===============================
# OVERVIEW
# ===============================
with tab1:
    colA, colB = st.columns(2)

    with colA:
        st.subheader("Sales Trend")
        fig1, ax1 = plt.subplots()
        sns.lineplot(x=monthly_sales.index, y=monthly_sales.values, marker='o', ax=ax1)
        st.pyplot(fig1)

    with colB:
        st.subheader("Profit by Region")
        fig2, ax2 = plt.subplots()
        sns.barplot(x=region_profit.index, y=region_profit.values, ax=ax2)
        plt.xticks(rotation=45)
        st.pyplot(fig2)

# ===============================
# TRENDS
# ===============================
with tab2:
    st.subheader("Discount vs Profit")
    fig3, ax3 = plt.subplots()
    sns.scatterplot(x=filtered_df['discount'], y=filtered_df['profit'], hue=filtered_df['region'], ax=ax3)
    st.pyplot(fig3)

# ===============================
# FORECAST
# ===============================
with tab3:
    st.subheader("Future Sales Prediction")

    if len(monthly_sales) > 1:
        x = np.arange(len(monthly_sales))
        y = monthly_sales.values

        coeff = np.polyfit(x, y, 1)
        poly = np.poly1d(coeff)

        future_x = np.arange(len(monthly_sales) + 3)
        predicted = poly(future_x)

        fig4, ax4 = plt.subplots()
        ax4.plot(x, y, marker='o', label="Actual")
        ax4.plot(future_x, predicted, linestyle="dashed", label="Forecast")
        ax4.legend()

        st.pyplot(fig4)

# ===============================
# DOWNLOAD
# ===============================
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("Download Data", csv, "filtered_data.csv")

# ===============================
# FOOTER
# ===============================
st.markdown("---")
st.caption("Business Intelligence Dashboard")
