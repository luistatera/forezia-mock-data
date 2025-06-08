'''
Generates a realistic CSV dataset for toy sales over the last 12 months.

Fields:
- ds: The date of the data point (YYYY-MM-DD).
- y: The sales quantity for the SKU on that day.
- sku: The Stock Keeping Unit (product identifier).
- is_weekend: Binary indicator (1 for weekend, 0 for weekday).
- day_of_week: Numerical day of the week (Monday=0, Sunday=6).
- valentines_day: Binary indicator for Valentine's Day (Feb 14th).
- bfcm_week: Binary indicator for Black Friday/Cyber Monday week.
'''
import csv
import datetime
import random

OUTPUT_FILE = "toy_sales_last_12_months.csv"
NUM_SKUS = 50

# Define the date range: last 12 months from today (June 8, 2025)
END_DATE = datetime.date(2025, 6, 7)
START_DATE = END_DATE - datetime.timedelta(days=365 -1) # -1 because we include the start date

# Generate SKUs
SKUS = [f"TOY_SKU_{i:03}" for i in range(1, NUM_SKUS + 1)]

# Base sales characteristics for each SKU (avg daily sales, weekend multiplier factor)
SKU_CHARACTERISTICS = {
    sku: {
        "base_sales": random.randint(10, 100),
        "weekend_factor": random.uniform(1.5, 3.0),
        "bfcm_factor": random.uniform(2.0, 5.0),
        "valentines_factor": random.uniform(1.2, 2.0) # Some toys might get a V-Day bump
    }
    for sku in SKUS
}

def get_bfcm_week_dates(year):
    """Determines the BFCM week (Monday before Black Friday to Cyber Monday)."""
    # Black Friday is the fourth Friday of November
    first_day_of_nov = datetime.date(year, 11, 1)
    # weekday() returns Monday as 0 and Sunday as 6. Friday is 4.
    days_to_first_friday = (4 - first_day_of_nov.weekday() + 7) % 7
    first_friday = first_day_of_nov + datetime.timedelta(days=days_to_first_friday)
    black_friday = first_friday + datetime.timedelta(weeks=3)

    # BFCM week starts the Monday before Black Friday and ends on Cyber Monday
    bfcm_start = black_friday - datetime.timedelta(days=black_friday.weekday()) # Monday of BF week
    bfcm_end = bfcm_start + datetime.timedelta(days=7) # End of Cyber Monday (effectively start of Tuesday)
    return bfcm_start, bfcm_end

BFCM_START_2024, BFCM_END_2024 = get_bfcm_week_dates(2024)

def generate_sales_data():
    data_rows = []
    current_date = START_DATE
    while current_date <= END_DATE:
        day_of_week = current_date.weekday()  # Monday=0, Sunday=6
        is_weekend_val = 1 if day_of_week >= 5 else 0

        is_valentines_val = 1 if current_date.month == 2 and current_date.day == 14 else 0
        is_bfcm_val = 1 if BFCM_START_2024 <= current_date < BFCM_END_2024 else 0

        for sku in SKUS:
            char = SKU_CHARACTERISTICS[sku]
            base_y = char["base_sales"]

            # Apply daily random fluctuation (e.g., +/- 20% of base)
            y = base_y * random.uniform(0.8, 1.2)

            # Weekend effect
            if is_weekend_val:
                y *= char["weekend_factor"]

            # Valentine's Day effect
            if is_valentines_val:
                y *= char["valentines_factor"]

            # BFCM effect
            if is_bfcm_val:
                y *= char["bfcm_factor"]
            
            # Ensure sales are not negative and are integers
            y = max(0, int(round(y)))

            data_rows.append([
                current_date.strftime("%Y-%m-%d"),
                y,
                sku,
                is_weekend_val,
                day_of_week,
                is_valentines_val,
                is_bfcm_val
            ])
        current_date += datetime.timedelta(days=1)
    return data_rows

def main():
    header = ['ds', 'y', 'sku', 'is_weekend', 'day_of_week', 'valentines_day', 'bfcm_week']
    sales_data = generate_sales_data()

    with open(OUTPUT_FILE, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(sales_data)
    print(f"Generated {len(sales_data)} rows of toy sales data into {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
