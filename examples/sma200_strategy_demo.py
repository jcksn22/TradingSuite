# SMA200 Strategy - Google Colab Demo
# Konzervatív trendkövető stratégia RSI szűréssel

# ============= TELEPÍTÉS =============
# Először telepítsd a TradingSuite csomagot
# !pip install git+https://github.com/your-repo/TradingSuite.git

# Vagy ha lokális fejlesztés:
# !pip install -e /path/to/TradingSuite

# ============= IMPORTOK =============
from tradingsuite.data.stocks import StockData
from tradingsuite.analysis.backtest import Backtest
from tradingsuite.strategies.sma200 import sma200_strategy, show_indicator_sma200_strategy
import pandas as pd
import numpy as np

# ============= PÉLDA 1: EGYSZERŰ BACKTEST =============
print("=" * 60)
print("PÉLDA 1: Alapértelmezett paraméterekkel")
print("=" * 60)

# Adat betöltés
ticker = 'AAPL'
stock = StockData(ticker)
df = stock.df

# Backtest futtatás alapértelmezett paraméterekkel
backtest = Backtest(df, sma200_strategy)

# Eredmények megjelenítése
print(f"\nTicker: {ticker}")
print(f"Trades: {backtest.trades_summary['number_of_trades']}")
print(f"Win Ratio: {backtest.trades_summary['win_ratio(%)']}%")
print(f"Average Result: {backtest.trades_summary['average_res(%)']}%")
print(f"Cumulative Result: {backtest.trades_summary['cumulative_result']}")

# Trade-ek megtekintése
print("\nTrade details:")
display(backtest.trades)

# Teljes összefoglaló
backtest.summarize_strategy()


# ============= PÉLDA 2: TESTRESZABOTT PARAMÉTEREKKEL =============
print("\n" + "=" * 60)
print("PÉLDA 2: Testreszabott paraméterekkel")
print("=" * 60)

# Adat betöltés
ticker = 'TSLA'
stock = StockData(ticker)
df = stock.df

# Backtest futtatás testreszabott paraméterekkel
backtest = Backtest(
    df, 
    sma200_strategy,
    rsi_period=14,           # RSI periódus
    rsi_threshold=60,        # RSI küszöb (konzervatívabb: 60 vs 65)
    sma_long=200,            # Hosszú távú SMA
    sma_short=50,            # Rövid távú SMA (kilépéshez)
    slope_period=10,         # SMA200 meredekség ellenőrzési periódus
    breakout_period=20,      # Breakout periódus
    atr_period=14,           # ATR periódus
    atr_multiplier_body=1.0, # Minimális gyertya test méret (ATR egységben)
    atr_multiplier_stop=2.5, # Stop loss távolság (ATR egységben) - konzervatívabb
    atr_multiplier_trail=2.0,# Trailing stop távolság (ATR egységben)
    max_rise_period=20,      # Parabolikus mozgás ellenőrzési periódus
    max_rise_percent=12.0    # Maximum emelkedés % (konzervatívabb: 12 vs 15)
)

print(f"\nTicker: {ticker}")
print(f"Trades: {backtest.trades_summary['number_of_trades']}")
print(f"Win Ratio: {backtest.trades_summary['win_ratio(%)']}%")
print(f"Average Result: {backtest.trades_summary['average_res(%)']}%")

# Teljes összefoglaló
backtest.summarize_strategy()


# ============= PÉLDA 3: VIZUALIZÁCIÓ SHOW_INDICATOR FÜGGVÉNNYEL =============
print("\n" + "=" * 60)
print("PÉLDA 3: Vizualizáció show_indicator függvénnyel")
print("=" * 60)

# Alapértelmezett vizualizáció
fig = show_indicator_sma200_strategy('NVDA')
fig.show()

# Testreszabott vizualizáció
fig = show_indicator_sma200_strategy(
    'MSFT',
    rsi_threshold=70,        # Enyhébb RSI szűrő
    ndays=500,               # Csak az utolsó 500 nap
    plot_height=1400,        # Magasabb ábra
    use_tradingview_title=False
)
fig.show()


# ============= PÉLDA 4: TÖBB TICKER TESZTELÉSE =============
print("\n" + "=" * 60)
print("PÉLDA 4: Több ticker összehasonlítása")
print("=" * 60)

tickers = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA', 'META', 'AMZN']
results = []

for ticker in tickers:
    try:
        print(f"Testing {ticker}...")
        stock = StockData(ticker)
        df = stock.df
        
        backtest = Backtest(df, sma200_strategy)
        
        results.append({
            'ticker': ticker,
            'trades': backtest.trades_summary['number_of_trades'],
            'win_ratio': backtest.trades_summary['win_ratio(%)'],
            'avg_result': backtest.trades_summary['average_res(%)'],
            'cumulative': backtest.trades_summary['cumulative_result'],
            'hold_result': backtest.trades_summary['hold_result']
        })
    except Exception as e:
        print(f"Error with {ticker}: {e}")
        continue

# Eredmények összehasonlítása
results_df = pd.DataFrame(results)
results_df = results_df.sort_values('avg_result', ascending=False)
print("\nÖsszehasonlító eredmények (átlagos eredmény szerint rendezve):")
display(results_df)


# ============= PÉLDA 5: PARAMÉTER OPTIMALIZÁCIÓ =============
print("\n" + "=" * 60)
print("PÉLDA 5: Egyszerű paraméter optimalizáció")
print("=" * 60)

ticker = 'AAPL'
stock = StockData(ticker)
df = stock.df

# Különböző RSI küszöbök tesztelése
rsi_thresholds = [55, 60, 65, 70, 75]
optimization_results = []

for rsi_thresh in rsi_thresholds:
    backtest = Backtest(
        df, 
        sma200_strategy,
        rsi_threshold=rsi_thresh
    )
    
    optimization_results.append({
        'rsi_threshold': rsi_thresh,
        'trades': backtest.trades_summary['number_of_trades'],
        'win_ratio': backtest.trades_summary['win_ratio(%)'],
        'avg_result': backtest.trades_summary['average_res(%)'],
        'cumulative': backtest.trades_summary['cumulative_result']
    })

opt_df = pd.DataFrame(optimization_results)
print(f"\nRSI küszöb optimalizáció eredményei ({ticker}):")
display(opt_df)

# Legjobb paraméter
best_row = opt_df.loc[opt_df['avg_result'].idxmax()]
print(f"\nLegjobb RSI küszöb: {best_row['rsi_threshold']}")
print(f"Átlagos eredmény: {best_row['avg_result']}%")
print(f"Win ratio: {best_row['win_ratio']}%")


# ============= PÉLDA 6: RÉSZLETES TRADE ELEMZÉS =============
print("\n" + "=" * 60)
print("PÉLDA 6: Részletes trade elemzés")
print("=" * 60)

ticker = 'AAPL'
stock = StockData(ticker)
df = stock.df

backtest = Backtest(df, sma200_strategy)
trades = backtest.trades

if not trades.empty:
    # Nyerő és vesztes trade-ek
    winning_trades = trades[trades['result'] > 1]
    losing_trades = trades[trades['result'] <= 1]
    
    print(f"\nTeljes trade-ek: {len(trades)}")
    print(f"Nyerő trade-ek: {len(winning_trades)}")
    print(f"Vesztes trade-ek: {len(losing_trades)}")
    
    # Kilépési okok elemzése
    if 'exit_reason' in trades.columns:
        exit_reasons = trades['exit_reason'].value_counts()
        print("\nKilépési okok eloszlása:")
        display(exit_reasons)
    
    # Legnyereségesebb trade-ek
    print("\nTop 5 legnyereségesebb trade:")
    top_trades = trades.nlargest(5, 'result')[['buy_date', 'sell_date', 
                                                'buy_price', 'sell_price', 
                                                'result', 'days_in_trade']]
    display(top_trades)
    
    # Trade időtartamok
    print(f"\nÁtlagos trade időtartam: {trades['days_in_trade'].mean():.1f} nap")
    print(f"Medián trade időtartam: {trades['days_in_trade'].median():.1f} nap")
    print(f"Leghosszabb trade: {trades['days_in_trade'].max()} nap")
    print(f"Legrövidebb trade: {trades['days_in_trade'].min()} nap")
else:
    print("Nincsenek trade-ek ebben az időszakban.")


# ============= MEGJEGYZÉSEK ÉS TIPPEK =============
"""
STRATÉGIA PARAMÉTEREK MAGYARÁZATA:

1. rsi_threshold (65): Maximum RSI érték belépéshez. 
   - Alacsonyabb érték (50-60) = konzervatívabb, kevesebb belépés
   - Magasabb érték (70-80) = agresszívabb, több belépés

2. atr_multiplier_stop (2.0): Stop loss távolság ATR egységben
   - Alacsonyabb (1.5) = szűkebb stop, gyakoribb kilépés
   - Magasabb (2.5-3.0) = tágabb stop, nagyobb lélegzetvételi tér

3. atr_multiplier_trail (2.0): Trailing stop távolság
   - Alacsonyabb (1.5) = gyorsabb profit fixing
   - Magasabb (2.5-3.0) = hosszabb trendek kifutása

4. max_rise_percent (15.0): Maximum emelkedés % a parabolikus szűrőhöz
   - Alacsonyabb (10-12) = konzervatívabb, kerüli a FOMO belépéseket
   - Magasabb (18-20) = több lehetőség, de több fals breakout

5. breakout_period (20): Hány napos high-t kell áttörni
   - Alacsonyabb (10-15) = több jelzés, több fals kitörés
   - Magasabb (30-40) = kevesebb, de erősebb jelzés

OPTIMALIZÁLÁSI TIPPEK:

1. Kezdd az alapértelmezett paraméterekkel
2. Nézd meg, mi a fő probléma:
   - Túl sok vesztes trade? → szigorítsd az RSI-t vagy emeld a body multiplier-t
   - Túl korán kilép? → növeld a trailing stop-ot
   - Túl kevés trade? → enyhítsd az RSI küszöböt vagy csökkentsd a max_rise_percent-et
3. Egy paramétert változtass egyszerre
4. Használj több tickert a validáláshoz
5. Figyelj a túloptimalizálásra (overfitting)

BACKTEST VALIDÁCIÓ:

- Mindig tesztelj több tickeren
- Nézd meg a stratégiát különböző piaci környezetekben (bull, bear, sideways)
- Vedd figyelembe a tranzakciós költségeket (0.1-0.5% per trade)
- A múltbeli teljesítmény nem garancia a jövőre!
"""

print("\n" + "=" * 60)
print("Demo befejezve!")
print("=" * 60)
