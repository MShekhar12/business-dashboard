import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
df = pd.read_csv("data/SuperStoreOrders.csv")
df.columns = df.columns.str.strip().str.lower().str.replace(" ","-")
df['order_date'] = pd.to_datetime(df['order_date'],dayfirst=True,errors='coerce')
df = df.dropna(subset=['order_date'])
df['month']= df['order_date'].dt.month
df['year']= df['order_date'].dt.year
df['day']= df['order_date'].dt.day

st.title("smart buisness dashboard")
st.write("Total sales:",round(df['sales'],sum(),2))
st.write("Total profit:",round(df['profit'],sum(),2))

st.subheader("Sales by Category")
category_sales = df.groupby('category')['sales'].sum()

fig1, ax1 = plt.subplots()
sns.barplot(x=category_sales.index, y=category_sales.values, ax=ax1)
plt.xticks(rotation=45)
st.pyplot(fig1)

# Monthly Trend
st.subheader("Monthly Sales Trend")
monthly_sales = df.groupby('month')['sales'].sum()
st.line_chart(monthly_sales)

# Discount vs Profit
st.subheader("Discount vs Profit")
fig2, ax2 = plt.subplots()
sns.scatterplot(x=df['discount'], y=df['profit'], ax=ax2)
st.pyplot(fig2)

# Region Profit
st.subheader("Profit by Region")
region_profit = df.groupby('region')['profit'].sum()

fig3, ax3 = plt.subplots()
sns.barplot(x=region_profit.index, y=region_profit.values, ax=ax3)
plt.xticks(rotation=45)
st.pyplot(fig3)

