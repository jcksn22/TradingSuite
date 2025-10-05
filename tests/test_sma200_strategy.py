"""
Quick test script for SMA200 Strategy
Run this to verify the strategy works correctly
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the tradingsuite to path
sys.path.insert(0, '/tmp/TradingSuite-main')

from tradingsuite.data.market_data import MarketData
from tradingsuite.analysis.backtest import Backtest
from tradingsuite.strategies.sma200 import sma200_strategy, show_indicator_sma200_strategy

def test_basic_functionality():
    """Test 1: Basic functionality with AAPL"""
    print("=" * 60)
    print("TEST 1: Basic Functionality Test (AAPL)")
    print("=" * 60)
    
    try:
        # Load data
        print("Loading AAPL data...")
        data = MarketData('AAPL')
        df = data.df
        print(f"✓ Data loaded: {len(df)} rows")
        
        # Run backtest
        print("Running backtest with default parameters...")
        backtest = Backtest(df, sma200_strategy)
        print(f"✓ Backtest completed")
        
        # Check results
        trades = backtest.trades
        print(f"✓ Trades generated: {len(trades)}")
        
        if len(trades) > 0:
            print(f"✓ First trade date: {trades['buy_date'].iloc[0]}")
            print(f"✓ Last trade date: {trades['sell_date'].iloc[-1]}")
            print(f"✓ Win ratio: {backtest.trades_summary['win_ratio(%)']}%")
            print(f"✓ Average result: {backtest.trades_summary['average_res(%)']}%")
            print(f"✓ Cumulative result: {backtest.trades_summary['cumulative_result']}")
        else:
            print("⚠ No trades generated (this might be expected with conservative parameters)")
        
        print("\n✓ TEST 1 PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ TEST 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_custom_parameters():
    """Test 2: Custom parameters"""
    print("\n" + "=" * 60)
    print("TEST 2: Custom Parameters Test")
    print("=" * 60)
    
    try:
        data = MarketData('MSFT')
        df = data.df
        print(f"✓ Data loaded: {len(df)} rows")
        
        # Run with custom parameters
        print("Running backtest with custom parameters...")
        backtest = Backtest(
            df,
            sma200_strategy,
            rsi_threshold=70,
            atr_multiplier_stop=2.5,
            max_rise_percent=20.0
        )
        print(f"✓ Backtest completed with custom params")
        
        trades = backtest.trades
        print(f"✓ Trades generated: {len(trades)}")
        
        if len(trades) > 0:
            # Check if exit_reason column exists
            if 'exit_reason' in trades.columns:
                exit_reasons = trades['exit_reason'].value_counts()
                print(f"✓ Exit reasons: {dict(exit_reasons)}")
            
            # Check if stop_loss column exists
            if 'stop_loss' in trades.columns:
                print(f"✓ Stop loss values calculated")
        
        print("\n✓ TEST 2 PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ TEST 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_visualization():
    """Test 3: Visualization function"""
    print("\n" + "=" * 60)
    print("TEST 3: Visualization Test")
    print("=" * 60)
    
    try:
        print("Generating visualization for NVDA...")
        fig = show_indicator_sma200_strategy(
            'NVDA',
            ndays=200,
            plot_height=1000,
            add_strategy_summary=True
        )
        print("✓ Visualization generated successfully")
        print(f"✓ Figure type: {type(fig)}")
        
        print("\n✓ TEST 3 PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ TEST 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_tickers():
    """Test 4: Multiple tickers"""
    print("\n" + "=" * 60)
    print("TEST 4: Multiple Tickers Test")
    print("=" * 60)
    
    tickers = ['AAPL', 'MSFT', 'GOOGL']
    results = []
    
    try:
        for ticker in tickers:
            print(f"Testing {ticker}...")
            data = MarketData(ticker)
            df = data.df
            backtest = Backtest(df, sma200_strategy)
            
            results.append({
                'ticker': ticker,
                'trades': len(backtest.trades),
                'win_ratio': backtest.trades_summary['win_ratio(%)'],
                'avg_result': backtest.trades_summary['average_res(%)']
            })
            print(f"  ✓ {ticker}: {len(backtest.trades)} trades")
        
        print("\n✓ All tickers processed")
        print("\nSummary:")
        for r in results:
            print(f"  {r['ticker']}: {r['trades']} trades, "
                  f"{r['win_ratio']}% win ratio, "
                  f"{r['avg_result']}% avg result")
        
        print("\n✓ TEST 4 PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ TEST 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_edge_cases():
    """Test 5: Edge cases"""
    print("\n" + "=" * 60)
    print("TEST 5: Edge Cases Test")
    print("=" * 60)
    
    try:
        # Test with very restrictive parameters (should produce few/no trades)
        print("Testing with very restrictive parameters...")
        data = MarketData('AAPL')
        df = data.df
        
        backtest = Backtest(
            df,
            sma200_strategy,
            rsi_threshold=30,  # Very restrictive
            max_rise_percent=5.0  # Very restrictive
        )
        
        print(f"✓ Restrictive params: {len(backtest.trades)} trades generated")
        
        # Test with very permissive parameters
        print("Testing with permissive parameters...")
        backtest = Backtest(
            df,
            sma200_strategy,
            rsi_threshold=85,  # Very permissive
            max_rise_percent=30.0  # Very permissive
        )
        
        print(f"✓ Permissive params: {len(backtest.trades)} trades generated")
        
        print("\n✓ TEST 5 PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ TEST 5 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("SMA200 STRATEGY - TEST SUITE")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    tests = [
        test_basic_functionality,
        test_custom_parameters,
        test_visualization,
        test_multiple_tickers,
        test_edge_cases
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total tests: {len(results)}")
    print(f"Passed: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("\n✓✓✓ ALL TESTS PASSED ✓✓✓")
    else:
        print("\n✗✗✗ SOME TESTS FAILED ✗✗✗")
    
    print(f"\nTest finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
