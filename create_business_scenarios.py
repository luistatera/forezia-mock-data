#!/usr/bin/env python3
"""
Demonstrate how different noise factors suit different business scenarios
"""

import json
import os

def create_example_configs():
    """Create example configuration files for different business scenarios."""
    
    # Base configuration
    base_config = {
        "data_generation": {
            "number_of_skus": 1,
            "number_of_months": 12,
            "average_monthly_growth": 0.08,
            "weekend_boost_factor": 1.8,
            "base_daily_orders": 15,
            "seasonal_factor": 0.3
        },
        "prophet_optimization": {
            "min_sales_days_per_sku": 30,
            "min_total_units_per_sku": 50,
            "ensure_sku_distribution": True,
            "sku_popularity_weights": True
        },
        "discounts": {
            "enable_discounts": True,
            "discount_ratio_probabilities": {
                "0.00": 0.75,
                "0.10": 0.08,
                "0.15": 0.06,
                "0.20": 0.05,
                "0.25": 0.03,
                "0.30": 0.02,
                "0.40": 0.005,
                "0.50": 0.005
            }
        },
        "quantity_settings": {
            "enable_quantity_variety": True,
            "min_quantity": 0,
            "max_quantity": 8,
            "stock_out_probability": 0.05,
            "bulk_order_probability": 0.20,
            "low_inventory_probability": 0.15,
            "high_demand_spike_probability": 0.10
        }
    }
    
    # Business scenario configurations
    scenarios = {
        "stable_business": {
            "description": "Grocery store, utilities, essential items",
            "noise_factor": 0.05,
            "characteristics": "Very predictable demand with minimal fluctuation"
        },
        "normal_retail": {
            "description": "Toy store, general retail, recommended default",
            "noise_factor": 0.1,
            "characteristics": "Typical retail demand with moderate fluctuation"
        },
        "seasonal_fashion": {
            "description": "Clothing, seasonal items, weather dependent",
            "noise_factor": 0.15,
            "characteristics": "Higher variability due to trends and seasonality"
        },
        "volatile_trending": {
            "description": "Viral products, social media driven, tech gadgets",
            "noise_factor": 0.2,
            "characteristics": "High unpredictability and demand spikes"
        }
    }
    
    print("🏪 Business Scenario Configuration Examples")
    print("=" * 50)
    
    for scenario_name, scenario_info in scenarios.items():
        # Create scenario-specific config
        scenario_config = base_config.copy()
        scenario_config["data_generation"]["random_noise_factor"] = scenario_info["noise_factor"]
        
        # Save configuration file
        filename = f"config_{scenario_name}.json"
        with open(filename, 'w') as f:
            json.dump(scenario_config, f, indent=4)
        
        print(f"📁 {filename}")
        print(f"   🏢 {scenario_info['description']}")
        print(f"   📊 Noise Factor: {scenario_info['noise_factor']} (±{scenario_info['noise_factor']*100:.0f}%)")
        print(f"   📈 {scenario_info['characteristics']}")
        print()
    
    print("💡 Usage Instructions:")
    print("   1. Copy the appropriate config file to 'config.json'")
    print("   2. Run: python generate_synthetic_orders.py")
    print("   3. Observe how noise affects demand patterns")
    print()
    print("🔧 Custom Configuration:")
    print("   - Edit 'random_noise_factor' in config.json")
    print("   - Range: 0.05 (very stable) to 0.2 (very volatile)")
    print("   - Test with: python test_noise_factor.py")

if __name__ == "__main__":
    create_example_configs()
