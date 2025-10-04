import pandas as pd
import random
from datetime import datetime
import os

def get_sp500_tickers_for_date(csv_path, target_date, num_tickers=10, seed=None):
    """
    Load S&P 500 historical components and select random tickers for a specific date.
    
    Parameters:
    -----------
    csv_path : str
        Path to the CSV file with historical S&P 500 components
    target_date : str or datetime
        Target date in format 'YYYY-MM-DD' or datetime object
    num_tickers : int
        Number of random tickers to select (default: 10)
    seed : int, optional
        Random seed for reproducibility
    
    Returns:
    --------
    list : Selected ticker symbols
    """
    
    # Read the CSV file
    print(f"Loading S&P 500 historical data from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Convert target_date to datetime if it's a string
    if isinstance(target_date, str):
        target_date = pd.to_datetime(target_date)
    
    print(f"\nTarget date: {target_date.strftime('%Y-%m-%d')}")
    print(f"Available date range: {df['date'].min()} to {df['date'].max()}")
    
    # Find the closest date that is <= target_date
    valid_dates = df[df['date'] <= target_date]
    
    if valid_dates.empty:
        raise ValueError(f"No data available for dates before {target_date}")
    
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


# Example usage
if __name__ == "__main__":
    # Path to the CSV file (adjust as needed)
    csv_path = 'data/S&P 500 Historical Components & Changes(07-12-2025).csv'
    
    # Check if file exists
    if not os.path.exists(csv_path):
        print(f"Error: File not found at {csv_path}")
        print("Please adjust the path to your CSV file.")
    else:
        # Select 10 random tickers for 2019-01-01
        TICKERS = get_sp500_tickers_for_date(
            csv_path=csv_path,
            target_date='2019-01-01',
            num_tickers=10,
            seed=42  # Use seed for reproducibility, or None for true randomness
        )
        
        print(f"\n{'='*60}")
        print("Use this instead of the hardcoded TICKERS list:")
        print(f"TICKERS = {TICKERS}")
        print(f"{'='*60}")
