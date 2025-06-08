import csv
from datetime import datetime, timedelta
import random
import re
import os
from datetime import datetime as dt

INPUT_FILE = 'orders_export copy.csv'
# Generate a unique output file name based on the input file and current timestamp
base, ext = os.path.splitext(INPUT_FILE)
timestamp = dt.now().strftime('%Y%m%d_%H%M%S')
OUTPUT_FILE = f'{base}_expanded_{timestamp}{ext}'
START_DATE = datetime(2024, 6, 7, 9, 0, 0)  # Start on June 7th, 2024
MULTIPLIER = 365  # 1 year
DATE_FIELDS = [
    'Paid at', 'Fulfilled at', 'Created at', 'Next Payment Due At'
]
ORDER_ID_FIELD = 'Name'
ORDER_NUM_PATTERN = re.compile(r'#(\d+)')
ID_FIELD = 'Id'

# Helper to increment date strings, now using a fixed start date

def increment_date(date_str, days):
    if not date_str or date_str.strip() == '':
        return date_str
    try:
        # Try with timezone
        dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S %z')
        # Replace with start date + days, keep time and tz
        base = START_DATE.replace(hour=dt.hour, minute=dt.minute, second=dt.second, tzinfo=dt.tzinfo)
        return (base + timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S %z')
    except Exception:
        try:
            # Try without timezone
            dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            base = START_DATE.replace(hour=dt.hour, minute=dt.minute, second=dt.second)
            return (base + timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            return date_str

def increment_order_num(order_name, offset):
    match = ORDER_NUM_PATTERN.match(order_name)
    if match:
        num = int(match.group(1)) + offset
        # Add a cycle-based suffix to ensure uniqueness
        return f'#{num:04d}_C{offset:02d}'
    return order_name

def increment_id(id_str, offset):
    if not id_str or not id_str.isdigit():
        return id_str
    return str(int(id_str) + offset * 1000000)

def main():
    with open(INPUT_FILE, newline='') as infile:
        reader = list(csv.reader(infile))
        header = reader[0]
        rows = reader[1:]

    # Group rows by order number (Name field)
    orders = []
    current_order = []
    last_order_num = None
    for row in rows:
        order_num = row[0]
        if order_num and order_num != last_order_num:
            if current_order:
                orders.append(current_order)
            current_order = [row]
            last_order_num = order_num
        else:
            current_order.append(row)
    if current_order:
        orders.append(current_order)

    # Find field indices
    field_idx = {name: i for i, name in enumerate(header)}

    expanded_rows = []
    order_offset = 0
    for cycle in range(MULTIPLIER):
        for order in orders:
            # Calculate offset for order number and id
            order_num_offset = order_offset
            id_offset = order_offset
            for row in order:
                new_row = row.copy()
                # Increment date fields
                for field in DATE_FIELDS:
                    if field in field_idx:
                        idx = field_idx[field]
                        new_row[idx] = increment_date(new_row[idx], cycle)
                # Increment order number
                if ORDER_ID_FIELD in field_idx:
                    idx = field_idx[ORDER_ID_FIELD]
                    new_row[idx] = increment_order_num(new_row[idx], order_num_offset)
                # Increment Id field
                if ID_FIELD in field_idx:
                    idx = field_idx[ID_FIELD]
                    new_row[idx] = increment_id(new_row[idx], id_offset)
                # Optionally, randomize times a bit
                for field in DATE_FIELDS:
                    if field in field_idx:
                        idx = field_idx[field]
                        val = new_row[idx]
                        if val and ':' in val:
                            try:
                                # Add random minutes (0-59)
                                if '+' in val or '-' in val:
                                    dt = datetime.strptime(val, '%Y-%m-%d %H:%M:%S %z')
                                    dt += timedelta(minutes=random.randint(0, 59))
                                    new_row[idx] = dt.strftime('%Y-%m-%d %H:%M:%S %z')
                                else:
                                    dt = datetime.strptime(val, '%Y-%m-%d %H:%M:%S')
                                    dt += timedelta(minutes=random.randint(0, 59))
                                    new_row[idx] = dt.strftime('%Y-%m-%d %H:%M:%S')
                            except Exception:
                                pass
                expanded_rows.append(new_row)
            order_offset += 1

    with open(OUTPUT_FILE, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(header)
        writer.writerows(expanded_rows)

    print(f'Expanded data written to {OUTPUT_FILE}')
    print(f'Original data remains in {INPUT_FILE}')

if __name__ == '__main__':
    main()
