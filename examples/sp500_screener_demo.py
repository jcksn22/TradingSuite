"""
S&P 500 Screener - Google Colab Example
========================================

This script demonstrates how to use the SP500Screener in Google Colab.
"""

# ============================================================================
# INSTALLATION (Run this first in Google Colab)
# ============================================================================
"""
!pip install -q cloudscraper pandas-ta plotly yfinance --no-deps
"""

# ============================================================================
# IMPORT SECTION
# ============================================================================

# After installing TradingSuite, import the screener
from tradingsuite.utils import SP500Screener
from tradingsuite.utils import (
    get_recent_sp500_additions,
    get_recent_additions_by_sector,
    get_top_market_cap_tech,
    get_lowest_rsi_stocks
)

# ============================================================================
# EXAMPLE 1: Quick Functions - Simple Filtering
# ============================================================================

print("=" * 80)
print("EXAMPLE 1: Using Quick Functions")
print("=" * 80)

# Get 10 most recent S&P 500 additions
print("\n1.1 Getting 10 most recent S&P 500 additions:")
recent_df = get_recent_sp500_additions(n=10)
print(recent_df[['Symbol', 'Security', 'Date added', 'GICS Sector']])

# Get 5 most recent additions from Health Care sector
print("\n1.2 Getting 5 most recent Health Care additions:")
healthcare_recent = get_recent_additions_by_sector('Health Care', n=5)
print(healthcare_recent[['Symbol', 'Security', 'Date added', 'GICS Sector']])

# Get top 10 tech companies by market cap
print("\n1.3 Getting top 10 tech companies by market cap:")
top_tech = get_top_market_cap_tech(n=10)
print(top_tech[['Symbol', 'Security', 'Market Cap Text', 'GICS Sector']])

# Get 10 stocks with lowest RSI
print("\n1.4 Getting 10 stocks with lowest RSI(14):")
low_rsi = get_lowest_rsi_stocks(n=10, rsi_period=14)
print(low_rsi[['Symbol', 'Security', 'RSI', 'Close', 'GICS Sector']])

# ============================================================================
# EXAMPLE 2: Using Screener Object with Method Chaining
# ============================================================================

print("\n" + "=" * 80)
print("EXAMPLE 2: Advanced Filtering with Method Chaining")
print("=" * 80)

# Initialize screener
screener = SP500Screener(auto_load=True)

# Example 2.1: Recent additions with high market cap
print("\n2.1 Top 5 market cap from 50 most recent additions:")
result = (screener
          .reset_filters()
          .filter_by_recent_additions(n=50)
          .filter_by_market_cap(n=5)
          .get_results())
print(result[['Symbol', 'Security', 'Market Cap Text', 'Date added']])

# Example 2.2: Recent tech additions with low RSI
print("\n2.2 Low RSI stocks from recent tech additions:")
result = (screener
          .reset_filters()
          .filter_by_sector_and_recent('Information Technology', n=30)
          .filter_by_rsi(n=5, rsi_period=14)
          .get_results())
print(result[['Symbol', 'Security', 'RSI', 'Date added']])

# Example 2.3: High market cap financials
print("\n2.3 Top 10 Financials by market cap:")
result = (screener
          .reset_filters()
          .filter_by_market_cap(n=10, sector='Financials')
          .get_results())
print(result[['Symbol', 'Security', 'Market Cap Text', 'GICS Sector']])

# ============================================================================
# EXAMPLE 3: Custom Complex Filtering
# ============================================================================

print("\n" + "=" * 80)
print("EXAMPLE 3: Complex Custom Filtering")
print("=" * 80)

# Create a screener instance
screener = SP500Screener(auto_load=True)

# Step 1: Get all available sectors
print("\n3.1 Available sectors:")
sectors = screener.get_available_sectors()
print(sectors)

# Step 2: Filter by specific criteria
print("\n3.2 Recent additions from multiple filters:")

# Get recent additions
screener.reset_filters().filter_by_recent_additions(n=100)
print(f"After recent filter: {len(screener.get_results())} companies")

# Further filter by market cap in tech sector
screener.filter_by_market_cap(n=15, sector='Information Technology')
print(f"After market cap filter: {len(screener.get_results())} companies")

# Get final results
final_results = screener.get_results()
print("\nFinal filtered companies:")
print(final_results[['Symbol', 'Security', 'Market Cap Text', 'Date added']])

# ============================================================================
# EXAMPLE 4: Working with Results
# ============================================================================

print("\n" + "=" * 80)
print("EXAMPLE 4: Working with Results DataFrame")
print("=" * 80)

# Get results as DataFrame
screener = SP500Screener(auto_load=True)
df = screener.filter_by_recent_additions(n=20).get_results()

print("\n4.1 DataFrame Info:")
print(f"Shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")

print("\n4.2 Extract ticker symbols:")
tickers = screener.get_tickers()
print(f"Tickers: {tickers}")

print("\n4.3 Group by sector:")
sector_counts = df['GICS Sector'].value_counts()
print(sector_counts)

print("\n4.4 Export to CSV (optional):")
# df.to_csv('sp500_filtered.csv', index=False)
print("Use: df.to_csv('sp500_filtered.csv', index=False)")

# ============================================================================
# EXAMPLE 5: Practical Use Cases
# ============================================================================

print("\n" + "=" * 80)
print("EXAMPLE 5: Practical Use Cases")
print("=" * 80)

# Use Case 1: Find oversold recent additions
print("\n5.1 Find oversold recent additions (RSI < 30 from recent 50):")
screener = SP500Screener(auto_load=True)
oversold = (screener
            .filter_by_recent_additions(n=50)
            .filter_by_rsi(n=10, rsi_period=14)
            .get_results())

# Filter RSI < 30
if 'RSI' in oversold.columns:
    oversold_filtered = oversold[oversold['RSI'] < 30]
    print(oversold_filtered[['Symbol', 'Security', 'RSI', 'Close']])
else:
    print("No RSI data available")

# Use Case 2: High market cap stocks from specific sector
print("\n5.2 Top 5 Financials by market cap:")
financials = (screener
              .reset_filters()
              .filter_by_market_cap(n=5, sector='Financials')
              .get_results())
print(financials[['Symbol', 'Security', 'Market Cap Text']])

# Use Case 3: Recent tech IPOs
print("\n5.3 Most recent 10 technology additions:")
recent_tech = (screener
               .reset_filters()
               .filter_by_sector_and_recent('Information Technology', n=10)
               .get_results())
print(recent_tech[['Symbol', 'Security', 'Date added', 'GICS Sub-Industry']])

# ============================================================================
# EXAMPLE 6: Integration with Other TradingSuite Features
# ============================================================================

print("\n" + "=" * 80)
print("EXAMPLE 6: Integration with TradingSuite")
print("=" * 80)

# Get filtered tickers
screener = SP500Screener(auto_load=True)
tickers = screener.filter_by_recent_additions(n=5).get_tickers()

print(f"\n6.1 Analyzing {len(tickers)} tickers with MarketData:")
print(f"Tickers: {tickers}")

# Example: Analyze with MarketData (uncomment to use)
"""
from tradingsuite.data.market_data import MarketData

for ticker in tickers[:3]:  # Analyze first 3 for demo
    print(f"\nAnalyzing {ticker}...")
    md = MarketData(ticker=ticker, range='1y', interval='1d')
    latest = md.df.tail(1)
    print(f"  Close: ${latest['close'].values[0]:.2f}")
    print(f"  RSI: {latest['rsi'].values[0]:.2f}")
    print(f"  SMA200: ${latest['sma_200'].values[0]:.2f}")
"""

print("\n" + "=" * 80)
print("Examples completed!")
print("=" * 80)

# ============================================================================
# TIPS FOR GOOGLE COLAB
# ============================================================================
"""
TIPS:
1. To display DataFrames nicely in Colab, use:
   from IPython.display import display
   display(df)

2. To save results:
   df.to_csv('/content/results.csv', index=False)

3. To download results from Colab:
   from google.colab import files
   files.download('/content/results.csv')

4. For large scale RSI calculations, consider:
   - Reducing the number of tickers first
   - Using shorter time ranges (range='3mo' instead of '1y')
   - Processing in batches

5. Available sectors for filtering:
   - Information Technology
   - Health Care
   - Financials
   - Consumer Discretionary
   - Communication Services
   - Industrials
   - Consumer Staples
   - Energy
   - Utilities
   - Real Estate
   - Materials
"""
