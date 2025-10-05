# StockData - Részvény technikai elemző osztály

Python osztály részvény, kripto és ETF adatok letöltésére és elemzésére technikai indikátorokkal és interaktív vizualizációkkal.

## Jellemzők

- 📊 Történelmi adatok letöltése Yahoo Finance API-ból
- 📈 Technikai indikátorok számítása (RSI, SMA, Bollinger Bands, SMMA)
- 🎯 Lokális minimumok és maximumok azonosítása
- 📉 Interaktív Plotly grafikonok generálása trendelemzéssel
- 🚀 Árváltozások követése szélsőértékek között emoji jelölésekkel

## Támogatott instrumentumok:
- 📈 Részvények (US, EU stb.)
- 💰 Kriptovaluták (szimbólum végén: `-USD`)
- 📊 ETF-ek
- 💱 Forex párok (szimbólum végén: `=X`)

## ⚠️ Fontos megjegyzés

**Ez az osztály kizárólag NAPI (daily) adatok kezelésére lett kifejlesztve.**

Bár a Yahoo Finance API lehetővé teszi perces és órás adatok letöltését is, a StockData osztály technikai indikátorai, lokális szélsőérték-detektálása és vizualizációi **napi felbontású adatokra vannak optimalizálva**. 

**Az `interval` paramétert mindig `'1d'`-re állítsd!**

A dátum kezelése nap pontosságú: **yyyy.mm.dd** formátumban (pl. 2025.01.03)

## Telepítés

```bash
pip install pandas pandas-ta plotly scipy numpy requests cloudscraper
```

**Miért kell a cloudscraper?**  
A Yahoo Finance API CloudFlare védelmet használ. A `cloudscraper` csomag lehetővé teszi, hogy megkerüljük ezeket a korlátozásokat és megbízhatóan letölthessük a historikus adatokat.

## Gyors kezdés

```python
from stock_data import StockData

# Inicializálás napi adatokkal (alapértelmezett)
stock = StockData('AAPL', range='5y', interval='1d')

# Hozzáférés a DataFrame-hez az összes indikátorral
df = stock.df

# Interaktív grafikonok generálása
fig1 = stock.plotly_last_year('AAPL - Utolsó év elemzése')
fig1.show()

fig2 = stock.plot_smma_ribbon('AAPL - SMMA Ribbon')
fig2.show()
```

## Osztály konstruktor

### `StockData(ticker, ad_ticker=True, range='18y', interval='1d')`

**Paraméterek:**
- `ticker` (str): Részvény ticker szimbólum (pl. 'AAPL', 'TSLA', 'BTC-USD', 'SPY')
- `ad_ticker` (bool, alapértelmezett=True): Ticker oszlop hozzáadása a DataFrame-hez
- `range` (str, alapértelmezett='18y'): Letöltendő időtartam
  - Példák: `'1d'`, `'5d'`, `'1mo'`, `'3mo'`, `'6mo'`, `'1y'`, `'5y'`, `'10y'`, `'max'`
- `interval` (str, alapértelmezett='1d'): Adat intervallum
  - **FIGYELEM:** Csak `'1d'` (napi) intervallumot használj! 
  - Az osztály nem megfelelően működik perces (`'1m'`, `'5m'`) vagy órás (`'1h'`) adatokkal

**Dátum kezelés:** A `date` oszlop **yyyy.mm.dd** formátumú (pl. 2025.01.03), nap pontossággal

## Metódusok

### 1. `plotly_last_year(plot_title, plot_height=900, ndays=500, ad_local_min_max=True)`

Interaktív OHLC gyertyás diagram generálása SMA indikátorokkal és lokális szélsőértékekkel.

**Paraméterek:**
- `plot_title` (str): Grafikon címe
- `plot_height` (int, alapértelmezett=900): Grafikon magassága pixelben
- `ndays` (int, alapértelmezett=500): Megjelenítendő napok száma
- `ad_local_min_max` (bool, alapértelmezett=True): Lokális min/max jelölések megjelenítése

**Visszatérés:** Plotly Figure objektum

**Példa:**
```python
stock = StockData('TSLA', range='2y', interval='1d')
fig = stock.plotly_last_year('Tesla részvény elemzés', ndays=365)
fig.show()
```

**A grafikon tartalmazza:**
- OHLC gyertyás diagram
- SMA 50 (világoskék vonal)
- SMA 200 (piros vonal)
- Lokális maximumok 🚀 jelöléssel (zöld szöveg)
- Lokális minimumok 💸😭 jelöléssel (piros szöveg)
- Árváltozás százalékok a szélsőértékek között

---

### 2. `plot_smma_ribbon(plot_title, plot_height=900, ndays=800, ad_local_min_max=True)`

Interaktív grafikon generálása SMMA Ribbon indikátorral trendelemzéshez.

**Paraméterek:**
- `plot_title` (str): Grafikon címe
- `plot_height` (int, alapértelmezett=900): Grafikon magassága pixelben
- `ndays` (int, alapértelmezett=800): Megjelenítendő napok száma
- `ad_local_min_max` (bool, alapértelmezett=True): Lokális min/max jelölések megjelenítése

**Visszatérés:** Plotly Figure objektum

**Példa:**
```python
stock = StockData('BTC-USD', range='3y', interval='1d')
fig = stock.plot_smma_ribbon('Bitcoin SMMA Ribbon elemzés', ndays=1000)
fig.show()
```

**A grafikon tartalmazza:**
- OHLC gyertyás diagram
- 4 SMMA vonal (periódusok: 15, 19, 25, 29)
- Színkódolt ribbon zónák:
  - 🟡 **Arany**: Bullish trend (v1 > v2 > v3 > v4)
  - 🔵 **Kék**: Bearish trend (v4 > v3 > v2 > v1)
  - ⚪ **Szürke**: Semleges (nincs egyértelmű trend)
- Lokális min/max jelölések árváltozásokkal

---

## Belső metódusok

Az alábbi metódusok automatikusan meghívódnak, közvetlenül nem szükséges őket használni:

- **`download_historical_data()`** - Adatletöltés és indikátorszámítás koordinálása (automatikusan fut az inicializáláskor)
- **`get_olhc()`** - Nyers OHLCV adatok letöltése Yahoo Finance-ról
- **`smma(data, window, colname)`** - Simított mozgóátlag (SMMA) számítása

---

## DataFrame oszlopok

Az inicializálás után a DataFrame elérhető a `stock.df`-en keresztül:

### Yahoo Finance eredeti adatok:
- `date`: Dátum (yyyy.mm.dd formátum, pl. 2025.01.03)
- `open`: Nyitóár
- `high`: Legmagasabb ár
- `low`: Legalacsonyabb ár
- `close`: Záróár
- `volume`: Kereskedési volumen
- `ticker`: Részvény ticker szimbólum

### Számított indikátorok:
- `hl2`: (High + Low) / 2
- `rsi`: Relative Strength Index (14 periódus)
- `sma_50`, `sma_100`, `sma_200`: Egyszerű mozgóátlagok
- `diff_sma50`, `diff_sma100`, `diff_sma200`: Százalékos eltérés az SMA-któl
- `bb_lower`, `bb_upper`: Bollinger Bands (alsó és felső sáv)
- `diff_upper_bb`, `diff_lower_bb`: Százalékos eltérés a Bollinger sávoktól
- `local`: 'minimum', 'maximum', vagy üres
- `local_text`: Formázott annotáció szöveg emoji-kkal és árváltozásokkal

---

## Forex (devizapár) támogatás

A StockData osztály **teljes mértékben támogatja a forex adatok letöltését és elemzését** a Yahoo Finance API-n keresztül.

### Forex ticker formátum

Yahoo Finance forex szimbólum: `ALAPDEVIZA+CÉLDEVIZA=X`

**Példák:**
```python
'EURUSD=X'  # Euro / US Dollar
'GBPUSD=X'  # British Pound / US Dollar  
'USDJPY=X'  # US Dollar / Japanese Yen
```

### Major forex párok (~80-85% globális forgalom)

```python
'EURUSD=X'  # Euro / US Dollar (Fiber) - ~28% forgalom
'USDJPY=X'  # US Dollar / Japanese Yen (Gopher) - ~13% forgalom
'GBPUSD=X'  # British Pound / US Dollar (Cable) - ~11% forgalom
'AUDUSD=X'  # Australian Dollar / US Dollar (Aussie) - ~6% forgalom
'USDCAD=X'  # US Dollar / Canadian Dollar (Loonie) - ~5% forgalom
'USDCHF=X'  # US Dollar / Swiss Franc (Swissy) - ~4% forgalom
'NZDUSD=X'  # New Zealand Dollar / US Dollar (Kiwi) - ~2% forgalom
```

### Minor forex párok (~10-15% forgalom)

```python
# Cross párok (USD nélkül)
'EURGBP=X'  # Euro / British Pound (Euro-Sterling) - ~2% forgalom
'EURJPY=X'  # Euro / Japanese Yen (Yuppy) - ~2% forgalom
'GBPJPY=X'  # British Pound / Japanese Yen (Guppy) - ~1.5% forgalom
'EURCHF=X'  # Euro / Swiss Franc (Euro-Swissy) - ~1.5% forgalom

# Egyéb likvid párok
'USDCNY=X'  # US Dollar / Chinese Yuan (Yuan) - ~4% forgalom
'USDMXN=X'  # US Dollar / Mexican Peso (Peso) - ~1.5% forgalom
'USDSEK=X'  # US Dollar / Swedish Krona (Stockie) - ~1% forgalom
'USDNOK=X'  # US Dollar / Norwegian Krone (Nockie) - ~1% forgalom
```

### Forex használati példa

```python
from stock_data import StockData

# EUR/USD napi adatok
eurusd = StockData('EURUSD=X', range='5y', interval='1d')

# Adatok megtekintése
print(f"Aktuális árfolyam: {eurusd.df['close'].iloc[-1]:.4f}")
print(f"RSI: {eurusd.df['rsi'].iloc[-1]:.2f}")

# Grafikon készítése
fig = eurusd.plotly_last_year('EUR/USD - 5 éves elemzés', ndays=500)
fig.show()

# SMMA Ribbon
fig2 = eurusd.plot_smma_ribbon('EUR/USD - SMMA Ribbon', ndays=800)
fig2.show()
```

**Forex specifikus megjegyzések:**
- ✅ Minden technikai indikátor működik (RSI, SMA, Bollinger, SMMA)
- ✅ Lokális min/max detektálás működik
- ✅ Mindkét vizualizáció elérhető
- ⚠️ A `volume` mező általában 0 vagy NA (nincs központosított forgalmi adat a devizapiacokon)

---

## Használati példák

### 1. példa: Apple részvény elemzése
```python
from stock_data import StockData

# 5 év napi adat letöltése
apple = StockData('AAPL', range='5y', interval='1d')

# Adatok összefoglalása
print(f"Összes sor: {len(apple.df)}")
print(f"Dátum tartomány: {apple.df['date'].min()} - {apple.df['date'].max()}")
print(f"Legutóbbi záróár: ${apple.df['close'].iloc[-1]:.2f}")

# Grafikon generálása
fig = apple.plotly_last_year('Apple Inc. - 5 éves elemzés')
fig.show()
```

### 2. példa: Bitcoin elemzés SMMA Ribbon-nal
```python
from stock_data import StockData

# Bitcoin adatok letöltése
btc = StockData('BTC-USD', range='3y', interval='1d')

# SMMA ribbon grafikon generálása
fig = btc.plot_smma_ribbon('Bitcoin - SMMA trendelemzés', ndays=1000)
fig.show()

# Aktuális trend ellenőrzése
latest = btc.df.iloc[-1]
print(f"Jelenlegi BTC ár: ${latest['close']:,.2f}")
print(f"RSI: {latest['rsi']:.2f}")
print(f"Távolság az SMA200-tól: {latest['diff_sma200']:.2f}%")
```

### 3. példa: Több részvény összehasonlítása
```python
from stock_data import StockData

tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']

for ticker in tickers:
    stock = StockData(ticker, range='1y', interval='1d')
    latest = stock.df.iloc[-1]
    
    print(f"\n{ticker}:")
    print(f"  Ár: ${latest['close']:.2f}")
    print(f"  RSI: {latest['rsi']:.2f}")
    print(f"  vs SMA50: {latest['diff_sma50']:+.2f}%")
    print(f"  vs SMA200: {latest['diff_sma200']:+.2f}%")
```

### 4. példa: Adatok exportálása CSV-be
```python
from stock_data import StockData

# Adatok letöltése és feldolgozása
stock = StockData('SPY', range='10y', interval='1d')

# Mentés CSV-be
stock.df.to_csv('spy_elemzes.csv', index=False)
print("Adatok exportálva: spy_elemzes.csv")
```

### 5. példa: Forex párok elemzése
```python
from stock_data import StockData

# Major forex párok
major_pairs = ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X']

for pair in major_pairs:
    forex = StockData(pair, range='1y', interval='1d')
    latest = forex.df.iloc[-1]
    
    print(f"\n{pair}:")
    print(f"  Árfolyam: {latest['close']:.4f}")
    print(f"  RSI: {latest['rsi']:.2f}")
    print(f"  vs SMA50: {latest['diff_sma50']:+.2f}%")
    print(f"  vs SMA200: {latest['diff_sma200']:+.2f}%")

# EUR/USD részletes grafikon
eurusd = StockData('EURUSD=X', range='3y', interval='1d')
fig = eurusd.plot_smma_ribbon('EUR/USD - SMMA Ribbon Trend Analysis', ndays=1000)
fig.show()
```

## Megjegyzések

- **Napi adatokra tervezve:** Az osztály napi intervallumú elemzésre optimalizált, megfelelő indikátor periódusokkal
- **Csak napi felbontás:** Perces vagy órás adatokkal az indikátorok, lokális szélsőérték-detektálás és grafikonok nem működnek megfelelően
- **Dátum formátum:** yyyy.mm.dd (pl. 2025.01.03) - nap pontosság, időpont nélkül
- **Adatok elérhetősége:** A történelmi adatok elérhetősége a Yahoo Finance-tól és az adott tickertől függ

## Függőségek

- pandas
- pandas-ta
- plotly
- scipy
- numpy
- requests
- cloudscraper

## Licenc

Ez a projekt a Yahoo Finance API-t használja. Kérjük, tartsd be a Yahoo Finance felhasználási feltételeit.

## API dokumentáció

Yahoo Finance API dokumentáció: https://cryptocointracker.com/yahoo-finance/yahoo-finance-api
