"""
S&P 500 Historical Components Utilities

This module provides functions to work with historical S&P 500 component data.
"""

import pandas as pd
import random
import os
from datetime import datetime, timedelta
import yfinance as yf


def validate_tickers(tickers, start_date, end_date=None, verbose=True):
    """
    Validate tickers by attempting to download data from yfinance.
    
    Parameters:
    -----------
    tickers : list
        List of ticker symbols to validate
    start_date : str or datetime
        Start date for validation check
    end_date : str or datetime, optional
        End date for validation check. If None, uses start_date + 7 days
    verbose : bool
        Print progress information
    
    Returns:
    --------
    tuple : (valid_tickers, invalid_tickers)
    """
    if isinstance(start_date, str):
        start_date = pd.to_datetime(start_date)
    
    if end_date is None:
        end_date = start_date + timedelta(days=7)
    elif isinstance(end_date, str):
        end_date = pd.to_datetime(end_date)
    
    valid_tickers = []
    invalid_tickers = []
    
    if verbose:
        print(f"\nValidating {len(tickers)} tickers...")
    
    for i, ticker in enumerate(tickers, 1):
        try:
            # Try to download a small sample of data
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            
            if data.empty:
                invalid_tickers.append(ticker)
                if verbose:
                    print(f"  [{i}/{len(tickers)}] ✗ {ticker} - No data available")
            else:
                valid_tickers.append(ticker)
                if verbose and i % 10 == 0:
                    print(f"  [{i}/{len(tickers)}] Validated...")
        except Exception as e:
            invalid_tickers.append(ticker)
            if verbose:
                print(f"  [{i}/{len(tickers)}] ✗ {ticker} - Error: {str(e)[:50]}")
    
    if verbose:
        print(f"\n✓ Valid tickers: {len(valid_tickers)}/{len(tickers)}")
        if invalid_tickers:
            print(f"✗ Invalid tickers: {', '.join(invalid_tickers)}")
    
    return valid_tickers, invalid_tickers


def get_sp500_tickers_for_date(target_date, num_tickers=10, seed=None, csv_path=None, validate=True):
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
    validate : bool
        If True, validates tickers by attempting to download data (default: True)
    
    Returns:
    --------
    list : Selected ticker symbols (validated if validate=True)
    
    Examples:
    ---------
    >>> # Get 10 random tickers for 2019-01-01 (reproducible and validated)
    >>> tickers = get_sp500_tickers_for_date('2019-01-01', num_tickers=10, seed=42)
    
    >>> # Get 20 random tickers without validation (faster)
    >>> tickers = get_sp500_tickers_for_date('2020-01-01', num_tickers=20, validate=False)
    """
    
    # Determine CSV path
    if csv_path is None:
        # Get the project root directory (two levels up from utils)
        module_dir = os.path.dirname(__file__)  # utils directory
        package_dir = os.path.dirname(module_dir)  # tradingsuite directory
        project_root = os.path.dirname(package_dir)  # TradingSuite directory
        csv_path = os.path.join(project_root, 'data', 'S&P 500 Historical Components & Changes(07-12-2025).csv')
    
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
    
    # If validation is enabled, we need to select more tickers initially
    # to compensate for those that will be filtered out
    if validate:
        # Request more tickers to ensure we get enough valid ones
        initial_num = min(int(num_tickers * 1.5), len(tickers_list))
        
        if initial_num > len(tickers_list):
            print(f"Warning: Requested {num_tickers} tickers but only {len(tickers_list)} available.")
            initial_tickers = tickers_list
        else:
            initial_tickers = random.sample(tickers_list, initial_num)
        
        print(f"\nInitially selected {len(initial_tickers)} tickers for validation...")
        
        # Validate tickers
        valid_tickers, invalid_tickers = validate_tickers(
            initial_tickers, 
            start_date=target_date,
            verbose=True
        )
        
        # If we don't have enough valid tickers, select more
        while len(valid_tickers) < num_tickers and len(valid_tickers) < len(tickers_list):
            remaining = [t for t in tickers_list if t not in initial_tickers]
            if not remaining:
                break
            
            # How many more do we need?
            needed = num_tickers - len(valid_tickers)
            additional = min(needed * 2, len(remaining))  # Get double to be safe
            
            print(f"\nNeed {needed} more tickers, validating {additional} additional...")
            new_batch = random.sample(remaining, additional)
            
            new_valid, new_invalid = validate_tickers(
                new_batch,
                start_date=target_date,
                verbose=True
            )
            
            valid_tickers.extend(new_valid)
            invalid_tickers.extend(new_invalid)
            initial_tickers.extend(new_batch)
        
        # Take only the requested number
        selected_tickers = valid_tickers[:num_tickers]
        
    else:
        # No validation, just random selection
        if num_tickers > len(tickers_list):
            print(f"Warning: Requested {num_tickers} tickers but only {len(tickers_list)} available.")
            selected_tickers = tickers_list
        else:
            selected_tickers = random.sample(tickers_list, num_tickers)
    
    print(f"\n{'='*80}")
    print(f"Final selection: {len(selected_tickers)} tickers")
    print(selected_tickers)
    print(f"{'='*80}")
    
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
        project_root = os.path.dirname(package_dir)
        csv_path = os.path.join(project_root, 'data', 'S&P 500 Historical Components & Changes(07-12-2025).csv')
    
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
