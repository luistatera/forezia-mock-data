"""
Outlier Handling in Forezia Time Series Data
--------------------------------------------

This example shows how to use the outlier handling functionality in the Forezia forecasting script.

Example usage:

# Basic usage with default parameters (IQR method, replace outliers with interpolated values)
python ds4.py --input ds4.csv --handle-outliers

# Skip outlier handling
python ds4.py --input ds4.csv --no-outlier-handling

# Use Z-score method instead of IQR
python ds4.py --input ds4.csv --outlier-method zscore --outlier-threshold 3.0

# Remove outliers instead of replacing them
python ds4.py --input ds4.csv --outlier-treatment remove

# Use percentile method with custom threshold (1% and 99% percentiles)
python ds4.py --input ds4.csv --outlier-method percentile --outlier-threshold 0.01

For more information about outlier detection methods:

1. IQR (Interquartile Range) Method:
   - Uses the spread between the 25th and 75th percentiles
   - Default threshold is 1.5 (mild outliers)
   - A threshold of 3.0 would detect only extreme outliers
   - Formula: Q1 - threshold*IQR and Q3 + threshold*IQR

2. Z-score Method:
   - Uses the number of standard deviations from the mean
   - Default threshold is 3.0 (3 standard deviations)
   - Assumes normally distributed data
   - Formula: |x - mean| / std > threshold

3. Percentile Method:
   - Simply cuts off values below and above specified percentiles
   - Threshold is the percentile value (e.g., 0.01 for 1st and 99th percentiles)
   - More intuitive for non-technical users

Tips for handling outliers in time series data:

1. First visualize your data to understand what kind of outliers you have:
   - Seasonal spikes (may be legitimate patterns)
   - Isolated extreme values (potential errors)
   - Clusters of outliers (potential regime shifts)

2. For time series forecasting, consider:
   - Using interpolation rather than removal to maintain time series continuity
   - Processing outliers by category to account for different patterns in different product lines
   - Being careful with automatic outlier removal on promotional items (outliers may be legitimate sales spikes)

3. After processing outliers, check the impact on your forecast accuracy:
   - Compare model metrics with and without outlier processing
   - Look for improvements in MAPE, RMSE, and forecast stability
"""

# Simple example of using the remove_outliers function directly
import pandas as pd
import matplotlib.pyplot as plt
from ds4 import load_data, clean_data, remove_outliers

# 1. Load and clean the data
df = load_data('ds4.csv')
df_clean = clean_data(df)

# 2. Identify outliers without removing them (for visualization)
if 'y' in df_clean.columns:
    # Calculate outlier thresholds
    Q1 = df_clean['y'].quantile(0.25)
    Q3 = df_clean['y'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    # Create masks
    outlier_mask = (df_clean['y'] < lower_bound) | (df_clean['y'] > upper_bound)
    outliers = df_clean[outlier_mask]
    
    # Visualize
    plt.figure(figsize=(12, 6))
    plt.scatter(df_clean['ds'], df_clean['y'], alpha=0.5, label='Normal data')
    plt.scatter(outliers['ds'], outliers['y'], color='red', label='Outliers')
    plt.title('Time Series with Outliers Highlighted')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.legend()
    plt.tight_layout()
    plt.show()
    
    print(f"Detected {len(outliers)} outliers out of {len(df_clean)} records ({len(outliers)/len(df_clean)*100:.2f}%)")

# 3. Process outliers with different methods

# a. Using IQR method, replacing outliers with interpolated values
df_interpolated = remove_outliers(
    df_clean,
    column='y',
    method='iqr',
    threshold=1.5,
    category_col='category' if 'category' in df_clean.columns else None,
    remove=False,
    replace_with='interpolate'
)

# b. Using Z-score method, removing outliers
df_removed = remove_outliers(
    df_clean,
    column='y',
    method='zscore',
    threshold=3.0,
    category_col='category' if 'category' in df_clean.columns else None,
    remove=True
)

# c. Using percentile method, replacing with median
df_median = remove_outliers(
    df_clean,
    column='y',
    method='percentile',
    threshold=0.01,  # 1% and 99% percentiles
    category_col='category' if 'category' in df_clean.columns else None,
    remove=False,
    replace_with='median'
)

# 4. Compare the results visually if we have category data
if 'category' in df_clean.columns:
    # Pick a specific category to compare
    categories = df_clean['category'].unique()
    if len(categories) > 0:
        category = categories[0]
        
        # Filter data for this category
        cat_original = df_clean[df_clean['category'] == category]
        cat_interpolated = df_interpolated[df_interpolated['category'] == category]
        cat_removed = df_removed[df_removed['category'] == category]
        cat_median = df_median[df_median['category'] == category]
        
        plt.figure(figsize=(12, 10))
        
        # Original data with outliers
        plt.subplot(4, 1, 1)
        plt.plot(cat_original['ds'], cat_original['y'])
        plt.title(f'Original Data for {category}')
        plt.ylabel('Value')
        
        # Interpolated outliers
        plt.subplot(4, 1, 2)
        plt.plot(cat_interpolated['ds'], cat_interpolated['y'])
        plt.title(f'Interpolated Outliers (IQR method)')
        plt.ylabel('Value')
        
        # Removed outliers
        plt.subplot(4, 1, 3)
        plt.plot(cat_removed['ds'], cat_removed['y'])
        plt.title(f'Removed Outliers (Z-score method)')
        plt.ylabel('Value')
        
        # Median replacement
        plt.subplot(4, 1, 4)
        plt.plot(cat_median['ds'], cat_median['y'])
        plt.title(f'Median Replacement (Percentile method)')
        plt.xlabel('Date')
        plt.ylabel('Value')
        
        plt.tight_layout()
        plt.show()

print("Outlier processing examples completed.")
