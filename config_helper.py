#!/usr/bin/env python3
"""
Configuration Helper for Forezia Mock Data Generator
Creates and validates config.json files
"""

import json
import os

def create_default_config():
    """Create a default config.json file."""
    default_config = {
        "data_generation": {
            "number_of_skus": 50,
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
    
    with open('config.json', 'w') as f:
        json.dump(default_config, f, indent=4)
    
    print("✅ Created default config.json file")
    return default_config

def validate_config(config_path='config.json'):
    """Validate the configuration file."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print("✅ Config file is valid JSON")
        
        # Check required sections
        required_sections = ['data_generation', 'prophet_optimization', 'discounts', 'quantity_settings']
        for section in required_sections:
            if section not in config:
                print(f"⚠️  Missing section: {section}")
            else:
                print(f"✅ Found section: {section}")
        
        # Check key values
        if 'data_generation' in config:
            num_skus = config['data_generation'].get('number_of_skus', 50)
            if num_skus < 1:
                print("❌ number_of_skus must be at least 1")
            elif num_skus > 1000:
                print("⚠️  number_of_skus is very large (>1000). This may generate a lot of data.")
            else:
                print(f"✅ number_of_skus: {num_skus}")
        
        # Check discount probabilities sum to 1.0
        if 'discounts' in config and 'discount_ratio_probabilities' in config['discounts']:
            probs = config['discounts']['discount_ratio_probabilities']
            total_prob = sum(probs.values())
            if abs(total_prob - 1.0) > 0.01:
                print(f"⚠️  Discount probabilities sum to {total_prob:.3f}, should be 1.0")
            else:
                print("✅ Discount probabilities sum correctly")
        
        return config
        
    except FileNotFoundError:
        print(f"❌ Config file not found: {config_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in config file: {e}")
        return None

def interactive_config():
    """Create a config file interactively."""
    print("🔧 Interactive Configuration Creator")
    print("Press Enter to use default values in [brackets]\n")
    
    # Data generation settings
    num_skus = input("Number of SKUs to generate [50]: ").strip()
    num_skus = int(num_skus) if num_skus else 50
    
    num_months = input("Number of months of data [12]: ").strip()
    num_months = int(num_months) if num_months else 12
    
    growth_rate = input("Monthly growth rate (0.08 = 8%) [0.08]: ").strip()
    growth_rate = float(growth_rate) if growth_rate else 0.08
    
    weekend_boost = input("Weekend boost factor (1.8 = 80% increase) [1.8]: ").strip()
    weekend_boost = float(weekend_boost) if weekend_boost else 1.8
    
    config = create_default_config()
    
    # Update with user inputs
    config['data_generation']['number_of_skus'] = num_skus
    config['data_generation']['number_of_months'] = num_months
    config['data_generation']['average_monthly_growth'] = growth_rate
    config['data_generation']['weekend_boost_factor'] = weekend_boost
    
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)
    
    print(f"\n✅ Created config.json with {num_skus} SKUs and {num_months} months of data")

def main():
    print("🚀 Forezia Mock Data Configuration Helper\n")
    
    if os.path.exists('config.json'):
        print("Found existing config.json file")
        config = validate_config()
        if config:
            num_skus = config.get('data_generation', {}).get('number_of_skus', 'unknown')
            print(f"📊 Currently configured for {num_skus} SKUs\n")
    else:
        print("No config.json file found\n")
    
    while True:
        print("Choose an option:")
        print("1. Create default config.json")
        print("2. Create config.json interactively")
        print("3. Validate existing config.json")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            create_default_config()
            break
        elif choice == '2':
            interactive_config()
            break
        elif choice == '3':
            validate_config()
            break
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.\n")

if __name__ == "__main__":
    main()
