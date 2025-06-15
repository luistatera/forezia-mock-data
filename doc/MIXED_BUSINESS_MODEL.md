# Category-Based Mixed Business Model Implementation

## ✅ What Changed: From Single-Scenario to Realistic Mixed Business

### The Problem with the Old Approach
The original system had **5 separate config files** representing different business types:
- `config_stable_business.json` - 5% noise (grocery stores)
- `config_normal_retail.json` - 10% noise (toy stores) 
- `config_seasonal_fashion.json` - 15% noise (fashion items)
- `config_volatile_trending.json` - 20% noise (viral products)
- `config_example_small.json` - Testing configuration

**This was unrealistic** because real businesses have **mixed product portfolios**, not uniform demand patterns across all products.

### The New Approach: Category-Based Mixed Business Model

Now we have **one flexible configuration** that supports mixed business scenarios with different product categories having different behaviors:

## 🏪 Product Categories

### 1. **Stable Essentials** (30% of products by default)
- **Examples**: LEGO Classic, Monopoly, UNO, basic educational toys
- **Noise Factor**: ±5% (very predictable demand)
- **Seasonal Factor**: 0.1 (minimal seasonal variation)
- **Discount Behavior**: Low discount frequency (15%), max 20% discount
- **Characteristics**: Consistent sellers, bread-and-butter products

### 2. **Normal Retail** (40% of products by default)
- **Examples**: Action figures, dolls, board games, building sets
- **Noise Factor**: ±10% (typical retail variability)
- **Seasonal Factor**: 0.3 (moderate seasonal patterns)
- **Discount Behavior**: Standard discounting
- **Characteristics**: Core toy store inventory

### 3. **Seasonal Trending** (20% of products by default)
- **Examples**: Holiday-themed toys, fashion dolls, movie tie-ins
- **Noise Factor**: ±15% (higher variability)
- **Seasonal Factor**: 0.5 (strong seasonal influence)
- **Discount Behavior**: Higher discount frequency (40%), max 50% discount
- **Characteristics**: Seasonal spikes and fashion-driven demand

### 4. **Volatile Viral** (10% of products by default)
- **Examples**: Pokémon cards, Minecraft items, fidget toys, viral TikTok products
- **Noise Factor**: ±25% (highly unpredictable)
- **Seasonal Factor**: 0.2 (less seasonal, more trend-driven)
- **Discount Behavior**: Highest discount frequency (60%), max 70% discount
- **Characteristics**: Boom-and-bust cycles, social media driven

## 🔧 Configuration Structure

```json
{
    "data_generation": {
        "number_of_skus": 50,
        "number_of_months": 12,
        "average_monthly_growth": 0.08,
        "weekend_boost_factor": 1.8,
        "base_daily_orders": 15,
        "seasonal_factor": 0.3
    },
    "product_categories": {
        "stable_essentials": {
            "description": "Basic toys, educational items, classic games",
            "percentage_of_skus": 0.30,
            "random_noise_factor": 0.05,
            "seasonal_factor": 0.1
        },
        "normal_retail": {
            "percentage_of_skus": 0.40,
            "random_noise_factor": 0.1,
            "seasonal_factor": 0.3
        },
        "seasonal_trending": {
            "percentage_of_skus": 0.20,
            "random_noise_factor": 0.15,
            "seasonal_factor": 0.5
        },
        "volatile_viral": {
            "percentage_of_skus": 0.10,
            "random_noise_factor": 0.25,
            "seasonal_factor": 0.2
        }
    },
    "discounts": {
        "category_specific_discounts": {
            "stable_essentials": {
                "discount_probability": 0.15,
                "max_discount": 0.20
            },
            "seasonal_trending": {
                "discount_probability": 0.40,
                "max_discount": 0.50
            },
            "volatile_viral": {
                "discount_probability": 0.60,
                "max_discount": 0.70
            }
        }
    }
}
```

## 🚀 Key Benefits

### 1. **Realistic Business Simulation**
- Matches how real businesses actually operate with mixed portfolios
- Different products have different demand patterns and seasonality
- Category-specific discounting strategies

### 2. **Better ML Training Data**
- More diverse patterns for forecasting models to learn from
- Represents real-world complexity that algorithms will encounter
- Improved Prophet model training with varied signal strengths

### 3. **Flexible Configuration**
- Easy to adjust category percentages based on actual customer mix
- Category-specific noise levels and seasonal factors
- No need for multiple separate config files

### 4. **Customer-Specific Customization**
- Grocery chain: 80% stable, 15% normal, 5% seasonal
- Fashion retailer: 20% stable, 30% normal, 40% seasonal, 10% viral
- Electronics store: 30% stable, 40% normal, 10% seasonal, 20% viral

## 📊 Implementation Details

### Product Assignment
- Products are automatically assigned to categories based on configured percentages
- Base products have predefined categories (e.g., LEGO → stable_essentials)
- Generated products are assigned categories based on weighted random selection

### Category-Specific Behavior
- **Noise factors** applied per category during quantity generation
- **Seasonal factors** modified per category for demand calculation
- **Discount probabilities** and maximum discounts vary by category
- **Product characteristics** (price ranges, popularity) tailored per category

### Backward Compatibility
- System falls back to global settings if categories are not configured
- Existing config files continue to work without modification
- Old single-scenario configs can still be used for specific testing

## 🎯 Real-World Examples

### Example 1: Balanced Toy Store
```json
"product_categories": {
    "stable_essentials": {"percentage_of_skus": 0.25},
    "normal_retail": {"percentage_of_skus": 0.50},
    "seasonal_trending": {"percentage_of_skus": 0.20},
    "volatile_viral": {"percentage_of_skus": 0.05}
}
```

### Example 2: Trend-Focused Retailer
```json
"product_categories": {
    "stable_essentials": {"percentage_of_skus": 0.15},
    "normal_retail": {"percentage_of_skus": 0.35},
    "seasonal_trending": {"percentage_of_skus": 0.30},
    "volatile_viral": {"percentage_of_skus": 0.20}
}
```

### Example 3: Conservative Family Store
```json
"product_categories": {
    "stable_essentials": {"percentage_of_skus": 0.50},
    "normal_retail": {"percentage_of_skus": 0.40},
    "seasonal_trending": {"percentage_of_skus": 0.08},
    "volatile_viral": {"percentage_of_skus": 0.02}
}
```

This new approach provides much more realistic synthetic data that actually prepares forecasting models for the complexity of real-world mixed business scenarios! 🎉
