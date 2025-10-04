"""
S&P 500 Historical Components Utilities

This module provides functions to work with historical S&P 500 component data.
"""

import pandas as pd
import random
import os
from datetime import datetime


def get_sp500_tickers_for_date(target_date, num_tickers=10, seed=None, csv_path=None):
    """
    Load S&P 500 historical components and select random tickers for a specific date.
    
    Parameters:
    -----------
    target_date : str or datetime
        Target date in format 'YYYY-MM-DD' or datetime object
    num_tickers : int
        Number of random tickers to select (default: 10)
    seed : int, optional
        Random seed for reproducibility. Use the same seed to get consistent results.
    csv_path : str, optional
        Custom path to the CSV file. If None, uses the default location in tradingsuite/data/
    
    Returns:
    --------
    list : Selected ticker symbols
    
    Examples:
    ---------
    >>> # Get 10 random tickers for 2019-01-01 (reproducible)
    >>> tickers = get_sp500_tickers_for_date('2019-01-01', num_tickers=10, seed=42)
    
    >>> # Get 20 random tickers (different each time)
    >>> tickers = get_sp500_tickers_for_date('2020-01-01', num_tickers=20)
    """
    
    # Determine CSV path
    if csv_path is None:
        # Get the package directory (one level up from utils)
        module_dir = os.path.dirname(__file__)  # utils directory
        package_dir = os.path.dirname(module_dir)  # tradingsuite directory
        csv_path = os.path.join(package_dir, 'data', 'S&P 500 Historical Components & Changes(07-12-2025).csv')
    
    # Check if file exists
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"S&P 500 data file not found at: {csv_path}")
    
    # Read the CSV file
    print(f"Loading S&P 500 historical data from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Convert target_date to datetime if it's a string
    if isinstance(target_date, str):
        target_date = pd.to_datetime(target_date)
    
    print(f"\nTarget date: {target_date.strftime('%Y-%m-%d')}")
    print(f"Available date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
    
    # Find the closest date that is <= target_date
    valid_dates = df[df['date'] <= target_date]
    
    if valid_dates.empty:
        raise ValueError(f"No data available for dates before {target_date.strftime('%Y-%m-%d')}")
    
    # Get the most recent date before or equal to target_date
    closest_date = valid_dates['date'].max()
    print(f"Using data from: {closest_date.strftime('%Y-%m-%d')}")
    
    # Get tickers for that date
    tickers_str = df[df['date'] == closest_date]['tickers'].iloc[0]
    tickers_list = [t.strip() for t in tickers_str.split(',')]
    
    print(f"\nTotal tickers available on {closest_date.strftime('%Y-%m-%d')}: {len(tickers_list)}")
    
    # Set random seed for reproducibility if provided
    if seed is not None:
        random.seed(seed)
    
    # Randomly select tickers
    if num_tickers > len(tickers_list):
        print(f"Warning: Requested {num_tickers} tickers but only {len(tickers_list)} available.")
        selected_tickers = tickers_list
    else:
        selected_tickers = random.sample(tickers_list, num_tickers)
    
    print(f"\nRandomly selected {len(selected_tickers)} tickers:")
    print(selected_tickers)
    
    return selected_tickers


def get_all_sp500_tickers_for_date(target_date, csv_path=None):
    """
    Get all S&P 500 tickers for a specific date (no random selection).
    
    Parameters:
    -----------
    target_date : str or datetime
        Target date in format 'YYYY-MM-DD' or datetime object
    csv_path : str, optional
        Custom path to the CSV file. If None, uses the default location.
    
    Returns:
    --------
    list : All ticker symbols for that date
    
    Examples:
    ---------
    >>> # Get all tickers for 2019-01-01
    >>> all_tickers = get_all_sp500_tickers_for_date('2019-01-01')
    """
    
    # Determine CSV path
    if csv_path is None:
        module_dir = os.path.dirname(__file__)
        package_dir = os.path.dirname(module_dir)
        csv_path = os.path.join(package_dir, 'data', 'S&P 500 Historical Components & Changes(07-12-2025).csv')
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"S&P 500 data file not found at: {csv_path}")
    
    # Read the CSV file
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])
    
    if isinstance(target_date, str):
        target_date = pd.to_datetime(target_date)
    
    # Find the closest date that is <= target_date
    valid_dates = df[df['date'] <= target_date]
    
    if valid_dates.empty:
        raise ValueError(f"No data available for dates before {target_date.strftime('%Y-%m-%d')}")
    
    closest_date = valid_dates['date'].max()
    
    # Get tickers for that date
    tickers_str = df[df['date'] == closest_date]['tickers'].iloc[0]
    tickers_list = [t.strip() for t in tickers_str.split(',')]
    
    print(f"Found {len(tickers_list)} tickers for {closest_date.strftime('%Y-%m-%d')}")
    
    return tickers_list


if __name__ == "__main__":
    # Example usage
    print("="*60)
    print("S&P 500 Ticker Selection Example")
    print("="*60)
    
    # Example 1: Get 10 random tickers for 2019-01-01
    TICKERS = get_sp500_tickers_for_date(
        target_date='2019-01-01',
        num_tickers=10,
        seed=42  # Use seed for reproducibility
    )
    
    print(f"\n{'='*60}")
    print("Selected tickers:")
    print(f"TICKERS = {TICKERS}")
    print(f"{'='*60}")
