# 🏷️ New Prophet-Optimized Discount System

## Overview
The synthetic data generator now includes a **simplified discount system** specifically designed for Prophet time series forecasting models. The new system removes complex discount codes and focuses on clean numerical ratio values perfect for use as regressors in Prophet models.

## 🎯 New Discount Rule for Mock Data

### Field Name: `discount_ratio`

### How to Generate:
- Simulates realistic discount ratios between `0.00` (no discount) and up to `0.50` (deep promotions)
- Uses a probability distribution favoring lower discounts:
  - `0.00` (no promo) for most days (75% of orders)
  - `0.10` to `0.30` occasionally (seasonal sales, 21% of orders)
  - `0.40` or `0.50` only on rare "big promo" days (1% of orders)
- Values are floats rounded to 4 decimal places for precision

### How It Relates to Other Fields:
- **discount_amount** is calculated as: `discount_amount = discount_ratio * subtotal`
- If `subtotal` = 0, then `discount_ratio` and `discount_amount` are also 0
- **Discount Code** field is now empty (removed complex code logic)

## 📊 Discount Distribution

### Probability Weights
- **0.00 (No Discount)**: 75% - Most orders have no promotional discount
- **0.10 (10% Off)**: 8% - Light promotional discounts
- **0.15 (15% Off)**: 6% - Moderate promotional discounts  
- **0.20 (20% Off)**: 5% - Standard seasonal discounts
- **0.25 (25% Off)**: 3% - Higher promotional discounts
- **0.30 (30% Off)**: 2% - Seasonal sale discounts
- **0.40 (40% Off)**: 0.5% - Rare big promotional events
- **0.50 (50% Off)**: 0.5% - Very rare deep discount events

### Contextual Adjustments
- **Weekend Boost**: Higher probability of discounts on weekends
- **Holiday Boost**: Increased discount probability during holidays
- **Bulk Order Boost**: More discounts for orders with 4+ items

## 🤖 Prophet Model Applications

### 1. Discount Ratio as Regressor
Use `discount_ratio` as a numerical regressor in Prophet models:
```python
# Add discount_ratio as a regressor in Prophet
model.add_regressor('discount_ratio')
```

### 2. Revenue Impact Analysis
Analyze the relationship between:
- Discount ratio vs. order size correlation
- Seasonal discount effectiveness patterns
- Customer response to different discount levels
- Revenue optimization through discount modeling

### 3. Time Series Forecasting
Train Prophet models to:
- Predict optimal discount timing
- Forecast sales impact of promotional strategies
- Model seasonal discount patterns
- Optimize promotional calendars

### 4. Customer Behavior Modeling
Segment customers based on:
- Discount ratio sensitivity
- Response patterns to different discount levels
- Seasonal purchasing behavior
- Price elasticity analysis

## 📊 Data Fields for Prophet Analysis

### Core Prophet Fields
- `ds` (date): Created at timestamp for time series
- `y` (target): Sales quantity or revenue
- `discount_ratio`: Clean numerical regressor (0.0000 to 0.5000)
- `discount_amount`: Dollar impact of discounts

### Additional Regressors
- `is_weekend`: Weekend indicator for Prophet
- `is_holiday`: Holiday indicator for Prophet  
- `subtotal`: Pre-discount order value
- `total`: Final order value after discount

## 🔍 Sample Prophet Implementation

### Basic Model with Discount Regressor
```python
from prophet import Prophet
import pandas as pd

# Prepare data for Prophet
df = pd.read_csv('toy_sales_synthetic_YYYYMMDD_HHMMSS.csv')
prophet_data = df.groupby('Created at').agg({
    'Lineitem quantity': 'sum',
    'discount_ratio': 'mean',
    'is_weekend': 'first',
    'is_holiday': 'first'
}).reset_index()

prophet_data.columns = ['ds', 'y', 'discount_ratio', 'is_weekend', 'is_holiday']

# Initialize and configure Prophet model
model = Prophet()
model.add_regressor('discount_ratio')
model.add_regressor('is_weekend')
model.add_regressor('is_holiday')

# Fit the model
model.fit(prophet_data)

# Create future dataframe and forecast
future = model.make_future_dataframe(periods=30)
# Add regressor values for future periods
future['discount_ratio'] = 0.1  # Assume 10% discount for forecast
future['is_weekend'] = future['ds'].dt.weekday >= 5
future['is_holiday'] = 0  # Assume no holidays in forecast period

forecast = model.predict(future)
```
```sql
SELECT 
    MONTH(STR_TO_DATE(`Created at`, '%Y-%m-%d %H:%i:%s')) as month,
    AVG(`Discount Amount`) as avg_discount,
    COUNT(*) as total_orders
FROM orders 
WHERE `Discount Amount` > 0
GROUP BY month;
```

### Customer Discount Sensitivity
```sql
SELECT 
    `Email`,
    COUNT(*) as total_orders,
    SUM(CASE WHEN `Discount Amount` > 0 THEN 1 ELSE 0 END) as discounted_orders,
    AVG(`Discount Amount`) as avg_discount
FROM orders 
WHERE `Email` != ''
GROUP BY `Email`
HAVING total_orders > 1;
```

## 🎲 Randomization Features

- **Smart Contextual Selection**: Discount codes chosen based on season, day of week, and order characteristics
- **Realistic Constraints**: Discounts never exceed 90% of order value
- **Minimum Order Thresholds**: Reduced discount probability for orders under $25
- **Shipping Calculation**: Free shipping applied to discounted orders over $50

## 📈 Model Training Benefits

This discount system provides rich training data for:
- **Classification Models**: Predict discount usage likelihood
- **Regression Models**: Predict optimal discount amounts
- **Time Series Models**: Forecast promotional impact
- **Clustering Models**: Segment customers by discount behavior
- **Recommendation Systems**: Suggest personalized promotions

## 🔧 Configuration Options

All discount parameters are configurable in `generate_synthetic_orders.py`:

```python
ENABLE_DISCOUNTS = True
DISCOUNT_PROBABILITY = 0.25
HOLIDAY_DISCOUNT_BOOST = 2.0
WEEKEND_DISCOUNT_BOOST = 1.3
BULK_ORDER_DISCOUNT_BOOST = 1.5
MIN_ORDER_FOR_DISCOUNT = 25.0
```

This creates a realistic and comprehensive dataset for training sophisticated promotional and pricing models.
