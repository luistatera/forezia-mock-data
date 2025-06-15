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
    df = generate_mock_sku_sales(
        sku="TOY-LEGO-001",
        start_date="2023-01-01",
        end_date="2025-06-15",
        base_sales=5,
        seasonality_strength=2.5,
        trend_slope=0.01,
        noise_std=1.2,
        promotion_days=["2023-12-25", "2024-11-29", "2025-11-28"],
        holiday_boost=10,
    )
    df.to_csv("mock_toy_lego_001.csv", index=False)
    print("✅ mock_toy_lego_001.csv created")
