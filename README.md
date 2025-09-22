# TradingSuite
TradingView alapú részvényelemző eszköz Pythonban.  
Tartalmazza a `tradingsuite` csomagot, amely lehetővé teszi amerikai és európai részvények, ETF-ek és kriptovaluták letöltését és vizsgálatát.  

## Telepítés

### Fejlesztői telepítés
```bash
git clone https://github.com/yourusername/TradingSuite.git
cd TradingSuite
pip install -e .
```

### Függőségek telepítése
```bash
pip install -r requirements.txt
```

## Használat

### Alapvető használat
```python
from tradingsuite import TradingViewData, StockData, Backtest
from tradingsuite.strategies import rsi_strategy

# TradingView adatok betöltése
tv_data = TradingViewData(auto_load=False)
tv_data.get_us_stocks()

# Részvény adatok letöltése
stock_data = StockData('AAPL')

# Backtest futtatása
backtest = Backtest(stock_data.df, rsi_strategy, buy_threshold=30, sell_threshold=70)
print(backtest.trades_summary)
```  

## Funkciók
### Adatlekérés
- Amerikai részvények betöltése (`get_us_stocks`)
- Európai részvények betöltése (`get_eu_stocks`)
- Amerikai ETF-ek betöltése (`get_us_etfs`)
- Kriptovaluták betöltése (`get_all_crypto`)

### Információ lekérés
- Amerikai részvények információi (`get_one_us_stock_info`)
- Európai részvények információi (`get_one_eu_stock_info`)
- Top részvények szektoronként (`get_top_n_us_stocks_by_sector`)

### Vizualizáció
- Szektor pozíció grafikon (`get_us_sec_plot`)
- Iparági pozíció grafikon (`get_us_ind_plot`)
- ETF összehasonlító grafikon (`get_us_etf_plot`)

## Telepítés és futtatás Google Colabban
1. Nyiss meg egy új Colab notebookot:  
   👉 [Google Colab](https://colab.research.google.com/)
2. Klónozd a repository-t és telepítsd a függőségeket:  
   ```python
   import os
   import sys
   import shutil
   import time
   # Függőségek telepítése
   print("Installing dependencies ...\n")
   os.system("pip install numpy pandas plotly scipy requests cloudscraper tqdm pandas_datareader -q")
   os.system("pip install pandas_ta --no-deps -q")
   # TradingSuite telepítése
   print("Installing TradingSuite ...\n")
   if os.path.exists('/content/TradingSuite'):
       shutil.rmtree('/content/TradingSuite')
       print("Existing TradingSuite directory removed\n")
   os.system("git clone https://github.com/jcksn22/TradingSuite.git")
   # Path hozzáadása
   sys.path.append('/content/TradingSuite')
   time.sleep(1)
   print("Installation complete", flush=True)
   ```
3. Futtasd a Colab demót:
   ```python
   !python /content/TradingSuite/colab_tv_demo.py
   ```
4. Példa használat (TradingViewData osztály)
   ```python
   from tradingview_data import TradingViewData
   
   # Inicializálás
   tv_data = TradingViewData(auto_load=False)
   
   # Amerikai részvények
   tv_data.get_us_stocks()
   print(f"US részvények: {len(tv_data.us_stock)}")
   
   # Európai részvények
   tv_data.get_eu_stocks()
   print(f"EU részvények: {len(tv_data.eu_stock)}")
   
   # Amerikai ETF-ek
   tv_data.get_us_etfs()
   print(f"US ETF-ek: {len(tv_data.us_etf)}")
   
   # Kriptovaluták
   tv_data.get_all_crypto()
   print(f"Kriptók: {len(tv_data.crypto)}")
   
   # Egyedi részvény infó
   info = tv_data.get_one_us_stock_info('AAPL')
   print(info)
   
   # Grafikon készítése
   fig = tv_data.get_us_sec_plot('MSFT')
   if fig:
       fig.show()
   ```
5. Fájlok
* tradingview_data.py – a fő modul (TradingViewData osztály)
* colab_tv_demo.py – példa futtató szkript Google Colabhoz
* README.md – dokumentáció (ez a fájl)
