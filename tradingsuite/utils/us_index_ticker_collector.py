"""
US Index Ticker Collector Module

This module provides functionality to collect ticker symbols from major US market indices
and enrich them with detailed information from Yahoo Finance.
"""

import cloudscraper
import pandas as pd
import time
import re
from io import StringIO
import logging
from typing import Optional, List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class USIndexTickerCollector:
    """
    Collects ticker symbols from major US market indices with Yahoo Finance integration.
    
    Supported Indices:
    - S&P 500 (SP500)
    - NASDAQ-100 (NASDAQ100)
    - Dow Jones Industrial Average (DOWJONES)
    - Russell 1000 (RUSSELL1000)
    
    Features:
    - Configurable index selection
    - Tracks which indices each ticker belongs to
    - Fetches detailed ticker information from Yahoo Finance
    - Filters EQUITY vs non-EQUITY securities
    - Exports to CSV
    """
    
    AVAILABLE_INDICES = ['SP500', 'NASDAQ100', 'DOWJONES', 'RUSSELL1000']
    
    def __init__(self, indices: Optional[List[str]] = None, auto_auth: bool = True):
        """
        Initialize the USIndexTickerCollector.
        
        Parameters:
        -----------
        indices : List[str], optional
            List of indices to collect. Options: ['SP500', 'NASDAQ100', 'DOWJONES', 'RUSSELL1000']
            If None, collects all available indices.
        auto_auth : bool
            Automatically authenticate with Yahoo Finance on initialization
        """
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        # Set enabled indices
        if indices is None:
            self.enabled_indices = self.AVAILABLE_INDICES.copy()
        else:
            # Validate indices
            invalid = [idx for idx in indices if idx not in self.AVAILABLE_INDICES]
            if invalid:
                raise ValueError(f"Invalid indices: {invalid}. Available: {self.AVAILABLE_INDICES}")
            self.enabled_indices = indices
        
        # Yahoo Finance authentication
        self.yahoo_cookies = None
        self.yahoo_crumb = None
        
        # Data storage
        self.ticker_indices: Dict[str, List[str]] = {}
        self.df_equity: Optional[pd.DataFrame] = None
        
        if auto_auth:
            self._authenticate_yahoo()
    
    def _authenticate_yahoo(self) -> bool:
        """
        Authenticate with Yahoo Finance to get cookies and crumb.
        
        Returns:
        --------
        bool : True if successful
        """
        try:
            response = self.scraper.get('https://finance.yahoo.com/')
            self.yahoo_cookies = response.cookies
            
            crumb_match = re.search(r'"crumb":"([^"]+)"', response.text)
            if crumb_match:
                self.yahoo_crumb = crumb_match.group(1)
                logger.info("✓ Yahoo Finance authentication successful")
                return True
            else:
                logger.warning("⚠ Crumb not found, continuing without it...")
                return True
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    def _get_sp500_tickers(self) -> List[str]:
        """Fetch S&P 500 tickers from Wikipedia."""
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        try:
            response = self.scraper.get(url)
            tables = pd.read_html(StringIO(response.text))
            df = tables[0]
            tickers = df['Symbol'].tolist()
            tickers = [t.replace('.', '-') for t in tickers]
            return tickers
        except Exception as e:
            logger.error(f"Error fetching S&P 500 tickers: {e}")
            return []
    
    def _get_nasdaq100_tickers(self) -> List[str]:
        """Fetch NASDAQ-100 tickers from Wikipedia."""
        url = "https://en.wikipedia.org/wiki/NASDAQ-100"
        try:
            response = self.scraper.get(url)
            tables = pd.read_html(StringIO(response.text))
            df = tables[4]
            return df['Ticker'].tolist()
        except Exception as e:
            logger.error(f"Error fetching NASDAQ-100 tickers: {e}")
            return []
    
    def _get_dowjones_tickers(self) -> List[str]:
        """Fetch Dow Jones tickers from Wikipedia."""
        url = "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average"
        try:
            response = self.scraper.get(url)
            tables = pd.read_html(StringIO(response.text))
            for table in tables:
                if 'Symbol' in table.columns:
                    tickers = table['Symbol'].tolist()
                    tickers = [t for t in tickers if isinstance(t, str) and len(t) <= 5]
                    return tickers
            return []
        except Exception as e:
            logger.error(f"Error fetching Dow Jones tickers: {e}")
            return []
    
    def _get_russell1000_tickers(self) -> List[str]:
        """Fetch Russell 1000 tickers from Wikipedia."""
        url = "https://en.wikipedia.org/wiki/Russell_1000_Index"
        try:
            response = self.scraper.get(url)
            tables = pd.read_html(StringIO(response.text))
            
            for table in tables:
                if 'Ticker' in table.columns or 'Symbol' in table.columns:
                    ticker_col = 'Ticker' if 'Ticker' in table.columns else 'Symbol'
                    tickers = table[ticker_col].tolist()
                    return tickers
            
            return []
        except Exception as e:
            logger.error(f"Error fetching Russell 1000 tickers: {e}")
            return []
    
    def _collect_tickers(self) -> Dict[str, List[str]]:
        """
        Collect tickers from enabled indices.
        
        Returns:
        --------
        Dict[str, List[str]] : Dictionary mapping ticker to list of indices
        """
        logger.info("="*80)
        logger.info("COLLECTING TICKERS FROM INDICES")
        logger.info("="*80)
        
        logger.info(f"\n🔧 Enabled indices: {', '.join(self.enabled_indices)}")
        
        ticker_indices = {}
        
        # S&P 500
        if 'SP500' in self.enabled_indices:
            tickers = self._get_sp500_tickers()
            for ticker in tickers:
                if ticker not in ticker_indices:
                    ticker_indices[ticker] = []
                ticker_indices[ticker].append('SP500')
            logger.info(f"  S&P 500: {len(tickers)} tickers")
        
        # NASDAQ-100
        if 'NASDAQ100' in self.enabled_indices:
            tickers = self._get_nasdaq100_tickers()
            for ticker in tickers:
                if ticker not in ticker_indices:
                    ticker_indices[ticker] = []
                ticker_indices[ticker].append('NASDAQ100')
            logger.info(f"  NASDAQ-100: {len(tickers)} tickers")
        
        # Dow Jones
        if 'DOWJONES' in self.enabled_indices:
            tickers = self._get_dowjones_tickers()
            for ticker in tickers:
                if ticker not in ticker_indices:
                    ticker_indices[ticker] = []
                ticker_indices[ticker].append('DOWJONES')
            logger.info(f"  Dow Jones: {len(tickers)} tickers")
        
        # Russell 1000
        if 'RUSSELL1000' in self.enabled_indices:
            tickers = self._get_russell1000_tickers()
            for ticker in tickers:
                if ticker not in ticker_indices:
                    ticker_indices[ticker] = []
                ticker_indices[ticker].append('RUSSELL1000')
            logger.info(f"  Russell 1000: {len(tickers)} tickers")
        
        logger.info(f"\n✓ Total unique tickers: {len(ticker_indices)}")
        
        return ticker_indices
    
    def _get_ticker_details(self, ticker: str) -> Optional[Dict]:
        """
        Fetch detailed information for a ticker from Yahoo Finance.
        
        Parameters:
        -----------
        ticker : str
            Ticker symbol
        
        Returns:
        --------
        Dict or None : Ticker details if successful
        """
        url = "https://query1.finance.yahoo.com/v7/finance/quote"
        
        params = {
            'symbols': ticker,
            'fields': 'symbol,longName,quoteType,exchange,sector,industry,marketCap,currency'
        }
        
        if self.yahoo_crumb:
            params['crumb'] = self.yahoo_crumb
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://finance.yahoo.com/',
            'Origin': 'https://finance.yahoo.com'
        }
        
        try:
            response = self.scraper.get(url, params=params, headers=headers, cookies=self.yahoo_cookies)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'quoteResponse' in data and 'result' in data['quoteResponse']:
                    results = data['quoteResponse']['result']
                    
                    if results and len(results) > 0:
                        quote = results[0]
                        
                        return {
                            'Ticker': quote.get('symbol', ticker),
                            'LongName': quote.get('longName', None),
                            'QuoteType': quote.get('quoteType', None),
                            'Exchange': quote.get('exchange', None),
                            'Sector': quote.get('sector', None),
                            'Industry': quote.get('industry', None),
                            'MarketCap': quote.get('marketCap', None),
                            'Currency': quote.get('currency', None)
                        }
            
            return None
            
        except Exception as e:
            logger.debug(f"Error fetching details for {ticker}: {e}")
            return None
    
    def collect(self, save_csv: bool = False, output_dir: str = '.') -> pd.DataFrame:
        """
        Collect all tickers with detailed information from Yahoo Finance.
        Only EQUITY type tickers are returned.
        
        Parameters:
        -----------
        save_csv : bool
            If True, save results to CSV file
        output_dir : str
            Directory to save CSV file (default: current directory)
        
        Returns:
        --------
        pd.DataFrame : EQUITY tickers with details
        """
        # Collect tickers from indices
        self.ticker_indices = self._collect_tickers()
        
        # Fetch details from Yahoo Finance
        logger.info("\n" + "="*80)
        logger.info("FETCHING TICKER DETAILS FROM YAHOO FINANCE")
        logger.info("="*80)
        
        ticker_list = sorted(list(self.ticker_indices.keys()))
        all_data = []
        
        for i, ticker in enumerate(ticker_list, 1):
            print(f"\r[{i}/{len(ticker_list)}] {ticker:10}", end='', flush=True)
            
            details = self._get_ticker_details(ticker)
            
            if details:
                # Add index information
                indices_str = ','.join(self.ticker_indices[ticker])
                details['Indices'] = indices_str
                all_data.append(details)
            
            time.sleep(0.5)
        
        print("\n")
        
        # Create DataFrame
        df_temp = pd.DataFrame(all_data)
        
        # Reorder columns
        column_order = ['Ticker', 'Indices', 'LongName', 'QuoteType', 'Exchange', 
                       'Sector', 'Industry', 'MarketCap', 'Currency']
        df_temp = df_temp[column_order]
        
        # Filter EQUITY only
        self.df_equity = df_temp[df_temp['QuoteType'] == 'EQUITY'].copy()
        
        # Print summary
        logger.info("="*80)
        logger.info("SUMMARY")
        logger.info("="*80)
        logger.info(f"✅ Total tickers collected: {len(df_temp)}")
        logger.info(f"✅ EQUITY tickers: {len(self.df_equity)}")
        logger.info(f"⚠️  Non-EQUITY filtered out: {len(df_temp) - len(self.df_equity)}")
        logger.info(f"❌ Failed fetches: {len(ticker_list) - len(df_temp)}")
        logger.info("="*80)
        
        # Save to CSV if requested
        if save_csv:
            equity_path = f"{output_dir}/equity_tickers.csv"
            self.df_equity.to_csv(equity_path, index=False, sep=';')
            logger.info(f"\n✓ EQUITY tickers saved: {equity_path}")
        
        return self.df_equity
    
    def print_statistics(self):
        """Print detailed statistics about collected tickers."""
        if self.df_equity is None or len(self.df_equity) == 0:
            logger.warning("No data available. Run collect() first.")
            return
        
        logger.info("\n" + "="*80)
        logger.info("EQUITY TICKERS STATISTICS")
        logger.info("="*80)
        
        logger.info("\n🏛️  EXCHANGES:")
        logger.info(self.df_equity['Exchange'].value_counts().head(10).to_string())
        
        logger.info("\n📈 SECTORS:")
        logger.info(self.df_equity['Sector'].value_counts().head(10).to_string())
        
        logger.info("\n📑 INDEX COMBINATIONS:")
        logger.info(self.df_equity['Indices'].value_counts().head(10).to_string())
        
        logger.info("\n🏆 TOP 10 BY MARKET CAP:")
        top10 = self.df_equity.nlargest(10, 'MarketCap')[['Ticker', 'Indices', 'LongName', 'MarketCap']]
        for idx, row in top10.iterrows():
            mc = row['MarketCap']
            if mc >= 1e12:
                cap_str = f"${mc/1e12:.2f}T"
            elif mc >= 1e9:
                cap_str = f"${mc/1e9:.2f}B"
            else:
                cap_str = f"${mc/1e6:.2f}M"
            longname = str(row['LongName'])[:35] if row['LongName'] else 'N/A'
            logger.info(f"  {row['Ticker']:6} [{row['Indices']:25}] {longname:35} - {cap_str}")
        
        logger.info("\n" + "="*80)


if __name__ == "__main__":
    """
    Example usage of USIndexTickerCollector
    """
    
    print("="*80)
    print("US INDEX TICKER COLLECTOR - EXAMPLES")
    print("="*80)
    
    # Example 1: Collect all indices (explicit)
    print("\n" + "="*80)
    print("EXAMPLE 1: Collect all available indices")
    print("="*80)
    print("Note: You can also use USIndexTickerCollector() without indices parameter for all indices")
    
    # collector = USIndexTickerCollector(indices=['SP500', 'NASDAQ100', 'DOWJONES', 'RUSSELL1000'])
    collector = USIndexTickerCollector(indices=['NASDAQ100', 'DOWJONES'])
    df_equity = collector.collect(save_csv=False)
    
    print(f"\n✅ Total EQUITY tickers: {len(df_equity)}")
    print("\n📊 First 10 rows:")
    
    # Display DataFrame (works in Jupyter/Colab notebooks)
    try:
        from IPython.display import display
        display(df_equity.head(10))
    except ImportError:
        # Fallback to string representation if not in notebook
        print(df_equity.head(10).to_string(index=False))
    
    # Print statistics
    collector.print_statistics()
    
    # Example 2: Collect only S&P 500 and NASDAQ-100
    print("\n\n" + "="*80)
    print("EXAMPLE 2: Collect only S&P 500 and NASDAQ-100")
    print("="*80)
    collector2 = USIndexTickerCollector(indices=['SP500', 'NASDAQ100'])
    df_equity2 = collector2.collect(save_csv=False)
    
    print(f"\n✅ Total EQUITY tickers: {len(df_equity2)}")
    
    print("\n📊 Tickers in both indices:")
    both_indices = df_equity2[df_equity2['Indices'].str.contains(',')]
    print(f"Count: {len(both_indices)}")
    print(both_indices[['Ticker', 'Indices', 'LongName']].head(10).to_string(index=False))
    
    # Example 3: Collect only Dow Jones
    print("\n\n" + "="*80)
    print("EXAMPLE 3: Collect only Dow Jones Industrial Average")
    print("="*80)
    collector3 = USIndexTickerCollector(indices=['DOWJONES'])
    df_equity3 = collector3.collect(save_csv=True)
    
    print(f"\n✅ Dow Jones EQUITY tickers: {len(df_equity3)}")
    print("\n📊 All Dow Jones tickers:")
    print(df_equity3[['Ticker', 'LongName', 'Sector']].to_string(index=False))
    
    # Example 4: Working with collected data
    print("\n\n" + "="*80)
    print("EXAMPLE 4: Working with collected data")
    print("="*80)
    
    # Filter by sector
    tech_stocks = df_equity[df_equity['Sector'] == 'Technology']
    print(f"\n📈 Technology stocks: {len(tech_stocks)}")
    print(tech_stocks[['Ticker', 'Indices', 'LongName']].head(10).to_string(index=False))
    
    # Example 5: Save to CSV
    print("\n\n" + "="*80)
    print("EXAMPLE 5: Save results to CSV file")
    print("="*80)
    print("To save to current directory:")
    print("  collector.collect(save_csv=True)")
    print("\nTo save to specific directory:")
    print("  collector.collect(save_csv=True, output_dir='/path/to/directory')")
    
    print("\n" + "="*80)
    print("✅ EXAMPLES COMPLETED!")
    print("="*80)






if __name__ == "__main__":
    """
    Example usage of USIndexTickerCollector
    """
    
    print("="*80)
    print("US INDEX TICKER COLLECTOR - EXAMPLES")
    print("="*80)
    
    # Example 1: Collect all indices (explicit)
    print("\n" + "="*80)
    print("EXAMPLE 1: Collect all available indices")
    print("="*80)
    print("Note: You can also use USIndexTickerCollector() without indices parameter for all indices")
    
    collector = USIndexTickerCollector(indices=['SP500', 'NASDAQ100', 'DOWJONES', 'RUSSELL1000'])
    df_equity = collector.collect(save_csv=False)
    
    print(f"\n✅ Total EQUITY tickers: {len(df_equity)}")
    print("\n📊 First 10 rows:")
    print(df_equity.head(10).to_string(index=False))
    
    # Print statistics
    collector.print_statistics()
    
    # Example 2: Collect only S&P 500 and NASDAQ-100
    print("\n\n" + "="*80)
    print("EXAMPLE 2: Collect only S&P 500 and NASDAQ-100")
    print("="*80)
    collector2 = USIndexTickerCollector(indices=['SP500', 'NASDAQ100'])
    df_equity2 = collector2.collect(save_csv=False)
    
    print(f"\n✅ Total EQUITY tickers: {len(df_equity2)}")
    
    print("\n📊 Tickers in both indices:")
    both_indices = df_equity2[df_equity2['Indices'].str.contains(',')]
    print(f"Count: {len(both_indices)}")
    print(both_indices[['Ticker', 'Indices', 'LongName']].head(10).to_string(index=False))
    
    # Example 3: Collect only Dow Jones
    print("\n\n" + "="*80)
    print("EXAMPLE 3: Collect only Dow Jones Industrial Average")
    print("="*80)
    collector3 = USIndexTickerCollector(indices=['DOWJONES'])
    df_equity3 = collector3.collect(save_csv=False)
    
    print(f"\n✅ Dow Jones EQUITY tickers: {len(df_equity3)}")
    print("\n📊 All Dow Jones tickers:")
    print(df_equity3[['Ticker', 'LongName', 'Sector']].to_string(index=False))
    
    # Example 4: Working with collected data
    print("\n\n" + "="*80)
    print("EXAMPLE 4: Working with collected data")
    print("="*80)
    
    # Filter by sector
    tech_stocks = df_equity[df_equity['Sector'] == 'Technology']
    print(f"\n📈 Technology stocks: {len(tech_stocks)}")
    print(tech_stocks[['Ticker', 'Indices', 'LongName']].head(10).to_string(index=False))
    
    # Example 5: Save to CSV
    print("\n\n" + "="*80)
    print("EXAMPLE 5: Save results to CSV file")
    print("="*80)
    print("To save to current directory:")
    print("  collector.collect(save_csv=True)")
    print("\nTo save to specific directory:")
    print("  collector.collect(save_csv=True, output_dir='/path/to/directory')")
    
    print("\n" + "="*80)
    print("✅ EXAMPLES COMPLETED!")
    print("="*80)
