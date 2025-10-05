"""
Advanced example: Analyzing multiple stocks with RSI strategy
"""

from tradingsuite import TradingViewData, MarketData, Backtest
from tradingsuite.strategies import rsi_strategy, smma_ribbon_strategy
import pandas as pd
from tqdm import tqdm

def analyze_top_stocks():
    """Analyze top stocks from a sector"""
    
    # 1. Load TradingView data
    print("Loading TradingView data...")
    tv_data = TradingViewData(auto_load=False)
    tv_data.get_us_stocks()
    
    # 2. Get top tech stocks
    tech_stocks = tv_data.get_top_n_us_stocks_by_sector(percent=5)
    tech_stocks = tech_stocks[tech_stocks['sector'] == 'Electronic Technology'].head(10)
    
    print(f"\nAnalyzing {len(tech_stocks)} top tech stocks...")
    
    # 3. Run backtest for each stock
    results = []
    for ticker in tqdm(tech_stocks['name']):
        try:
            # Get stock data
            stock = MarketData(ticker)
            
            # Run RSI strategy
            backtest = Backtest(stock.df, rsi_strategy, 
                              buy_threshold=30, sell_threshold=70)
            
            # Store results
            results.append({
                'ticker': ticker,
                'trades': backtest.trades_summary['number_of_trades'],
                'win_ratio': backtest.trades_summary['win_ratio(%)'],
                'avg_result': backtest.trades_summary['average_res(%)'],
                'cumulative': backtest.trades_summary['cumulative_result']
            })
        except Exception as e:
            print(f"Error with {ticker}: {e}")
            continue
    
    # 4. Create results DataFrame
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('avg_result', ascending=False)
    
    # 5. Display results
    print("\nTop Performers (by average result):")
    print(results_df.head())
    
    return results_df

def compare_strategies(ticker='AAPL'):
    """Compare different strategies on the same stock"""
    
    print(f"\nComparing strategies for {ticker}...")
    
    # Get stock data
    stock = MarketData(ticker)
    
    # Strategy 1: RSI
    rsi_backtest = Backtest(stock.df, rsi_strategy,
                            buy_threshold=30, sell_threshold=70)
    
    # Strategy 2: SMMA Ribbon
    smma_backtest = Backtest(stock.df, smma_ribbon_strategy,
                             buy_at='gold', sell_at='grey')
    
    # Compare results
    comparison = pd.DataFrame({
        'Strategy': ['RSI', 'SMMA Ribbon'],
        'Trades': [
            rsi_backtest.trades_summary['number_of_trades'],
            smma_backtest.trades_summary['number_of_trades']
        ],
        'Win Ratio': [
            rsi_backtest.trades_summary['win_ratio(%)'],
            smma_backtest.trades_summary['win_ratio(%)']
        ],
        'Avg Result': [
            rsi_backtest.trades_summary['average_res(%)'],
            smma_backtest.trades_summary['average_res(%)']
        ],
        'Cumulative': [
            rsi_backtest.trades_summary['cumulative_result'],
            smma_backtest.trades_summary['cumulative_result']
        ]
    })
    
    print(comparison)
    return comparison

if __name__ == "__main__":
    # Run analysis
    results = analyze_top_stocks()
    
    # Compare strategies
    comparison = compare_strategies('MSFT')
