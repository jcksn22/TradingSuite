"""
S&P 500 Screener Module - Refactored Version

All filter methods are now independent and chainable.
"""

import pandas as pd
import numpy as np
import cloudscraper
from io import StringIO
from datetime import datetime
import logging
from typing import Optional, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from ..data.market_data import MarketData
    from ..data.tradingview_data import TradingViewData
except ImportError:
    from tradingsuite.data.market_data import MarketData
    from tradingsuite.data.tradingview_data import TradingViewData


class SP500Loader:
    """Loads current S&P 500 companies from Wikipedia."""
    
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.sp500_df = None
        self.url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    
    def load(self) -> pd.DataFrame:
        """Download current S&P 500 companies list from Wikipedia."""
        try:
            logger.info(f"Downloading S&P 500 data from Wikipedia...")
            response = self.scraper.get(self.url)
            tables = pd.read_html(StringIO(response.text))
            self.sp500_df = tables[0]
            self.sp500_df['Date added'] = pd.to_datetime(
                self.sp500_df['Date added'], 
                errors='coerce'
            )
            logger.info(f"Successfully loaded {len(self.sp500_df)} S&P 500 companies")
            return self.sp500_df
        except Exception as e:
            logger.error(f"Error loading S&P 500 data: {str(e)}")
            raise


class SP500Screener:
    """
    S&P 500 stock screener with multiple filtering capabilities.
    
    Features:
    - Filter by date added (most recent additions)
    - Filter by sector
    - Filter by market capitalization
    - Filter by RSI indicator
    - Combine multiple filters with method chaining
    """
    
    def __init__(self, auto_load: bool = True):
        self.loader = SP500Loader()
        self.sp500_df = None
        self.filtered_df = None
        self.tradingview_data = None
        
        if auto_load:
            self.sp500_df = self.loader.load()
            self.filtered_df = self.sp500_df.copy()
    
    def load_sp500_data(self) -> pd.DataFrame:
        """Load S&P 500 data if not already loaded."""
        if self.sp500_df is None:
            self.sp500_df = self.loader.load()
            self.filtered_df = self.sp500_df.copy()
        return self.sp500_df
    
    def reset_filters(self) -> 'SP500Screener':
        """Reset all filters and return to original S&P 500 list."""
        if self.sp500_df is None:
            self.load_sp500_data()
        self.filtered_df = self.sp500_df.copy()
        logger.info(f"Filters reset. Total companies: {len(self.filtered_df)}")
        return self
    
    def filter_by_recent_additions(self, n: int = 10) -> 'SP500Screener':
        """Filter for the N most recently added companies to S&P 500."""
        if self.filtered_df is None:
            self.load_sp500_data()
        
        sorted_df = self.filtered_df.sort_values('Date added', ascending=False)
        self.filtered_df = sorted_df.head(n).copy()
        
        logger.info(f"Filtered to {len(self.filtered_df)} most recent additions")
        return self
    
    def filter_by_sector(self, sector: str) -> 'SP500Screener':
        """Filter for companies from a specific sector."""
        if self.filtered_df is None:
            self.load_sp500_data()
        
        sector_df = self.filtered_df[
            self.filtered_df['GICS Sector'] == sector
        ].copy()
        
        if len(sector_df) == 0:
            logger.warning(f"No companies found in sector: {sector}")
            logger.info(f"Available sectors: {self.filtered_df['GICS Sector'].unique().tolist()}")
            self.filtered_df = pd.DataFrame()
            return self
        
        self.filtered_df = sector_df
        
        logger.info(f"Filtered to {len(self.filtered_df)} companies from {sector}")
        return self
    
    def filter_by_market_cap(self, n: int = 10) -> 'SP500Screener':
        """Filter for N companies with highest market capitalization."""
        if self.filtered_df is None:
            self.load_sp500_data()
        
        if self.tradingview_data is None:
            logger.info("Loading TradingView data for market cap information...")
            self.tradingview_data = TradingViewData(auto_load=True)
        
        tickers = self.filtered_df['Symbol'].tolist()
        
        if len(tickers) == 0:
            logger.warning("No tickers to filter by market cap")
            return self
        
        tv_stocks = self.tradingview_data.us_stock
        matched_stocks = tv_stocks[tv_stocks['name'].isin(tickers)].copy()
        
        if len(matched_stocks) == 0:
            logger.warning("No market cap data found for filtered tickers")
            return self
        
        top_stocks = matched_stocks.nlargest(n, 'market_cap_basic')
        top_tickers = top_stocks['name'].tolist()
        
        self.filtered_df = self.filtered_df[
            self.filtered_df['Symbol'].isin(top_tickers)
        ].copy()
        
        # Add market cap data
        market_cap_dict = dict(zip(top_stocks['name'], top_stocks['market_cap_basic']))
        self.filtered_df['Market Cap'] = self.filtered_df['Symbol'].map(market_cap_dict)
        
        # Add formatted market cap text if available
        if 'market_cap_text' in top_stocks.columns:
            market_cap_text_dict = dict(zip(top_stocks['name'], top_stocks['market_cap_text']))
            self.filtered_df['Market Cap Text'] = self.filtered_df['Symbol'].map(market_cap_text_dict)
        else:
            # Create formatted text from numeric value
            def format_market_cap(value):
                if pd.isna(value):
                    return 'N/A'
                if value >= 1e12:
                    return f"{value/1e12:.2f}T"
                elif value >= 1e9:
                    return f"{value/1e9:.2f}B"
                elif value >= 1e6:
                    return f"{value/1e6:.2f}M"
                else:
                    return f"{value:.0f}"
            
            self.filtered_df['Market Cap Text'] = self.filtered_df['Market Cap'].apply(format_market_cap)
        
        self.filtered_df = self.filtered_df.sort_values('Market Cap', ascending=False)
        
        logger.info(f"Filtered to {len(self.filtered_df)} highest market cap companies")
        return self
    
    def filter_by_rsi(self, n: int = 10, rsi_period: int = 14, 
                      range: str = '1y', interval: str = '1d') -> 'SP500Screener':
        """Filter for N companies with lowest RSI values."""
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
                md = MarketData(ticker=ticker, ad_ticker=False, 
                               range=range, interval=interval)
                
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
        
        rsi_df = pd.DataFrame(rsi_results)
        rsi_df = rsi_df.sort_values('RSI', ascending=True).head(n)
        
        self.filtered_df = self.filtered_df.merge(
            rsi_df[['Symbol', 'RSI', 'Close', 'Date']], 
            on='Symbol', 
            how='inner'
        )
        
        self.filtered_df = self.filtered_df.sort_values('RSI', ascending=True)
        
        logger.info(f"Filtered to {len(self.filtered_df)} companies with lowest RSI values")
        return self
    
    def get_results(self) -> pd.DataFrame:
        """Get the filtered results as a DataFrame."""
        if self.filtered_df is None:
            logger.warning("No data loaded. Loading S&P 500 data...")
            self.load_sp500_data()
        
        return self.filtered_df.copy()


if __name__ == "__main__":
    print("="*80)
    print("S&P 500 Screener - Refactored Version")
    print("="*80)
    
    screener = SP500Screener(auto_load=True)
    
    print("\n1. Getting 10 most recent S&P 500 additions...")
    recent = screener.filter_by_recent_additions(n=10).get_results()
    print(recent[['Symbol', 'Security', 'Date added', 'GICS Sector']].to_string(index=False))
    
    print("\n2. Getting 5 most recent additions from Information Technology...")
    tech_recent = (screener
                   .reset_filters()
                   .filter_by_sector('Information Technology')
                   .filter_by_recent_additions(n=5)
                   .get_results())
    print(tech_recent[['Symbol', 'Security', 'Date added']].to_string(index=False))
    
    print("\n3. Complex filtering with method chaining...")
    result = (screener
              .reset_filters()
              .filter_by_recent_additions(n=50)
              .filter_by_sector('Information Technology')
              .filter_by_market_cap(n=10)
              .get_results())
    print(result[['Symbol', 'Security', 'Market Cap Text', 'Date added']].to_string(index=False))
    
    print("\n4. Alternative chaining order - sector first...")
    result2 = (screener
               .reset_filters()
               .filter_by_sector('Health Care')
               .filter_by_market_cap(n=5)
               .get_results())
    print(result2[['Symbol', 'Security', 'Market Cap Text', 'GICS Sector']].to_string(index=False))
