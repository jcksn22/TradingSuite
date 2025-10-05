"""
Basic usage example for TradingSuite package
"""

# Import the package
from tradingsuite import TradingViewData, MarketData, Backtest
from tradingsuite.strategies import rsi_strategy

def main():
    """Main example function"""
    
    # 1. Get TradingView data
    print("Loading TradingView data...")
    tv_data = TradingViewData(auto_load=False)
    tv_data.get_us_stocks()
    print(f"Loaded {len(tv_data.us_stock)} US stocks")
    
    # 2. Get stock price data
    print("\nGetting Tesla stock data...")
    tesla = MarketData('TSLA')
    print(f"Loaded {len(tesla.df)} days of TSLA data")
    
    # 3. Run backtest
    print("\nRunning RSI strategy backtest...")
    backtest = Backtest(tesla.df, rsi_strategy, buy_threshold=30, sell_threshold=70)
    
    # 4. Show results
    print("\nBacktest Results:")
    print(f"Number of trades: {backtest.trades_summary['number_of_trades']}")
    print(f"Win ratio: {backtest.trades_summary['win_ratio(%)']}%")
    print(f"Average result: {backtest.trades_summary['average_res(%)']}%")
    print(f"Cumulative result: {backtest.trades_summary['cumulative_result']}")
    
    # 5. Display chart (if in Jupyter/Colab)
    try:
        fig = backtest.show_trades()
        fig.show()
    except:
        print("Charts can be displayed in Jupyter/Colab environments")

if __name__ == "__main__":
    main()
