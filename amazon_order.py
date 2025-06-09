import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Read the CSV files
amazon_df = pd.read_csv('amazon.csv')
shopify_df = pd.read_csv('orders_export.csv')

# Get unique structure from Shopify (first order as template)
shopify_columns = shopify_df.columns.tolist()

# Helper functions
def generate_email(name):
    """Generate email from name"""
    if pd.isna(name) or name == '':
        return ''
    name_parts = name.lower().replace(' ', '.').replace(',', '')
    return f"{name_parts}@example.com"

def convert_inr_to_eur(amount):
    """Convert INR to EUR (approximate rate)"""
    if pd.isna(amount) or amount == '':
        return 0.00
    try:
        return round(float(amount) / 88.5, 2)  # Approximate INR to EUR rate
    except:
        return 0.00

def map_amazon_status_to_shopify(status, fulfillment):
    """Map Amazon status to Shopify financial and fulfillment status"""
    financial_status = ''
    fulfillment_status = ''
    
    if 'Shipped' in str(status):
        financial_status = 'paid'
        if 'Delivered' in str(status):
            fulfillment_status = 'fulfilled'
        else:
            fulfillment_status = 'fulfilled'
    elif status == 'Cancelled':
        financial_status = 'refunded'
        fulfillment_status = 'restocked'
    else:
        financial_status = 'pending'
        fulfillment_status = 'unfulfilled'
    
    return financial_status, fulfillment_status

def convert_amazon_date(date_str):
    """Convert Amazon date format to Shopify format"""
    try:
        # Parse Amazon date (04-30-22 format)
        date_obj = datetime.strptime(date_str, '%m-%d-%y')
        # Add year 2020 to make it more recent
        date_obj = date_obj.replace(year=date_obj.year + 3)
        # Format for Shopify (2025-05-11 09:55:16 -0400)
        return date_obj.strftime('%Y-%m-%d %H:%M:%S -0400')
    except:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S -0400')

def map_category_to_product(category, size):
    """Map Amazon category to Shopify-like product names"""
    product_mapping = {
        'T-shirt': ['The Minimal Snowboard', 'The Multi-location Snowboard', 'The Videographer Snowboard'],
        'Shirt': ['The Collection Snowboard: Hydrogen', 'The Collection Snowboard: Oxygen', 'The Complete Snowboard - Ice'],
        'Blazzer': ['The Inventory Not Tracked Snowboard'],
        'Trousers': ['Selling Plans Ski Wax - Selling Plans Ski Wax', 'Selling Plans Ski Wax - Special Selling Plans Ski Wax'],
        'Perfume': ['Gift Card - $100', 'Gift Card - $50', 'Gift Card - $25'],
        'Socks': ['Gift Card - $10'],
        'Shoes': ['Gift Card - $10'],
        'Wallet': ['Gift Card - $10']
    }
    
    products = product_mapping.get(category, ['The Multi-location Snowboard'])
    return random.choice(products)

# Create new dataframe for converted data
converted_orders = []

# Group Amazon orders by Order ID to handle multiple items
order_groups = amazon_df.groupby('Order ID')

order_counter = 1001  # Starting order number

for order_id, group in order_groups:
    # Skip if no valid items
    valid_items = group[group['Status'] != 'Cancelled']
    if len(valid_items) == 0:
        continue
    
    # Use first item for order-level data
    first_item = group.iloc[0]
    
    # Generate order data
    order_name = f"#{order_counter}"
    order_counter += 1
    
    # Map statuses
    financial_status, fulfillment_status = map_amazon_status_to_shopify(
        first_item['Status'], first_item['Fulfilment']
    )
    
    # Calculate dates
    created_at = convert_amazon_date(first_item['Date'])
    paid_at = created_at if financial_status == 'paid' else ''
    fulfilled_at = ''
    if fulfillment_status == 'fulfilled':
        # Add 1-3 days for fulfillment
        fulfilled_date = datetime.strptime(created_at.split(' -')[0], '%Y-%m-%d %H:%M:%S')
        fulfilled_date += timedelta(days=random.randint(1, 3))
        fulfilled_at = fulfilled_date.strftime('%Y-%m-%d %H:%M:%S -0400')
    
    # Generate customer data
    customer_name = f"{first_item['ship-city'].title()} Customer" if pd.notna(first_item['ship-city']) else ''
    email = generate_email(customer_name)
    
    # Calculate totals for all items in order
    subtotal = 0
    for _, item in group.iterrows():
        if item['Status'] != 'Cancelled' and pd.notna(item['Amount']):
            subtotal += convert_inr_to_eur(item['Amount'])
    
    total = subtotal
    
    # Create line items
    for _, item in group.iterrows():
        if item['Status'] == 'Cancelled':
            continue
            
        # Map product
        product_name = map_category_to_product(item['Category'], item['Size'])
        item_price = convert_inr_to_eur(item['Amount'])
        
        # Create order row
        order_row = {
            'Name': order_name,
            'Email': email,
            'Financial Status': financial_status,
            'Paid at': paid_at,
            'Fulfillment Status': fulfillment_status,
            'Fulfilled at': fulfilled_at,
            'Accepts Marketing': 'no',
            'Currency': 'EUR',
            'Subtotal': subtotal if len(converted_orders) == 0 or converted_orders[-1].get('Name') != order_name else '',
            'Shipping': 0.00 if len(converted_orders) == 0 or converted_orders[-1].get('Name') != order_name else '',
            'Taxes': 0.00 if len(converted_orders) == 0 or converted_orders[-1].get('Name') != order_name else '',
            'Total': total if len(converted_orders) == 0 or converted_orders[-1].get('Name') != order_name else '',
            'Discount Code': '',
            'Discount Amount': 0.00,
            'Shipping Method': '',
            'Created at': created_at,
            'Lineitem quantity': int(item['Qty']) if pd.notna(item['Qty']) else 1,
            'Lineitem name': product_name,
            'Lineitem price': item_price,
            'Lineitem compare at price': '',
            'Lineitem sku': f"SKU-{item['Category']}-{item['Size']}" if pd.notna(item['Size']) else '',
            'Lineitem requires shipping': 'true' if item['Category'] not in ['Perfume', 'Wallet'] else 'false',
            'Lineitem taxable': 'true',
            'Lineitem fulfillment status': 'fulfilled' if fulfillment_status == 'fulfilled' else 'pending',
            'Billing Name': customer_name if len(converted_orders) == 0 or converted_orders[-1].get('Name') != order_name else '',
            'Billing Street': '',
            'Billing Address1': f"{item['ship-city']}" if pd.notna(item['ship-city']) and (len(converted_orders) == 0 or converted_orders[-1].get('Name') != order_name) else '',
            'Billing Address2': '',
            'Billing Company': '',
            'Billing City': item['ship-city'] if pd.notna(item['ship-city']) and (len(converted_orders) == 0 or converted_orders[-1].get('Name') != order_name) else '',
            'Billing Zip': item['ship-postal-code'] if pd.notna(item['ship-postal-code']) and (len(converted_orders) == 0 or converted_orders[-1].get('Name') != order_name) else '',
            'Billing Province': item['ship-state'] if pd.notna(item['ship-state']) and (len(converted_orders) == 0 or converted_orders[-1].get('Name') != order_name) else '',
            'Billing Country': item['ship-country'] if pd.notna(item['ship-country']) and (len(converted_orders) == 0 or converted_orders[-1].get('Name') != order_name) else '',
            'Billing Phone': '',
            'Shipping Name': customer_name if len(converted_orders) == 0 or converted_orders[-1].get('Name') != order_name else '',
            'Shipping Street': '',
            'Shipping Address1': f"{item['ship-city']}" if pd.notna(item['ship-city']) and (len(converted_orders) == 0 or converted_orders[-1].get('Name') != order_name) else '',
            'Shipping Address2': '',
            'Shipping Company': '',
            'Shipping City': item['ship-city'] if pd.notna(item['ship-city']) and (len(converted_orders) == 0 or converted_orders[-1].get('Name') != order_name) else '',
            'Shipping Zip': item['ship-postal-code'] if pd.notna(item['ship-postal-code']) and (len(converted_orders) == 0 or converted_orders[-1].get('Name') != order_name) else '',
            'Shipping Province': item['ship-state'] if pd.notna(item['ship-state']) and (len(converted_orders) == 0 or converted_orders[-1].get('Name') != order_name) else '',
            'Shipping Country': item['ship-country'] if pd.notna(item['ship-country']) and (len(converted_orders) == 0 or converted_orders[-1].get('Name') != order_name) else '',
            'Shipping Phone': '',
            'Notes': '',
            'Note Attributes': '',
            'Cancelled at': '',
            'Payment Method': 'manual',
            'Payment Reference': f"r{order_id.replace('-', '')[:25]}" if len(converted_orders) == 0 or converted_orders[-1].get('Name') != order_name else '',
            'Refunded Amount': 0.00,
            'Vendor': random.choice(['Snowboard Vendor', 'Test Cycle Sense App', 'Hydrogen Vendor']),
            'Outstanding Balance': 0.00,
            'Employee': 'Luis Guimaraes',
            'Location': 'Shop location' if random.random() > 0.3 else '',
            'Device ID': '',
            'Id': np.random.randint(6630000000000, 6650000000000),
            'Tags': '',
            'Risk Level': 'Low',
            'Source': 'shopify_draft_order',
            'Lineitem discount': 0.00,
            'Tax 1 Name': '',
            'Tax 1 Value': '',
            'Tax 2 Name': '',
            'Tax 2 Value': '',
            'Tax 3 Name': '',
            'Tax 3 Value': '',
            'Tax 4 Name': '',
            'Tax 4 Value': '',
            'Tax 5 Name': '',
            'Tax 5 Value': '',
            'Phone': '',
            'Receipt Number': '',
            'Duties': '',
            'Billing Province Name': item['ship-state'] if pd.notna(item['ship-state']) and (len(converted_orders) == 0 or converted_orders[-1].get('Name') != order_name) else '',
            'Shipping Province Name': item['ship-state'] if pd.notna(item['ship-state']) and (len(converted_orders) == 0 or converted_orders[-1].get('Name') != order_name) else '',
            'Payment ID': f"r{order_id.replace('-', '')[:25]}" if len(converted_orders) == 0 or converted_orders[-1].get('Name') != order_name else '',
            'Payment Terms Name': '',
            'Next Payment Due At': '',
            'Payment References': f"r{order_id.replace('-', '')[:25]}" if len(converted_orders) == 0 or converted_orders[-1].get('Name') != order_name else ''
        }
        
        converted_orders.append(order_row)

# Create DataFrame with converted orders
converted_df = pd.DataFrame(converted_orders)

# Ensure all columns from Shopify are present
for col in shopify_columns:
    if col not in converted_df.columns:
        converted_df[col] = ''

# Reorder columns to match Shopify
converted_df = converted_df[shopify_columns]

# Save to new CSV file
converted_df.to_csv('orders_export_new.csv', index=False)

print(f"Successfully converted {len(order_groups)} Amazon orders to {len(converted_df)} Shopify order lines")
print(f"Output saved to: orders_export_new.csv")
print(f"\nSample of converted data:")
print(converted_df.head(10))