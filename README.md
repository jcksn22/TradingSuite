# 📈 TradingSuite

> **Professional Trading Strategy Backtesting Framework in Python**

TradingSuite is a comprehensive Python package for downloading, analyzing, and backtesting trading strategies on stocks, ETFs, and cryptocurrencies with TradingView data integration.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## ✨ Features

### 📊 Data Acquisition
- **US Stocks**: Download American stock data from Yahoo Finance
- **European Stocks**: Access UK, German, and Polish markets
- **ETFs**: US ETF data with sector/industry filtering
- **Cryptocurrencies**: Major crypto pairs data
- **Historical Data**: Up to 18 years of daily OHLCV data

### 🎯 Trading Strategies

#### Built-in Strategies
1. **RSI Strategy** - Classic RSI-based mean reversion
2. **SMMA Ribbon Strategy** - Trend-following with smoothed moving averages
3. **SMA200 Strategy** ⭐ NEW - Conservative trend-following with RSI filter
   - Long-term trend confirmation (SMA200)
   - RSI overbought filter
   - Breakout confirmation
   - ATR-based volatility-adaptive stops
   - Trailing stop and SMA50 exit

### 📈 Analysis & Visualization
- **Backtest Framework**: Comprehensive backtesting engine
- **Interactive Charts**: Plotly-based visualizations
- **Trade Analysis**: Win ratio, returns, drawdowns
- **Technical Indicators**: RSI, SMA, ATR, Bollinger Bands, and more

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/TradingSuite.git
cd TradingSuite

# Install dependencies
pip install -r requirements.txt

# Install package (editable mode)
pip install -e .
```

### Basic Usage

```python
from tradingsuite.data.stocks import StockData
from tradingsuite.analysis.backtest import Backtest
from tradingsuite.strategies import sma200_strategy

# Download stock data
stock = StockData('AAPL')

# Run backtest
backtest = Backtest(stock.df, sma200_strategy)

# View results
backtest.summarize_strategy()
```

### Visualization

```python
from tradingsuite.strategies.sma200 import show_indicator_sma200_strategy

# Create interactive chart
fig = show_indicator_sma200_strategy('AAPL', ndays=500)
fig.show()
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [SMA200 Strategy Guide](docs/SMA200_STRATEGY.md) | Complete SMA200 strategy documentation |
| [Examples](examples/) | Usage examples and demos |
| [API Reference](docs/API.md) | Detailed API documentation |
| [CHANGELOG](CHANGELOG.md) | Version history and updates |

---

## 🎓 Examples

### 1. Simple Backtest
```python
from tradingsuite.data.stocks import StockData
from tradingsuite.analysis.backtest import Backtest
from tradingsuite.strategies import rsi_strategy

stock = StockData('TSLA')
backtest = Backtest(stock.df, rsi_strategy, buy_threshold=30, sell_threshold=70)
print(backtest.trades_summary)
```

### 2. Custom Parameters
```python
from tradingsuite.strategies import sma200_strategy

backtest = Backtest(
    stock.df, 
    sma200_strategy,
    rsi_threshold=60,         # More conservative
    atr_multiplier_stop=2.5,  # Wider stop
    max_rise_percent=12.0     # Stricter parabolic filter
)
```

### 3. Multiple Tickers
```python
tickers = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA']
results = []

for ticker in tickers:
    stock = StockData(ticker)
    backtest = Backtest(stock.df, sma200_strategy)
    results.append({
        'ticker': ticker,
        'trades': backtest.trades_summary['number_of_trades'],
        'win_ratio': backtest.trades_summary['win_ratio(%)'],
        'avg_result': backtest.trades_summary['average_res(%)']
    })

import pandas as pd
df_results = pd.DataFrame(results)
print(df_results.sort_values('avg_result', ascending=False))
```

More examples in [`examples/`](examples/) directory.

---

## 📦 Package Structure

```
TradingSuite/
├── tradingsuite/
│   ├── analysis/          # Backtesting framework
│   ├── data/              # Data acquisition modules
│   ├── strategies/        # Trading strategies
│   │   ├── rsi.py
│   │   ├── smma_ribbon.py
│   │   └── sma200.py     ⭐ NEW
│   └── utils/            # Helper functions
├── examples/             # Usage examples
├── tests/               # Unit tests
├── docs/                # Documentation
└── notebooks/           # Jupyter notebooks
```

---

## 🔧 Configuration

### Requirements

- Python 3.8+
- pandas >= 1.3.0
- numpy >= 1.19.0
- plotly >= 5.0.0
- scipy >= 1.7.0
- pandas-ta >= 0.3.14b0
- requests >= 2.26.0
- cloudscraper >= 1.2.58
- IPython >= 7.0.0

Install all dependencies:
```bash
pip install -r requirements.txt
```

---

## 🧪 Testing

Run unit tests:

```bash
# All tests
python -m pytest tests/

# Specific test
python tests/test_sma200_unit.py
```

---

## 🌐 Google Colab

### Installation in Colab

```python
# Install dependencies
!pip install pandas numpy plotly scipy requests cloudscraper pandas-ta IPython

# Clone repository
!git clone https://github.com/yourusername/TradingSuite.git

# Add to path
import sys
sys.path.insert(0, '/content/TradingSuite')

# Import and use
from tradingsuite.data.stocks import StockData
from tradingsuite.strategies import sma200_strategy
```

See [`examples/colab_demo.py`](examples/colab_demo.py) for complete Colab demo.

---

## 📊 Strategy Performance

### SMA200 Strategy Example Results

```
Ticker: AAPL
Trades: 8
Win ratio: 75.0%
Average result: 12.5%
Cumulative result: 2.1x
Average trade length: 45 days
Hold result: 1.8x
```

*Note: Past performance is not indicative of future results.*

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

This software is for educational purposes only. Do not risk money which you are afraid to lose. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS.

Always practice risk management and never invest more than you can afford to lose.

---

## 🙏 Acknowledgments

- Yahoo Finance for historical data
- TradingView for market data
- pandas-ta for technical indicators
- Plotly for interactive visualizations

---

## 📧 Contact

For questions and support, please open an issue in the GitHub repository.

---

## 🗺️ Roadmap

- [ ] More built-in strategies
- [ ] Machine learning integration
- [ ] Real-time data support
- [ ] Portfolio optimization
- [ ] Risk management tools
- [ ] Multi-timeframe analysis

---

**Happy Trading! 📈🚀**
