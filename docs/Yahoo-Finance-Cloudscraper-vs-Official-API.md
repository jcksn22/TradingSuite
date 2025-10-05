# Yahoo Finance: Hivatalos API vs Cloudscraper összehasonlítás

A Yahoo Finance adatainak két fő elérési módja van: a hivatalos, fizetős API és a webes scraping megoldás. Ez a dokumentum részletesen összehasonlítja a két megközelítést, hogy segítsen eldönteni, melyik a legmegfelelőbb az adott projekthez.

## 💸 Árazási különbségek

### Hivatalos Yahoo Finance API (RapidAPI-n keresztül)

| Csomag | Ár/hó | Kérések száma | Ár/kérés |
|---------|-------------|----------|---------------|
| Basic | $0 | 500/hó | Ingyenes |
| Pro | $10 | 10,000/hó | $0.001 |
| Ultra | $30 | 50,000/hó | $0.0006 |
| Mega | $75+ | 100,000+/hó | $0.00075 |

### Cloudscraper "költségek"

| Szempont | Költség | Megjegyzés |
|--------|------|------|
| Licenc | $0 | Open source |
| API díjak | $0 | Nincsenek |
| Kérési limit | $0 | Soft limit (~60/perc) |
| Fejlesztési idő | Magas | Karbantartás szükséges |

**Példa kalkuláció:** Napi 1000 részvény × 365 nap = 365,000 kérés/év
- Hivatalos API: ~$275/év
- Cloudscraper: $0/év

## 🚀 Funkcionalitás összehasonlítása

### 1. Elérhető adatok

| Adattípus | Cloudscraper | Hivatalos API | Előny |
|-----------|--------------|--------------|-----------|
| Historikus OHLCV | ✅ Max 60 év | ✅ Max 30 nap (ingyenes) | Scraper |
| Intraday (1m, 5m) | ✅ 30 nap | ✅ 7 nap | Scraper |
| Real-time árfolyam | ✅ Igen | ✅ Igen | Egyenlő |
| Options láncok | ✅ Teljes | ⚠️ Korlátozott | Scraper |
| Fundamentális adatok | ✅ Teljes | ⚠️ Csomag függő | Scraper |
| Elemzői értékelések | ✅ Igen | ❌ Csak Premium | Scraper |
| Insider kereskedés | ✅ Igen | ❌ Csak Premium | Scraper |

### 2. Technikai paraméterek

| Paraméter | Cloudscraper | Hivatalos API |
|-----------|--------------|--------------|
| Max időtartam | "max" (IPO-tól) | 2 év (standard) |
| Intervallumok | 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo | Csomag függő |
| Batch kérések | Nem | Igen (Premium) |
| WebSocket | Nem | Igen (Premium) |

## 📈 Konkrét példák - Mit NEM tudsz az ingyenes hivatalos API-val

### 1. Hosszú időtávú historikus adatok

```python
# Cloudscraper - MŰKÖDIK
scraper.get("chart/AAPL?range=max")  # Minden adat 1980-tól

# Hivatalos API Basic - NEM MŰKÖDIK
api.get_history(period="max")  # Hiba: Max 1 hónap az ingyenes verzióban
```

### 2. Részletes fundamentális adatok

```python
# Cloudscraper - TELJES pénzügyi adatok
data = scraper.get("/quote/AAPL/financials")
# Eredmény: Összes negyedéves jelentés 5 évre visszamenőleg

# Hivatalos API Basic - KORLÁTOZOTT
data = api.get_financials("AAPL")  
# Eredmény: Csak kulcs mutatók, TTM (trailing twelve months)
```

### 3. Opciós adatok

```python
# Cloudscraper - TELJES opciós lánc
options = scraper.get("/quote/AAPL/options")
# Minden lejárat, minden strike ár

# Hivatalos API - FIZETŐS
# $50+/hó az opciós adatokért
```

## 🎯 Valós felhasználási esetek

### Mikor használj Cloudscraper-t?

#### 1. Backtesting/Kutatás

```python
# 10 éves historikus adat 500 részvényre
# Hivatalos API költség: ~$150/hó
# Cloudscraper: $0

for ticker in sp500_list:
    data = scraper.get(f"chart/{ticker}?range=10y&interval=1d")
    # 10 év × 252 kereskedési nap = 2520 adatpont/részvény
```

#### 2. Akadémiai/Hobbi projektek

- Egyetemi kutatás
- Személyes portfólió követő
- Kereskedési bot fejlesztés/tesztelés
- Gépi tanulás tanító adatok

#### 3. Szűrő alkalmazások

```python
# Fundamentális szűrő - teljes S&P 500
for ticker in sp500:
    financials = scraper.get(f"/quote/{ticker}/key-statistics")
    # P/E, P/B, ROE, Debt/Equity, stb.
# Hivatalos API: Premium csomag szükséges
```

### Mikor NE használj Cloudscraper-t?

#### 1. Éles kereskedési rendszer

```python
# ❌ ROSSZ: Kritikus kereskedési döntések
if scraper_data['price'] < limit:  
    execute_trade(1000000)  # Mi van, ha timeout/hiba lép fel?
```

#### 2. Kereskedelmi szolgáltatás

```python
# ❌ ROSSZ: SaaS alkalmazás
class TradingPlatform:
    def get_user_data(self):
        return scraper.get(...)  # ToS megsértés, jogi kockázat
```

#### 3. Nagy frekvenciájú/alacsony késleltetésű kereskedés

```python
# ❌ ROSSZ: HFT vagy arbitrage
while True:
    price = scraper.get(...)  # 200-500ms késleltetés
    # Hivatalos WebSocket: <10ms
```

## 📊 Teljesítmény összehasonlítása

| Metrika | Cloudscraper | Hivatalos API |
|--------|--------------|--------------|
| Késleltetés | 200-500ms | 50-100ms |
| Megbízhatóság | ~95% | ~99.9% |
| Rate limit | ~60/perc | Csomag függő |
| Párhuzamos kérések | 5-10 | 100+ (Premium) |
| Uptime garancia | Nincs | SLA 99.9% |

## 🔧 Gyakorlati megoldás: hibrid megközelítés

```python
class HybridDataProvider:
    """Egyesíti mindkét megoldás előnyeit"""
    
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.official_api = YahooFinanceAPI(key="...")
        self.cache = {}
    
    def get_realtime_quote(self, ticker):
        """Kritikus real-time adat - hivatalos API"""
        return self.official_api.get_quote(ticker)
    
    def get_historical_data(self, ticker, years=10):
        """Nem kritikus historikus adat - scraper"""
        if ticker in self.cache:
            return self.cache[ticker]
        
        try:
            # Először próbáld a scraper-t (ingyenes)
            data = self.scraper.get(f"chart/{ticker}?range={years}y")
            self.cache[ticker] = data
            return data
        except:
            # Fallback a hivatalos API-ra
            return self.official_api.get_history(ticker, period="max")
    
    def get_critical_trade_signal(self, ticker):
        """Kritikus kereskedési jel - CSAK hivatalos"""
        return self.official_api.get_realtime(ticker)
```

## 💡 Költség-haszon elemzés

### Kis projekt (Hobbi/Kutatás)

- Éves költség hivatalos API: $120-360
- Cloudscraper költség: $0
- Megtakarítás: $120-360/év
- Kockázat: Alacsony (nem kritikus)
- **Döntés: ✅ Cloudscraper**

### Közepes projekt (Startup/Kisvállalat)

- Éves költség hivatalos API: $900-2400
- Cloudscraper karbantartás: ~20 óra/év × $50 = $1000
- Megtakarítás: -$100 és $1400 között
- Kockázat: Közepes
- **Döntés: ⚠️ Hibrid megoldás**

### Nagy projekt (Nagyvállalat)

- Éves költség hivatalos API: $10,000+
- Cloudscraper kockázat: Reputáció, jogi, uptime
- Alternatíva: Bloomberg Terminal ($24,000/év)
- **Döntés: ❌ Hivatalos API/Bloomberg**

## 🎯 Végső következtetés

### Cloudscraper előnyei:

1. **INGYENES** - Ez a fő ok
2. **Több adat** - Hosszabb történelmi adatok, több endpoint
3. **Nincs limit** - Csak soft rate limit
4. **Teljes hozzáférés** - Minden, ami a weben elérhető

### Hivatalos API előnyei:

1. **Megbízhatóság** - SLA, támogatás
2. **Sebesség** - Alacsonyabb késleltetés
3. **Legalitás** - Nincs ToS (felhasználási feltételek) probléma
4. **Stabilitás** - Nem törik el frissítések miatt
5. **Támogatás** - Van kihez fordulni problémák esetén

### A valóság:

- **80% hobbi projektek:** Cloudscraper
- **15% semi-professional:** Hibrid megoldás
- **5% professional:** Hivatalos API

---

## 🚀 Kezdő lépések

### Cloudscraper telepítése és használata

#### Alaptelepítés

```bash
# Telepítés pip-pel
pip install cloudscraper

# Vagy requirements.txt-ben
echo "cloudscraper>=1.2.71" >> requirements.txt
pip install -r requirements.txt
```

#### Első lépések kóddal

```python
import cloudscraper
import json

# Scraper létrehozása
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

# Yahoo Finance base URL
base_url = "https://query1.finance.yahoo.com/v8/finance"

# Példa: Historikus adatok lekérése
def get_historical_data(ticker, period="1y", interval="1d"):
    """
    Historikus OHLCV adatok lekérése
    
    Args:
        ticker: Részvény szimbólum (pl. "AAPL")
        period: Időszak (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Intervallum (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    """
    url = f"{base_url}/chart/{ticker}"
    params = {
        "range": period,
        "interval": interval,
        "includePrePost": "false"
    }
    
    response = scraper.get(url, params=params)
    data = response.json()
    
    return data['chart']['result'][0]

# Példa használat
apple_data = get_historical_data("AAPL", period="1y", interval="1d")
print(json.dumps(apple_data, indent=2))
```

#### Haladó használat - több endpoint

```python
# Real-time árfolyam
def get_quote(ticker):
    """Aktuális árfolyam és alapadatok"""
    url = f"{base_url}/quote"
    params = {"symbols": ticker}
    response = scraper.get(url, params=params)
    return response.json()

# Fundamentális adatok
def get_financials(ticker):
    """Pénzügyi kimutatások"""
    url = f"https://finance.yahoo.com/quote/{ticker}/financials"
    response = scraper.get(url)
    # HTML parsing szükséges (BeautifulSoup vagy lxml)
    return response.text

# Options lánc
def get_options_chain(ticker):
    """Opciós lánc adatok"""
    url = f"{base_url}/options/{ticker}"
    response = scraper.get(url)
    return response.json()

# Múltbeli dividend és split adatok
def get_dividends(ticker):
    """Osztalék történet"""
    url = f"{base_url}/chart/{ticker}"
    params = {
        "range": "max",
        "interval": "1d",
        "events": "div,split"
    }
    response = scraper.get(url, params=params)
    return response.json()
```

#### Rate limiting és hibakezelés

```python
import time
from requests.exceptions import RequestException

def safe_get(scraper, url, max_retries=3, delay=1):
    """
    Biztonságos GET kérés retry logikával
    """
    for attempt in range(max_retries):
        try:
            response = scraper.get(url)
            response.raise_for_status()
            
            # Rate limiting - ne bombázzuk a szervert
            time.sleep(delay)
            
            return response.json()
        except RequestException as e:
            if attempt == max_retries - 1:
                raise
            print(f"Hiba történt, újrapróbálás {attempt + 1}/{max_retries}...")
            time.sleep(delay * (attempt + 1))
```

### Hivatalos API Beállítása (RapidAPI)

#### Regisztráció és API kulcs beszerzése

1. Regisztráció a [RapidAPI](https://rapidapi.com/) oldalon
2. Keresés: "Yahoo Finance API"
3. Válassz egy csomagot (Basic $0-tól)
4. Másold ki az API kulcsot a Dashboard-ról

#### Python használat hivatalos API-val

```bash
# Telepítsd a requests könyvtárat
pip install requests python-dotenv
```

```python
import requests
import os
from dotenv import load_dotenv

# Töltsd be a környezeti változókat
load_dotenv()

class YahooFinanceAPI:
    def __init__(self):
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.base_url = "https://yahoo-finance15.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "yahoo-finance15.p.rapidapi.com"
        }
    
    def get_quote(self, ticker):
        """Real-time árfolyam"""
        url = f"{self.base_url}/api/v1/markets/quote"
        params = {"ticker": ticker}
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()
    
    def get_historical(self, ticker, period="1mo"):
        """Historikus adatok (limitált az ingyenes verzióban)"""
        url = f"{self.base_url}/api/v1/markets/stock/history"
        params = {
            "symbol": ticker,
            "interval": "1d",
            "diffandsplits": "false"
        }
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

# Használat
api = YahooFinanceAPI()
quote = api.get_quote("AAPL")
print(quote)
```

#### .env fájl beállítása

```bash
# Hozz létre egy .env fájlt a projekt gyökérkönyvtárában
RAPIDAPI_KEY=your_api_key_here
```

### Függőségek

#### Cloudscraper megoldáshoz

```txt
cloudscraper>=1.2.71
requests>=2.28.0
beautifulsoup4>=4.11.0  # HTML parsing-hez
lxml>=4.9.0  # Gyorsabb HTML parsing
pandas>=1.5.0  # Adatelemzéshez (opcionális)
```

#### Hivatalos API megoldáshoz

```txt
requests>=2.28.0
python-dotenv>=0.21.0  # Környezeti változók kezeléséhez
```

### Docker használat (opcionális)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "your_script.py"]
```

```bash
# Build
docker build -t yahoo-finance-scraper .

# Run
docker run -e RAPIDAPI_KEY=your_key yahoo-finance-scraper
```

## 📚 További hasznos információk

### Elérhető Yahoo Finance endpointok

#### Cloudscraper-rel elérhető főbb endpointok:

```python
# 1. Chart/Historikus adatok
f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
# Paraméterek: range, interval, events (div, split)

# 2. Quote - Real-time ár
f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={ticker}"

# 3. Options
f"https://query1.finance.yahoo.com/v7/finance/options/{ticker}"

# 4. Spark (mini chart adatok)
f"https://query1.finance.yahoo.com/v7/finance/spark?symbols={ticker}"

# 5. News
f"https://query1.finance.yahoo.com/v1/finance/search?q={ticker}"

# 6. Trending tickers
"https://query1.finance.yahoo.com/v1/finance/trending/US"

# 7. Market summary
"https://query1.finance.yahoo.com/v6/finance/quote/marketSummary"

# 8. Screener eredmények
"https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved"
```

### Gyakori hibák és megoldásaik

#### 1. Rate limiting (429 hiba)

```python
import time
from functools import wraps

def rate_limit(max_per_minute=60):
    """Dekorátor rate limiting-hez"""
    min_interval = 60.0 / max_per_minute
    
    def decorator(func):
        last_called = [0.0]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        
        return wrapper
    return decorator

# Használat
@rate_limit(max_per_minute=50)
def get_data(ticker):
    return scraper.get(f"chart/{ticker}")
```

#### 2. Cloudflare védelem megkerülése

```python
# Haladó scraper konfiguráció
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    },
    delay=10,  # Késleltetés Cloudflare kihívás megoldásához
    captcha={
        'provider': '2captcha',  # Opcionális: captcha szolgáltatás
        'api_key': 'your_api_key'
    }
)
```

#### 3. Timeout hibák kezelése

```python
from requests.exceptions import Timeout

def get_with_timeout(url, timeout=10, retries=3):
    """Timeout kezeléssel rendelkező GET kérés"""
    for i in range(retries):
        try:
            response = scraper.get(url, timeout=timeout)
            return response.json()
        except Timeout:
            if i == retries - 1:
                raise
            print(f"Timeout, újrapróbálás... ({i+1}/{retries})")
            time.sleep(2 ** i)  # Exponenciális backoff
```

### Adatok tárolása és cache-elése

#### SQLite cache példa

```python
import sqlite3
import json
from datetime import datetime, timedelta

class DataCache:
    def __init__(self, db_path='yahoo_cache.db'):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS cache (
                ticker TEXT,
                data_type TEXT,
                data TEXT,
                timestamp DATETIME,
                PRIMARY KEY (ticker, data_type)
            )
        ''')
    
    def get(self, ticker, data_type, max_age_hours=1):
        """Cache-ből olvas, ha friss az adat"""
        cursor = self.conn.execute(
            'SELECT data, timestamp FROM cache WHERE ticker=? AND data_type=?',
            (ticker, data_type)
        )
        row = cursor.fetchone()
        
        if row:
            data, timestamp = row
            cache_time = datetime.fromisoformat(timestamp)
            if datetime.now() - cache_time < timedelta(hours=max_age_hours):
                return json.loads(data)
        
        return None
    
    def set(self, ticker, data_type, data):
        """Adatok cache-elése"""
        self.conn.execute(
            'INSERT OR REPLACE INTO cache VALUES (?, ?, ?, ?)',
            (ticker, data_type, json.dumps(data), datetime.now().isoformat())
        )
        self.conn.commit()

# Használat
cache = DataCache()

def get_cached_data(ticker):
    # Először cache-ből próbáld
    cached = cache.get(ticker, 'historical')
    if cached:
        return cached
    
    # Ha nincs cache-ben, lekérjük
    data = scraper.get(f"chart/{ticker}?range=1y").json()
    cache.set(ticker, 'historical', data)
    return data
```

#### Redis cache (production környezethez)

```python
import redis
import json

class RedisCache:
    def __init__(self, host='localhost', port=6379, ttl=3600):
        self.redis = redis.Redis(host=host, port=port, decode_responses=True)
        self.ttl = ttl
    
    def get(self, key):
        data = self.redis.get(key)
        return json.loads(data) if data else None
    
    def set(self, key, value):
        self.redis.setex(key, self.ttl, json.dumps(value))

# Használat
cache = RedisCache(ttl=3600)  # 1 óra TTL

def get_quote_cached(ticker):
    cache_key = f"quote:{ticker}"
    cached = cache.get(cache_key)
    
    if cached:
        return cached
    
    data = scraper.get(f"quote?symbols={ticker}").json()
    cache.set(cache_key, data)
    return data
```

### Adatok feldolgozása Pandas-szal

```python
import pandas as pd
from datetime import datetime

def parse_yahoo_data(ticker, period="1y"):
    """Yahoo Finance adatok Pandas DataFrame-be"""
    response = scraper.get(
        f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}",
        params={"range": period, "interval": "1d"}
    )
    data = response.json()
    
    result = data['chart']['result'][0]
    timestamps = result['timestamp']
    quote = result['indicators']['quote'][0]
    
    df = pd.DataFrame({
        'date': pd.to_datetime(timestamps, unit='s'),
        'open': quote['open'],
        'high': quote['high'],
        'low': quote['low'],
        'close': quote['close'],
        'volume': quote['volume']
    })
    
    df.set_index('date', inplace=True)
    return df

# Használat
df = parse_yahoo_data('AAPL', period='1mo')
print(df.head())

# Technikai indikátorok számítása
df['SMA_20'] = df['close'].rolling(window=20).mean()
df['SMA_50'] = df['close'].rolling(window=50).mean()
df['daily_return'] = df['close'].pct_change()

# Export
df.to_csv('aapl_data.csv')
df.to_excel('aapl_data.xlsx')
```

### Teljesítmény optimalizálás

#### Párhuzamos lekérések

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_multiple_tickers(tickers, max_workers=5):
    """
    Több ticker párhuzamos lekérése
    FIGYELEM: Ne állítsd túl magasra a max_workers-t (rate limit!)
    """
    results = {}
    
    def fetch_ticker(ticker):
        try:
            data = scraper.get(f"chart/{ticker}?range=1d").json()
            return ticker, data
        except Exception as e:
            return ticker, None
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_ticker, t): t for t in tickers}
        
        for future in as_completed(futures):
            ticker, data = future.result()
            results[ticker] = data
            
    return results

# Használat
sp500_sample = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
data = fetch_multiple_tickers(sp500_sample, max_workers=3)
```

### Jogszabályi és etikai megfontolások

#### ⚖️ Jogi szempontok

1. **Yahoo Finance ToS**: A scraping technikailag sérti a felhasználási feltételeket
2. **CFAA (Computer Fraud and Abuse Act)**: USA-ban potenciálisan illegális
3. **EU GDPR**: Személyes adatok kezelésére vonatkozó szabályok
4. **Kereskedelmi használat**: Kifejezetten tilos hivatalos engedély nélkül

#### 🤝 Etikus használat

```python
# JÓ gyakorlatok
✅ Ésszerű rate limiting (max 60 req/perc)
✅ User-Agent beállítása
✅ Csak publikus adatok
✅ Nem kereskedelmi célra
✅ Cache használata az ismételt kérések elkerülésére

# ROSSZ gyakorlatok  
❌ Agresszív scraping (100+ req/perc)
❌ Fake User-Agent
❌ Kereskedelmi szolgáltatás alapja
❌ Adatok újra értékesítése
❌ Védett tartalom letöltése
```

### Alternatív adatforrások

Ha a Yahoo Finance nem elegendő vagy problémás:

```python
# Alpha Vantage API (ingyenes tier)
# https://www.alphavantage.co
# Limit: 5 kérés/perc, 500 kérés/nap

# Finnhub API (ingyenes tier)
# https://finnhub.io
# Limit: 60 kérés/perc

# IEX Cloud (ingyenes tier)
# https://iexcloud.io
# Limit: 50,000 kérés/hó

# Polygon.io (fizetős)
# https://polygon.io
# Limit: Nincs (tier függő)

# yfinance Python könyvtár
pip install yfinance
import yfinance as yf
ticker = yf.Ticker("AAPL")
hist = ticker.history(period="1mo")
```

### Monitoring és naplózás

```python
import logging
from datetime import datetime

# Logging beállítása
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('yahoo_scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('YahooScraper')

def monitored_request(ticker):
    """Monitorozott kérés naplózással"""
    start_time = datetime.now()
    
    try:
        logger.info(f"Fetching data for {ticker}")
        response = scraper.get(f"chart/{ticker}")
        
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"Success: {ticker} in {elapsed:.2f}s")
        
        return response.json()
    except Exception as e:
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.error(f"Error fetching {ticker} after {elapsed:.2f}s: {str(e)}")
        raise
```

### Tesztelés

```python
import unittest
from unittest.mock import patch, Mock

class TestYahooScraper(unittest.TestCase):
    
    def setUp(self):
        self.scraper = cloudscraper.create_scraper()
    
    @patch('cloudscraper.CloudScraper.get')
    def test_get_quote(self, mock_get):
        """Quote endpoint tesztelése"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'quoteResponse': {
                'result': [{'symbol': 'AAPL', 'regularMarketPrice': 150.0}]
            }
        }
        mock_get.return_value = mock_response
        
        result = get_quote('AAPL')
        self.assertEqual(result['quoteResponse']['result'][0]['symbol'], 'AAPL')
    
    def test_rate_limiting(self):
        """Rate limiting működésének tesztelése"""
        start = time.time()
        
        @rate_limit(max_per_minute=30)
        def dummy_request():
            return True
        
        # 3 kérés
        for _ in range(3):
            dummy_request()
        
        elapsed = time.time() - start
        # Legalább 4 másodperc kellene (2 sec/kérés 30/perc limit mellett)
        self.assertGreater(elapsed, 4)

if __name__ == '__main__':
    unittest.main()
```

## Fontos
- A web scraping technikailag sértheti a Yahoo Finance szolgáltatási feltételeit
- Kereskedelmi felhasználáshoz mindig szerezz hivatalos engedélyt
- Ez a dokumentum nem jelent jogi tanácsadást
- A szerzők nem vállalnak felelősséget az itt leírt módszerek használatából eredő következményekért

## 📞 Kapcsolat és további források

- [Yahoo Finance hivatalos oldal](https://finance.yahoo.com)
- [RapidAPI Yahoo Finance API](https://rapidapi.com/apidojo/api/yahoo-finance1)
- [Cloudscraper GitHub](https://github.com/venomous/cloudscraper)
- [yfinance könyvtár](https://github.com/ranaroussi/yfinance)
- [Pandas dokumentáció](https://pandas.pydata.org/docs/)
