#!/usr/bin/env python3
"""
Visualization script for synthetic toy sales data patterns
Perfect for understanding the data before machine learning training
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np

def create_sales_visualizations(filename):
    """Create visualizations to show sales patterns."""
    print(f"📈 Creating visualizations for: {filename}")
    
    # Load and prepare data
    df = pd.read_csv(filename)
    main_orders = df[df['Financial Status'].notna() & (df['Financial Status'] != '')].copy()
    main_orders['Created at'] = pd.to_datetime(main_orders['Created at'])
    main_orders['Total'] = main_orders['Total'].astype(float)
    main_orders['Date'] = main_orders['Created at'].dt.date
    main_orders['Month'] = main_orders['Created at'].dt.to_period('M')
    main_orders['Weekday'] = main_orders['Created at'].dt.day_name()
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Synthetic Toy Sales Data Analysis', fontsize=16, fontweight='bold')
    
    # 1. Daily Sales Volume
    daily_sales = main_orders.groupby('Date').agg({
        'Name': 'count',
        'Total': 'sum'
    }).rename(columns={'Name': 'Orders'})
    
    axes[0, 0].plot(daily_sales.index, daily_sales['Orders'], alpha=0.7, linewidth=1)
    axes[0, 0].set_title('Daily Order Volume Over Time')
    axes[0, 0].set_xlabel('Date')
    axes[0, 0].set_ylabel('Number of Orders')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # 2. Monthly Revenue Growth
    monthly_revenue = main_orders.groupby('Month')['Total'].sum()
    axes[0, 1].bar(range(len(monthly_revenue)), monthly_revenue.values, 
                   color='skyblue', alpha=0.8)
    axes[0, 1].set_title('Monthly Revenue Growth')
    axes[0, 1].set_xlabel('Month')
    axes[0, 1].set_ylabel('Revenue ($)')
    axes[0, 1].set_xticks(range(len(monthly_revenue)))
    axes[0, 1].set_xticklabels([str(m) for m in monthly_revenue.index], rotation=45)
    
    # 3. Weekend vs Weekday Sales
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_sales = main_orders.groupby('Weekday')['Name'].count().reindex(weekday_order)
    
    colors = ['lightcoral' if day in ['Saturday', 'Sunday'] else 'lightblue' for day in weekday_order]
    axes[1, 0].bar(weekday_order, weekday_sales.values, color=colors, alpha=0.8)
    axes[1, 0].set_title('Sales by Day of Week')
    axes[1, 0].set_xlabel('Day of Week')
    axes[1, 0].set_ylabel('Number of Orders')
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # 4. Top Product Categories
    all_products = df[df['Lineitem name'].notna()]
    top_products = all_products['Lineitem name'].value_counts().head(10)
    
    axes[1, 1].barh(range(len(top_products)), top_products.values, color='lightgreen', alpha=0.8)
    axes[1, 1].set_title('Top 10 Products by Sales Volume')
    axes[1, 1].set_xlabel('Units Sold')
    axes[1, 1].set_ylabel('Product')
    axes[1, 1].set_yticks(range(len(top_products)))
    axes[1, 1].set_yticklabels([name[:30] + '...' if len(name) > 30 else name 
                                for name in top_products.index])
    
    # Adjust layout and save
    plt.tight_layout()
    output_file = f"sales_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"📊 Visualization saved as: {output_file}")
    
    # Show key insights
    print(f"\n🎯 Key Insights for Machine Learning:")
    print(f"   - Date range: {main_orders['Date'].min()} to {main_orders['Date'].max()}")
    print(f"   - Average daily orders: {daily_sales['Orders'].mean():.1f}")
    print(f"   - Weekend boost: {weekday_sales[['Saturday', 'Sunday']].mean() / weekday_sales[['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']].mean():.2f}x")
    
    total_growth = (monthly_revenue.iloc[-1] - monthly_revenue.iloc[0]) / monthly_revenue.iloc[0] * 100
    print(f"   - Total revenue growth: {total_growth:.1f}% over {len(monthly_revenue)} months")
    print(f"   - Most popular product: {top_products.index[0]} ({top_products.iloc[0]} units)")
    
    return output_file

if __name__ == "__main__":
    import glob
    import os
    
    # Find the most recent synthetic file
    synthetic_files = glob.glob("toy_sales_synthetic_*.csv")
    if synthetic_files:
        latest_file = max(synthetic_files, key=os.path.getctime)
        create_sales_visualizations(latest_file)
    else:
        print("❌ No synthetic data files found!")
