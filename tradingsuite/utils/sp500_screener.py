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
import time
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
    - Filter by sector (GICS sectors)
    - Filter by industry (GICS Sub-Industries)
    - Filter by date added (most recent additions to S&P 500)
    - Filter by date range (companies added between dates)
    - Filter by market capitalization (largest/smallest or range)
    - Filter by RSI indicator (lowest/highest or range)
    - Limit results to top N
    - List available sectors and industries
    - Combine multiple filters with method chaining
    
    All filter methods return self for method chaining.
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
    
    def filter_by_recent_additions(self, n: int = 10, newest: bool = True) -> 'SP500Screener':
        """
        Filter for the N most recently added companies to S&P 500.
        
        Sorts current filtered dataset by 'Date added' and takes top N.
        Note: If called multiple times, it operates on already filtered data.
        For flexible limiting after other filters, use .limit(n) instead.
        
        Args:
            n: Number of additions to keep
            newest: If True, get newest additions. If False, get oldest additions.
            
        Returns:
            Self for method chaining
        """
        if self.filtered_df is None:
            self.load_sp500_data()
        
        sorted_df = self.filtered_df.sort_values('Date added', ascending=not newest)
        self.filtered_df = sorted_df.head(n).copy()
        
        direction = "newest" if newest else "oldest"
        logger.info(f"Filtered to {len(self.filtered_df)} {direction} additions")
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
    
    def filter_by_industry(self, industry: str) -> 'SP500Screener':
        """Filter for companies from a specific GICS Sub-Industry."""
        if self.filtered_df is None:
            self.load_sp500_data()
        
        industry_df = self.filtered_df[
            self.filtered_df['GICS Sub-Industry'] == industry
        ].copy()
        
        if len(industry_df) == 0:
            logger.warning(f"No companies found in industry: {industry}")
            logger.info(f"Available industries: {self.filtered_df['GICS Sub-Industry'].unique().tolist()}")
            self.filtered_df = pd.DataFrame()
            return self
        
        self.filtered_df = industry_df
        
        logger.info(f"Filtered to {len(self.filtered_df)} companies from {industry}")
        return self
    
    def get_available_sectors(self) -> List[str]:
        """
        Return list of available GICS sectors in current filtered dataset.
        
        Returns:
            Sorted list of sector names
        """
        if self.filtered_df is None:
            self.load_sp500_data()
        
        return sorted(self.filtered_df['GICS Sector'].unique().tolist())
    
    def get_available_industries(self, sector: Optional[str] = None) -> List[str]:
        """
        Return list of available GICS Sub-Industries.
        
        Args:
            sector: Optional sector name to filter industries. If None, returns all industries.
            
        Returns:
            Sorted list of industry names
        """
        if self.filtered_df is None:
            self.load_sp500_data()
        
        if sector:
            industries_df = self.filtered_df[self.filtered_df['GICS Sector'] == sector]
        else:
            industries_df = self.filtered_df
        
        return sorted(industries_df['GICS Sub-Industry'].unique().tolist())
    
    def print_available_sectors(self) -> 'SP500Screener':
        """
        Print formatted list of available sectors with company counts.
        
        Returns:
            Self for method chaining
        """
        if self.filtered_df is None:
            self.load_sp500_data()
        
        sector_counts = self.filtered_df['GICS Sector'].value_counts().sort_index()
        
        print("\n" + "="*60)
        print("Available GICS Sectors")
        print("="*60)
        for sector, count in sector_counts.items():
            print(f"{sector:.<50} {count:>3} companies")
        print("="*60)
        print(f"Total: {len(sector_counts)} sectors, {len(self.filtered_df)} companies\n")
        
        return self
    
    def print_available_industries(self, sector: Optional[str] = None) -> 'SP500Screener':
        """
        Print formatted list of available industries with company counts.
        
        Args:
            sector: Optional sector name to filter industries. If None, shows all industries.
            
        Returns:
            Self for method chaining
        """
        if self.filtered_df is None:
            self.load_sp500_data()
        
        if sector:
            industries_df = self.filtered_df[self.filtered_df['GICS Sector'] == sector]
            title = f"Available GICS Sub-Industries in {sector}"
        else:
            industries_df = self.filtered_df
            title = "Available GICS Sub-Industries (All Sectors)"
        
        if len(industries_df) == 0:
            print(f"\nNo companies found in sector: {sector}\n")
            return self
        
        industry_counts = industries_df['GICS Sub-Industry'].value_counts().sort_index()
        
        print("\n" + "="*60)
        print(title)
        print("="*60)
        for industry, count in industry_counts.items():
            print(f"{industry:.<50} {count:>3} companies")
        print("="*60)
        print(f"Total: {len(industry_counts)} industries, {len(industries_df)} companies\n")
        
        return self
    
    def limit(self, n: int) -> 'SP500Screener':
        """Limit results to top N rows from current filtered dataset."""
        if self.filtered_df is None:
            self.load_sp500_data()
        
        if len(self.filtered_df) == 0:
            logger.warning("No data to limit")
            return self
        
        original_count = len(self.filtered_df)
        self.filtered_df = self.filtered_df.head(n).copy()
        
        logger.info(f"Limited results from {original_count} to {len(self.filtered_df)} companies")
        return self
    
    def filter_by_market_cap(self, n: int = 10, largest: bool = True) -> 'SP500Screener':
        """
        Filter for N companies by market capitalization.
        
        Args:
            n: Number of companies to keep
            largest: If True, get largest market cap. If False, get smallest market cap.
            
        Returns:
            Self for method chaining
        """
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
        
        # Select top N by market cap (largest or smallest)
        if largest:
            top_stocks = matched_stocks.nlargest(n, 'market_cap_basic')
        else:
            top_stocks = matched_stocks.nsmallest(n, 'market_cap_basic')
        
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
        
        self.filtered_df = self.filtered_df.sort_values('Market Cap', ascending=not largest)
        
        direction = "largest" if largest else "smallest"
        logger.info(f"Filtered to {len(self.filtered_df)} {direction} market cap companies")
        return self
    
    def filter_by_rsi(self, n: int = 10, rsi_period: int = 14, 
                      range: str = '1y', interval: str = '1d', 
                      delay: float = 0.5, lowest: bool = True) -> 'SP500Screener':
        """
        Filter for N companies by RSI values.
        
        Args:
            n: Number of companies to keep
            rsi_period: RSI period for calculation (default 14)
            range: Time range for data (default '1y')
            interval: Data interval (default '1d')
            delay: Delay in seconds between API calls to avoid rate limiting (default 0.5)
            lowest: If True, get lowest RSI. If False, get highest RSI.
            
        Returns:
            Self for method chaining
        """
        if self.filtered_df is None:
            self.load_sp500_data()
        
        tickers = self.filtered_df['Symbol'].tolist()
        
        if len(tickers) == 0:
            logger.warning("No tickers to calculate RSI for")
            return self
        
        direction = "lowest" if lowest else "highest"
        logger.info(f"Calculating RSI({rsi_period}) for {len(tickers)} tickers (with {delay}s delay between requests)...")
        
        rsi_results = []
        failed_tickers = []
        
        for i, ticker in enumerate(tickers, 1):
            try:
                md = MarketData(ticker=ticker, ad_ticker=False, 
                               range=range, interval=interval)
                
                if md.df is None or len(md.df) == 0:
                    logger.warning(f"No data available for {ticker}")
                    failed_tickers.append(ticker)
                    continue
                
                if 'rsi' not in md.df.columns:
                    logger.warning(f"RSI column not found for {ticker}")
                    failed_tickers.append(ticker)
                    continue
                
                latest_rsi = md.df['rsi'].iloc[-1]
                
                if pd.notna(latest_rsi):
                    rsi_results.append({
                        'Symbol': ticker,
                        'RSI': latest_rsi,
                        'Close': md.df['close'].iloc[-1],
                        'Date': md.df['date'].iloc[-1]
                    })
                else:
                    logger.warning(f"RSI is NaN for {ticker}")
                    failed_tickers.append(ticker)
                
                if i % 10 == 0:
                    logger.info(f"Progress: {i}/{len(tickers)} tickers processed ({len(rsi_results)} successful)")
                
                # Add delay between requests to avoid rate limiting
                if i < len(tickers):  # Don't sleep after the last ticker
                    time.sleep(delay)
                    
            except Exception as e:
                logger.warning(f"Error calculating RSI for {ticker}: {str(e)}")
                failed_tickers.append(ticker)
                # Still add delay even on error to avoid hammering the API
                if i < len(tickers):
                    time.sleep(delay)
                continue
        
        if len(failed_tickers) > 0:
            logger.info(f"Failed to calculate RSI for {len(failed_tickers)} tickers: {', '.join(failed_tickers[:10])}{'...' if len(failed_tickers) > 10 else ''}")
        
        if len(rsi_results) == 0:
            logger.warning("No RSI data calculated successfully")
            self.filtered_df = pd.DataFrame()
            return self
        
        rsi_df = pd.DataFrame(rsi_results)
        rsi_df = rsi_df.sort_values('RSI', ascending=lowest).head(n)
        
        self.filtered_df = self.filtered_df.merge(
            rsi_df[['Symbol', 'RSI', 'Close', 'Date']], 
            on='Symbol', 
            how='inner'
        )
        
        self.filtered_df = self.filtered_df.sort_values('RSI', ascending=lowest)
        
        logger.info(f"Filtered to {len(self.filtered_df)} companies with {direction} RSI values")
        return self
    
    def filter_by_rsi_range(self, min_rsi: float, max_rsi: float, 
                            rsi_period: int = 14, range: str = '1y', 
                            interval: str = '1d', delay: float = 0.5) -> 'SP500Screener':
        """
        Filter companies with RSI between min and max values.
        
        Args:
            min_rsi: Minimum RSI value (inclusive)
            max_rsi: Maximum RSI value (inclusive)
            rsi_period: RSI period for calculation (default 14)
            range: Time range for data (default '1y')
            interval: Data interval (default '1d')
            delay: Delay in seconds between API calls (default 0.5)
            
        Returns:
            Self for method chaining
        """
        if self.filtered_df is None:
            self.load_sp500_data()
        
        tickers = self.filtered_df['Symbol'].tolist()
        
        if len(tickers) == 0:
            logger.warning("No tickers to calculate RSI for")
            return self
        
        logger.info(f"Calculating RSI({rsi_period}) for {len(tickers)} tickers (filtering range {min_rsi}-{max_rsi})...")
        
        rsi_results = []
        failed_tickers = []
        
        for i, ticker in enumerate(tickers, 1):
            try:
                md = MarketData(ticker=ticker, ad_ticker=False, 
                               range=range, interval=interval)
                
                if md.df is None or len(md.df) == 0:
                    logger.warning(f"No data available for {ticker}")
                    failed_tickers.append(ticker)
                    continue
                
                if 'rsi' not in md.df.columns:
                    logger.warning(f"RSI column not found for {ticker}")
                    failed_tickers.append(ticker)
                    continue
                
                latest_rsi = md.df['rsi'].iloc[-1]
                
                if pd.notna(latest_rsi) and min_rsi <= latest_rsi <= max_rsi:
                    rsi_results.append({
                        'Symbol': ticker,
                        'RSI': latest_rsi,
                        'Close': md.df['close'].iloc[-1],
                        'Date': md.df['date'].iloc[-1]
                    })
                
                if i % 10 == 0:
                    logger.info(f"Progress: {i}/{len(tickers)} tickers processed ({len(rsi_results)} in range)")
                
                if i < len(tickers):
                    time.sleep(delay)
                    
            except Exception as e:
                logger.warning(f"Error calculating RSI for {ticker}: {str(e)}")
                failed_tickers.append(ticker)
                if i < len(tickers):
                    time.sleep(delay)
                continue
        
        if len(failed_tickers) > 0:
            logger.info(f"Failed to calculate RSI for {len(failed_tickers)} tickers")
        
        if len(rsi_results) == 0:
            logger.warning(f"No companies found with RSI in range {min_rsi}-{max_rsi}")
            self.filtered_df = pd.DataFrame()
            return self
        
        rsi_df = pd.DataFrame(rsi_results)
        
        self.filtered_df = self.filtered_df.merge(
            rsi_df[['Symbol', 'RSI', 'Close', 'Date']], 
            on='Symbol', 
            how='inner'
        )
        
        self.filtered_df = self.filtered_df.sort_values('RSI', ascending=True)
        
        logger.info(f"Filtered to {len(self.filtered_df)} companies with RSI between {min_rsi}-{max_rsi}")
        return self
    
    def filter_by_market_cap_range(self, min_cap: float, max_cap: float) -> 'SP500Screener':
        """
        Filter companies with market cap between min and max values.
        
        Args:
            min_cap: Minimum market cap in dollars (e.g., 1e9 for $1B)
            max_cap: Maximum market cap in dollars (e.g., 100e9 for $100B)
            
        Returns:
            Self for method chaining
        """
        if self.filtered_df is None:
            self.load_sp500_data()
        
        if self.tradingview_data is None:
            logger.info("Loading TradingView data for market cap information...")
            self.tradingview_data = TradingViewData(auto_load=True)
        
        tickers = self.filtered_df['Symbol'].tolist()
        
        if len(tickers) == 0:
            logger.warning("No tickers to filter by market cap range")
            return self
        
        tv_stocks = self.tradingview_data.us_stock
        matched_stocks = tv_stocks[tv_stocks['name'].isin(tickers)].copy()
        
        if len(matched_stocks) == 0:
            logger.warning("No market cap data found for filtered tickers")
            return self
        
        # Filter by market cap range
        filtered_stocks = matched_stocks[
            (matched_stocks['market_cap_basic'] >= min_cap) & 
            (matched_stocks['market_cap_basic'] <= max_cap)
        ].copy()
        
        if len(filtered_stocks) == 0:
            logger.warning(f"No companies found with market cap between ${min_cap:,.0f} and ${max_cap:,.0f}")
            self.filtered_df = pd.DataFrame()
            return self
        
        filtered_tickers = filtered_stocks['name'].tolist()
        
        self.filtered_df = self.filtered_df[
            self.filtered_df['Symbol'].isin(filtered_tickers)
        ].copy()
        
        # Add market cap data
        market_cap_dict = dict(zip(filtered_stocks['name'], filtered_stocks['market_cap_basic']))
        self.filtered_df['Market Cap'] = self.filtered_df['Symbol'].map(market_cap_dict)
        
        # Add formatted market cap text
        if 'market_cap_text' in filtered_stocks.columns:
            market_cap_text_dict = dict(zip(filtered_stocks['name'], filtered_stocks['market_cap_text']))
            self.filtered_df['Market Cap Text'] = self.filtered_df['Symbol'].map(market_cap_text_dict)
        else:
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
        
        logger.info(f"Filtered to {len(self.filtered_df)} companies with market cap between ${min_cap:,.0f}-${max_cap:,.0f}")
        return self
    
    def filter_by_date_range(self, start_date: str, end_date: str) -> 'SP500Screener':
        """
        Filter companies added to S&P 500 between start_date and end_date.
        
        Args:
            start_date: Start date in format 'YYYY-MM-DD'
            end_date: End date in format 'YYYY-MM-DD'
            
        Returns:
            Self for method chaining
        """
        if self.filtered_df is None:
            self.load_sp500_data()
        
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        date_filtered = self.filtered_df[
            (self.filtered_df['Date added'] >= start) & 
            (self.filtered_df['Date added'] <= end)
        ].copy()
        
        if len(date_filtered) == 0:
            logger.warning(f"No companies found added between {start_date} and {end_date}")
            self.filtered_df = pd.DataFrame()
            return self
        
        self.filtered_df = date_filtered
        
        logger.info(f"Filtered to {len(self.filtered_df)} companies added between {start_date} and {end_date}")
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
    
    print("\n5. Using limit() method for flexible result restriction...")
    result3 = (screener
               .reset_filters()
               .filter_by_sector('Information Technology')
               .filter_by_recent_additions(n=100)
               .limit(20)  # Take top 20 from the 100 most recent
               .get_results())
    print(result3[['Symbol', 'Security', 'Date added']].to_string(index=False))
    
    print("\n6. Complete workflow with RSI filtering...")
    print("(Note: RSI calculation includes 0.5s delay between tickers to avoid rate limiting)")
    result4 = (screener
               .reset_filters()
               .filter_by_sector('Energy')
               .filter_by_market_cap(n=20)
               .filter_by_rsi(n=5, rsi_period=14, delay=0.5)
               .get_results())
    if len(result4) > 0:
        print(result4[['Symbol', 'Security', 'RSI', 'Close', 'Market Cap Text']].to_string(index=False))
    
    print("\n7. Demonstrating direction parameters...")
    print("Finding oldest S&P 500 additions from Tech sector with smallest market cap:")
    result5 = (screener
               .reset_filters()
               .filter_by_sector('Information Technology')
               .filter_by_recent_additions(n=50, newest=False)  # Oldest additions
               .filter_by_market_cap(n=10, largest=False)       # Smallest market cap
               .get_results())
    print(result5[['Symbol', 'Security', 'Date added', 'Market Cap Text']].to_string(index=False))
    
    print("\n8. Finding companies with highest RSI (overbought)...")
    result6 = (screener
               .reset_filters()
               .filter_by_sector('Consumer Discretionary')
               .filter_by_market_cap(n=30)
               .filter_by_rsi(n=5, lowest=False, delay=0.5)  # Highest RSI
               .get_results())
    if len(result6) > 0:
        print(result6[['Symbol', 'Security', 'RSI', 'Market Cap Text']].to_string(index=False))
    
    print("\n9. Listing available sectors and industries...")
    screener.reset_filters().print_available_sectors()
    
    print("\nIndustries in Information Technology sector:")
    screener.print_available_industries('Information Technology')
    
    print("\n10. Using range-based filters...")
    print("Finding mid-cap companies ($10B-$50B) with neutral RSI (40-60):")
    result7 = (screener
               .reset_filters()
               .filter_by_market_cap_range(min_cap=10e9, max_cap=50e9)
               .filter_by_rsi_range(min_rsi=40, max_rsi=60, delay=0.5)
               .get_results())
    if len(result7) > 0:
        print(result7[['Symbol', 'Security', 'Market Cap Text', 'RSI']].head(10).to_string(index=False))
    
    print("\n11. Filtering by industry and date range...")
    result8 = (screener
               .reset_filters()
               .filter_by_industry('Software')
               .filter_by_date_range('2020-01-01', '2023-12-31')
               .get_results())
    print(f"Software companies added between 2020-2023:")
    if len(result8) > 0:
        print(result8[['Symbol', 'Security', 'Date added', 'GICS Sub-Industry']].to_string(index=False))
