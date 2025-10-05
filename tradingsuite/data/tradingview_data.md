# TradingViewData - Piaci Adatok Tömeges Letöltése

Python osztály részvények, kriptovaluták és ETF-ek tömeges adatletöltésére a TradingView Scanner API-ból.

## Jellemzők

- 📊 **~8000 amerikai részvény** egyetlen API hívással
- 🌍 **Európai részvények** (korlátozva az alábbiakra: UK, Németország, Lengyelország)
- 💰 **Top 300 kriptovaluta** piaci kapitalizáció szerint
- 📈 **~3000 amerikai ETF** kezelt vagyon (AUM, Assets Under Management) szerint rendezve
- 🎯 **60+ adatmező** részvényenként (ár, fundamentális, technikai indikátorok)
- 📉 **Interaktív Plotly grafikonok** piaci pozíció vizualizációhoz
- ⚡ **Gyors és hatékony** - tömeges lekérdezésre optimalizált

## ⚠️ Fontos megjegyzés

**Ez az osztály tömeges piaci adatok snapshot-jának letöltésére szolgál.**

- ✅ **Használd, ha:** Nagy mennyiségű részvény/kripto/ETF összehasonlító elemzésére van szükséged
- ✅ **Használd, ha:** Szektorális vagy piaci szűrést szeretnél végezni
- ❌ **NE használd, ha:** Részletes historikus adatokra van szükséged (használd a csomag StockData osztályát)
- ❌ **NE használd, ha:** Perces/órás felbontású adatokat szeretnél

**Nem hivatalos API:** A TradingView Scanner API nem hivatalos, ezért változhat vagy megszűnhet. Használd felelősséggel és cache-elj adatokat.

## Telepítés

```bash
pip install pandas plotly requests
```

## Gyors kezdés

```python
from tradingview_data import TradingViewData

# Automatikus betöltés inicializáláskor
tv = TradingViewData(auto_load=True)

# Adatok elérése
print(f"Amerikai részvények: {len(tv.us_stock)}")
print(f"Európai részvények: {len(tv.eu_stock)}")
print(f"Kriptovaluták: {len(tv.crypto)}")
print(f"Amerikai ETF-ek: {len(tv.us_etf)}")

# Egyedi részvény információ
apple_info = tv.get_one_us_stock_info('AAPL')
print(apple_info)

# Interaktív grafikon
fig = tv.get_us_sec_plot('MSFT')
fig.show()
```

## Osztály konstruktor

### `TradingViewData(auto_load=True)`

**Paraméterek:**
- `auto_load` (bool, alapértelmezett=True): Ha True, automatikusan letölti az összes adatot az inicializáláskor

**Adatstruktúrák:**
Az osztály 4 pandas DataFrame-et hoz létre és tölt fel:
- `tv.us_stock` - Amerikai részvények (~8000)
- `tv.eu_stock` - Európai részvények (~5000-15000, piacoktól függően)
- `tv.crypto` - Kriptovaluták (~300, stablecoin-ok nélkül)
- `tv.us_etf` - Amerikai ETF-ek (~3000)

## Publikus metódusok

### 1. Adatletöltő metódusok

#### `load_all_data()`

Egyszerre tölti le az összes adatot (amerikai részvények, kriptók, ETF-ek, európai részvények).

**Példa:**
```python
tv = TradingViewData(auto_load=False)
tv.load_all_data()  # Mindent betölt
```

---

#### `get_us_stocks()`

Letölti az összes amerikai tőzsdén jegyzett részvényt (AMEX, NASDAQ, NYSE).

**Visszatérés:** True ha sikeres, False egyébként

**Lekért adatok:** ~8000 részvény, 60+ adatmezővel

**Példa:**
```python
tv = TradingViewData(auto_load=False)
tv.get_us_stocks()
print(f"Betöltve: {len(tv.us_stock)} amerikai részvény")

# Top 10 piaci kapitalizáció szerint
top10 = tv.us_stock.nlargest(10, 'market_cap_basic')
print(top10[['name', 'description', 'market_cap_basic']])
```

**Főbb oszlopok:**
- `name`: Ticker szimbólum
- `description`: Cég teljes neve
- `close`: Aktuális záróár
- `market_cap_basic`: Piaci kapitalizáció
- `sector`, `industry`: Besorolás
- `RSI7`, `SMA50`, `SMA200`: Technikai indikátorok
- `Perf.W`, `Perf.1M`, `Perf.Y`: Teljesítmény mutatók

---

#### `get_eu_stocks(markets=['uk', 'germany', 'poland'], replace=True)`

Letölti az európai részvényeket a megadott piacokról.

**Paraméterek:**
- `markets` (list): Európai piacok listája
  - Támogatott: `'uk'`, `'germany'`, `'poland'`
- `replace` (bool): True esetén felülírja, False esetén hozzáadja a meglévő adatokhoz

**Visszatérés:** True ha sikeres, False egyébként

**Példa:**
```python
# Csak német részvények
tv.get_eu_stocks(markets=['germany'], replace=True)

# UK hozzáadása
tv.get_eu_stocks(markets=['uk'], replace=False)

# Régiónkénti megoszlás
print(tv.eu_stock['region'].value_counts())
```

**Európai piacok:**
- **UK**: London Stock Exchange (LSE, AIM) - ~2000 részvény
- **Germany**: XETR, FSE, SWB, HAM, DUS, BER, STU, MUN - ~1000 részvény
- **Poland**: Warsaw Stock Exchange (WSE) - ~800 részvény

**Fontos:** Az európai API-ból hiányzó mezők:
- Technikai indikátorok (SMA, EMA, RSI, MACD, Bollinger)
- Historikus árak (52 week high/low, All time high/low)

---

#### `get_all_crypto()`

Letölti a top 300 kriptovalutát piaci kapitalizáció szerint.

**Visszatérés:** True ha sikeres, False egyébként

**Automatikus szűrés:** Stablecoin-ok kizárva

**Példa:**
```python
tv.get_all_crypto()

# Top 10 kriptó
top10_crypto = tv.crypto.head(10)
print(top10_crypto[['base_currency', 'base_currency_desc', 'market_cap_calc']])

# DeFi kategória keresése
defi = tv.crypto[tv.crypto['crypto_common_categories'].str.contains('DeFi', na=False)]
print(f"DeFi projektek: {len(defi)}")
```

**Főbb oszlopok:**
- `base_currency`: Szimbólum (BTC, ETH)
- `base_currency_desc`: Teljes név
- `ticker`: USD pár (BTC-USD)
- `market_cap_calc`: Piaci kapitalizáció
- `24h_vol_cmc`: 24 órás forgalom
- `crypto_common_categories`: Kategóriák (DeFi, layer-1, stb.)

---

#### `get_us_etfs()`

Letölti az amerikai ETF-eket (Exchange Traded Funds) AUM szerint rendezve.

**Visszatérés:** True ha sikeres, False egyébként

**Lekért adatok:** ~3000 ETF és ETN

**Példa:**
```python
tv.get_us_etfs()

# Top 10 ETF AUM szerint
top10_etf = tv.us_etf.nlargest(10, 'aum')
print(top10_etf[['name', 'description', 'aum', 'expense_ratio']])

# Technology fókuszú ETF-ek
tech_etfs = tv.us_etf[tv.us_etf['focus.tr'] == 'Technology Sector']
```

**Főbb oszlopok:**
- `name`: Ticker szimbólum
- `description`: ETF teljes neve
- `aum`: Assets Under Management (kezelt vagyon)
- `expense_ratio`: Költségráta
- `focus.tr`: Befektetési fókusz
- `category.tr`: ETF kategória

---

### 2. Információ lekérő metódusok

#### `get_one_us_stock_info(ticker)`

Egyetlen amerikai részvény részletes információit adja vissza.

**Paraméterek:**
- `ticker` (str): Részvény szimbólum (pl. "AAPL", "MSFT")

**Visszatérés:** Dictionary vagy None

**Példa:**
```python
info = tv.get_one_us_stock_info('AAPL')
print(f"Név: {info['name']}")
print(f"Ár: ${info['price']}")
print(f"Piaci kap.: ${info['market_cap_text']}")
print(f"Szektor pozíció: {info['sec_loc']}")
print(f"Iparági pozíció: {info['ind_loc']}")
print(info['performance'])
```

**Visszaadott dictionary mezők:**
- `ticker`, `name`: Azonosítók
- `price`: Aktuális ár
- `market_cap`, `market_cap_text`: Piaci kapitalizáció
- `sector`, `industry`: Besorolás
- `sec_loc`, `ind_loc`: Pozíció a szektorban/iparágban (pl. "5/123")
- `performance`: Teljesítmény szöveg

---

#### `get_one_eu_stock_info(ticker)`

Egyetlen európai részvény részletes információit adja vissza.

**Paraméterek:**
- `ticker` (str): Részvény szimbólum (pl. "VOD", "BMW")

**Visszatérés:** Dictionary vagy None

**Példa:**
```python
info = tv.get_one_eu_stock_info('BMW')
print(f"Név: {info['name']}")
print(f"Régió: {info['region']}")
print(f"Deviza: {info['currency']}")
print(f"Tőzsde: {info['exchange']}")
```

---

#### `get_top_n_us_stocks_by_sector(percent=10)`

Szektoronként visszaadja a legnagyobb amerikai részvényeket megadott százalékban.

**Paraméterek:**
- `percent` (float): Visszaadandó részvények százaléka szektoronként (0-100)

**Visszatérés:** pandas DataFrame

**Példa:**
```python
# Minden szektor top 5%-a
top5_percent = tv.get_top_n_us_stocks_by_sector(percent=5)

# Technology szektor top 10
tech = top5_percent[top5_percent['sector'] == 'Technology'].head(10)
print(tech[['name', 'description', 'market_cap_basic']])

# Szektoronkénti összesítés
sector_summary = top5_percent.groupby('sector').agg({
    'market_cap_basic': ['count', 'sum', 'mean']
})
print(sector_summary)
```

---

#### `get_plotly_title(ticker)`

Plotly grafikonokhoz generál informatív címet.

**Paraméterek:**
- `ticker` (str): Ticker szimbólum (részvény, kripto, ETF)

**Visszatérés:** Formázott string

**Példa:**
```python
# Részvény cím
title = tv.get_plotly_title('AAPL')
# "Apple Inc. (AAPL) [US] - $2.85 Trillion - Technology (3/456) - Consumer Electronics (1/89)"

# Kripto cím
title = tv.get_plotly_title('BTC-USD')
# "Bitcoin (BTC) - $850 Billion - store-of-value, layer-1"

# ETF cím
title = tv.get_plotly_title('SPY')
# "SPDR S&P 500 ETF Trust (SPY) - AUM: $450 Billion - Fókusz: Large Cap - Költség: 0.09%"
```

---

### 3. Vizualizációs metódusok

#### `get_us_sec_plot(ticker)`

Oszlopdiagram az amerikai részvény pozíciójáról a szektorán belül.

**Paraméterek:**
- `ticker` (str): Amerikai részvény szimbólum

**Visszatérés:** Plotly Figure vagy None

**Példa:**
```python
fig = tv.get_us_sec_plot('MSFT')
fig.show()
```

**A grafikon tartalmazza:**
- Az összes részvény a szektorban
- Piaci kapitalizáció szerinti rendezés
- Kiemelt annotáció a keresett részvényre
- Cégnevek az oszlopokon

---

#### `get_us_ind_plot(ticker)`

Oszlopdiagram az amerikai részvény pozíciójáról az iparágán belül.

**Paraméterek:**
- `ticker` (str): Amerikai részvény szimbólum

**Visszatérés:** Plotly Figure vagy None

**Példa:**
```python
fig = tv.get_us_ind_plot('NVDA')
fig.show()
```

**Használat:** Szűkebb fókusz mint a szektor - csak az azonos iparágban működő cégek

---

#### `get_us_etf_plot(ticker)`

Oszlopdiagram amerikai ETF-ek összehasonlítására azonos befektetési fókusz alapján.

**Paraméterek:**
- `ticker` (str): Amerikai ETF szimbólum

**Visszatérés:** Plotly Figure vagy None

**Példa:**
```python
fig = tv.get_us_etf_plot('QQQ')
fig.show()
```

**A grafikon tartalmazza:**
- Azonos fókuszú ETF-ek
- AUM (kezelt vagyon) szerinti összehasonlítás
- ETF nevek az oszlopokon

---

### 4. Segédfüggvény

#### `moneystring(money)`

Pénzösszeget alakít át olvasható formátumra.

**Paraméterek:**
- `money` (float/int): Pénzösszeg

**Visszatérés:** String mértékegységgel

**Példa:**
```python
print(tv.moneystring(1234567890))        # "1.23 Billion"
print(tv.moneystring(45600000))          # "45.6 Million"
print(tv.moneystring(2345678901234))     # "2.35 Trillion"
```

---

## Belső metódusok

Az alábbi metódus automatikusan meghívódik, közvetlenül nem szükséges használni:

- **`_make_request(url, data_query)`** - HTTP kérés végrehajtása hibakezeléssel

---

## DataFrame oszlopok

### Amerikai részvények (`us_stock`) - 60+ oszlop

**Alapvető:**
- `name`, `description`, `close`, `volume`, `market_cap_basic`
- `sector`, `industry`, `country`
- `price_earnings_ttm`, `earnings_per_share_basic_ttm`
- `number_of_employees`, `beta_1_year`

**Technikai indikátorok:**
- Mozgóátlagok: `SMA50`, `SMA100`, `SMA200`, `EMA50`, `EMA100`, `EMA200`
- Oszcillátorok: `RSI7`, `Mom`, `Stoch.RSI.K`, `Stoch.RSI.D`
- MACD: `MACD.macd`, `MACD.signal`
- Bollinger: `BB.lower`, `BB.upper`

**Teljesítmény:**
- `Perf.W`, `Perf.1M`, `Perf.3M`, `Perf.6M`, `Perf.Y`, `Perf.YTD`, `Perf.5Y`, `Perf.All`

**Árszélsőértékek:**
- `High.1M`, `Low.1M`, `High.3M`, `Low.3M`, `High.6M`, `Low.6M`
- `price_52_week_high`, `price_52_week_low`
- `High.All`, `Low.All`

### Európai részvények (`eu_stock`) - 25+ oszlop

**Alapvető:**
- `name`, `description`, `close`, `volume`, `market_cap_basic`
- `sector`, `industry`, `exchange`, `currency`
- `region`, `default_currency` (hozzáadott mezők)

**Teljesítmény:**
- `Perf.W`, `Perf.1M`, `Perf.3M`, `Perf.6M`, `Perf.Y`, `Perf.YTD`, `Perf.5Y`, `Perf.All`

**Hiányzó:** Technikai indikátorok, historikus árak

### Kriptovaluták (`crypto`) - 20+ oszlop

**Alapvető:**
- `base_currency`, `base_currency_desc`, `ticker` (pl. BTC-USD)
- `close`, `market_cap_calc`, `24h_vol_cmc`
- `circulating_supply`

**Kategorizálás:**
- `crypto_common_categories` (pl. DeFi, layer-1, meme)
- `crypto_blockchain_ecosystems` (pl. Ethereum, Solana)
- `crypto_total_rank`: Rangsor

### Amerikai ETF-ek (`us_etf`) - 25+ oszlop

**Alapvető:**
- `name`, `description`, `close`
- `aum`: Kezelt vagyon (Assets Under Management)
- `expense_ratio`: Költségráta

**Kategorizálás:**
- `focus.tr`: Befektetési fókusz (pl. Large Cap, Technology Sector)
- `category.tr`: ETF kategória
- `asset_class.tr`: Eszközosztály
- `brand.tr`: Kibocsátó márka

---

## Használati példák

### 1. példa: Amerikai tech óriások elemzése

```python
from tradingview_data import TradingViewData

tv = TradingViewData()

# Technology szektor szűrése
tech = tv.us_stock[tv.us_stock['sector'] == 'Technology']

# Top 20 piaci kapitalizáció szerint
top20_tech = tech.nlargest(20, 'market_cap_basic')

# P/E ráta elemzése
print("Tech óriások P/E rátája:")
for _, row in top20_tech.iterrows():
    pe = row['price_earnings_ttm']
    print(f"{row['name']}: {pe:.2f}" if pe > 0 else f"{row['name']}: N/A")

# Éves teljesítmény
print("\nÉves teljesítmény:")
for _, row in top20_tech.iterrows():
    print(f"{row['name']}: {row['Perf.Y']:.2f}%")
```

### 2. példa: Momentum kereskedési screener

```python
# Erős momentum részvények keresése
momentum_stocks = tv.us_stock[
    (tv.us_stock['Perf.1M'] > 10) &          # 1 havi +10%
    (tv.us_stock['RSI7'] < 70) &             # Még nem túlvett
    (tv.us_stock['volume'] > 1_000_000) &    # Likvid
    (tv.us_stock['market_cap_basic'] > 1e9)  # Min 1B market cap
].sort_values('Perf.1M', ascending=False)

print(f"Talált momentum részvények: {len(momentum_stocks)}")
print(momentum_stocks[['name', 'description', 'Perf.1M', 'RSI7']].head(10))
```

### 3. példa: Szektorális összehasonlítás

```python
# Szektoronkénti teljesítmény aggregálás
sector_perf = tv.us_stock.groupby('sector').agg({
    'Perf.YTD': 'mean',
    'market_cap_basic': 'sum',
    'volume': 'sum',
    'name': 'count'
}).rename(columns={'name': 'stock_count'})

sector_perf = sector_perf.sort_values('Perf.YTD', ascending=False)
print(sector_perf)

# Legjobb szektor top részvényei
best_sector = sector_perf.index[0]
best_sector_stocks = tv.us_stock[tv.us_stock['sector'] == best_sector]
print(f"\n{best_sector} top 10:")
print(best_sector_stocks.nlargest(10, 'market_cap_basic')[['name', 'description']])
```

### 4. példa: Kriptovaluta elemzés

```python
# Layer-1 blockchain projektek
layer1 = tv.crypto[
    tv.crypto['crypto_common_categories'].str.contains('layer-1', na=False)
]

print(f"Layer-1 projektek: {len(layer1)}")
print(layer1[['base_currency', 'base_currency_desc', 'market_cap_calc']].head(10))

# 24 órás forgalom top 10
top_volume = tv.crypto.nlargest(10, '24h_vol_cmc')
print("\nLegnagyobb 24h forgalom:")
for _, row in top_volume.iterrows():
    vol_str = tv.moneystring(row['24h_vol_cmc'])
    print(f"{row['base_currency']}: ${vol_str}")
```

### 5. példa: ETF összehasonlítás

```python
# S&P 500 ETF-ek keresése
sp500_etfs = tv.us_etf[tv.us_etf['description'].str.contains('S&P 500', na=False)]

# Költségráta szerint rendezés
sp500_sorted = sp500_etfs.sort_values('expense_ratio')

print("S&P 500 ETF-ek költségráta szerint:")
for _, etf in sp500_sorted.iterrows():
    print(f"{etf['name']} - AUM: ${tv.moneystring(etf['aum'])} - "
          f"Költség: {etf['expense_ratio']:.2f}%")
```

### 6. példa: Európai autóipar elemzés

```python
# Európai autóipari cégek
if not tv.eu_stock.empty:
    auto_industry = tv.eu_stock[
        tv.eu_stock['industry'].str.contains('Auto', na=False, case=False)
    ]
    
    print(f"Európai autóipari részvények: {len(auto_industry)}")
    print(auto_industry[['name', 'description', 'region', 'close', 'Perf.Y']])
    
    # Régió szerinti megoszlás
    print("\nRégió szerint:")
    print(auto_industry['region'].value_counts())
```

### 7. példa: Túladott részvények keresése

```python
# Technikai alapú túladott részvények
oversold = tv.us_stock[
    (tv.us_stock['RSI7'] < 30) &                    # RSI túladott
    (tv.us_stock['close'] < tv.us_stock['SMA200']) & # Ár SMA200 alatt
    (tv.us_stock['Perf.3M'] < -20) &                # 3 havi -20%
    (tv.us_stock['market_cap_basic'] > 5e9)         # Min 5B market cap
]

print(f"Túladott large-cap részvények: {len(oversold)}")
print(oversold[['name', 'sector', 'RSI7', 'Perf.3M']].head(10))
```

### 8. példa: Grafikon készítés és exportálás

```python
# Apple pozíció a szektorban
fig = tv.get_us_sec_plot('AAPL')
fig.show()
# fig.write_html('apple_sector.html')  # Export HTML-be

# NVIDIA pozíció az iparágban
fig = tv.get_us_ind_plot('NVDA')
fig.show()

# QQQ ETF összehasonlítás
fig = tv.get_us_etf_plot('QQQ')
fig.show()
```

### 9. példa: Adatok exportálása

```python
# Top 100 részvény exportálása
top100 = tv.us_stock.nlargest(100, 'market_cap_basic')
top100.to_csv('top100_us_stocks.csv', index=False)

# Kripto adatok JSON-ba
tv.crypto.to_json('crypto_data.json', orient='records')

# Európai részvények Excel-be
tv.eu_stock.to_excel('eu_stocks.xlsx', index=False)
```

---

## Megjegyzések

- **Snapshot jellegű:** Aktuális piaci állapot, nincs historikus idősor
- **Rate limiting:** Túl gyakori hívások blokkoláshoz vezethetnek - használj cache-elést
- **Nem hivatalos API:** Változhat vagy megszűnhet figyelmeztetés nélkül
- **Adatminőség:** Kritikus döntések előtt ellenőrizd az adatokat
- **Visszafelé kompatibilitás:** Régebbi szkriptek működnek az új verzióval

## Limitációk és megoldások

### 1. Nincs historikus idősor
**Probléma:** Csak aktuális snapshot, nincs múltbeli adattörténet  
**Megoldás:** Kombináld a StockData osztállyal részletes historikus elemzéshez

### 2. Rate limiting
**Probléma:** Túl gyakori API hívások blokkoláshoz vezetnek  
**Megoldás:** Cache-elj adatokat, mentsd DataFrame-eket pickle/parquet formátumban

```python
# Adatok mentése
tv.us_stock.to_pickle('us_stock_cache.pkl')

# Adatok betöltése
import pandas as pd
tv = TradingViewData(auto_load=False)
tv.us_stock = pd.read_pickle('us_stock_cache.pkl')
```

### 3. Európai adatok hiányosak
**Probléma:** Hiányzó technikai indikátorok az európai részvényeknél  
**Megoldás:** Használd amerikai részvényekhez, vagy számítsd ki saját magad pandas_ta-val

### 4. Stablecoin szűrés
**Megjegyzés:** Stablecoin-ok automatikusan ki vannak szűrve a kripto adatokból  
**Megoldás:** Ha szükséged van rájuk, módosítsd a `get_all_crypto()` metódust

---

## Fejlesztési javaslatok

1. **Cache implementálása:** Redis vagy file-based cache a rate limiting elkerülésére
2. **Incremental update:** Csak változások lekérése
3. **Historikus tracking:** Snapshot-ok tárolása idősorokhoz
4. **Backup data source:** Yahoo Finance fallback
5. **Data validation:** Automatikus adatminőség ellenőrzés
6. **Async support:** Párhuzamos letöltés több piacról
7. **WebSocket stream:** Valós idejű árfolyam frissítések

---

## Függőségek

- pandas
- plotly
- requests

## Kapcsolódó osztályok

- **StockData**: Részletes historikus adatok és technikai elemzés egyedi részvényekhez
- Használd együtt: TradingViewData a szűréshez, StockData a részletes elemzéshez


## API dokumentáció

TradingView Scanner: Nem hivatalos API, nincs nyilvános dokumentáció.
