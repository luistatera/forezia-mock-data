#!/usr/bin/env python3
"""
Synthetic Orders Data Generator for Toys for Kids
Generates realistic sales data with weekend spikes and monthly growth patterns
"""

import csv
import json
import random
import string
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import math
import holidays
import os

def load_config():
    """Load configuration from config.json file."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️  Config file not found at {config_path}. Using default values.")
        return {}
    except json.JSONDecodeError as e:
        print(f"⚠️  Error parsing config file: {e}. Using default values.")
        return {}

# Load configuration
CONFIG = load_config()

# Configuration Variables - loaded from config.json or using defaults
NUMBER_OF_MONTHS = CONFIG.get('data_generation', {}).get('number_of_months', 12)
AVERAGE_MONTHLY_GROWTH = CONFIG.get('data_generation', {}).get('average_monthly_growth', 0.08)
WEEKEND_BOOST_FACTOR = CONFIG.get('data_generation', {}).get('weekend_boost_factor', 1.8)
BASE_DAILY_ORDERS = CONFIG.get('data_generation', {}).get('base_daily_orders', 15)
SEASONAL_FACTOR = CONFIG.get('data_generation', {}).get('seasonal_factor', 0.3)
RANDOM_NOISE_FACTOR = CONFIG.get('data_generation', {}).get('random_noise_factor', 0.1)

# Random Noise Configuration
# The RANDOM_NOISE_FACTOR adds controlled randomness to simulate real-world demand fluctuations
# - 0.1 = ±10% Gaussian noise (realistic for most businesses)
# - 0.05 = ±5% noise (more stable demand)
# - 0.2 = ±20% noise (highly volatile demand)
# This affects both daily order counts and individual quantity calculations

# Number of SKUs to generate (loaded from config)
NUMBER_OF_SKUS = CONFIG.get('data_generation', {}).get('number_of_skus', 50)

# Enhanced Prophet Learning Patterns
ENABLE_STRONG_PATTERNS = True  # Enable stronger patterns for Prophet to learn
AUTOCORRELATION_FACTOR = 0.3  # How much previous days affect current day
CYCLICAL_PATTERNS = True  # Enable cyclical demand patterns
TREND_STRENGTH = 0.4  # How strong trending signals should be

# Prophet Model Compatibility Settings - loaded from config.json or using defaults
MIN_SALES_DAYS_PER_SKU = CONFIG.get('prophet_optimization', {}).get('min_sales_days_per_sku', 30)
MIN_TOTAL_UNITS_PER_SKU = CONFIG.get('prophet_optimization', {}).get('min_total_units_per_sku', 50)
ENSURE_SKU_DISTRIBUTION = CONFIG.get('prophet_optimization', {}).get('ensure_sku_distribution', True)
SKU_POPULARITY_WEIGHTS = CONFIG.get('prophet_optimization', {}).get('sku_popularity_weights', True)

# New Discount Configuration for Prophet Training Data - loaded from config.json
ENABLE_DISCOUNTS = CONFIG.get('discounts', {}).get('enable_discounts', True)

# Discount ratio configuration - simplified for Prophet model
config_discount_probs = CONFIG.get('discounts', {}).get('discount_ratio_probabilities', {})
DISCOUNT_RATIO_PROBABILITIES = {}
for ratio_str, prob in config_discount_probs.items():
    DISCOUNT_RATIO_PROBABILITIES[float(ratio_str)] = prob

# Default discount probabilities if not in config
if not DISCOUNT_RATIO_PROBABILITIES:
    DISCOUNT_RATIO_PROBABILITIES = {
        0.00: 0.75,   # 75% of orders have no discount (most common)
        0.10: 0.08,   # 8% have 10% discount (light promotions)
        0.15: 0.06,   # 6% have 15% discount
        0.20: 0.05,   # 5% have 20% discount
        0.25: 0.03,   # 3% have 25% discount
        0.30: 0.02,   # 2% have 30% discount (seasonal sales)
        0.40: 0.005,  # 0.5% have 40% discount (rare big promotions)
        0.50: 0.005,  # 0.5% have 50% discount (very rare deep promotions)
    }

# Quantity Variety Settings for Better ML Performance - loaded from config.json
ENABLE_QUANTITY_VARIETY = CONFIG.get('quantity_settings', {}).get('enable_quantity_variety', True)
MIN_QUANTITY = CONFIG.get('quantity_settings', {}).get('min_quantity', 0)
MAX_QUANTITY = CONFIG.get('quantity_settings', {}).get('max_quantity', 8)
STOCK_OUT_PROBABILITY = CONFIG.get('quantity_settings', {}).get('stock_out_probability', 0.05)
BULK_ORDER_PROBABILITY = CONFIG.get('quantity_settings', {}).get('bulk_order_probability', 0.20)
LOW_INVENTORY_PROBABILITY = CONFIG.get('quantity_settings', {}).get('low_inventory_probability', 0.15)
HIGH_DEMAND_SPIKE_PROBABILITY = CONFIG.get('quantity_settings', {}).get('high_demand_spike_probability', 0.10)

# Quantity patterns based on product popularity and demand
QUANTITY_PATTERNS = {
    'high_demand': {'weights': [0.03, 0.12, 0.25, 0.30, 0.20, 0.08, 0.02], 'values': [0, 1, 2, 3, 4, 5, 6]},
    'medium_demand': {'weights': [0.05, 0.20, 0.35, 0.25, 0.12, 0.03], 'values': [0, 1, 2, 3, 4, 5]},
    'low_demand': {'weights': [0.15, 0.40, 0.25, 0.15, 0.05], 'values': [0, 1, 2, 3, 4]},
    'variable': {'weights': [0.10, 0.18, 0.22, 0.20, 0.15, 0.10, 0.05], 'values': [0, 1, 2, 3, 4, 5, 6]}
}

# Toy Products Database - dynamically generated based on config
def generate_toy_products(num_skus):
    """Generate toy products list based on the configured number of SKUs."""
    
    # Base product templates to use for generation
    base_products = [
        {"name": "LEGO Classic Creative Bricks", "price": 29.99, "sku": "TOY-LEGO-001", "vendor": "LEGO Group", "popularity": 0.95, "trend": "stable"},
        {"name": "Barbie Dreamhouse Playset", "price": 199.99, "sku": "TOY-BARB-001", "vendor": "Mattel", "popularity": 0.85, "trend": "growing"},
        {"name": "Hot Wheels Track Builder", "price": 34.99, "sku": "TOY-HW-001", "vendor": "Mattel", "popularity": 0.90, "trend": "stable"},
        {"name": "Monopoly Board Game", "price": 24.99, "sku": "TOY-MONO-001", "vendor": "Hasbro", "popularity": 0.88, "trend": "stable"},
        {"name": "Nerf Elite Blaster", "price": 19.99, "sku": "TOY-NERF-001", "vendor": "Hasbro", "popularity": 0.92, "trend": "growing"},
        {"name": "Play-Doh Creative Set", "price": 15.99, "sku": "TOY-PD-001", "vendor": "Hasbro", "popularity": 0.89, "trend": "stable"},
        {"name": "Fisher-Price Rock-a-Stack", "price": 8.99, "sku": "TOY-FP-001", "vendor": "Fisher-Price", "popularity": 0.75, "trend": "declining"},
        {"name": "Crayola Art Supplies Kit", "price": 22.99, "sku": "TOY-CRAY-001", "vendor": "Crayola", "popularity": 0.82, "trend": "stable"},
        {"name": "Rubik's Cube Classic", "price": 12.99, "sku": "TOY-RUB-001", "vendor": "Spin Master", "popularity": 0.70, "trend": "volatile"},
        {"name": "Transformers Action Figure", "price": 29.99, "sku": "TOY-TRANS-001", "vendor": "Hasbro", "popularity": 0.78, "trend": "stable"},
        {"name": "Pokémon Trading Cards", "price": 4.99, "sku": "TOY-POKE-001", "vendor": "Pokémon Company", "popularity": 0.95, "trend": "growing"},
        {"name": "My Little Pony Figure", "price": 16.99, "sku": "TOY-MLP-001", "vendor": "Hasbro", "popularity": 0.72, "trend": "declining"},
        {"name": "Thomas & Friends Train Set", "price": 39.99, "sku": "TOY-THOMAS-001", "vendor": "Mattel", "popularity": 0.68, "trend": "declining"},
        {"name": "Minecraft Building Set", "price": 44.99, "sku": "TOY-MC-001", "vendor": "LEGO Group", "popularity": 0.87, "trend": "growing"},
        {"name": "Scrabble Junior", "price": 19.99, "sku": "TOY-SCRAB-001", "vendor": "Hasbro", "popularity": 0.60, "trend": "stable"},
        {"name": "UNO Card Game", "price": 7.99, "sku": "TOY-UNO-001", "vendor": "Mattel", "popularity": 0.85, "trend": "stable"},
        {"name": "Jenga Classic Game", "price": 9.99, "sku": "TOY-JENGA-001", "vendor": "Hasbro", "popularity": 0.80, "trend": "stable"},
        {"name": "Peppa Pig Playhouse", "price": 54.99, "sku": "TOY-PEPPA-001", "vendor": "Character Options", "popularity": 0.65, "trend": "declining"},
        {"name": "Disney Princess Doll", "price": 24.99, "sku": "TOY-DISNEY-001", "vendor": "Mattel", "popularity": 0.83, "trend": "stable"},
        {"name": "Spider-Man Action Figure", "price": 18.99, "sku": "TOY-SPIDER-001", "vendor": "Hasbro", "popularity": 0.86, "trend": "growing"},
        {"name": "Frozen Elsa Dress-Up", "price": 32.99, "sku": "TOY-FROZEN-001", "vendor": "Disney", "popularity": 0.81, "trend": "declining"},
        {"name": "Cars Lightning McQueen", "price": 21.99, "sku": "TOY-CARS-001", "vendor": "Mattel", "popularity": 0.77, "trend": "stable"},
        {"name": "Paw Patrol Rescue Vehicle", "price": 26.99, "sku": "TOY-PAW-001", "vendor": "Spin Master", "popularity": 0.84, "trend": "growing"},
        {"name": "Baby Alive Interactive Doll", "price": 49.99, "sku": "TOY-BABY-001", "vendor": "Hasbro", "popularity": 0.69, "trend": "stable"},
        {"name": "Magic 8 Ball", "price": 11.99, "sku": "TOY-MAGIC-001", "vendor": "Mattel", "popularity": 0.55, "trend": "stable"},
        {"name": "Slinky Original", "price": 5.99, "sku": "TOY-SLINK-001", "vendor": "Poof Slinky", "popularity": 0.58, "trend": "declining"},
        {"name": "Connect 4 Game", "price": 14.99, "sku": "TOY-CON4-001", "vendor": "Hasbro", "popularity": 0.74, "trend": "stable"},
        {"name": "Operation Board Game", "price": 16.99, "sku": "TOY-OP-001", "vendor": "Hasbro", "popularity": 0.67, "trend": "stable"},
        {"name": "Risk Strategy Game", "price": 39.99, "sku": "TOY-RISK-001", "vendor": "Hasbro", "popularity": 0.52, "trend": "stable"},
        {"name": "Clue Mystery Game", "price": 19.99, "sku": "TOY-CLUE-001", "vendor": "Hasbro", "popularity": 0.63, "trend": "stable"},
        {"name": "Yahtzee Dice Game", "price": 8.99, "sku": "TOY-YAH-001", "vendor": "Hasbro", "popularity": 0.71, "trend": "stable"},
        {"name": "Twister Floor Game", "price": 12.99, "sku": "TOY-TWIST-001", "vendor": "Hasbro", "popularity": 0.76, "trend": "stable"},
        {"name": "Sorry! Board Game", "price": 17.99, "sku": "TOY-SORRY-001", "vendor": "Hasbro", "popularity": 0.59, "trend": "declining"},
        {"name": "Trouble Pop-O-Matic", "price": 13.99, "sku": "TOY-TROUB-001", "vendor": "Hasbro", "popularity": 0.61, "trend": "stable"},
        {"name": "Guess Who? Game", "price": 11.99, "sku": "TOY-GUESS-001", "vendor": "Hasbro", "popularity": 0.66, "trend": "stable"},
        {"name": "Battleship Strategy Game", "price": 18.99, "sku": "TOY-BATTLE-001", "vendor": "Hasbro", "popularity": 0.64, "trend": "stable"},
        {"name": "Candy Land Adventure", "price": 9.99, "sku": "TOY-CANDY-001", "vendor": "Hasbro", "popularity": 0.79, "trend": "stable"},
        {"name": "Chutes and Ladders", "price": 8.99, "sku": "TOY-CHUTES-001", "vendor": "Hasbro", "popularity": 0.73, "trend": "stable"},
        {"name": "LEGO Friends Heartlake City", "price": 89.99, "sku": "TOY-LEGO-002", "vendor": "LEGO Group", "popularity": 0.75, "trend": "growing"},
        {"name": "LEGO Technic Race Car", "price": 69.99, "sku": "TOY-LEGO-003", "vendor": "LEGO Group", "popularity": 0.68, "trend": "growing"},
        {"name": "K'NEX Building Set", "price": 24.99, "sku": "TOY-KNEX-001", "vendor": "K'NEX", "popularity": 0.48, "trend": "declining"},
        {"name": "Lincoln Logs Cabin", "price": 29.99, "sku": "TOY-LINC-001", "vendor": "K'NEX", "popularity": 0.54, "trend": "declining"},
        {"name": "Tinker Toys Classic Set", "price": 19.99, "sku": "TOY-TINK-001", "vendor": "K'NEX", "popularity": 0.51, "trend": "declining"},
        {"name": "Magna-Tiles Clear Colors", "price": 49.99, "sku": "TOY-MAGNA-001", "vendor": "Magna-Tiles", "popularity": 0.70, "trend": "growing"},
        {"name": "Playmobil Pirate Ship", "price": 79.99, "sku": "TOY-PLAY-001", "vendor": "Playmobil", "popularity": 0.56, "trend": "stable"},
        {"name": "Calico Critters Family", "price": 34.99, "sku": "TOY-CALI-001", "vendor": "Epoch Everlasting Play", "popularity": 0.62, "trend": "stable"},
        {"name": "Shopkins Mini Figures", "price": 6.99, "sku": "TOY-SHOP-001", "vendor": "Moose Toys", "popularity": 0.73, "trend": "declining"},
        {"name": "LOL Surprise Dolls", "price": 9.99, "sku": "TOY-LOL-001", "vendor": "MGA Entertainment", "popularity": 0.88, "trend": "volatile"},
        {"name": "Hatchimals Surprise Egg", "price": 59.99, "sku": "TOY-HATCH-001", "vendor": "Spin Master", "popularity": 0.67, "trend": "declining"},
        {"name": "Fidget Spinner Classic", "price": 3.99, "sku": "TOY-FIDG-001", "vendor": "Various", "popularity": 0.45, "trend": "declining"}
    ]
    
    vendors = ["Hasbro", "Mattel", "LEGO Group", "Fisher-Price", "Spin Master", "Disney", "Crayola", "K'NEX", "Playmobil", "Various"]
    trends = ["stable", "growing", "declining", "volatile"]
    product_types = [
        "Building Set", "Action Figure", "Doll", "Board Game", "Card Game", "Puzzle", "Art Supplies",
        "Educational Toy", "Electronic Toy", "Outdoor Toy", "Vehicle", "Plush Toy", "Dress-Up", "Musical Toy"
    ]
    
    products = []
    
    # Use base products first (up to the number available)
    for i in range(min(num_skus, len(base_products))):
        products.append(base_products[i].copy())
    
    # Generate additional products if needed
    for i in range(len(base_products), num_skus):
        sku_num = i + 1
        product_type = random.choice(product_types)
        vendor = random.choice(vendors)
        
        product = {
            "name": f"{product_type} #{sku_num}",
            "price": round(random.uniform(3.99, 199.99), 2),
            "sku": f"TOY-GEN-{sku_num:03d}",
            "vendor": vendor,
            "popularity": round(random.uniform(0.45, 0.95), 2),
            "trend": random.choice(trends)
        }
        products.append(product)
    
    return products

# Generate TOY_PRODUCTS based on config
TOY_PRODUCTS = generate_toy_products(NUMBER_OF_SKUS)

# Customer database for realistic names and emails
CUSTOMERS = [
    {"name": "Emma Johnson", "email": "emma.johnson@example.com", "phone": "+1234567890"},
    {"name": "Liam Smith", "email": "liam.smith@example.com", "phone": "+1234567891"},
    {"name": "Olivia Williams", "email": "olivia.williams@example.com", "phone": "+1234567892"},
    {"name": "Noah Brown", "email": "noah.brown@example.com", "phone": "+1234567893"},
    {"name": "Ava Jones", "email": "ava.jones@example.com", "phone": "+1234567894"},
    {"name": "Isabella Garcia", "email": "isabella.garcia@example.com", "phone": "+1234567895"},
    {"name": "Sophia Miller", "email": "sophia.miller@example.com", "phone": "+1234567896"},
    {"name": "Jackson Davis", "email": "jackson.davis@example.com", "phone": "+1234567897"},
    {"name": "Mia Rodriguez", "email": "mia.rodriguez@example.com", "phone": "+1234567898"},
    {"name": "Lucas Wilson", "email": "lucas.wilson@example.com", "phone": "+1234567899"},
    {"name": "Charlotte Martinez", "email": "charlotte.martinez@example.com", "phone": "+1234567800"},
    {"name": "Ethan Anderson", "email": "ethan.anderson@example.com", "phone": "+1234567801"},
    {"name": "Amelia Taylor", "email": "amelia.taylor@example.com", "phone": "+1234567802"},
    {"name": "Alexander Thomas", "email": "alexander.thomas@example.com", "phone": "+1234567803"},
    {"name": "Harper Jackson", "email": "harper.jackson@example.com", "phone": "+1234567804"},
]

# Supported Countries Configuration
SUPPORTED_COUNTRIES = ['US', 'CA', 'GB', 'AU']  # Each order is randomly assigned to one of these countries

# Address database with multiple countries
# Each order will randomly select one country and then choose a random address from that country
ADDRESSES = {
    'US': [
        {"street": "123 Maple Street", "city": "Springfield", "zip": "12345", "province": "NY", "country": "US"},
        {"street": "456 Oak Avenue", "city": "Madison", "zip": "53706", "province": "WI", "country": "US"},
        {"street": "789 Pine Road", "city": "Austin", "zip": "73301", "province": "TX", "country": "US"},
        {"street": "321 Elm Street", "city": "Portland", "zip": "97201", "province": "OR", "country": "US"},
        {"street": "654 Cedar Lane", "city": "Denver", "zip": "80202", "province": "CO", "country": "US"},
        {"street": "987 Birch Drive", "city": "Seattle", "zip": "98101", "province": "WA", "country": "US"},
        {"street": "147 Willow Way", "city": "Phoenix", "zip": "85001", "province": "AZ", "country": "US"},
        {"street": "258 Spruce Court", "city": "Miami", "zip": "33101", "province": "FL", "country": "US"},
        {"street": "369 Aspen Place", "city": "Boston", "zip": "02101", "province": "MA", "country": "US"},
        {"street": "741 Poplar Boulevard", "city": "Chicago", "zip": "60601", "province": "IL", "country": "US"},
    ],
    'CA': [
        {"street": "100 King Street", "city": "Toronto", "zip": "M5H 1A1", "province": "ON", "country": "CA"},
        {"street": "200 Robson Street", "city": "Vancouver", "zip": "V6B 2A7", "province": "BC", "country": "CA"},
        {"street": "300 8th Avenue SW", "city": "Calgary", "zip": "T2P 1C5", "province": "AB", "country": "CA"},
        {"street": "400 Portage Avenue", "city": "Winnipeg", "zip": "R3C 0C8", "province": "MB", "country": "CA"},
        {"street": "500 University Avenue", "city": "Toronto", "zip": "M5G 1V7", "province": "ON", "country": "CA"},
        {"street": "600 René-Lévesque Blvd", "city": "Montreal", "zip": "H3B 1H7", "province": "QC", "country": "CA"},
        {"street": "700 Water Street", "city": "St. John's", "zip": "A1E 1B6", "province": "NL", "country": "CA"},
        {"street": "800 Jasper Avenue", "city": "Edmonton", "zip": "T5J 3N4", "province": "AB", "country": "CA"},
        {"street": "900 Georgia Street", "city": "Vancouver", "zip": "V6C 2W6", "province": "BC", "country": "CA"},
        {"street": "1000 Yonge Street", "city": "Toronto", "zip": "M4W 2K2", "province": "ON", "country": "CA"},
    ],
    'GB': [
        {"street": "10 Downing Street", "city": "London", "zip": "SW1A 2AA", "province": "England", "country": "GB"},
        {"street": "15 Baker Street", "city": "London", "zip": "NW1 6XE", "province": "England", "country": "GB"},
        {"street": "20 Princess Street", "city": "Manchester", "zip": "M1 4LY", "province": "England", "country": "GB"},
        {"street": "25 Rose Street", "city": "Edinburgh", "zip": "EH2 2PR", "province": "Scotland", "country": "GB"},
        {"street": "30 Castle Street", "city": "Cardiff", "zip": "CF10 1BH", "province": "Wales", "country": "GB"},
        {"street": "35 High Street", "city": "Birmingham", "zip": "B4 7SL", "province": "England", "country": "GB"},
        {"street": "40 Church Street", "city": "Liverpool", "zip": "L1 3AX", "province": "England", "country": "GB"},
        {"street": "45 Queen Street", "city": "Glasgow", "zip": "G1 3DX", "province": "Scotland", "country": "GB"},
        {"street": "50 Market Street", "city": "Leeds", "zip": "LS1 6DT", "province": "England", "country": "GB"},
        {"street": "55 King Street", "city": "Bristol", "zip": "BS1 4ER", "province": "England", "country": "GB"},
    ],
    'AU': [
        {"street": "123 Collins Street", "city": "Melbourne", "zip": "3000", "province": "VIC", "country": "AU"},
        {"street": "456 George Street", "city": "Sydney", "zip": "2000", "province": "NSW", "country": "AU"},
        {"street": "789 Queen Street", "city": "Brisbane", "zip": "4000", "province": "QLD", "country": "AU"},
        {"street": "321 King William Street", "city": "Adelaide", "zip": "5000", "province": "SA", "country": "AU"},
        {"street": "654 Hay Street", "city": "Perth", "zip": "6000", "province": "WA", "country": "AU"},
        {"street": "987 Elizabeth Street", "city": "Hobart", "zip": "7000", "province": "TAS", "country": "AU"},
        {"street": "147 Smith Street", "city": "Darwin", "zip": "0800", "province": "NT", "country": "AU"},
        {"street": "258 Northbourne Avenue", "city": "Canberra", "zip": "2600", "province": "ACT", "country": "AU"},
        {"street": "369 Flinders Street", "city": "Melbourne", "zip": "3000", "province": "VIC", "country": "AU"},
        {"street": "741 Pitt Street", "city": "Sydney", "zip": "2000", "province": "NSW", "country": "AU"},
    ]
}

def generate_random_id(length: int = 25) -> str:
    """Generate a random alphanumeric ID."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_order_id() -> int:
    """Generate a sequential order ID."""
    if not hasattr(generate_order_id, "counter"):
        generate_order_id.counter = 2000
    generate_order_id.counter += 1
    return generate_order_id.counter

def calculate_seasonal_factor(date: datetime) -> float:
    """Calculate seasonal factor with more realistic, less extreme patterns."""
    month = date.month
    day_of_year = date.timetuple().tm_yday
    # Softer seasonal multipliers
    seasonal_multipliers = {
        1: 1.10,   # January
        2: 0.92,   # February
        3: 0.97,   # March
        4: 1.05,   # April
        5: 1.03,   # May
        6: 0.98,   # June
        7: 1.04,   # July
        8: 1.00,   # August
        9: 1.02,   # September
        10: 1.08,  # October
        11: 1.13,  # November
        12: 1.18,  # December
    }
    base_seasonal = seasonal_multipliers.get(month, 1.0)
    # Smoother sinusoidal variation
    yearly_cycle = 1 + 0.12 * math.sin(2 * math.pi * day_of_year / 365.25 + math.pi/2)
    return (base_seasonal + yearly_cycle) / 2

def get_us_holidays(start_date, end_date):
    """Return a set of US holiday dates between start_date and end_date."""
    us_holidays = holidays.country_holidays('US', years=range(start_date.year, end_date.year + 1))
    return set(us_holidays.keys())

def calculate_daily_orders(date: datetime, month_index: int, us_holiday_dates=None, prev_orders: int = None, sku: str = None, sku_trend: float = 0.0, mean_sku_sales: float = 10.0) -> int:
    """Calculate number of orders for a given date with advanced realism: event spikes, trend drift, heteroskedastic noise, and improved outlier smoothing."""
    if us_holiday_dates is None:
        us_holiday_dates = set()
    # --- Trend Drift ---
    drift = sku_trend * (date - (date.replace(month=1, day=1))).days
    # --- Base multipliers ---
    monthly_multiplier = (1 + AVERAGE_MONTHLY_GROWTH * random.uniform(0.92, 1.08)) ** month_index
    weekend_multiplier = 1.18 if date.weekday() >= 5 else 1.0
    seasonal_multiplier = calculate_seasonal_factor(date)
    weekday = date.weekday()
    weekly_pattern = {
        0: 1.0,   # Monday
        1: 1.02,  # Tuesday
        2: 0.98,  # Wednesday
        3: 1.0,   # Thursday
        4: 1.05,  # Friday
        5: 1.18,  # Saturday
        6: 1.12,  # Sunday
    }
    weekly_multiplier = weekly_pattern.get(weekday, 1.0)
    day_of_month = date.day
    if day_of_month <= 10:
        monthly_progression = 0.98
    elif day_of_month <= 20:
        monthly_progression = 1.0
    else:
        monthly_progression = 1.02
    # --- Event/Promotion Spikes ---
    event_multiplier = 1.0
    # 3-day window around major holidays
    for offset in [-1, 0, 1]:
        event_date = date + timedelta(days=offset)
        if event_date in us_holiday_dates:
            if event_date.month == 12 and event_date.day in [24, 25]:
                event_multiplier = max(event_multiplier, random.uniform(1.2, 1.5))
            elif event_date.month == 11 and event_date.day in [24, 25, 26]:
                event_multiplier = max(event_multiplier, random.uniform(1.15, 1.3))
            elif event_date.month == 10 and event_date.day == 31:
                event_multiplier = max(event_multiplier, random.uniform(1.1, 1.2))
    # --- Heteroskedastic Noise ---
    base_orders = (BASE_DAILY_ORDERS * monthly_multiplier * weekend_multiplier * 
                   seasonal_multiplier * weekly_multiplier * monthly_progression * event_multiplier)
    base_orders += drift
    # Mild autocorrelation
    if prev_orders is not None:
        base_orders = 0.5 * base_orders + 0.5 * prev_orders
    
    # Apply configurable Gaussian noise for realistic demand fluctuation
    # Noise factor controls the intensity of random fluctuation (0.1 = ±10%)
    noise = random.gauss(0, RANDOM_NOISE_FACTOR * max(base_orders, 1))
    
    # Clamp to reasonable range
    orders = int(max(5, min(40, base_orders + noise)))
    return orders

# Global tracking for quantity patterns per SKU
sku_quantity_history = {}

def generate_varied_quantity(product: Dict, date: datetime, sku_history: List[int] = None) -> int:
    """Generate realistic quantity with heteroskedastic noise and weekday/weekend bias for zeros."""
    if not ENABLE_QUANTITY_VARIETY:
        return random.randint(1, 3)
    popularity = product.get("popularity", 0.5)
    if popularity >= 0.85:
        pattern = QUANTITY_PATTERNS['high_demand']
    elif popularity >= 0.70:
        pattern = QUANTITY_PATTERNS['medium_demand']
    elif popularity >= 0.55:
        pattern = QUANTITY_PATTERNS['low_demand']
    else:
        pattern = QUANTITY_PATTERNS['variable']
    is_weekend = date.weekday() >= 5
    seasonal_boost = calculate_seasonal_factor(date)
    # --- Weekday/Weekend zero bias ---
    if is_weekend and random.random() < 0.15:
        return 0
    if not is_weekend and random.random() < 0.03:
        return 0
    base_qty = random.choices(pattern['values'], weights=pattern['weights'])[0]
    
    # Apply configurable noise to quantity generation
    # Use RANDOM_NOISE_FACTOR for consistent noise across all calculations
    mean_qty = sum(pattern['values']) / len(pattern['values'])
    noisy_qty = int(round(base_qty + random.gauss(0, RANDOM_NOISE_FACTOR * max(mean_qty, 1))))
    final_qty = max(MIN_QUANTITY, min(MAX_QUANTITY, noisy_qty))
    return max(1, final_qty)

def get_demand_pattern(popularity: float, date: datetime) -> str:
    """Determine demand pattern based on popularity and date."""
    seasonal = calculate_seasonal_factor(date)
    is_weekend = date.weekday() >= 5
    
    # Adjust popularity based on context
    adjusted_popularity = popularity * seasonal
    if is_weekend:
        adjusted_popularity *= 1.2
    
    if adjusted_popularity >= 0.9:
        return 'high_demand'
    elif adjusted_popularity >= 0.7:
        return 'medium_demand'
    elif adjusted_popularity >= 0.5:
        return 'low_demand'
    else:
        return 'variable'

def add_realistic_noise(base_value: int, noise_factor: float = None) -> int:
    """Add realistic noise to quantity values using configurable noise factor."""
    if noise_factor is None:
        noise_factor = RANDOM_NOISE_FACTOR
    
    noise = random.uniform(-noise_factor, noise_factor)
    noisy_value = int(base_value * (1 + noise))
    return max(1, min(MAX_QUANTITY, noisy_value))

def get_season_from_date(date: datetime) -> str:
    """Determine season from date for seasonal discount codes."""
    month = date.month
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    else:
        return "fall"

def generate_discount_code(date: datetime, discount_ratio: float, is_holiday: bool = False) -> str:
    """Generate realistic discount codes based on season, holidays, and discount amount."""
    if discount_ratio == 0.0:
        return ""
    
    # Get season and date context
    season = get_season_from_date(date)
    month = date.month
    is_weekend = date.weekday() >= 5
    
    # Define discount code patterns based on different contexts
    seasonal_codes = {
        "winter": ["WINTER", "HOLIDAY", "COZY", "WARMUP", "SNOW"],
        "spring": ["SPRING", "BLOOM", "FRESH", "EASTER", "RENEW"],
        "summer": ["SUMMER", "SUN", "BEACH", "VACATION", "HOT"],
        "fall": ["FALL", "AUTUMN", "HARVEST", "SCHOOL", "LEAF"]
    }
    
    holiday_codes = {
        1: ["NEWYEAR", "FRESH", "RESOLUTION"],
        2: ["VALENTINE", "LOVE", "HEARTS"],
        3: ["SPRING", "EASTER", "BLOOM"],
        4: ["EASTER", "SPRING", "BUNNY"],
        5: ["MOTHER", "MOM", "SPRING"],
        6: ["FATHER", "DAD", "SUMMER"],
        7: ["SUMMER", "JULY4", "FREEDOM"],
        8: ["SUMMER", "VACATION", "HOT"],
        9: ["BACK2SCHOOL", "AUTUMN", "LEARN"],
        10: ["HALLOWEEN", "SPOOKY", "FALL"],
        11: ["THANKSGIVING", "TURKEY", "GRATEFUL"],
        12: ["HOLIDAY", "XMAS", "WINTER"]
    }
    
    weekend_codes = ["WEEKEND", "RELAX", "FUNDAY", "CHILL"]
    
    # Discount amount-based prefixes
    if discount_ratio >= 0.40:
        amount_codes = ["MEGA", "SUPER", "HUGE", "BIG", "FLASH"]
    elif discount_ratio >= 0.25:
        amount_codes = ["GREAT", "AWESOME", "SPECIAL", "PRIME"]
    elif discount_ratio >= 0.15:
        amount_codes = ["SAVE", "DEAL", "GOOD", "NICE"]
    else:
        amount_codes = ["WELCOME", "TRY", "FIRST", "SMALL"]
    
    # Choose base code
    if is_holiday and month in holiday_codes:
        base_code = random.choice(holiday_codes[month])
    elif is_weekend and random.random() < 0.3:
        base_code = random.choice(weekend_codes)
    else:
        base_code = random.choice(seasonal_codes[season])
    
    # Add amount prefix 30% of the time
    if random.random() < 0.3:
        prefix = random.choice(amount_codes)
        code = f"{prefix}{base_code}"
    else:
        code = base_code
    
    # Add discount percentage as suffix
    discount_pct = int(discount_ratio * 100)
    
    # Add number suffix (percentage or random)
    if random.random() < 0.7:  # 70% chance to include actual percentage
        code += str(discount_pct)
    else:  # 30% chance for creative numbering
        if discount_ratio >= 0.40:
            code += random.choice(["50", "40", "MAX"])
        elif discount_ratio >= 0.25:
            code += random.choice(["25", "30", "PLUS"])
        else:
            code += random.choice(["15", "20", "NOW"])
    
    return code

def generate_discount_ratio(date: datetime, subtotal: float, total_quantity: int, is_holiday: bool = False) -> float:
    """Generate realistic discount ratio for Prophet training data."""
    if not ENABLE_DISCOUNTS or subtotal == 0:
        return 0.0
    
    # Base distribution with contextual adjustments
    base_ratios = list(DISCOUNT_RATIO_PROBABILITIES.keys())
    base_weights = list(DISCOUNT_RATIO_PROBABILITIES.values())
    
    # Adjust weights based on context
    adjusted_weights = base_weights.copy()
    
    # Increase probability of discounts on weekends
    if date.weekday() >= 5:  # Weekend
        # Shift probability from 0.0 to higher discount ratios
        for i in range(len(adjusted_weights)):
            if base_ratios[i] == 0.0:
                adjusted_weights[i] *= 0.8  # Reduce no-discount probability
            elif base_ratios[i] > 0.0:
                adjusted_weights[i] *= 1.3  # Increase discount probability
    
    # Increase probability of discounts on holidays
    if is_holiday:
        for i in range(len(adjusted_weights)):
            if base_ratios[i] == 0.0:
                adjusted_weights[i] *= 0.6  # Reduce no-discount probability more
            elif base_ratios[i] >= 0.20:
                adjusted_weights[i] *= 2.0  # Double higher discount probabilities
    
    # Bulk orders get more discounts
    if total_quantity >= 4:
        for i in range(len(adjusted_weights)):
            if base_ratios[i] == 0.0:
                adjusted_weights[i] *= 0.7
            elif base_ratios[i] >= 0.15:
                adjusted_weights[i] *= 1.5
    
    # Normalize weights
    total_weight = sum(adjusted_weights)
    normalized_weights = [w / total_weight for w in adjusted_weights]
    
    # Select discount ratio
    selected_ratio = random.choices(base_ratios, weights=normalized_weights, k=1)[0]
    
    # Round to 4 decimal places as specified
    return round(selected_ratio, 4)

def generate_realistic_discount(date: datetime, subtotal: float, total_quantity: int, is_holiday: bool = False) -> tuple:
    """Generate realistic discount ratio and amount for Prophet training data."""
    discount_ratio = generate_discount_ratio(date, subtotal, total_quantity, is_holiday)
    
    if discount_ratio == 0.0:
        return 0.0, 0.0
    
    # Calculate discount amount
    discount_amount = discount_ratio * subtotal
    
    return round(discount_ratio, 4), round(discount_amount, 2)

def generate_customer_info() -> Dict:
    """Generate random customer information with random country selection."""
    use_customer = random.choice([True, False])  # 50% chance of having customer info
    
    if use_customer:
        customer = random.choice(CUSTOMERS)
        # Randomly select a country from supported countries
        selected_country = random.choice(SUPPORTED_COUNTRIES)
        # Choose a random address from the selected country
        address = random.choice(ADDRESSES[selected_country])
        
        return {
            "name": customer["name"],
            "email": customer["email"],
            "phone": customer["phone"],
            "address": address
        }
    else:
        # Even for empty customer info, we need to assign a country for the order
        selected_country = random.choice(SUPPORTED_COUNTRIES)
        address = random.choice(ADDRESSES[selected_country])
        
        return {
            "name": "",
            "email": "",
            "phone": "",
            "address": address  # Still include address with country info
        }

def calculate_trend_multiplier(product: Dict, date: datetime, start_date: datetime) -> float:
    """Calculate trending multiplier based on product trend and time progression."""
    trend = product.get("trend", "stable")
    days_elapsed = (date - start_date).days
    total_days = NUMBER_OF_MONTHS * 30
    progress = days_elapsed / total_days  # 0.0 to 1.0
    
    if trend == "growing":
        # Stronger growth signals for Prophet to detect
        # S-curve growth: slow start, rapid middle, plateau
        growth_factor = 1 / (1 + math.exp(-10 * (progress - 0.5)))
        return 0.6 + (0.8 * growth_factor)  # 0.6 to 1.4
    elif trend == "declining":
        # Clear declining pattern
        decline_factor = math.exp(-2 * progress)
        return 0.5 + (0.8 * decline_factor)  # 1.3 declining to 0.5
    elif trend == "volatile":
        # Multiple clear cycles for Prophet to learn
        base_volatility = 0.9 + (0.2 * random.random())  # 0.9 to 1.1
        # Create 3 clear cycles over the time period
        cycle_factor = math.sin(progress * 6 * math.pi) * 0.3
        seasonal_correlation = math.sin(progress * 12 * math.pi) * 0.1
        return max(0.4, min(1.6, base_volatility + cycle_factor + seasonal_correlation))
    else:  # stable
        # Very stable with minimal variation for contrast
        return 0.98 + (0.04 * random.random())  # 0.98 to 1.02

def calculate_product_popularity_at_date(product: Dict, date: datetime, start_date: datetime) -> float:
    """Calculate effective popularity considering trends and date."""
    base_popularity = product.get("popularity", 0.5)
    trend_multiplier = calculate_trend_multiplier(product, date, start_date)
    seasonal_multiplier = calculate_seasonal_factor(date)
    
    # Combine all factors
    effective_popularity = base_popularity * trend_multiplier * seasonal_multiplier
    
    # Ensure within reasonable bounds
    return max(0.1, min(1.0, effective_popularity))

def generate_order_data(date: datetime, order_id: int, start_date: datetime = None, us_holiday_dates=None) -> List[Dict]:
    """Generate order data with line items and holiday/stockout flags."""
    if start_date is None:
        start_date = date
    if us_holiday_dates is None:
        us_holiday_dates = set()
    
    # Determine number of line items (1-4 items per order)
    num_items = random.choices([1, 2, 3, 4], weights=[60, 25, 10, 5])[0]
    
    # Select products using time-adjusted popularity weights for Prophet compatibility
    if SKU_POPULARITY_WEIGHTS and ENSURE_SKU_DISTRIBUTION:
        # Calculate time-adjusted popularity for all products
        products_with_adjusted_popularity = []
        for product in TOY_PRODUCTS:
            adjusted_popularity = calculate_product_popularity_at_date(product, date, start_date)
            products_with_adjusted_popularity.append({
                **product,
                'adjusted_popularity': adjusted_popularity
            })
        
        # Use weighted selection based on adjusted popularity scores
        products = products_with_adjusted_popularity.copy()
        weights = [product["adjusted_popularity"] for product in products]
        selected_products = []
        
        for _ in range(num_items):
            if not products:
                break
            
            try:
                selected_product = random.choices(products, weights=weights)[0]
                selected_products.append(selected_product)
                
                # Remove selected product to avoid duplicates in same order
                idx = products.index(selected_product)
                products.pop(idx)
                weights.pop(idx)
            except (ValueError, IndexError):
                # Fallback to random selection
                if products:
                    selected_products.append(random.choice(products))
                break
    else:
        # Simple random selection without popularity weighting
        selected_products = random.choices(TOY_PRODUCTS, k=min(num_items, len(TOY_PRODUCTS)))
    
    line_items = []
    for product in selected_products:
        # Generate quantity for this line item
        quantity = random.choices(
            [1, 2, 3, 4, 5], 
            weights=[50, 25, 15, 7, 3]
        )[0]
        
        # Calculate base subtotal
        item_price = product['price']
        subtotal = item_price * quantity
        
        # Generate customer info
        customer = generate_customer_info()
        
        # Calculate discount
        is_holiday = date in us_holiday_dates
        discount_ratio, discount_amount = generate_realistic_discount(date, subtotal, quantity, is_holiday)
        
        # Generate discount code if there's a discount
        discount_code = generate_discount_code(date, discount_ratio, discount_amount) if discount_amount > 0 else ""
        
        # Apply discount
        discounted_subtotal = subtotal - discount_amount
        
        # Calculate shipping and taxes
        shipping_cost = 0.0 if discounted_subtotal > 50 else 5.99
        taxes = discounted_subtotal * 0.08
        total = discounted_subtotal + shipping_cost + taxes
        
        # Create timestamp
        created_at = date + timedelta(
            hours=random.randint(8, 22),
            minutes=random.randint(0, 59)
        )
        
        line_item = {
            "Name": f"#{order_id}",
            "Email": customer["email"],
            "Financial Status": "paid",
            "Paid at": created_at.strftime("%Y-%m-%d %H:%M:%S -0400"),
            "Fulfillment Status": "fulfilled",
            "Fulfilled at": (created_at + timedelta(hours=random.randint(1, 24))).strftime("%Y-%m-%d %H:%M:%S -0400"),
            "Accepts Marketing": random.choice(["yes", "no"]),
            "Currency": "USD",
            "Subtotal": f"{subtotal:.2f}",
            "Shipping": f"{shipping_cost:.2f}",
            "Taxes": f"{taxes:.2f}",
            "Total": f"{total:.2f}",
            "Discount Code": discount_code,
            "Discount Amount": f"{discount_amount:.2f}",
            "discount_ratio": f"{discount_ratio:.4f}",
            "Shipping Method": random.choice(["Standard", "Express"]),
            "Created at": created_at.strftime("%Y-%m-%d %H:%M:%S -0400"),
            "Lineitem quantity": str(quantity),
            "Lineitem name": product["name"],
            "Lineitem price": f"{item_price:.2f}",
            "Lineitem compare at price": "",
            "Lineitem sku": product["sku"],
            "Lineitem requires shipping": "TRUE",
            "Lineitem taxable": "TRUE",
            "Lineitem fulfillment status": "fulfilled",
            "Billing Name": customer["name"],
            "Billing Street": customer["address"]["street"],
            "Billing Address1": customer["address"]["street"],
            "Billing Address2": "",
            "Billing Company": "",
            "Billing City": customer["address"]["city"],
            "Billing Zip": customer["address"]["zip"],
            "Billing Province": customer["address"]["province"],
            "Billing Country": customer["address"]["country"],
            "Billing Phone": customer["phone"],
            "Shipping Name": customer["name"],
            "Shipping Street": customer["address"]["street"],
            "Shipping Address1": customer["address"]["street"],
            "Shipping Address2": "",
            "Shipping Company": "",
            "Shipping City": customer["address"]["city"],
            "Shipping Zip": customer["address"]["zip"],
            "Shipping Province": customer["address"]["province"],
            "Shipping Country": customer["address"]["country"],
            "Shipping Phone": customer["phone"],
            "Notes": "",
            "Note Attributes": "",
            "Cancelled at": "",
            "Payment Method": "Credit Card",
            "Payment Reference": generate_random_id(),
            "Refunded Amount": "",
            "Vendor": product["vendor"],
            "Outstanding Balance": "",
            "Employee": "",
            "Location": "",
            "Device ID": "",
            "Id": "",
            "Tags": "",
            "Risk Level": "",
            "Source": "",
            "Lineitem discount": "0.00",
            "Tax 1 Name": "",
            "Tax 1 Value": "",
            "Tax 2 Name": "",
            "Tax 2 Value": "",
            "Tax 3 Name": "",
            "Tax 3 Value": "",
            "Tax 4 Name": "",
            "Tax 4 Value": "",
            "Tax 5 Name": "",
            "Tax 5 Value": "",
            "Phone": customer["phone"],
            "Receipt Number": "",
            "Duties": "",
            "Billing Province Name": "",
            "Shipping Province Name": "",
            "Payment ID": "",
            "Payment Terms Name": "",
            "Next Payment Due At": "",
            "Payment References": "",
            "is_weekend": str(date.weekday() >= 5),
            "is_holiday": str(is_holiday),
            "stockout": "False",
            "Lineitem grams": "500",
            "Lineitem variant id": "",
            "Processed at": created_at.strftime("%Y-%m-%d %H:%M:%S -0400"),
            "Customer": customer["name"],
            "Lineitem variant": "",
            "Updated at": created_at.strftime("%Y-%m-%d %H:%M:%S -0400"),
            "Lineitem product id": "",
        }
        
        line_items.append(line_item)
    
    return line_items

def ensure_minimum_sku_distribution(all_orders: List[Dict], start_date: datetime, end_date: datetime) -> List[Dict]:
    """Ensure all SKUs meet minimum requirements for Prophet model compatibility."""
    if not ENSURE_SKU_DISTRIBUTION:
        return all_orders
    
    print("🔍 Analyzing SKU distribution for Prophet compatibility...")
    
    # Count sales per SKU
    sku_sales = {}
    sku_dates = {}
    
    for order in all_orders:
        sku = order.get("Lineitem sku", "")
        date_str = order.get("Created at", "")
        quantity = int(order.get("Lineitem quantity", 1))
        
        if sku and date_str:
            date = datetime.strptime(date_str.split()[0], "%Y-%m-%d")
            
            if sku not in sku_sales:
                sku_sales[sku] = 0
                sku_dates[sku] = set()
            
            sku_sales[sku] += quantity
            sku_dates[sku].add(date.strftime("%Y-%m-%d"))
    
    # Find SKUs that need more sales
    skus_needing_boost = []
    
    for product in TOY_PRODUCTS:
        sku = product["sku"]
        total_units = sku_sales.get(sku, 0)
        unique_days = len(sku_dates.get(sku, set()))
        
        if total_units < MIN_TOTAL_UNITS_PER_SKU or unique_days < MIN_SALES_DAYS_PER_SKU:
            needed_units = max(0, MIN_TOTAL_UNITS_PER_SKU - total_units)
            needed_days = max(0, MIN_SALES_DAYS_PER_SKU - unique_days)
            skus_needing_boost.append({
                "product": product,
                "needed_units": needed_units,
                "needed_days": needed_days,
                "current_units": total_units,
                "current_days": unique_days
            })
    
    if skus_needing_boost:
        print(f"📈 Boosting {len(skus_needing_boost)} SKUs to meet Prophet requirements...")
        
        # Generate additional orders for under-performing SKUs
        additional_orders = []
        next_order_id = max(int(order.get("Name", "#0").replace("#", "")) for order in all_orders if order.get("Name", "").startswith("#")) + 1
        
        for sku_info in skus_needing_boost:
            product = sku_info["product"]
            needed_units = sku_info["needed_units"]
            needed_days = sku_info["needed_days"]
            
            # Generate sales across random dates to meet minimum day requirement
            total_days = (end_date - start_date).days
            date_range = [start_date + timedelta(days=i) for i in range(total_days)]
            selected_dates = random.sample(date_range, min(needed_days, len(date_range)))
            
            units_per_date = max(1, needed_units // max(1, len(selected_dates)))
            
            for date in selected_dates:
                # Create a focused order with just this SKU
                quantity = min(3, units_per_date + random.randint(0, 2))
                customer = generate_customer_info()
                
                created_at = date + timedelta(
                    hours=random.randint(8, 22),
                    minutes=random.randint(0, 59)
                )
                
                # Calculate discount for this additional order
                subtotal = product['price'] * quantity
                is_holiday = date in get_us_holidays(start_date, end_date) if start_date and end_date else False
                discount_ratio, discount_amount = generate_realistic_discount(date, subtotal, quantity, is_holiday)
                
                # Generate discount code if there's a discount
                discount_code = generate_discount_code(date, discount_ratio, discount_amount) if discount_amount > 0 else ""
                
                # Apply discount
                discounted_subtotal = subtotal - discount_amount
                shipping_cost = 0.0 if discounted_subtotal > 50 else 5.99
                taxes = discounted_subtotal * 0.08
                total = discounted_subtotal + shipping_cost + taxes
                
                # Single line item order focused on the needed SKU
                line_item = {
                    "Name": f"#{next_order_id}",
                    "Email": customer["email"],
                    "Financial Status": "paid",
                    "Paid at": created_at.strftime("%Y-%m-%d %H:%M:%S -0400"),
                    "Fulfillment Status": "fulfilled", 
                    "Fulfilled at": (created_at + timedelta(hours=random.randint(1, 24))).strftime("%Y-%m-%d %H:%M:%S -0400"),
                    "Accepts Marketing": random.choice(["yes", "no"]),
                    "Currency": "USD",
                    "Subtotal": f"{subtotal:.2f}",
                    "Shipping": f"{shipping_cost:.2f}",
                    "Taxes": f"{taxes:.2f}",
                    "Total": f"{total:.2f}",
                    "Discount Code": discount_code,  # Use generated discount code
                    "Discount Amount": f"{discount_amount:.2f}",
                    "discount_ratio": f"{discount_ratio:.4f}",  # New field for Prophet
                    "Shipping Method": "Standard",
                    "Created at": created_at.strftime("%Y-%m-%d %H:%M:%S -0400"),
                    "Updated at": created_at.strftime("%Y-%m-%d %H:%M:%S -0400"),
                    "Processed at": created_at.strftime("%Y-%m-%d %H:%M:%S -0400"),
                    "Customer": customer["name"],
                    "Shipping Name": customer["name"],
                    "Billing Name": customer["name"],
                    "Shipping Street": customer["address"]["street"],
                    "Shipping City": customer["address"]["city"],
                    "Shipping Zip": customer["address"]["zip"],
                    "Shipping Province": customer["address"]["province"],
                    "Shipping Country": customer["address"]["country"],
                    "Billing Street": customer["address"]["street"],
                    "Billing City": customer["address"]["city"], 
                    "Billing Zip": customer["address"]["zip"],
                    "Billing Province": customer["address"]["province"],
                    "Billing Country": customer["address"]["country"],
                    "Notes": "",
                    "Note Attributes": "",
                    "Cancelled at": "",
                    "Payment Method": "Credit Card",
                    "Payment Reference": generate_random_id(),
                    "Refunded Amount": "",
                    "Vendor": product["vendor"],
                    "Outstanding Balance": "",
                    "Employee": "",
                    "Location": "",
                    "Device ID": "",
                    "Id": "",
                    "Tags": "",
                    "Risk Level": "",
                    "Source": "",
                    "Lineitem discount": "0.00",
                    "Tax 1 Name": "",
                    "Tax 1 Value": "",
                    "Tax 2 Name": "",
                    "Tax 2 Value": "",
                    "Tax 3 Name": "",
                    "Tax 3 Value": "",
                    "Tax 4 Name": "",
                    "Tax 4 Value": "",
                    "Tax 5 Name": "",
                    "Tax 5 Value": "",
                    "Phone": customer["phone"],
                    "Receipt Number": "",
                    "Duties": "",
                    "Billing Province Name": "",
                    "Shipping Province Name": "",
                    "Payment ID": "",
                    "Payment Terms Name": "",
                    "Next Payment Due At": "",
                    "Payment References": "",
                    "Lineitem variant id": "",
                    "Lineitem product id": "",
                    "Lineitem name": product["name"],
                    "Lineitem variant": "",
                    "Lineitem sku": product["sku"],
                    "Lineitem requires shipping": "TRUE",
                    "Lineitem taxable": "TRUE",
                    "Lineitem fulfillment status": "fulfilled",
                    "Lineitem price": f"{product['price']:.2f}",
                    "Lineitem compare at price": "",
                    "Lineitem quantity": str(quantity),
                    "Lineitem grams": "500"
                }
                
                additional_orders.append(line_item)
                next_order_id += 1
                
                needed_units -= quantity
                if needed_units <= 0:
                    break
        
        print(f"➕ Added {len(additional_orders)} additional orders for SKU distribution")
        all_orders.extend(additional_orders)
    
    return all_orders

def generate_synthetic_data():
    """Generate the complete synthetic dataset with advanced realism: event spikes, trend drift, heteroskedastic noise, and improved smoothing."""
    print("🚀 Starting synthetic toy sales data generation...")
    print(f"📊 Configuration:")
    print(f"   - Number of SKUs (from config): {NUMBER_OF_SKUS}")
    print(f"   - Months to generate: {NUMBER_OF_MONTHS}")
    print(f"   - Average monthly growth: {AVERAGE_MONTHLY_GROWTH*100:.1f}%")
    print(f"   - Weekend boost factor: {WEEKEND_BOOST_FACTOR}x")
    print(f"   - Base daily orders: {BASE_DAILY_ORDERS}")
    print(f"   - Total toy products generated: {len(TOY_PRODUCTS)}")
    end_date = datetime.now() - timedelta(days=1)
    start_date = end_date - timedelta(days=30 * NUMBER_OF_MONTHS)
    print(f"📅 Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"📊 Generating data for {(end_date - start_date).days} days")
    all_orders = []
    total_orders_generated = 0
    us_holiday_dates = get_us_holidays(start_date, end_date)
    current_date = start_date
    month_index = 0
    last_month = start_date.month
    prev_orders = None
    # Assign a random trend to each SKU for drift
    sku_trends = {p['sku']: random.uniform(-0.02, 0.04) for p in TOY_PRODUCTS}
    sku_means = {p['sku']: p.get('popularity', 0.5) * 15 + 5 for p in TOY_PRODUCTS}
    while current_date <= end_date:
        if random.random() < 0.02:
            current_date += timedelta(days=1)
            prev_orders = None
            continue
        if current_date.month != last_month:
            month_index += 1
            last_month = current_date.month
        rep_product = random.choice(TOY_PRODUCTS)
        rep_sku = rep_product["sku"]
        trend = sku_trends[rep_sku]
        mean_sales = sku_means[rep_sku]
        daily_orders = calculate_daily_orders(current_date, month_index, us_holiday_dates, prev_orders, rep_sku, trend, mean_sales)
        if random.random() < 0.02:
            daily_orders = 0
        prev_orders = daily_orders
        for _ in range(daily_orders):
            order_id = generate_order_id()
            order_line_items = generate_order_data(current_date, order_id, start_date, us_holiday_dates)
            if random.random() < 0.01 and order_line_items:
                order_line_items[0]["Financial Status"] = "refunded"
                order_line_items[0]["Total"] = "0.00"
            all_orders.extend(order_line_items)
            total_orders_generated += 1
        if current_date.day == 1:
            print(f"📅 Processing {current_date.strftime('%B %Y')} - Orders so far: {total_orders_generated}")
        current_date += timedelta(days=1)
    all_orders = ensure_minimum_sku_distribution(all_orders, start_date, end_date)
    output_filename = f"toy_sales_synthetic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    if all_orders:
        # Define the specific column order as requested
        fieldnames = [
            "Name", "Email", "Financial Status", "Paid at", "Fulfillment Status", "Fulfilled at",
            "Accepts Marketing", "Currency", "Subtotal", "Shipping", "Taxes", "Total", "Discount Code",
            "Discount Amount", "discount_ratio", "Shipping Method", "Created at", "Lineitem quantity", "Lineitem name",
            "Lineitem price", "Lineitem compare at price", "Lineitem sku", "Lineitem requires shipping",
            "Lineitem taxable", "Lineitem fulfillment status", "Billing Name", "Billing Street",
            "Billing Address1", "Billing Address2", "Billing Company", "Billing City", "Billing Zip",
            "Billing Province", "Billing Country", "Billing Phone", "Shipping Name", "Shipping Street",
            "Shipping Address1", "Shipping Address2", "Shipping Company", "Shipping City", "Shipping Zip",
            "Shipping Province", "Shipping Country", "Shipping Phone", "Notes", "Note Attributes",
            "Cancelled at", "Payment Method", "Payment Reference", "Refunded Amount", "Vendor",
            "Outstanding Balance", "Employee", "Location", "Device ID", "Id", "Tags", "Risk Level",
            "Source", "Lineitem discount", "Tax 1 Name", "Tax 1 Value", "Tax 2 Name", "Tax 2 Value",
            "Tax 3 Name", "Tax 3 Value", "Tax 4 Name", "Tax 4 Value", "Tax 5 Name", "Tax 5 Value",
            "Phone", "Receipt Number", "Duties", "Billing Province Name", "Shipping Province Name",
            "Payment ID", "Payment Terms Name", "Next Payment Due At", "Payment References", 
            "is_weekend", "is_holiday", "stockout", "Lineitem grams", "Lineitem variant id", 
            "Processed at", "Customer", "Lineitem variant", "Updated at", "Lineitem product id"
        ]

        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_orders)
    print(f"✅ Data generation complete!")
    print(f"📁 Output file: {output_filename}")
    print(f"🎯 Total orders generated: {total_orders_generated}")
    print(f"📋 Total line items: {len(all_orders)}")
    print(f"💰 Estimated total revenue: ${sum(float(order['Total']) for order in all_orders if order['Total']):.2f}")

if __name__ == "__main__":
    generate_synthetic_data()
