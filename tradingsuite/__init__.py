"""
TradingSuite - Trading analysis and backtest package
"""

__version__ = "1.0.0"

from .data.tradingview_data import TradingViewData
from .data.market_data import MarketData
from .analysis.backtest import Backtest

__all__ = ['TradingViewData', 'MarketData', 'Backtest']
