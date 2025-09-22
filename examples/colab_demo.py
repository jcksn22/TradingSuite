# colab_tradingview_demo.py

import pandas as pd
import numpy as np
from tradingsuite import TradingViewData

# Inicializálás auto_load=False opcióval
tv_data = TradingViewData(auto_load=False)

# ============= ADATOK BETÖLTÉSE =============

# 1. load_all_data() - Minden adat egyszerre
# tv_data.load_all_data()  # Ez betöltené az összes US stock, crypto, ETF-et

# 2. get_us_stocks() - Amerikai részvények
print("Amerikai részvények betöltése...")
tv_data.get_us_stocks()
print(f"Betöltve: {len(tv_data.us_stock)} amerikai részvény\n")

# 3. get_all_crypto() - Kriptovaluták
print("Kriptovaluták betöltése...")
tv_data.get_all_crypto()
print(f"Betöltve: {len(tv_data.crypto)} kriptovaluta\n")

# 4. get_us_etfs() - Amerikai ETF-ek
print("Amerikai ETF-ek betöltése...")
tv_data.get_us_etfs()
print(f"Betöltve: {len(tv_data.us_etf)} amerikai ETF\n")

# 5. get_eu_stocks() - Európai részvények
print("Európai részvények betöltése...")
tv_data.get_eu_stocks()  # Alapértelmezett: UK, Germany, Poland
print(f"Betöltve: {len(tv_data.eu_stock)} európai részvény")

# Replace paraméter demonstrálása
print("\nCsak német részvények (replace=True)...")
tv_data.get_eu_stocks(markets=['germany'], replace=True)
print(f"Felülírás után: {len(tv_data.eu_stock)} német részvény")

# BMW információ lekérése a német adatokból
print("\nNÉMET RÉSZVÉNY INFORMÁCIÓ (BMW):")
bmw_info = tv_data.get_one_eu_stock_info('BMW')
if bmw_info:
    for key, value in bmw_info.items():
        print(f"  {key}: {value}")
else:
    print("  BMW nem található")

print("\nLengyel hozzáadása (replace=False)...")
tv_data.get_eu_stocks(markets=['poland'], replace=False)
print(f"Hozzáadás után: {len(tv_data.eu_stock)} részvény összesen\n")

print("\nAngol hozzáadása (replace=False)...")
tv_data.get_eu_stocks(markets=['uk'], replace=False)
print(f"Hozzáadás után: {len(tv_data.eu_stock)} részvény összesen")

print("\nVégső európai részvény megoszlás:")
if not tv_data.eu_stock.empty:
    region_counts = tv_data.eu_stock['region'].value_counts()
    for region, count in region_counts.items():
        print(f"  {region}: {count} részvény")
print()

# ============= EGYEDI INFORMÁCIÓK =============

# 6. get_one_us_stock_info() - Amerikai részvény info
print("="*50)
print("AMERIKAI RÉSZVÉNY INFORMÁCIÓ:")
info = tv_data.get_one_us_stock_info('AAPL')
if info:
    for key, value in info.items():
        print(f"  {key}: {value}")

# 7. get_one_eu_stock_info() - Európai részvény info (UK példa)
print("\nEURÓPAI RÉSZVÉNY INFORMÁCIÓ (UK):")
eu_info = tv_data.get_one_eu_stock_info('VOD')
if eu_info:
    for key, value in eu_info.items():
        print(f"  {key}: {value}")

# ============= ELEMZÉSEK =============

# 8. get_top_n_us_stocks_by_sector() - Top amerikai részvények szektoronként
print("\n" + "="*50)
print("TOP 5% AMERIKAI RÉSZVÉNYEK SZEKTORONKÉNT:")
top_stocks = tv_data.get_top_n_us_stocks_by_sector(percent=5)
if not top_stocks.empty:
    print(f"Összesen {len(top_stocks)} részvény a top 5%-ban")
    print("Szektorok:", top_stocks['sector'].unique()[:5])  # Első 5 szektor
    
    # Példa: Technology szektor top 3
    tech_stocks = top_stocks[top_stocks['sector'] == 'Electronic Technology'].head(3)
    if not tech_stocks.empty:
        print("\nElectronic Technology top 3:")
        for _, row in tech_stocks.iterrows():
            print(f"  {row['name']}: ${tv_data.moneystring(row['market_cap_basic'])}")

# ============= SEGÉDFÜGGVÉNYEK =============

# 9. moneystring() - Pénzösszeg formázása
print("\n" + "="*50)
print("PÉNZÖSSZEG FORMÁZÁS PÉLDÁK:")
amounts = [1234, 5678900, 1234567890, 9876543210000]
for amount in amounts:
    print(f"  {amount:,} -> {tv_data.moneystring(amount)}")

# ============= PLOTLY CÍMEK ÉS GRAFIKONOK =============

# 10. get_plotly_title() - Grafikon címek generálása
print("\n" + "="*50)
print("PLOTLY CÍMEK:")
tickers = ['AAPL', 'BTC-USD', 'SPY']
for ticker in tickers:
    title = tv_data.get_plotly_title(ticker)
    print(f"\n{ticker}:")
    print(f"  {title.replace('<br>', ' | ')}")  # <br> helyett | a konzolon

# 11. get_us_sec_plot() - Amerikai szektor pozíció grafikon
print("\n" + "="*50)
print("AMERIKAI SZEKTOR GRAFIKON:")
fig = tv_data.get_us_sec_plot('MSFT')
if fig:
    print("  MSFT szektor grafikon létrehozva")
    # fig.show()  # Megjeleníti a grafikont

# 12. get_us_ind_plot() - Amerikai iparági pozíció grafikon
print("\nAMERIKAI IPARÁGI GRAFIKON:")
fig = tv_data.get_us_ind_plot('NVDA')
if fig:
    print("  NVDA iparági grafikon létrehozva")
    # fig.show()  # Megjeleníti a grafikont

# 13. get_us_etf_plot() - Amerikai ETF összehasonlító grafikon
print("\nAMERIKAI ETF GRAFIKON:")
fig = tv_data.get_us_etf_plot('QQQ')
if fig:
    print("  QQQ ETF grafikon létrehozva")
    # fig.show()  # Megjeleníti a grafikont

# ============= DATAFRAME MŰVELETEK =============

print("\n" + "="*50)
print("DATAFRAME STATISZTIKÁK:")

# Amerikai részvények
if not tv_data.us_stock.empty:
    print(f"\nAmerikai részvények top 5 piaci kap szerint:")
    top5 = tv_data.us_stock.nlargest(5, 'market_cap_basic')[['name', 'market_cap_basic', 'sector']]
    for _, row in top5.iterrows():
        print(f"  {row['name']}: ${tv_data.moneystring(row['market_cap_basic'])} ({row['sector']})")

# Európai részvények régiónként
if not tv_data.eu_stock.empty:
    print(f"\nEurópai részvények régiónként:")
    region_counts = tv_data.eu_stock['region'].value_counts()
    for region, count in region_counts.items():
        print(f"  {region}: {count} részvény")

# Kriptók top 5
if not tv_data.crypto.empty:
    print(f"\nTop 5 kriptovaluta:")
    top5_crypto = tv_data.crypto.head(5)[['base_currency', 'market_cap_calc']]
    for _, row in top5_crypto.iterrows():
        print(f"  {row['base_currency']}: ${tv_data.moneystring(row['market_cap_calc'])}")

# Amerikai ETF-ek fókusz szerint
if not tv_data.us_etf.empty:
    print(f"\nAmerikai ETF-ek fókusz szerint (top 5 kategória):")
    focus_counts = tv_data.us_etf['focus.tr'].value_counts().head(5)
    for focus, count in focus_counts.items():
        print(f"  {focus}: {count} ETF")

print("\n" + "="*50)
print("PÉLDA FUTTATÁS VÉGE")
