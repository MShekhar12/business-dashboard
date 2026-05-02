import pandas as pd
df = pd.read_csv("data/SuperStoreOrders.csv")
df.columns= df.columns.str.strip().str.lower()
df=df.reset_index(drop=True)
df['order_date'] = pd.to_datetime(df['order_date'],dayfirst=True,errors='coerce')
df = df.dropna(subset=['order_date'])
df['month']= df['order_date'].dt.month
df['year']= df['order_date'].dt.year
df['day']= df['order_date'].dt.day
print(df.sample(20))
print(df.isnull().sum())