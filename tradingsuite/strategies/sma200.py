from IPython.display import display
import numpy as np
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# Import the required modules
try:
    # When used as a package
    from ..data.market_data import MarketData
    from ..analysis.backtest import Backtest
except ImportError:
    # When used as standalone
    from tradingsuite.data.market_data import MarketData
    from tradingsuite.analysis.backtest import Backtest


def sma200_strategy(data, 
                    rsi_period=14,
                    rsi_threshold=65,
                    sma_long=200,
                    sma_short=50,
                    slope_period=10,
                    breakout_period=20,
                    atr_period=14,
                    atr_multiplier_body=1.0,
                    atr_multiplier_stop=2.0,
                    atr_multiplier_trail=2.0,
                    max_rise_period=20,
                    max_rise_percent=15.0):
    """
    Conservative trend-following strategy with RSI filter and breakout confirmation
    
    Parameters:
    - data: pandas DataFrame with columns: date, open, high, low, close, volume
    - rsi_period: int, default 14, RSI calculation period
    - rsi_threshold: float, default 65, maximum RSI for entry (filter overbought)
    - sma_long: int, default 200, long-term SMA period for trend filter
    - sma_short: int, default 50, short-term SMA period for exit
    - slope_period: int, default 10, period to check SMA200 slope
    - breakout_period: int, default 20, period for high breakout
    - atr_period: int, default 14, ATR calculation period
    - atr_multiplier_body: float, default 1.0, minimum candle body size in ATR units
    - atr_multiplier_stop: float, default 2.0, stop loss distance in ATR units
    - atr_multiplier_trail: float, default 2.0, trailing stop distance in ATR units
    - max_rise_period: int, default 20, period to check for parabolic move
    - max_rise_percent: float, default 15.0, maximum rise % to avoid parabolic moves
    """
    
    # Create a copy to avoid modifying original data
    df = data.copy()
    
    # Calculate required indicators if not present
    if 'rsi' not in df.columns:
        df['rsi'] = ta.rsi(df['close'], length=rsi_period)
    
    if f'sma_{sma_long}' not in df.columns:
        df[f'sma_{sma_long}'] = ta.sma(df['close'], length=sma_long)
    
    if f'sma_{sma_short}' not in df.columns:
        df[f'sma_{sma_short}'] = ta.sma(df['close'], length=sma_short)
    
    # Calculate ATR
    df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=atr_period)
    
    # Calculate rolling high for breakout detection
    df['rolling_high'] = df['high'].shift(1).rolling(window=breakout_period).max()
    
    # Calculate SMA200 slope
    df['sma_long_slope'] = df[f'sma_{sma_long}'] > df[f'sma_{sma_long}'].shift(slope_period)
    
    # Calculate price rise over max_rise_period
    df['price_rise_pct'] = ((df['close'] / df['close'].shift(max_rise_period)) - 1) * 100
    
    # Calculate candle body size
    df['body_size'] = abs(df['close'] - df['open'])
    
    # Trading logic
    in_trade = False
    trade_id = 1
    all_trades = []
    temp_trade = {}
    trailing_stop = 0
    highest_price = 0
    
    for i in range(max(sma_long, breakout_period, max_rise_period) + 1, len(df)):
        
        if not in_trade:
            # Entry conditions
            # 1. RSI filter: RSI < threshold
            rsi_ok = df['rsi'].iloc[i] < rsi_threshold
            
            # 2. Trend filter: Close > SMA200 and SMA200 slope positive
            trend_ok = (df['close'].iloc[i] > df[f'sma_{sma_long}'].iloc[i] and 
                       df['sma_long_slope'].iloc[i])
            
            # 3. Breakout trigger: Close > 20-day high
            breakout_ok = df['close'].iloc[i] > df['rolling_high'].iloc[i]
            
            # 4. ATR body size: candle body >= 1 * ATR
            body_ok = df['body_size'].iloc[i] >= (atr_multiplier_body * df['atr'].iloc[i])
            
            # 5. Parabolic move filter: not risen more than max_rise_percent in last max_rise_period days
            not_parabolic = df['price_rise_pct'].iloc[i] <= max_rise_percent
            
            # 6. Doji/long wick filter
            candle_range = df['high'].iloc[i] - df['low'].iloc[i]
            body = df['body_size'].iloc[i]
            upper_wick = df['high'].iloc[i] - max(df['open'].iloc[i], df['close'].iloc[i])
            
            # Avoid doji (body < 10% of range) and long upper wick (wick > 2x body)
            not_doji = body >= (0.1 * candle_range) if candle_range > 0 else False
            not_long_wick = upper_wick <= (2 * body) if body > 0 else True
            candle_ok = not_doji and not_long_wick
            
            # ALL CONDITIONS MUST BE TRUE
            if (rsi_ok and trend_ok and breakout_ok and body_ok and 
                not_parabolic and candle_ok and 
                pd.notna(df['atr'].iloc[i])):
                
                # Enter trade at next bar's open
                if i == (len(df) - 1):
                    entry_price = df['close'].iloc[i]
                    entry_data = df.iloc[i]
                else:
                    entry_price = df['open'].iloc[i+1]
                    entry_data = df.iloc[i+1]
                
                temp_trade['buy_price'] = entry_price
                temp_trade.update(dict(entry_data.add_prefix('buy_')))
                temp_trade['trade_id'] = trade_id
                temp_trade['status'] = 'open'
                
                # Calculate stop loss: entry candle low - 2*ATR
                entry_low = df['low'].iloc[i]
                stop_distance = atr_multiplier_stop * df['atr'].iloc[i]
                temp_trade['stop_loss'] = entry_low - stop_distance
                
                # Initialize trailing stop and highest price
                trailing_stop = temp_trade['stop_loss']
                highest_price = entry_price
                
                in_trade = True
        
        else:
            # Exit conditions
            current_price = df['close'].iloc[i]
            
            # Update highest price and trailing stop
            if current_price > highest_price:
                highest_price = current_price
                new_trailing_stop = highest_price - (atr_multiplier_trail * df['atr'].iloc[i])
                trailing_stop = max(trailing_stop, new_trailing_stop)
            
            # Exit condition 1: Trailing stop hit
            stop_hit = df['low'].iloc[i] <= trailing_stop
            
            # Exit condition 2: Close below SMA50
            below_sma50 = df['close'].iloc[i] < df[f'sma_{sma_short}'].iloc[i]
            
            if stop_hit or below_sma50:
                # Exit trade
                if i == (len(df) - 1):
                    exit_price = df['close'].iloc[i]
                    exit_data = df.iloc[i]
                else:
                    exit_price = df['open'].iloc[i+1]
                    exit_data = df.iloc[i+1]
                
                temp_trade['sell_price'] = exit_price
                temp_trade.update(dict(exit_data.add_prefix('sell_')))
                temp_trade['trade_id'] = trade_id
                temp_trade['status'] = 'closed'
                temp_trade['exit_reason'] = 'trailing_stop' if stop_hit else 'below_sma50'
                
                # Calculate results
                temp_trade['result'] = temp_trade['sell_price'] / temp_trade['buy_price']
                temp_trade['days_in_trade'] = (temp_trade['sell_date'] - temp_trade['buy_date']).days
                
                in_trade = False
                trade_id += 1
                all_trades.append(temp_trade)
                temp_trade = {}
                trailing_stop = 0
                highest_price = 0
    
    # Close any open trade at the end
    if temp_trade:
        temp_trade['sell_price'] = df['close'].iloc[-1]
        temp_trade['trade_id'] = trade_id
        temp_trade['sell_date'] = df['date'].iloc[-1]
        temp_trade['exit_reason'] = 'end_of_data'
        
        temp_trade['result'] = temp_trade['sell_price'] / temp_trade['buy_price']
        temp_trade['days_in_trade'] = (temp_trade['sell_date'] - temp_trade['buy_date']).days
        all_trades.append(temp_trade)
    
    # Create results DataFrame
    if not all_trades:
        # Return empty DataFrame with expected columns
        return pd.DataFrame(columns=['result', 'buy_price', 'sell_price', 'buy_date', 
                                    'sell_date', 'days_in_trade', 'trade_id', 'status'])
    
    res_df = pd.DataFrame(all_trades)
    
    # Reorder columns
    all_col = res_df.columns.tolist()
    first = ['result', 'buy_price', 'sell_price', 'buy_date', 'sell_date', 
             'days_in_trade', 'exit_reason', 'stop_loss']
    first.extend([x for x in all_col if x not in first])
    res_df = res_df[first]
    
    return res_df


def show_indicator_sma200_strategy(ticker, 
                                   rsi_period=14,
                                   rsi_threshold=65,
                                   sma_long=200,
                                   sma_short=50,
                                   slope_period=10,
                                   breakout_period=20,
                                   atr_period=14,
                                   atr_multiplier_body=1.0,
                                   atr_multiplier_stop=2.0,
                                   atr_multiplier_trail=2.0,
                                   max_rise_period=20,
                                   max_rise_percent=15.0,
                                   plot_title='',
                                   ndays=0,
                                   plot_height=1200,
                                   add_strategy_summary=True,
                                   use_tradingview_title=False):
    """
    Show SMA200 strategy result in one plot: candlestick chart, SMA lines, trades, 
    RSI indicator, ATR indicator, summary of the strategy on the left side of the plot
    
    Parameters:
    - ticker: str, ticker symbol
    - rsi_period: int, default 14, RSI calculation period
    - rsi_threshold: float, default 65, maximum RSI for entry
    - sma_long: int, default 200, long-term SMA period
    - sma_short: int, default 50, short-term SMA period
    - slope_period: int, default 10, period to check SMA200 slope
    - breakout_period: int, default 20, period for high breakout
    - atr_period: int, default 14, ATR calculation period
    - atr_multiplier_body: float, default 1.0, minimum candle body size in ATR units
    - atr_multiplier_stop: float, default 2.0, stop loss distance in ATR units
    - atr_multiplier_trail: float, default 2.0, trailing stop distance in ATR units
    - max_rise_period: int, default 20, period to check for parabolic move
    - max_rise_percent: float, default 15.0, maximum rise % to avoid parabolic moves
    - plot_title: str, default '', title of the plot
    - ndays: int, default 0, number of days to show, if 0, show all data
    - plot_height: int, default 1200, height of the plot
    - add_strategy_summary: bool, default True, add strategy summary to the plot
    - use_tradingview_title: bool, default False, use TradingViewData to get a formatted title
    """
    
    # Load data
    stock_data = StockData(ticker)
    tdf = stock_data.df
    
    # Run backtest
    backtest = Backtest(
        tdf, 
        sma200_strategy,
        rsi_period=rsi_period,
        rsi_threshold=rsi_threshold,
        sma_long=sma_long,
        sma_short=sma_short,
        slope_period=slope_period,
        breakout_period=breakout_period,
        atr_period=atr_period,
        atr_multiplier_body=atr_multiplier_body,
        atr_multiplier_stop=atr_multiplier_stop,
        atr_multiplier_trail=atr_multiplier_trail,
        max_rise_period=max_rise_period,
        max_rise_percent=max_rise_percent
    )
    trades = backtest.trades

    if 'atr' not in tdf.columns:
        tdf['atr'] = ta.atr(tdf['high'], tdf['low'], tdf['close'], length=atr_period)
                                       
    # Filter data for display
    if ndays > 0:
        tdf = tdf.tail(ndays)
        trades = trades.loc[trades['buy_date'] > tdf.date.min()] if not trades.empty else trades
    
    # Determine text location for summary
    if tdf['high'].max() == max(tdf['high'][0:50]):
        tex_loc = [0.1, 0.2]
    else:
        tex_loc = [0.1, 0.85]
    
    # Get plot title
    if use_tradingview_title and plot_title == '':
        try:
            from tradingview_data import TradingViewData
            tv_data = TradingViewData(auto_load=False)
            plot_title = tv_data.get_plotly_title(ticker)
        except:
            plot_title = f'{ticker} - SMA200 Strategy'
    elif plot_title == '':
        plot_title = f'{ticker} - SMA200 Strategy'
    
    # Create subplots with shared x-axis and custom heights
    fig = make_subplots(
        rows=3, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.05, 
        subplot_titles=['', 'RSI', 'ATR'],
        row_heights=[0.6, 0.2, 0.2]
    )
    
    # Add OHLC candlestick chart
    fig.add_trace(
        go.Ohlc(x=tdf['date'], open=tdf['open'], high=tdf['high'], 
                low=tdf['low'], close=tdf['close']), 
        row=1, col=1
    )
    
    # Add SMA lines
    fig.add_trace(
        go.Scatter(x=tdf['date'], y=tdf[f'sma_{sma_short}'], 
                  opacity=0.5, line=dict(color='lightblue', width=2), 
                  name=f'SMA {sma_short}'), 
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=tdf['date'], y=tdf[f'sma_{sma_long}'], 
                  opacity=0.7, line=dict(color='red', width=2.5), 
                  name=f'SMA {sma_long}'), 
        row=1, col=1
    )
    
    # Add trade points and annotations
    if not trades.empty:
        for index, row in trades.iterrows():
            buy_date = row['buy_date']
            sell_date = row['sell_date']
            buy_price = row['buy_price']
            sell_price = row['sell_price']
            trade_id = row['trade_id']
            status = row['status']
            triangle_color = 'green' if row['result'] > 1 else 'red'
            
            rise = (row['result'] - 1) * 100
            
            if rise > 100:
                if status == 'closed':
                    result = f'Up:{round(((rise + 100) / 100), 2)}x'
                else:
                    result = f'Up:{round(((rise + 100) / 100), 2)}x <br> Still open'
            else:
                if status == 'closed':
                    result = f"{round(((row['result'] - 1) * 100), 2)}%"
                else:
                    result = f"{round(((row['result'] - 1) * 100), 2)}% <br> Still open"
            
            # Add buy marker
            buy_point = (buy_date, buy_price)
            triangle_trace = go.Scatter(
                x=[buy_point[0]], y=[buy_point[1]], mode='markers',
                marker=dict(symbol='triangle-up', size=16, color=triangle_color)
            )
            fig.add_trace(triangle_trace, row=1, col=1)
            fig.add_annotation(
                x=buy_date, y=buy_price, 
                text=f"Buy: ${round(buy_price, 2)}<br>#{trade_id}",
                showarrow=True, align="center", bordercolor="#c7c7c7",
                font=dict(family="Courier New, monospace", size=12, color=triangle_color),
                borderwidth=2, borderpad=4, bgcolor="#f4fdff", opacity=0.8,
                arrowhead=2, arrowsize=1, arrowwidth=1, ax=30, ay=30,
                hovertext=f"Buy: ${round(buy_price, 2)}",
                row=1, col=1
            )
            
            # Add sell marker
            sell_point = (sell_date, sell_price)
            triangle_trace = go.Scatter(
                x=[sell_point[0]], y=[sell_point[1]], mode='markers',
                marker=dict(symbol='triangle-down', size=16, color=triangle_color)
            )
            fig.add_trace(triangle_trace, row=1, col=1)
            
            exit_reason = row.get('exit_reason', 'unknown')
            fig.add_annotation(
                x=sell_date, y=sell_price,
                text=f"Sell: ${round(sell_price, 2)}<br>#{trade_id}, {result}<br>{exit_reason}",
                showarrow=True, align="center", bordercolor="#c7c7c7",
                font=dict(family="Courier New, monospace", size=12, color=triangle_color),
                borderwidth=2, borderpad=4, bgcolor="#f4fdff", opacity=0.8,
                arrowhead=2, arrowsize=1, arrowwidth=1, ax=-30, ay=-30,
                hovertext=f"Sell: ${round(sell_price, 2)}<br>#{trade_id}, {result}",
                row=1, col=1
            )
            
            # Add rectangle showing trade duration
            fig.add_shape(
                type="rect", x0=buy_point[0], y0=buy_point[1], 
                x1=sell_point[0], y1=sell_point[1],
                line=dict(color=triangle_color, width=2),
                fillcolor="LightSkyBlue", opacity=0.3,
                label=dict(
                    text=f"{result}<br>{row['days_in_trade']} days",
                    textposition="bottom center",
                    font=dict(size=13, color=triangle_color, family="Times New Roman")
                ),
                row=1, col=1
            )
            
            # Add stop loss line
            if 'stop_loss' in row:
                fig.add_shape(
                    type="line",
                    x0=buy_date, x1=sell_date,
                    y0=row['stop_loss'], y1=row['stop_loss'],
                    line=dict(color="red", width=1, dash="dot"),
                    row=1, col=1
                )
    
    # Update layout
    fig.update_layout(
        showlegend=False, 
        plot_bgcolor='white', 
        height=plot_height, 
        title=plot_title
    )
    fig.update(layout_xaxis_rangeslider_visible=False)
    
    # Update x-axes and y-axes for all subplots
    for i in range(1, 4):
        fig.update_xaxes(
            mirror=True, ticks='outside', showline=True, 
            linecolor='black', gridcolor='lightgrey', row=i, col=1
        )
        fig.update_yaxes(
            mirror=True, ticks='outside', showline=True, 
            linecolor='black', gridcolor='lightgrey', row=i, col=1
        )
    
    # Add strategy summary
    if add_strategy_summary and not trades.empty:
        fig.add_annotation(
            go.layout.Annotation(
                x=tex_loc[0], y=tex_loc[1], xref='paper', yref='paper',
                text=backtest.trade_summary_plot_text,
                showarrow=True, arrowhead=4, ax=0, ay=0,
                bordercolor='black', borderwidth=2, bgcolor='white',
                align='left', font=dict(size=14, color='black')
            )
        )
    
    # Add RSI line
    if 'rsi' in tdf.columns:
        fig.add_trace(
            go.Scatter(x=tdf['date'], y=tdf['rsi'], 
                      line=dict(color='green', width=2), name='RSI'),
            row=2, col=1
        )
        # Add RSI threshold line
        fig.add_shape(
            type="line", 
            x0=tdf['date'].min(), x1=tdf['date'].max(),
            y0=rsi_threshold, y1=rsi_threshold,
            line=dict(color="red", width=2, dash="dash"),
            row=2, col=1
        )
        # Add RSI 30 and 70 lines
        fig.add_shape(
            type="line",
            x0=tdf['date'].min(), x1=tdf['date'].max(),
            y0=30, y1=30,
            line=dict(color="gray", width=1, dash="dash"),
            row=2, col=1
        )
        fig.add_shape(
            type="line",
            x0=tdf['date'].min(), x1=tdf['date'].max(),
            y0=70, y1=70,
            line=dict(color="gray", width=1, dash="dash"),
            row=2, col=1
        )
    
    # Add ATR line
    if 'atr' in tdf.columns:
        # Clean ATR data - remove NaN values
        atr_clean = tdf[['date', 'atr']].dropna()
        
        # Debug info
        print(f"\n🔍 ATR DEBUG INFO:")
        print(f"   Total rows in tdf: {len(tdf)}")
        print(f"   Rows with ATR data: {len(atr_clean)}")
        
        if len(atr_clean) > 0:
            fig.add_trace(
                go.Scatter(x=tdf['date'], y=tdf['atr'],
                          line=dict(color='purple', width=2), name='ATR'),
                row=3, col=1
            )
        
        # Set y-axis range for ATR to ensure visibility
        atr_values = tdf['atr'].dropna()
        if len(atr_values) > 0:
            atr_min = atr_values.min()
            atr_max = atr_values.max()
            atr_padding = (atr_max - atr_min) * 0.1  # 10% padding
            fig.update_yaxes(
                range=[max(0, atr_min - atr_padding), atr_max + atr_padding],
                title_text="ATR",
                row=3, col=1
            )
    
    # Add y-axis titles for other subplots
    fig.update_yaxes(title_text="Price", title_standoff=5, row=1, col=1)
    fig.update_yaxes(title_text="RSI", title_standoff=5, row=2, col=1)                                   
    
    return fig

# Test examples:
# show_indicator_sma200_strategy('TSLA')
# show_indicator_sma200_strategy('AAPL', use_tradingview_title=True)
# show_indicator_sma200_strategy('NVDA', ndays=500, rsi_threshold=70)
