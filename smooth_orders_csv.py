import pandas as pd
import numpy as np
from datetime import timedelta, date

# Parameters
INPUT_FILE = 'orders_export_new.csv'
OUTPUT_FILE = 'orders_export_smoothed.csv'
MIN_DAYS = 30
SMOOTH_WINDOW = 7  # days for moving average
MAX_DAILY_CHANGE = 2  # max allowed change in sales per day
TODAY = date(2025, 6, 9)

# Load data
orders = pd.read_csv(INPUT_FILE)
orders['date'] = pd.to_datetime(orders['Created at']).dt.date

# Aggregate sales per SKU per day
daily = orders.groupby(['Lineitem sku', 'date']).size().reset_index(name='sales')

# Ensure each SKU has at least MIN_DAYS of data (fill missing dates with 0)
all_skus = daily['Lineitem sku'].unique()
all_dates = pd.date_range(daily['date'].min(), daily['date'].max())
full_idx = pd.MultiIndex.from_product([all_skus, all_dates], names=['Lineitem sku', 'date'])
daily = daily.set_index(['Lineitem sku', 'date']).reindex(full_idx, fill_value=0).reset_index()

# --- Outlier capping using IQR (upper fence only) ---
def cap_upper_outliers(s, k=1.5):
    Q1 = s.quantile(0.25)
    Q3 = s.quantile(0.75)
    IQR = Q3 - Q1
    upper = Q3 + k * IQR
    capped = s.copy()
    # Only cap values above upper fence
    capped[s > upper] = upper
    return capped

# --- Sanity check: percent of nonzero sales zeroed ---
def percent_zeroed(original, smoothed):
    nonzero = (original > 0)
    zeroed = (original > 0) & (smoothed == 0)
    if nonzero.sum() == 0:
        return 0.0
    return 100 * zeroed.sum() / nonzero.sum()

# Smoothing function
# (apply outlier capping before smoothing)
def smooth_and_cap(sales, window=SMOOTH_WINDOW, max_change=MAX_DAILY_CHANGE):
    # Cap upper outliers only
    capped = cap_upper_outliers(pd.Series(sales))
    # Moving average
    smoothed = capped.rolling(window, min_periods=1, center=True).mean()
    # Cap daily change
    capped2 = [smoothed.iloc[0]]
    for s in smoothed.iloc[1:]:
        prev = capped2[-1]
        capped2.append(max(min(s, prev + max_change), prev - max_change))
    return np.round(capped2).astype(int)

daily['smoothed_sales'] = daily.groupby('Lineitem sku')['sales'].transform(smooth_and_cap)

# Filter to SKUs with at least MIN_DAYS of nonzero sales
good_skus = daily.groupby('Lineitem sku').apply(lambda g: (g['smoothed_sales'] > 0).sum() >= MIN_DAYS)
good_skus = good_skus[good_skus].index
smoothed = daily[daily['Lineitem sku'].isin(good_skus)]

# --- Shift all dates so the latest is TODAY ---
if not smoothed.empty:
    max_date = smoothed['date'].max()
    if hasattr(max_date, 'date'):
        max_date = max_date.date()
    date_shift = (TODAY - max_date).days
    smoothed['date'] = smoothed['date'] + timedelta(days=date_shift)

# Reconstruct orders: for each SKU/date, create that many order lines, copying template info from original orders
rows = []
for (sku, d), group in smoothed.groupby(['Lineitem sku', 'date']):
    n = int(group['smoothed_sales'].iloc[0])
    if n == 0:
        continue
    # Use a template row from original orders for this SKU
    template = orders[orders['Lineitem sku'] == sku].iloc[0].copy()
    # Set all date fields to the shifted date
    new_created_at = pd.Timestamp(d).strftime('%Y-%m-%d 00:00:00 -0400')
    template['Created at'] = new_created_at
    template['date'] = d
    # Optionally update Paid at and Fulfilled at to be consistent and not in the future
    template['Paid at'] = new_created_at
    fulfilled_at = pd.Timestamp(d) + pd.Timedelta(days=2)
    if fulfilled_at.date() > TODAY:
        fulfilled_at = pd.Timestamp(TODAY)
    template['Fulfilled at'] = fulfilled_at.strftime('%Y-%m-%d 00:00:00 -0400')
    for _ in range(n):
        rows.append(template.copy())

# Create DataFrame and save
smoothed_orders = pd.DataFrame(rows)
smoothed_orders.to_csv(OUTPUT_FILE, index=False)

# --- After smoothing, check for excessive zeroing ---
zeroed_pct = percent_zeroed(daily['sales'], daily['smoothed_sales'])
if zeroed_pct > 5:
    print(f"WARNING: {zeroed_pct:.2f}% of nonzero sales were zeroed after smoothing! Check your pipeline.")

print(f"Smoothed orders saved to {OUTPUT_FILE}. Total rows: {len(smoothed_orders)}")
