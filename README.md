# Forezia Mock Data Generator

A comprehensive synthetic data generation toolkit for creating realistic toy sales data, specifically designed for machine learning forecasting models like Facebook Prophet.

## 🎯 Overview

This project generates realistic e-commerce sales data for a toy store with sophisticated patterns including seasonal trends, weekly cycles, product popularity variations, and growth trajectories. The data is specifically optimized for time series forecasting and machine learning applications.

## 📁 Project Structure

```
forezia-mock-data/
├── generate_synthetic_orders.py    # Main data generator
├── analyze_synthetic_data.py       # Data analysis and validation
├── visualize_sales_patterns.py     # Sales pattern visualization
├── expand_orders_csv.py            # Order data expansion utility
├── forezia_forecast.ipynb          # Prophet forecasting notebook
├── outlier_examples.py             # Outlier detection examples
├── orders_export.csv               # Original order export
├── toy_sales_*.csv                 # Generated synthetic data files
├── sku_daily_sales.csv            # SKU-level daily sales data
└── top_sku_daily_sales.csv        # Top SKU daily sales data
```

## 🚀 Quick Start

### Prerequisites

```bash
# Required Python packages
pip install pandas numpy matplotlib seaborn prophet tqdm
```

### Generate Synthetic Data

```bash
python generate_synthetic_orders.py
```

This will create a new CSV file with synthetic order data: `toy_sales_synthetic_YYYYMMDD_HHMMSS.csv`

**Note**: The generator automatically creates data for the past 12 months, ending yesterday to ensure no future dates are included in the dataset.

### Analyze Generated Data

```bash
python analyze_synthetic_data.py
```

### Visualize Sales Patterns

```bash
python visualize_sales_patterns.py
```

### Run Forecasting Model

Open and run the Jupyter notebook:
```bash
jupyter notebook forezia_forecast.ipynb
```

## 🎮 Product Catalog

The generator includes **50 realistic toy products** across various categories:

- **Building Sets**: LEGO, K'NEX, Lincoln Logs, Magna-Tiles
- **Action Figures**: Transformers, Spider-Man, Pokémon
- **Dolls & Figures**: Barbie, Disney Princess, LOL Surprise
- **Board Games**: Monopoly, Scrabble, UNO, Clue, Risk
- **Educational Toys**: Play-Doh, Crayola, Fisher-Price
- **Trending Items**: Hatchimals, Fidget Spinners, Shopkins

Each product includes:
- Realistic pricing ($3.99 - $199.99)
- Popularity scores (0.45 - 0.95)
- Trend patterns (growing, declining, stable, volatile)
- Vendor information

## 📊 Data Features

### Realistic Patterns
- **Seasonal Trends**: Holiday spikes, summer peaks, post-holiday dips
- **Weekly Cycles**: Weekend boosts, mid-week dips
- **Growth Patterns**: 8% average monthly growth with variations
- **Product Lifecycles**: Growing, declining, stable, and volatile trends

### Prophet Model Optimization
- **Minimum Sales Distribution**: Each SKU guaranteed 15+ sales days and 20+ total units
- **Autocorrelation**: Previous day sales influence current day patterns
- **Trend Strength**: Configurable trend signals for ML detection
- **Cyclical Patterns**: Multiple seasonal and weekly cycles

### Advanced Features
- **Quantity Variety**: Realistic quantity patterns based on popularity
- **Stock-out Simulation**: 5% probability of zero inventory
- **Bulk Orders**: 20% probability of high-quantity orders
- **Customer Diversity**: 15 realistic customer profiles with addresses
- **🏷️ Comprehensive Discount System**: Realistic promotional patterns for ML training

### 🏷️ New Discount System for Prophet Training
- **Simplified discount_ratio Field**: Clean ratio values between 0.00 and 0.50 for Prophet regressors
- **Realistic Distribution**: 75% no discount, gradually decreasing probabilities for higher discounts
- **Contextual Adjustments**: Higher discount probabilities on weekends, holidays, and bulk orders
- **Prophet-Optimized**: Clean numerical values perfect for time series forecasting models
- **ML Training Ready**: Designed specifically for discount propensity and revenue impact analysis

## ⚙️ Configuration

Key configuration variables in `generate_synthetic_orders.py`:

```python
# Time Period
NUMBER_OF_MONTHS = 12          # Generate 12 months of data
AVERAGE_MONTHLY_GROWTH = 0.08  # 8% monthly growth

# Pattern Strength
WEEKEND_BOOST_FACTOR = 1.8     # 80% weekend sales increase
BASE_DAILY_ORDERS = 15         # Starting daily order volume
SEASONAL_FACTOR = 0.3          # Seasonal variation strength

# Prophet Optimization
MIN_SALES_DAYS_PER_SKU = 15    # Minimum sales days per product
MIN_TOTAL_UNITS_PER_SKU = 20   # Minimum total units per product
ENSURE_SKU_DISTRIBUTION = True  # Force minimum distribution

# Quantity Patterns
ENABLE_QUANTITY_VARIETY = True  # Enable varied quantity patterns
STOCK_OUT_PROBABILITY = 0.05   # 5% chance of stock-outs
BULK_ORDER_PROBABILITY = 0.20  # 20% chance of bulk orders

# Discount System
ENABLE_DISCOUNTS = True         # Enable discount functionality
DISCOUNT_RATIO_PROBABILITIES = { # Probability distribution for discount ratios
    0.00: 0.75,   # 75% of orders have no discount (most common)
    0.10: 0.08,   # 8% have 10% discount (light promotions)
    0.15: 0.06,   # 6% have 15% discount
    0.20: 0.05,   # 5% have 20% discount
    0.25: 0.03,   # 3% have 25% discount
    0.30: 0.02,   # 2% have 30% discount (seasonal sales)
    0.40: 0.005,  # 0.5% have 40% discount (rare big promotions)
    0.50: 0.005,  # 0.5% have 50% discount (very rare deep promotions)
}
```

## 📈 Generated Data Format

The output CSV follows Shopify order export format with these key fields:

- **Order Info**: Name, Email, Created at, Total, Subtotal
- **Financial**: Payment Method, Financial Status, Paid at
- **Promotions**: **discount_ratio, Discount Amount** (NEW Prophet-optimized field!)
- **Fulfillment**: Fulfillment Status, Fulfilled at, Shipping
- **Line Items**: Quantity, Name, Price, SKU, Vendor
- **Customer**: Billing/Shipping addresses, Phone
- **Product**: SKU, Price, Vendor, Quantity

## 🔍 Analysis Tools

### analyze_synthetic_data.py
- Data quality validation
- Pattern verification
- Statistical summaries
- Anomaly detection

### visualize_sales_patterns.py
- Daily sales volume charts
- Revenue growth trends
- Product popularity analysis
- Seasonal pattern visualization

### forezia_forecast.ipynb
- Prophet model implementation
- Forecast generation
- Model evaluation
- Interactive plotting

## ⚠️ Important Notes

- **Date Range**: Data is generated for the past 12 months, ending yesterday to prevent future dates
- **Time Zone**: All timestamps use Eastern Time (-0400 offset)
- **Data Quality**: Each SKU guaranteed minimum sales distribution for Prophet compatibility

## 🎯 Use Cases

### Machine Learning
- **Time Series Forecasting**: Prophet, ARIMA, LSTM models
- **Demand Prediction**: Product-level demand forecasting
- **Seasonal Analysis**: Holiday and seasonal trend detection
- **Anomaly Detection**: Unusual sales pattern identification
- **🆕 Discount Propensity**: Predict customer discount usage likelihood
- **🆕 Revenue Impact**: Analyze promotional effectiveness and ROI
- **🆕 Price Optimization**: Model optimal discount strategies

### Business Intelligence
- **Sales Analytics**: Revenue and volume analysis
- **Product Performance**: SKU-level performance tracking
- **Customer Insights**: Purchase pattern analysis
- **Inventory Planning**: Stock level optimization
- **🆕 Promotional Analytics**: Discount performance and customer segmentation

### Development & Testing
- **API Testing**: Realistic data for e-commerce APIs
- **Dashboard Development**: Rich dataset for visualization tools
- **Performance Testing**: Large datasets for system testing
- **Algorithm Training**: Ground truth data for ML experiments

## 🛠️ Customization

### Adding New Products
Edit the `TOY_PRODUCTS` list in `generate_synthetic_orders.py`:

```python
{"name": "New Toy", "price": 24.99, "sku": "TOY-NEW-001", 
 "vendor": "Vendor Name", "popularity": 0.75, "trend": "growing"}
```

### Adjusting Patterns
Modify configuration variables:
- `SEASONAL_FACTOR`: Seasonal variation strength
- `WEEKEND_BOOST_FACTOR`: Weekend sales multiplier  
- `TREND_STRENGTH`: Trend pattern visibility

### Custom Time Periods
Change `NUMBER_OF_MONTHS` and date calculations in `generate_synthetic_data()`

## 📋 Dependencies

- **Python 3.7+**
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **matplotlib**: Basic plotting
- **seaborn**: Statistical visualization
- **prophet**: Time series forecasting
- **tqdm**: Progress bars (optional)
- **jupyter**: Notebook interface (optional)

## 🎲 Data Quality

The generator ensures:
- **Realistic Distributions**: Natural quantity and price patterns
- **Temporal Consistency**: Logical order, payment, and fulfillment timing
- **Product Variety**: Balanced representation across all SKUs
- **Customer Diversity**: Varied customer and address information
- **Financial Accuracy**: Correct tax and shipping calculations

## 🔮 Future Enhancements

- **Multi-store Support**: Generate data for multiple locations
- **Return/Refund Patterns**: Simulate return behaviors
- **Customer Loyalty**: Repeat customer patterns
- **Promotional Events**: Sale and discount simulations
- **Inventory Constraints**: Advanced stock management
- **International Sales**: Multi-currency and region support

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:
- New product categories
- Additional sales patterns
- Performance improvements
- Documentation updates

---

**Generated with ❤️ for machine learning and business intelligence applications**
