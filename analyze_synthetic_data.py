#!/usr/bin/env python3
"""
Analysis script to verify the synthetic orders data patterns
"""

import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

def analyze_synthetic_data(filename):
    """Analyze the synthetic data to verify patterns."""
    print(f"🔍 Analyzing synthetic data: {filename}")
    
    # Load the data
    df = pd.read_csv(filename)
    
    # Basic statistics
    print(f"\n📊 Basic Statistics:")
    print(f"   - Total rows: {len(df):,}")
    print(f"   - Unique orders: {len(df['Name'].unique()):,}")
    print(f"   - Date range: {df['Created at'].min()} to {df['Created at'].max()}")
    
    # Filter main order rows (first line item per order)
    main_orders = df[df['Financial Status'].notna() & (df['Financial Status'] != '')].copy()
    
    # Convert dates
    main_orders['Created at'] = pd.to_datetime(main_orders['Created at'])
    main_orders['Month'] = main_orders['Created at'].dt.to_period('M')
    main_orders['Weekday'] = main_orders['Created at'].dt.dayofweek
    main_orders['Total'] = main_orders['Total'].astype(float)
    
    print(f"\n💰 Revenue Analysis:")
    print(f"   - Total revenue: ${main_orders['Total'].sum():,.2f}")
    print(f"   - Average order value: ${main_orders['Total'].mean():.2f}")
    print(f"   - Min order value: ${main_orders['Total'].min():.2f}")
    print(f"   - Max order value: ${main_orders['Total'].max():.2f}")
    
    # Monthly growth analysis
    monthly_orders = main_orders.groupby('Month').agg({
        'Name': 'count',
        'Total': 'sum'
    }).rename(columns={'Name': 'Orders'})
    
    print(f"\n📈 Monthly Growth Analysis:")
    for i in range(1, len(monthly_orders)):
        prev_orders = monthly_orders.iloc[i-1]['Orders']
        curr_orders = monthly_orders.iloc[i]['Orders']
        growth = ((curr_orders - prev_orders) / prev_orders) * 100
        month = monthly_orders.index[i]
        print(f"   - {month}: {curr_orders:,} orders ({growth:+.1f}% vs prev month)")
    
    # Weekend vs weekday analysis
    weekend_orders = main_orders[main_orders['Weekday'].isin([5, 6])]  # Saturday, Sunday
    weekday_orders = main_orders[~main_orders['Weekday'].isin([5, 6])]
    
    weekend_avg = len(weekend_orders) / (len(main_orders['Created at'].dt.date.unique()) * 2/7)
    weekday_avg = len(weekday_orders) / (len(main_orders['Created at'].dt.date.unique()) * 5/7)
    weekend_boost = weekend_avg / weekday_avg
    
    print(f"\n🎯 Weekend Analysis:")
    print(f"   - Weekend orders: {len(weekend_orders):,}")
    print(f"   - Weekday orders: {len(weekday_orders):,}")
    print(f"   - Weekend boost factor: {weekend_boost:.2f}x")
    
    # Product analysis
    all_products = df[df['Lineitem name'].notna()]['Lineitem name'].value_counts()
    print(f"\n🧸 Product Analysis:")
    print(f"   - Unique products sold: {len(all_products)}")
    print(f"   - Top 5 products:")
    for i, (product, count) in enumerate(all_products.head().items(), 1):
        print(f"     {i}. {product}: {count} units")
    
    # Vendor analysis
    vendor_sales = df[df['Vendor'].notna()]['Vendor'].value_counts()
    print(f"\n🏭 Vendor Analysis:")
    print(f"   - Top 5 vendors:")
    for i, (vendor, count) in enumerate(vendor_sales.head().items(), 1):
        print(f"     {i}. {vendor}: {count} line items")
    
    print(f"\n✅ Analysis complete!")

if __name__ == "__main__":
    # Find the most recent synthetic file
    import glob
    import os
    
    synthetic_files = glob.glob("toy_sales_synthetic_*.csv")
    if synthetic_files:
        latest_file = max(synthetic_files, key=os.path.getctime)
        analyze_synthetic_data(latest_file)
    else:
        print("❌ No synthetic data files found!")
