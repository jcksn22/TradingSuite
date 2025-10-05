# TradingSuite Documentation

## Package Structure

```
tradingsuite/
├── data/                    # Data acquisition modules
│   ├── tradingview_data.py  # TradingView API wrapper
│   └── market_data.py       # Yahoo Finance data fetcher
├── strategies/              # Trading strategies
│   ├── rsi.py               # RSI-based strategy
│   └── smma_ribbon.py       # SMMA Ribbon strategy
├── analysis/                # Analysis tools
│   └── backtest.py          # Backtesting framework
└── utils/                   # Utility functions
    └── helpers.py           # Helper functions
```

## Installation

### From GitHub
```bash
git clone https://github.com/yourusername/TradingSuite.git
cd TradingSuite
pip install -e .
```

### Dependencies
```bash
pip install -r requirements.txt
```

## Usage Guide

### 1. Loading Market Data from TradingView

```python
from tradingsuite import TradingViewData

# Initialize TradingView data handler
tv_data = TradingViewData(auto_load=False)

# Load US stocks
tv_data.get_us_stocks()
print(f"Loaded {len(tv_data.us_stock)} US stocks")

# Load European stocks
tv_data.get_eu_stocks()
print(f"Loaded {len(tv_data.eu_stock)} EU stocks")

# Load ETFs
tv_data.get_us_etfs()
print(f"Loaded {len(tv_data.us_etf)} ETFs")

# Load crypto data
tv_data.get_all_crypto()
print(f"Loaded {len(tv_data.crypto)} cryptocurrencies")
```

### 2. Getting Individual Market Data

```python
from tradingsuite import MarketData

# Get historical data for a stock
apple = MarketData('AAPL')
print(f"Loaded {len(apple.df)} days of data")

# The DataFrame includes:
# - OHLC prices
# - Volume
# - Technical indicators (RSI, SMA, Bollinger Bands)
# - Local min/max points
```

### 3. Running Backtests

```python
from tradingsuite import Backtest
from tradingsuite.strategies import rsi_strategy

# Run RSI strategy backtest
backtest = Backtest(
    apple.df,
    rsi_strategy,
    buy_threshold=30,
    sell_threshold=70
)

# View results
print(backtest.trades_summary)
backtest.show_trades()  # Display chart
```

### 4. Strategy Comparison

```python
from tradingsuite.strategies import rsi_strategy, smma_ribbon_strategy

# Compare strategies on same stock
stock = MarketData('MSFT')

# RSI Strategy
rsi_bt = Backtest(stock.df, rsi_strategy, buy_threshold=30, sell_threshold=70)

# SMMA Ribbon Strategy  
smma_bt = Backtest(stock.df, smma_ribbon_strategy, buy_at='gold', sell_at='grey')

# Compare results
print(f"RSI: {rsi_bt.trades_summary['cumulative_result']}")
print(f"SMMA: {smma_bt.trades_summary['cumulative_result']}")
```

## Available Strategies

### RSI Strategy
- Buys when RSI < buy_threshold (default: 30)
- Sells when RSI > sell_threshold (default: 70)

### SMMA Ribbon Strategy
- Uses 4 SMMA lines (15, 19, 25, 29 periods)
- Buys on golden cross pattern
- Sells on death cross pattern

## API Reference

### TradingViewData Class

#### Methods:
- `get_us_stocks()` - Load US stock data
- `get_eu_stocks(markets=['uk', 'germany', 'poland'])` - Load European stocks
- `get_us_etfs()` - Load US ETF data
- `get_all_crypto()` - Load cryptocurrency data
- `get_one_us_stock_info(ticker)` - Get detailed info for a US stock
- `get_one_eu_stock_info(ticker)` - Get detailed info for an EU stock
- `get_top_n_us_stocks_by_sector(percent)` - Get top stocks by sector

### MarketData Class

#### Methods:
- `__init__(ticker, range='18y', interval='1d')` - Initialize with ticker
- `plotly_last_year(plot_title, ndays=500)` - Plot price chart
- `plot_smma_ribbon(plot_title, ndays=800)` - Plot with SMMA ribbon

### Backtest Class

#### Methods:
- `__init__(data, strategy_function, **kwargs)` - Initialize backtest
- `show_trades()` - Display trades on chart
- `summarize_strategy()` - Display complete summary

## Examples

See the `examples/` directory for complete working examples:
- `basic_usage.py` - Simple getting started example
- `advanced_analysis.py` - Multi-stock analysis and strategy comparison
- `colab_demo.py` - Google Colab notebook example

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details
