"""
S&P 500 Screener Module

This module provides functionality to download current S&P 500 companies list
and filter them based on various criteria.
"""

import pandas as pd
import cloudscraper
from io import StringIO
from datetime import datetime
import logging
from typing import Optional, List, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import TradingSuite modules
try:
    from ..data.market_data import MarketData
    from ..data.tradingview_data import TradingViewData
except ImportError:
    from tradingsuite.data.market_data import MarketData
    from tradingsuite.data.tradingview_data import TradingViewData


class SP500Loader:
    """
    Loads current S&P 500 companies from Wikipedia.
    """
    
    def __init__(self):
        """Initialize the SP500Loader with cloudscraper."""
        self.scraper = cloudscraper.create_scraper()
        self.sp500_df = None
        self.url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    
    def load(self) -> pd.DataFrame:
        """
        Download current S&P 500 companies list from Wikipedia.
        
        Returns:
        --------
        pd.DataFrame : DataFrame with S&P 500 companies information
        """
        try:
            logger.info(f"Downloading S&P 500 data from Wikipedia...")
            response = self.scraper.get(self.url)
            
            # Parse tables from HTML
            tables = pd.read_html(StringIO(response.text))
            self.sp500_df = tables[0]
            
            # Convert 'Date added' to datetime
            self.sp500_df['Date added'] = pd.to_datetime(
                self.sp500_df['Date added'], 
                errors='coerce'
            )
            
            logger.info(f"Successfully loaded {len(self.sp500_df)} S&P 500 companies")
            return self.sp500_df
            
        except Exception as e:
            logger.error(f"Error loading S&P 500 data: {str(e)}")
            raise
    
    def get_dataframe(self) -> pd.DataFrame:
        """
        Get the loaded S&P 500 DataFrame.
        
        Returns:
        --------
        pd.DataFrame : S&P 500 companies DataFrame
        """
        if self.sp500_df is None:
            self.load()
        return self.sp500_df.copy()


class SP500Screener:
    """
    Advanced S&P 500 stock screener with multiple filtering capabilities.
    
    Features:
    - Filter by date added (most recent additions)
    - Filter by sector and date
    - Filter by market capitalization
    - Filter by RSI indicator
    - Combine multiple filters
    """
    
    def __init__(self, auto_load: bool = True):
        """
        Initialize the SP500Screener.
        
        Parameters:
        -----------
        auto_load : bool
            If True, automatically load S&P 500 data on initialization
        """
        self.loader = SP500Loader()
        self.sp500_df = None
        self.filtered_df = None
        self.tradingview_data = None
        
        if auto_load:
            self.sp500_df = self.loader.load()
            self.filtered_df = self.sp500_df.copy()
    
    def load_sp500_data(self) -> pd.DataFrame:
        """
        Load S&P 500 data if not already loaded.
        
        Returns:
        --------
        pd.DataFrame : S&P 500 companies DataFrame
        """
        if self.sp500_df is None:
            self.sp500_df = self.loader.load()
            self.filtered_df = self.sp500_df.copy()
        return self.sp500_df
    
    def reset_filters(self) -> 'SP500Screener':
        """
        Reset all filters and return to original S&P 500 list.
        
        Returns:
        --------
        SP500Screener : self for method chaining
        """
        if self.sp500_df is None:
            self.load_sp500_data()
        self.filtered_df = self.sp500_df.copy()
        logger.info(f"Filters reset. Total companies: {len(self.filtered_df)}")
        return self
    
    def filter_by_recent_additions(self, n: int = 10) -> 'SP500Screener':
        """
        Filter for the N most recently added companies to S&P 500.
        
        Parameters:
        -----------
        n : int
            Number of most recent additions to return
        
        Returns:
        --------
        SP500Screener : self for method chaining
        """
        if self.filtered_df is None:
            self.load_sp500_data()
        
        # Sort by date added (most recent first)
        sorted_df = self.filtered_df.sort_values('Date added', ascending=False)
        
        # Get top N
        self.filtered_df = sorted_df.head(n).copy()
        
        logger.info(f"Filtered to {len(self.filtered_df)} most recent additions")
        return self
    
    def filter_by_sector_and_recent(self, sector: str, n: int = 10) -> 'SP500Screener':
        """
        Filter for N most recently added companies from a specific sector.
        
        Parameters:
        -----------
        sector : str
            GICS Sector name (e.g., 'Information Technology', 'Health Care')
        n : int
            Number of companies to return
        
        Returns:
        --------
        SP500Screener : self for method chaining
        """
        if self.filtered_df is None:
            self.load_sp500_data()
        
        # Filter by sector
        sector_df = self.filtered_df[
            self.filtered_df['GICS Sector'] == sector
        ].copy()
        
        if len(sector_df) == 0:
            logger.warning(f"No companies found in sector: {sector}")
            logger.info(f"Available sectors: {self.filtered_df['GICS Sector'].unique().tolist()}")
            self.filtered_df = pd.DataFrame()
            return self
        
        # Sort by date and get top N
        sorted_df = sector_df.sort_values('Date added', ascending=False)
        self.filtered_df = sorted_df.head(n).copy()
        
        logger.info(f"Filtered to {len(self.filtered_df)} most recent additions from {sector}")
        return self
    
    def filter_by_market_cap(self, n: int = 10, sector: Optional[str] = None) -> 'SP500Screener':
        """
        Filter for N companies with highest market capitalization.
        Uses TradingViewData to get market cap information.
        
        Parameters:
        -----------
        n : int
            Number of companies to return
        sector : str, optional
            If provided, filter only within this sector (e.g., 'Information Technology')
        
        Returns:
        --------
        SP500Screener : self for method chaining
        """
        if self.filtered_df is None:
            self.load_sp500_data()
        
        # Load TradingView data if not already loaded
        if self.tradingview_data is None:
            logger.info("Loading TradingView data for market cap information...")
            self.tradingview_data = TradingViewData(auto_load=True)
        
        # Get tickers from filtered DataFrame
        tickers = self.filtered_df['Symbol'].tolist()
        
        # Filter by sector if specified
        if sector:
            sector_tickers = self.filtered_df[
                self.filtered_df['GICS Sector'] == sector
            ]['Symbol'].tolist()
            tickers = sector_tickers
            
            if len(tickers) == 0:
                logger.warning(f"No companies found in sector: {sector}")
                self.filtered_df = pd.DataFrame()
                return self
        
        # Get market cap data from TradingView
        tv_stocks = self.tradingview_data.us_stock
        
        # Match tickers and get market cap
        matched_stocks = tv_stocks[tv_stocks['name'].isin(tickers)].copy()
        
        if len(matched_stocks) == 0:
            logger.warning("No market cap data found for filtered tickers")
            return self
        
        # Sort by market cap and get top N
        top_stocks = matched_stocks.nlargest(n, 'market_cap_basic')
        
        # Filter original DataFrame to only these tickers
        top_tickers = top_stocks['name'].tolist()
        self.filtered_df = self.filtered_df[
            self.filtered_df['Symbol'].isin(top_tickers)
        ].copy()
        
        # Add market cap info to the result
        market_cap_dict = dict(zip(top_stocks['name'], top_stocks['market_cap_basic']))
        market_cap_text_dict = dict(zip(top_stocks['name'], top_stocks['market_cap_text']))
        
        self.filtered_df['Market Cap'] = self.filtered_df['Symbol'].map(market_cap_dict)
        self.filtered_df['Market Cap Text'] = self.filtered_df['Symbol'].map(market_cap_text_dict)
        
        # Sort by market cap descending
        self.filtered_df = self.filtered_df.sort_values('Market Cap', ascending=False)
        
        sector_msg = f" from {sector}" if sector else ""
        logger.info(f"Filtered to {len(self.filtered_df)} highest market cap companies{sector_msg}")
        return self
    
    def filter_by_rsi(self, n: int = 10, rsi_period: int = 14, 
                      range: str = '1y', interval: str = '1d') -> 'SP500Screener':
        """
        Filter for N companies with lowest RSI values.
        Uses MarketData class to calculate RSI for each ticker.
        
        Parameters:
        -----------
        n : int
            Number of companies to return
        rsi_period : int
            RSI period (default: 14)
        range : str
            Time range for historical data (default: '1y')
        interval : str
            Data interval (default: '1d')
        
        Returns:
        --------
        SP500Screener : self for method chaining
        """
        if self.filtered_df is None:
            self.load_sp500_data()
        
        tickers = self.filtered_df['Symbol'].tolist()
        
        if len(tickers) == 0:
            logger.warning("No tickers to calculate RSI for")
            return self
        
        logger.info(f"Calculating RSI({rsi_period}) for {len(tickers)} tickers...")
        
        rsi_results = []
        
        for i, ticker in enumerate(tickers, 1):
            try:
                # Download data and calculate RSI
                md = MarketData(ticker=ticker, ad_ticker=False, 
                               range=range, interval=interval)
                
                # Get the latest RSI value
                latest_rsi = md.df['rsi'].iloc[-1]
                
                if pd.notna(latest_rsi):
                    rsi_results.append({
                        'Symbol': ticker,
                        'RSI': latest_rsi,
                        'Close': md.df['close'].iloc[-1],
                        'Date': md.df['date'].iloc[-1]
                    })
                
                if i % 10 == 0:
                    logger.info(f"Progress: {i}/{len(tickers)} tickers processed")
                    
            except Exception as e:
                logger.warning(f"Error calculating RSI for {ticker}: {str(e)}")
                continue
        
        if len(rsi_results) == 0:
            logger.warning("No RSI data calculated successfully")
            self.filtered_df = pd.DataFrame()
            return self
        
        # Create RSI DataFrame
        rsi_df = pd.DataFrame(rsi_results)
        
        # Sort by RSI (lowest first) and get top N
        rsi_df = rsi_df.sort_values('RSI', ascending=True).head(n)
        
        # Merge with filtered_df
        self.filtered_df = self.filtered_df.merge(
            rsi_df[['Symbol', 'RSI', 'Close', 'Date']], 
            on='Symbol', 
            how='inner'
        )
        
        # Sort by RSI
        self.filtered_df = self.filtered_df.sort_values('RSI', ascending=True)
        
        logger.info(f"Filtered to {len(self.filtered_df)} companies with lowest RSI values")
        return self
    
    def get_results(self) -> pd.DataFrame:
        """
        Get the filtered results as a DataFrame.
        
        Returns:
        --------
        pd.DataFrame : Filtered companies DataFrame
        """
        if self.filtered_df is None:
            logger.warning("No data loaded. Loading S&P 500 data...")
            self.load_sp500_data()
        
        return self.filtered_df.copy()
    
    def get_tickers(self) -> List[str]:
        """
        Get list of ticker symbols from filtered results.
        
        Returns:
        --------
        List[str] : List of ticker symbols
        """
        if self.filtered_df is None or len(self.filtered_df) == 0:
            return []
        
        return self.filtered_df['Symbol'].tolist()
    
    def print_summary(self):
        """Print a summary of the filtered results."""
        if self.filtered_df is None or len(self.filtered_df) == 0:
            print("No companies in filtered results")
            return
        
        print(f"\n{'='*80}")
        print(f"S&P 500 Screener Results - {len(self.filtered_df)} companies")
        print(f"{'='*80}")
        print(self.filtered_df.to_string(index=False))
        print(f"{'='*80}\n")
    
    def get_available_sectors(self) -> List[str]:
        """
        Get list of available GICS sectors in current filtered data.
        
        Returns:
        --------
        List[str] : List of sector names
        """
        if self.filtered_df is None:
            self.load_sp500_data()
        
        return sorted(self.filtered_df['GICS Sector'].unique().tolist())


# Convenience functions for quick filtering

def get_recent_sp500_additions(n: int = 10) -> pd.DataFrame:
    """
    Quick function to get N most recent S&P 500 additions.
    
    Parameters:
    -----------
    n : int
        Number of companies to return
    
    Returns:
    --------
    pd.DataFrame : Filtered companies
    """
    screener = SP500Screener(auto_load=True)
    screener.filter_by_recent_additions(n=n)
    return screener.get_results()


def get_recent_additions_by_sector(sector: str, n: int = 10) -> pd.DataFrame:
    """
    Quick function to get N most recent additions from a sector.
    
    Parameters:
    -----------
    sector : str
        GICS Sector name
    n : int
        Number of companies to return
    
    Returns:
    --------
    pd.DataFrame : Filtered companies
    """
    screener = SP500Screener(auto_load=True)
    screener.filter_by_sector_and_recent(sector=sector, n=n)
    return screener.get_results()


def get_top_market_cap_tech(n: int = 10) -> pd.DataFrame:
    """
    Quick function to get N highest market cap technology companies.
    
    Parameters:
    -----------
    n : int
        Number of companies to return
    
    Returns:
    --------
    pd.DataFrame : Filtered companies
    """
    screener = SP500Screener(auto_load=True)
    screener.filter_by_market_cap(n=n, sector='Information Technology')
    return screener.get_results()


def get_lowest_rsi_stocks(n: int = 10, rsi_period: int = 14) -> pd.DataFrame:
    """
    Quick function to get N stocks with lowest RSI values.
    
    Parameters:
    -----------
    n : int
        Number of companies to return
    rsi_period : int
        RSI period
    
    Returns:
    --------
    pd.DataFrame : Filtered companies
    """
    screener = SP500Screener(auto_load=True)
    screener.filter_by_rsi(n=n, rsi_period=rsi_period)
    return screener.get_results()


if __name__ == "__main__":
    # Example usage
    print("="*80)
    print("S&P 500 Screener Examples")
    print("="*80)
    
    # Example 1: Get 10 most recent additions
    print("\n1. Getting 10 most recent S&P 500 additions...")
    recent = get_recent_sp500_additions(n=10)
    print(recent[['Symbol', 'Security', 'Date added', 'GICS Sector']].to_string(index=False))
    
    # Example 2: Get recent additions from Technology sector
    print("\n2. Getting 5 most recent additions from Information Technology...")
    tech_recent = get_recent_additions_by_sector('Information Technology', n=5)
    print(tech_recent[['Symbol', 'Security', 'Date added']].to_string(index=False))
    
    # Example 3: Method chaining - multiple filters
    print("\n3. Using method chaining for complex filtering...")
    screener = SP500Screener(auto_load=True)
    result = (screener
              .filter_by_recent_additions(n=50)
              .filter_by_market_cap(n=10, sector='Information Technology')
              .get_results())
    print(result[['Symbol', 'Security', 'Market Cap Text', 'Date added']].to_string(index=False))
