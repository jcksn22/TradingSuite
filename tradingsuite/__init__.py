"""
TradingSuite - Trading analysis and backtest package
"""

__version__ = "1.0.0"

from .data.tradingview_data import TradingViewData
from .data.stocks import StockData
from .analysis.backtest import Backtest

__all__ = ['TradingViewData', 'StockData', 'Backtest']
