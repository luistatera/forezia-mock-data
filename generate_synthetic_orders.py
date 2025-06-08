#!/usr/bin/env python3
"""
Synthetic Orders Data Generator for Toys for Kids
Generates realistic sales data with weekend spikes and monthly growth patterns
"""

import csv
import random
import string
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import math

# Configuration Variables
NUMBER_OF_MONTHS = 12  # Generate data for last 12 months
AVERAGE_MONTHLY_GROWTH = 0.08  # 8% monthly growth rate
WEEKEND_BOOST_FACTOR = 1.8  # Sales increase 80% on weekends
BASE_DAILY_ORDERS = 15  # Base number of orders per day (will grow monthly)
SEASONAL_FACTOR = 0.3  # How much seasonal variation affects sales

# Enhanced Prophet Learning Patterns
ENABLE_STRONG_PATTERNS = True  # Enable stronger patterns for Prophet to learn
AUTOCORRELATION_FACTOR = 0.3  # How much previous days affect current day
CYCLICAL_PATTERNS = True  # Enable cyclical demand patterns
TREND_STRENGTH = 0.4  # How strong trending signals should be

# Prophet Model Compatibility Settings
MIN_SALES_DAYS_PER_SKU = 15  # Minimum days a SKU must be sold to avoid Prophet crashes
MIN_TOTAL_UNITS_PER_SKU = 20  # Minimum total units sold per SKU across all time
ENSURE_SKU_DISTRIBUTION = True  # Ensure all SKUs have adequate sales distribution
SKU_POPULARITY_WEIGHTS = True  # Use realistic popularity weights for SKUs

# Quantity Variety Settings for Better ML Performance
ENABLE_QUANTITY_VARIETY = True  # Enable varied quantity patterns
MIN_QUANTITY = 0  # Minimum quantity (0 = out of stock days)
MAX_QUANTITY = 8  # Maximum quantity per line item
STOCK_OUT_PROBABILITY = 0.05  # 5% chance of stock-out (0 quantity) - reduced for Prophet
BULK_ORDER_PROBABILITY = 0.20  # 20% chance of bulk orders (4+ quantity) - increased variety
LOW_INVENTORY_PROBABILITY = 0.15  # 15% chance of low inventory (1-2 units)
HIGH_DEMAND_SPIKE_PROBABILITY = 0.10  # 10% chance of demand spikes

# Quantity patterns based on product popularity and demand
QUANTITY_PATTERNS = {
    'high_demand': {'weights': [0.03, 0.12, 0.25, 0.30, 0.20, 0.08, 0.02], 'values': [0, 1, 2, 3, 4, 5, 6]},
    'medium_demand': {'weights': [0.05, 0.20, 0.35, 0.25, 0.12, 0.03], 'values': [0, 1, 2, 3, 4, 5]},
    'low_demand': {'weights': [0.15, 0.40, 0.25, 0.15, 0.05], 'values': [0, 1, 2, 3, 4]},
    'variable': {'weights': [0.10, 0.18, 0.22, 0.20, 0.15, 0.10, 0.05], 'values': [0, 1, 2, 3, 4, 5, 6]}
}

# Toy Products Database (50 products) with popularity weights and trend patterns
TOY_PRODUCTS = [
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

# Address database
ADDRESSES = [
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
]

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
    """Calculate seasonal factor with stronger, more obvious patterns."""
    month = date.month
    day_of_year = date.timetuple().tm_yday
    
    # Base seasonal multipliers (more pronounced)
    seasonal_multipliers = {
        1: 1.3,   # January - New Year gifts, post-holiday sales
        2: 0.7,   # February - post-holiday slump
        3: 0.9,   # March - spring preparation
        4: 1.2,   # April - Easter, spring toys
        5: 1.1,   # May - outdoor season starts
        6: 0.8,   # June - summer vacation planning
        7: 1.2,   # July - peak summer, vacation toys
        8: 1.0,   # August - back-to-school prep
        9: 1.1,   # September - back to school
        10: 1.3,  # October - Halloween, holiday prep
        11: 1.6,  # November - Black Friday, holiday shopping
        12: 1.8,  # December - Christmas peak
    }
    
    base_seasonal = seasonal_multipliers.get(month, 1.0)
    
    # Add sinusoidal variation for smoother transitions
    yearly_cycle = 1 + 0.3 * math.sin(2 * math.pi * day_of_year / 365.25 + math.pi/2)
    
    # Combine base seasonal with smooth cycle
    return (base_seasonal + yearly_cycle) / 2

def calculate_daily_orders(date: datetime, month_index: int) -> int:
    """Calculate number of orders for a given date with improved patterns."""
    # Base growth calculation with some volatility
    monthly_multiplier = (1 + AVERAGE_MONTHLY_GROWTH) ** month_index
    
    # Weekend boost
    weekend_multiplier = WEEKEND_BOOST_FACTOR if date.weekday() >= 5 else 1.0
    
    # Seasonal factor
    seasonal_multiplier = calculate_seasonal_factor(date)
    
    # Add weekly patterns (mid-week dip)
    weekday = date.weekday()
    weekly_pattern = {
        0: 1.0,   # Monday
        1: 1.1,   # Tuesday
        2: 0.9,   # Wednesday (mid-week dip)
        3: 1.0,   # Thursday
        4: 1.2,   # Friday (pre-weekend boost)
        5: 1.8,   # Saturday
        6: 1.6,   # Sunday
    }
    weekly_multiplier = weekly_pattern.get(weekday, 1.0)
    
    # Add monthly progression (stronger sales towards month-end)
    day_of_month = date.day
    if day_of_month <= 10:
        monthly_progression = 0.9  # Slower start
    elif day_of_month <= 20:
        monthly_progression = 1.0  # Normal
    else:
        monthly_progression = 1.1  # End of month boost
    
    # Random daily variation with some autocorrelation
    daily_variation = random.uniform(0.8, 1.2)
    
    # Calculate final order count
    orders = (BASE_DAILY_ORDERS * monthly_multiplier * weekend_multiplier * 
              seasonal_multiplier * weekly_multiplier * monthly_progression * daily_variation)
    
    # Add some noise and ensure minimum orders
    noise = random.uniform(-2, 3)
    return max(int(orders + noise), 1)

# Global tracking for quantity patterns per SKU
sku_quantity_history = {}

def generate_varied_quantity(product: Dict, date: datetime, sku_history: List[int] = None) -> int:
    """Generate realistic quantity with variety based on product popularity and patterns."""
    if not ENABLE_QUANTITY_VARIETY:
        return random.randint(1, 3)  # Fallback to original logic
    
    popularity = product.get("popularity", 0.5)
    
    # Select pattern based on product popularity
    if popularity >= 0.85:
        pattern = QUANTITY_PATTERNS['high_demand']
    elif popularity >= 0.70:
        pattern = QUANTITY_PATTERNS['medium_demand']
    elif popularity >= 0.55:
        pattern = QUANTITY_PATTERNS['low_demand']
    else:
        pattern = QUANTITY_PATTERNS['variable']
    
    # Add day-of-week variation
    is_weekend = date.weekday() >= 5
    weekend_boost = 1.3 if is_weekend else 1.0
    
    # Add seasonal variation
    seasonal_boost = calculate_seasonal_factor(date)
    
    # Calculate base quantity using weighted selection
    base_qty = random.choices(pattern['values'], weights=pattern['weights'])[0]
    
    # Apply boosts probabilistically
    if is_weekend and random.random() < 0.4:  # 40% chance of weekend boost
        base_qty += random.randint(1, 2)
    
    if seasonal_boost > 1.1 and random.random() < (seasonal_boost - 1.0):
        base_qty += random.randint(0, 2)
    
    # Avoid too many consecutive same values for variety
    if sku_history and len(sku_history) >= 2:
        recent_values = sku_history[-2:]
        if len(set(recent_values)) == 1 and base_qty == recent_values[-1]:
            # Force variety - choose different value
            available_values = [v for v in pattern['values'] if v != base_qty and v > 0]
            if available_values:
                base_qty = random.choice(available_values)
    
    # Ensure within bounds
    final_qty = max(MIN_QUANTITY, min(MAX_QUANTITY, base_qty))
    
    # Handle stock-outs realistically (but rarely for Prophet compatibility)
    if random.random() < STOCK_OUT_PROBABILITY and popularity < 0.6:
        return 0  # Out of stock
    
    # Bulk order probability for popular items
    if popularity > 0.8 and random.random() < BULK_ORDER_PROBABILITY:
        final_qty += random.randint(2, 4)
    
    # Ensure minimum of 1 for Prophet compatibility (avoid too many zeros)
    return max(1, min(MAX_QUANTITY, final_qty))

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

def add_realistic_noise(base_value: int, noise_factor: float = 0.15) -> int:
    """Add realistic noise to quantity values."""
    noise = random.uniform(-noise_factor, noise_factor)
    noisy_value = int(base_value * (1 + noise))
    return max(1, min(MAX_QUANTITY, noisy_value))

def generate_customer_info() -> Dict:
    """Generate random customer information."""
    use_customer = random.choice([True, False])  # 50% chance of having customer info
    
    if use_customer:
        customer = random.choice(CUSTOMERS)
        address = random.choice(ADDRESSES)
        return {
            "name": customer["name"],
            "email": customer["email"],
            "phone": customer["phone"],
            "address": address
        }
    else:
        return {
            "name": "",
            "email": "",
            "phone": "",
            "address": {"street": "", "city": "", "zip": "", "province": "", "country": ""}
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

def generate_order_data(date: datetime, order_id: int, start_date: datetime = None) -> List[Dict]:
    """Generate order data with line items."""
    # Use start_date for trend calculations (fallback to current date if not provided)
    if start_date is None:
        start_date = date
    
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
            if products:  # Ensure we have products left to choose from
                chosen_product = random.choices(products, weights=weights, k=1)[0]
                selected_products.append(chosen_product)
                # Remove chosen product and its weight to avoid duplicates in same order
                chosen_index = products.index(chosen_product)
                products.pop(chosen_index)
                weights.pop(chosen_index)
    else:
        # Original random selection (fallback)
        selected_products = random.sample(TOY_PRODUCTS, num_items)
    
    # Generate customer info
    customer = generate_customer_info()
    
    # Order-level details
    payment_ref = generate_random_id()
    order_number = f"#{order_id}"
    
    # Calculate order timing
    created_at = date + timedelta(
        hours=random.randint(8, 22),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )
    
    # Payment and fulfillment timing
    paid_at = created_at + timedelta(minutes=random.randint(1, 30))
    fulfilled_at = paid_at + timedelta(hours=random.randint(1, 48))
    
    # Order status
    financial_status = random.choices(
        ["paid", "pending", "refunded"], 
        weights=[85, 12, 3]
    )[0]
    
    fulfillment_status = "fulfilled" if financial_status == "paid" else random.choice(["pending", "partial"])
    
    # First, generate quantities for each product to calculate accurate totals
    product_quantities = []
    for product in selected_products:
        # Get quantity history for this SKU to ensure variety
        sku = product["sku"]
        sku_history = sku_quantity_history.get(sku, [])
        
        # Generate realistic quantity with variety
        quantity = generate_varied_quantity(product, date, sku_history)
        
        # Update quantity history for this SKU
        if sku not in sku_quantity_history:
            sku_quantity_history[sku] = []
        sku_quantity_history[sku].append(quantity)
        
        # Keep only last 10 quantities for pattern tracking
        if len(sku_quantity_history[sku]) > 10:
            sku_quantity_history[sku] = sku_quantity_history[sku][-10:]
        
        product_quantities.append(quantity)
    
    # Calculate totals using actual quantities
    subtotal = sum(product["price"] * qty for product, qty in zip(selected_products, product_quantities))
    shipping = 0.0 if subtotal > 50 else random.choice([5.99, 7.99, 9.99])
    taxes = subtotal * 0.08  # 8% tax
    total = subtotal + shipping + taxes
    
    # Generate line items
    line_items = []
    for i, (product, quantity) in enumerate(zip(selected_products, product_quantities)):
        
        # First line item has full order details
        if i == 0:
            line_item = {
                "Name": order_number,
                "Email": customer["email"],
                "Financial Status": financial_status,
                "Paid at": paid_at.strftime("%Y-%m-%d %H:%M:%S -0400") if financial_status == "paid" else "",
                "Fulfillment Status": fulfillment_status,
                "Fulfilled at": fulfilled_at.strftime("%Y-%m-%d %H:%M:%S -0400") if fulfillment_status == "fulfilled" else "",
                "Accepts Marketing": random.choice(["yes", "no"]),
                "Currency": "USD",
                "Subtotal": f"{subtotal:.2f}",
                "Shipping": f"{shipping:.2f}",
                "Taxes": f"{taxes:.2f}",
                "Total": f"{total:.2f}",
                "Discount Code": "",
                "Discount Amount": "0.00",
                "Shipping Method": random.choice(["Standard", "Express", "Priority"]) if shipping > 0 else "",
                "Created at": created_at.strftime("%Y-%m-%d %H:%M:%S -0400"),
                "Lineitem quantity": str(quantity),
                "Lineitem name": product["name"],
                "Lineitem price": f"{product['price']:.2f}",
                "Lineitem compare at price": "",
                "Lineitem sku": product["sku"],
                "Lineitem requires shipping": "true",
                "Lineitem taxable": "true",
                "Lineitem fulfillment status": fulfillment_status,
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
                "Note Attributes": '""',
                "Cancelled at": "",
                "Payment Method": "manual",
                "Payment Reference": payment_ref,
                "Refunded Amount": "0.00",
                "Vendor": product["vendor"],
                "Outstanding Balance": "0.00",
                "Employee": "Store Manager",
                "Location": "Main Store",
                "Device ID": "",
                "Id": str(random.randint(6000000000000, 7000000000000)),
                "Tags": "",
                "Risk Level": "Low",
                "Source": "shopify_draft_order",
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
                "Billing Province Name": customer["address"]["province"],
                "Shipping Province Name": customer["address"]["province"],
                "Payment ID": payment_ref,
                "Payment Terms Name": "",
                "Next Payment Due At": "",
                "Payment References": payment_ref
            }
        else:
            # Additional line items have minimal data
            line_item = {
                "Name": order_number,
                "Email": customer["email"] if customer["email"] else "",
                "Financial Status": "",
                "Paid at": "",
                "Fulfillment Status": "",
                "Fulfilled at": "",
                "Accepts Marketing": "",
                "Currency": "",
                "Subtotal": "",
                "Shipping": "",
                "Taxes": "",
                "Total": "",
                "Discount Code": "",
                "Discount Amount": "",
                "Shipping Method": "",
                "Created at": created_at.strftime("%Y-%m-%d %H:%M:%S -0400"),
                "Lineitem quantity": str(quantity),
                "Lineitem name": product["name"],
                "Lineitem price": f"{product['price']:.2f}",
                "Lineitem compare at price": "",
                "Lineitem sku": product["sku"],
                "Lineitem requires shipping": "true",
                "Lineitem taxable": "true",
                "Lineitem fulfillment status": fulfillment_status,
                "Billing Name": "",
                "Billing Street": "",
                "Billing Address1": "",
                "Billing Address2": "",
                "Billing Company": "",
                "Billing City": "",
                "Billing Zip": "",
                "Billing Province": "",
                "Billing Country": "",
                "Billing Phone": "",
                "Shipping Name": "",
                "Shipping Street": "",
                "Shipping Address1": "",
                "Shipping Address2": "",
                "Shipping Company": "",
                "Shipping City": "",
                "Shipping Zip": "",
                "Shipping Province": "",
                "Shipping Country": "",
                "Shipping Phone": "",
                "Notes": "",
                "Note Attributes": "",
                "Cancelled at": "",
                "Payment Method": "",
                "Payment Reference": "",
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
                "Phone": customer["phone"] if customer["phone"] else "",
                "Receipt Number": "",
                "Duties": "",
                "Billing Province Name": "",
                "Shipping Province Name": "",
                "Payment ID": "",
                "Payment Terms Name": "",
                "Next Payment Due At": "",
                "Payment References": ""
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
                    "Subtotal": f"{product['price'] * quantity:.2f}",
                    "Shipping": "0.00",
                    "Taxes": f"{product['price'] * quantity * 0.08:.2f}",
                    "Total": f"{product['price'] * quantity * 1.08:.2f}",
                    "Discount Code": "",
                    "Discount Amount": "0.00",
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
    """Generate the complete synthetic dataset."""
    print("🚀 Starting synthetic toy sales data generation...")
    print(f"📊 Configuration:")
    print(f"   - Months to generate: {NUMBER_OF_MONTHS}")
    print(f"   - Average monthly growth: {AVERAGE_MONTHLY_GROWTH*100:.1f}%")
    print(f"   - Weekend boost factor: {WEEKEND_BOOST_FACTOR}x")
    print(f"   - Base daily orders: {BASE_DAILY_ORDERS}")
    print(f"   - Total toy products: {len(TOY_PRODUCTS)}")
    
    # Calculate date range (last 12 months)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30 * NUMBER_OF_MONTHS)
    
    all_orders = []
    total_orders_generated = 0
    
    # Generate data for each day
    current_date = start_date
    month_index = 0
    last_month = start_date.month
    
    while current_date <= end_date:
        # Update month index when month changes
        if current_date.month != last_month:
            month_index += 1
            last_month = current_date.month
        
        # Calculate orders for this day
        daily_orders = calculate_daily_orders(current_date, month_index)
        
        # Generate orders for the day
        for _ in range(daily_orders):
            order_id = generate_order_id()
            order_line_items = generate_order_data(current_date, order_id, start_date)
            all_orders.extend(order_line_items)
            total_orders_generated += 1
        
        # Progress indicator
        if current_date.day == 1:
            print(f"📅 Processing {current_date.strftime('%B %Y')} - Orders so far: {total_orders_generated}")
        
        current_date += timedelta(days=1)
    
    # Ensure minimum SKU distribution
    all_orders = ensure_minimum_sku_distribution(all_orders, start_date, end_date)
    
    # Write to CSV
    output_filename = f"toy_sales_synthetic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    if all_orders:
        fieldnames = all_orders[0].keys()
        
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
