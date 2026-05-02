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
# PREMIUM CSS
# ===============================
st.markdown("""
<style>
.main {background-color:#0E1117;}
.card {
    background:#1c1f26;
    padding:20px;
    border-radius:12px;
    box-shadow:0 4px 20px rgba(0,0,0,0.4);
}
.metric {font-size:28px;font-weight:bold;}
.subtext {color:#9aa0a6;font-size:14px;}
#MainMenu, footer, header {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ===============================
# STYLE
# ===============================
plt.style.use('dark_background')
sns.set_style("darkgrid")

# ===============================
# LOADING EFFECT
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

# ===============================
# SIDEBAR FILTERS
# ===============================
st.sidebar.header("🔍 Filters")

years = sorted(df['year'].dropna().unique())
year = st.sidebar.selectbox("Select Year", ["All"] + list(years))
region = st.sidebar.selectbox("Select Region", ["All"] + list(df['region'].dropna().unique()))

filtered_df = df.copy()

if year != "All":
    filtered_df = filtered_df[filtered_df['year'] == year]

if region != "All":
    filtered_df = filtered_df[filtered_df['region'] == region]

# ===============================
# KPI FUNCTION
# ===============================
def color_metric(value):
    return "#00FF9C" if value > 0 else "#FF4B4B"

# ===============================
# KPIs
# ===============================
total_sales = round(filtered_df['sales'].sum(), 2)
total_profit = round(filtered_df['profit'].sum(), 2)
total_orders = filtered_df.shape[0]

col1, col2, col3 = st.columns(3)

col1.markdown(f"<div class='card'><div class='subtext'>Total Sales</div><div class='metric'>${total_sales}</div></div>", unsafe_allow_html=True)

col2.markdown(f"<div class='card'><div class='subtext'>Total Profit</div><div class='metric' style='color:{color_metric(total_profit)};'>${total_profit}</div></div>", unsafe_allow_html=True)

col3.markdown(f"<div class='card'><div class='subtext'>Orders</div><div class='metric'>{total_orders}</div></div>", unsafe_allow_html=True)

# ===============================
# INSIGHTS CALCULATION
# ===============================
monthly_sales = filtered_df.groupby('month')['sales'].sum()
best_month = monthly_sales.idxmax()
worst_month = monthly_sales.idxmin()

region_profit = filtered_df.groupby('region')['profit'].sum()
best_region = region_profit.idxmax()
worst_region = region_profit.idxmin()

corr = filtered_df[['discount', 'profit']].corr().iloc[0,1]

# ===============================
# EXECUTIVE SUMMARY
# ===============================
st.markdown("## 📌 Executive Summary")

summary = f"""
In {year if year!='All' else 'all selected years'}, the business generated **${total_sales}** in sales 
and **${total_profit}** in profit.

The strongest region is **{best_region}**, while **{worst_region} needs attention**.

Sales peaked in **month {best_month}**, indicating demand trends.

Discount vs profit correlation is **{round(corr,2)}**, suggesting 
{'discounting is hurting profit' if corr < 0 else 'discounting is stable'}.
"""

st.markdown(f"<div class='card'>{summary}</div>", unsafe_allow_html=True)

# ===============================
# TABS
# ===============================
tab1, tab2, tab3 = st.tabs(["📊 Overview", "📈 Trends", "🔮 Forecast"])

# ===============================
# OVERVIEW TAB
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
# TRENDS TAB
# ===============================
with tab2:
    st.subheader("Discount vs Profit")
    fig3, ax3 = plt.subplots()
    sns.scatterplot(x=filtered_df['discount'], y=filtered_df['profit'], hue=filtered_df['region'], ax=ax3)
    st.pyplot(fig3)

# ===============================
# 🔮 FORECAST TAB
# ===============================
with tab3:
    st.subheader("Future Sales Prediction")

    if len(monthly_sales) > 1:
        x = np.array(monthly_sales.index)
        y = np.array(monthly_sales.values)

        # Linear regression
        coeff = np.polyfit(x, y, 1)
        poly = np.poly1d(coeff)

        future_months = np.arange(1, 13)
        predicted = poly(future_months)

        fig4, ax4 = plt.subplots()
        ax4.plot(x, y, label="Actual", marker='o')
        ax4.plot(future_months, predicted, linestyle="dashed", label="Predicted")

        ax4.legend()
        st.pyplot(fig4)

        st.markdown(f"""
        <div class='card'>
        📊 Based on trend, future sales are expected to follow a 
        {"growing 📈" if coeff[0] > 0 else "declining 📉"} pattern.
        </div>
        """, unsafe_allow_html=True)

# ===============================
# DOWNLOAD BUTTON
# ===============================
csv = filtered_df.to_csv(index=False).encode('utf-8')

st.download_button("📥 Download Data", csv, "filtered_data.csv")

# ===============================
# FOOTER
# ===============================
st.markdown("---")
st.caption("🚀 Built by Mayank | Premium Data Analyst Dashboard")
