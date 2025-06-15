#!/usr/bin/env python3
"""Realistic SKU-level sales data generator.

This module provides ``generate_mock_sku_sales`` to create realistic
sales patterns for a single SKU. The generated dataframe follows
a structure compatible with time-series forecasting tools such as
Facebook Prophet.

The function supports basic trend, weekly and yearly seasonality,
random noise and optional promotion spikes on specific dates.
"""

from datetime import datetime, timedelta
from typing import List

import numpy as np
import pandas as pd


def generate_mock_sku_sales(
    sku: str,
    start_date: str,
    end_date: str,
    base_sales: float,
    seasonality_strength: float = 0.3,
    trend_slope: float = 0.05,
    noise_std: float = 1.0,
    promotion_days: List[str] | None = None,
    holiday_boost: float = 2.0,
) -> pd.DataFrame:
    """Generate daily sales for a SKU with realistic patterns.

    Parameters
    ----------
    sku : str
        Identifier for the SKU.
    start_date, end_date : str
        Date range in ``YYYY-MM-DD`` format.
    base_sales : float
        Baseline daily sales volume.
    seasonality_strength : float, optional
        Amplitude of seasonal components.
    trend_slope : float, optional
        Linear trend added to ``base_sales`` (per day).
    noise_std : float, optional
        Standard deviation of random noise.
    promotion_days : list[str] | None, optional
        Dates with promotional boosts.
    holiday_boost : float, optional
        Additional sales amount applied on ``promotion_days``.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing ``ds`` (date), ``y`` (sales) and ``sku``.
    """

    date_range = pd.date_range(start=start_date, end=end_date, freq="D")
    num_days = len(date_range)

    # Linear trend
    trend = np.linspace(0, trend_slope * num_days, num_days)

    # Weekly seasonality (higher on weekends)
    weekly = np.sin(2 * np.pi * date_range.dayofweek / 7) * seasonality_strength

    # Yearly-like seasonality
    monthly = (
        np.sin(2 * np.pi * date_range.dayofyear / 365.25) * seasonality_strength
    )

    # Random noise
    noise = np.random.normal(0, noise_std, num_days)

    promo_effect = np.zeros(num_days)
    if promotion_days:
        for promo_day in promotion_days:
            idx = date_range == pd.to_datetime(promo_day)
            promo_effect[idx] = holiday_boost

    sales = base_sales + trend + weekly + monthly + promo_effect + noise
    sales = np.clip(sales, 0, None).round()

    return pd.DataFrame({"ds": date_range, "y": sales.astype(int), "sku": sku})


if __name__ == "__main__":
    # Define 10 toy variations
    toy_skus = [
        {"sku": "TOY-LEGO-001", "name": "Classic LEGO City Set", "base_sales": 5},
        {"sku": "TOY-LEGO-002", "name": "LEGO Star Wars Set", "base_sales": 8},
        {"sku": "TOY-BARBIE-001", "name": "Barbie Dreamhouse", "base_sales": 4},
        {"sku": "TOY-HOTWHEELS-001", "name": "Hot Wheels Track Set", "base_sales": 6},
        {"sku": "TOY-NERF-001", "name": "Nerf Elite Blaster", "base_sales": 7},
        {"sku": "TOY-PUZZLE-001", "name": "1000 Piece Jigsaw Puzzle", "base_sales": 3},
        {"sku": "TOY-MONOPOLY-001", "name": "Monopoly Board Game", "base_sales": 5},
        {"sku": "TOY-PLAYDOH-001", "name": "Play-Doh Creative Set", "base_sales": 4},
        {"sku": "TOY-TRANSFORMER-001", "name": "Transformers Action Figure", "base_sales": 6},
        {"sku": "TOY-POKEMON-001", "name": "Pokemon Trading Card Game", "base_sales": 9}
    ]
    
    # Generate data for all toys and combine into one dataset
    all_data = []
    
    for toy in toy_skus:
        print(f"Generating data for {toy['name']} ({toy['sku']})...")
        df = generate_mock_sku_sales(
            sku=toy['sku'],
            start_date="2023-01-01",
            end_date="2025-06-15",
            base_sales=toy['base_sales'],
            seasonality_strength=2.5,
            trend_slope=0.01,
            noise_std=1.2,
            promotion_days=[
                # 2023 US National Holidays
                "2023-01-01",  # New Year's Day
                "2023-01-16",  # Martin Luther King Jr. Day
                "2023-02-20",  # Presidents' Day
                "2023-05-29",  # Memorial Day
                "2023-06-19",  # Juneteenth
                "2023-07-04",  # Independence Day
                "2023-09-04",  # Labor Day
                "2023-10-09",  # Columbus Day
                "2023-11-11",  # Veterans Day
                "2023-11-23",  # Thanksgiving
                "2023-12-25",  # Christmas Day
                
                # 2024 US National Holidays
                "2024-01-01",  # New Year's Day
                "2024-01-15",  # Martin Luther King Jr. Day
                "2024-02-19",  # Presidents' Day
                "2024-05-27",  # Memorial Day
                "2024-06-19",  # Juneteenth
                "2024-07-04",  # Independence Day
                "2024-09-02",  # Labor Day
                "2024-10-14",  # Columbus Day
                "2024-11-11",  # Veterans Day
                "2024-11-28",  # Thanksgiving
                "2024-12-25",  # Christmas Day
                
                # 2025 US National Holidays (up to current date)
                "2025-01-01",  # New Year's Day
                "2025-01-20",  # Martin Luther King Jr. Day
                "2025-02-17",  # Presidents' Day
                "2025-05-26",  # Memorial Day
            ],
            holiday_boost=10,
        )
        all_data.append(df)
    
    # Combine all toy data into one CSV
    combined_df = pd.concat(all_data, ignore_index=True)
    combined_df.to_csv("mock_toys_all_skus.csv", index=False)
    print(f"✅ mock_toys_all_skus.csv created with {len(toy_skus)} toy variations")
    print(f"📊 Total records: {len(combined_df)}")
    
    # Also create individual CSV files for each toy
    for toy in toy_skus:
        toy_data = combined_df[combined_df['sku'] == toy['sku']]
        filename = f"mock_{toy['sku'].lower().replace('-', '_')}.csv"
        toy_data.to_csv(filename, index=False)
        print(f"✅ {filename} created")
