import json
import random
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine, text

# Generate Raw Data
def generate_raw_ecommerce_data(num_records=1000):
    # Simulate a raw JSON payload from an application database log
    random.seed(42)
    products = {
        "Laptop": 999.99,
        "4K Monitor": 299.99,
        "Mechanical Keyboard": 85.50,
        "Wireless Mouse": 25.00,
        "USB-C Dock": 45.00 
    }

    raw_payload = []
    # Generate data over a 60-day past window
    base_date = datetime(2026, 9, 1)

    for i in range(num_records):
        product_name, price = random.choice(list(products.items()))

        # Randomizing missing data to show data cleaning
        quantity = random.choice([1, 2, 3, None])
        discount = random.choice([0.0, 0.05, 0.1, 0.15])

        # Spread timestamps across 60 days
        timestamp = base_date + timedelta(
            days=random.randint(0,60),
            hours=random.randint(0,23),
            minutes=random.randint(0,59)
        )

        raw_payload.append({
            "order_id": 10000 + i,
            "user_id": random.randint(100, 250),
            "product": product_name,
            "price": price,
            "quantity": quantity,
            "discount": discount,
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })
    return json.dumps(raw_payload)

# Data Cleaning
print("Initializing data pipeline")

# Fetch JSON string
raw_json_stream = generate_raw_ecommerce_data(num_records=1000)

# Convert to Pandas Dataframe
df = pd.DataFrame(json.loads(raw_json_stream))

# Clean the messy fields by filling in missing quanities with a default of 1
df["quantity"] = df["quantity"].fillna(1).astype(int)

# Calculate exact net revenue per transaction row
df['net_revenue'] = round((df['price'] * df['quantity']) * (1 - df['discount']), 2)


# Load to the database using SQLite

# Connect to SQLite
DB_URL = "postgresql+psycopg2://postgres@localhost:5432/ecommerce_db"
engine = create_engine(DB_URL)

# Read and execute sql script with the schema
with open('schema.sql', 'r') as sql_file:
    schema_script = sql_file.read()

with engine.connect() as connection:
    with connection.begin():
        for command in schema_script.split(';'):
            clean_command = command.strip()
            if clean_command:
                connection.execute(text(clean_command))

# Load clean dataframe into SQL
dim_df = df[['product', 'price']].drop_duplicates().rename(columns={'product': 'product_name', 'price': 'unit_price'})
dim_df.to_sql('dim_products', engine, if_exists='append', index=False)

fact_df = df[['order_id', 'user_id', 'product', 'quantity', 'discount', 'net_revenue', 'timestamp']].rename(columns={'product': 'product_name', 'timestamp': 'order_timestamp'})
fact_df.to_sql('fact_orders', engine, if_exists='append', index=False)


print("Pipeline run complete. 'ecommerce_warehouse.db' created with 1000 cleaned records")

# Run and Export an analytical query to an Excel File for business stakeholders as an "ad-hoc"

query = """
SELECT user_id, COUNT(order_id) as total_orders, SUM(net_revenue) as customer_lifetime_value
FROM fact_orders
GROUP BY user_id
ORDER BY customer_lifetime_value DESC;
"""

report_df = pd.read_sql_query(query, engine)
report_df.to_excel('clv_business_report.xlsx', index=False)

print("Generated 'clv_busniess_report.xlsx' Excel report for the business stakeholders.")
