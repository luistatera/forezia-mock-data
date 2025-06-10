import pandas as pd
import numpy as np
from datetime import timedelta, date

np.random.seed(42)

# Parameters
NUM_SKUS = 50
DAYS = 365
START_DATE = date(2024, 6, 10)
SKUS = [f"SKU-{i+1:03}" for i in range(NUM_SKUS)]

# Generate base sales per SKU (some SKUs are bestsellers)
sku_base_sales = np.random.randint(1, 20, NUM_SKUS) * np.random.uniform(0.5, 2, NUM_SKUS)
trend_per_sku = np.random.uniform(0.995, 1.005, NUM_SKUS)  # some grow, some decline

rows = []
for i, sku in enumerate(SKUS):
    sales = sku_base_sales[i]
    trend = trend_per_sku[i]
    for day in range(DAYS):
        curr_date = START_DATE + timedelta(days=day)
        # Weekly seasonality: weekends 30-70% higher
        weekday = curr_date.weekday()
        seasonality = 1.0
        if weekday >= 5:
            seasonality += np.random.uniform(0.3, 0.7)
        # Holiday spikes (Black Friday in Nov, Christmas in Dec)
        if curr_date.month == 11 and 22 <= curr_date.day <= 30:
            seasonality += 1.2  # Black Friday
        if curr_date.month == 12 and 20 <= curr_date.day <= 26:
            seasonality += 1.5  # Christmas
        # Add some random noise
        daily_sales = sales * seasonality * np.random.uniform(0.85, 1.15)
        daily_sales = np.round(daily_sales)
        rows.append({
            "date": curr_date.isoformat(),
            "sku": sku,
            "sales": max(0, int(daily_sales))
        })
        sales *= trend  # update trend

df = pd.DataFrame(rows)
df.to_csv("synthetic_sales_1y.csv", index=False)
print("Saved synthetic sales to synthetic_sales_1y.csv")
