import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
import json
import logging
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradingViewData:
    def __init__(self, auto_load: bool = True):
        """ 
        Inicializálja a TradingViewData osztályt, amely a TradingView adatok lekéréséért felelős.
        
        A konstruktor létrehozza az üres DataFrame-eket a részvények, kriptovaluták és ETF-ek
        tárolására. Opcionálisan automatikusan letölti az összes adatot az inicializálás során.
        
        Parameters:
        - auto_load: Ha True, automatikusan betölti az összes adatot inicializáláskor
        
        Működés:
        1. Inicializálja az üres DataFrame-eket
        2. Ha auto_load=True, meghívja a load_all_data() metódust
        """
        self.us_stock = pd.DataFrame()
        self.eu_stock = pd.DataFrame()
        self.crypto = pd.DataFrame()
        self.us_etf = pd.DataFrame()
        
        if auto_load:
            self.load_all_data()
    
    def load_all_data(self):
        """Betölti az összes adatot (US részvények, kripto, ETF)"""
        self.get_us_stocks()
        self.get_all_crypto()
        self.get_us_etfs()
        self.get_eu_stocks()

    def _make_request(self, url: str, data_query: str) -> Optional[Dict[str, Any]]:
        """
        HTTP kérés végrehajtása hibakezeléssel
        
        Paraméterek:
        - url: API végpont URL címe
        - data_query: JSON query string
        
        Visszatérési érték:
        - Válasz JSON vagy None hiba esetén
        """
        try:
            response = requests.post(url, data=data_query, timeout=30)
            response.raise_for_status()  # Kivételt dob rossz státuszkódok esetén
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Sikertelen kérés {url}: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON válasz dekódolása sikertelen: {str(e)}")
            return None

    def get_us_stocks(self) -> bool:
        """ 
        Letölti az összes amerikai tőzsdén (AMEX, NASDAQ, NYSE) jegyzett részvény adatát a TradingView-ról.
        
        Ez a függvény egy nem hivatalos TradingView scanner API végpontot használ, amely körülbelül
        8000 részvény adatát kéri le egyetlen HTTP POST kérésben. A lekért adatok között szerepel
        az árfolyam, piaci kapitalizáció, technikai indikátorok, teljesítmény mutatók és más
        fundamentális adatok.
        
        Returns:
        - True ha sikeres, False egyébként
        
        Működés:
        1. Strukturált query dictionary építése a karbantarthatóság érdekében
        2. HTTP POST kérés küldése a TradingView scanner API-nak
        3. Válasz feldolgozása és DataFrame létrehozása
        4. Szűrés: pont karaktert tartalmazó ticker-ek kizárása, pl. BRK.A, BRK.B (Berkshire Hathaway)
        5. Index újraszámozás és log üzenet
        
        Hibakezelés:
        - HTTP kérés hibák kezelése
        - JSON dekódolási hibák kezelése
        - Adatfeldolgozási hibák kezelése
        """
        
        # Részvény adatmezők definiálása
        stock_columns = [
            "logoid",                     # Logo azonosító
            "name",                       # Ticker szimbólum (pl. AAPL, MSFT)
            "close",                      # Záróárfolyam
            "change",                     # Árfolyamváltozás %
            "change_abs",                 # Árfolyamváltozás abszolút értékben
            "Recommend.All",              # Összesített ajánlás
            "volume",                     # Forgalom (darabszám)
            "Value.Traded",               # Forgalmazott érték dollárban
            "market_cap_basic",           # Piaci kapitalizáció
            "price_earnings_ttm",         # P/E ráta (TTM)
            "earnings_per_share_basic_ttm", # EPS (TTM)
            "number_of_employees",        # Alkalmazottak száma
            "sector",                     # Szektor
            "High.3M",                    # 3 havi maximum
            "Low.3M",                     # 3 havi minimum
            "Perf.3M",                    # 3 havi teljesítmény %
            "Perf.5Y",                    # 5 éves teljesítmény %
            "High.1M",                    # 1 havi maximum
            "Low.1M",                     # 1 havi minimum
            "High.6M",                    # 6 havi maximum
            "Low.6M",                     # 6 havi minimum
            "Perf.6M",                    # 6 havi teljesítmény %
            "beta_1_year",                # Beta (1 év)
            "price_52_week_high",         # 52 hetes maximum
            "price_52_week_low",          # 52 hetes minimum
            "High.All",                   # Historikus maximum
            "Low.All",                    # Historikus minimum
            "BB.lower",                   # Bollinger alsó sáv
            "BB.upper",                   # Bollinger felső sáv
            "change|1M",                  # 1 havi változás %
            "change_abs|1M",              # 1 havi változás abszolút
            "change|1W",                  # 1 heti változás %
            "change_abs|1W",              # 1 heti változás abszolút
            "change|240",                 # 240 napos változás %
            "country",                    # Ország
            "EMA50",                      # 50 napos exponenciális mozgóátlag
            "EMA100",                     # 100 napos exponenciális mozgóátlag
            "EMA200",                     # 200 napos exponenciális mozgóátlag
            "MACD.macd",                  # MACD érték
            "MACD.signal",                # MACD signal
            "Mom",                        # Momentum
            "Perf.1M",                    # 1 havi teljesítmény %
            "RSI7",                       # RSI 7 napos
            "SMA50",                      # 50 napos egyszerű mozgóátlag
            "SMA100",                     # 100 napos egyszerű mozgóátlag
            "SMA200",                     # 200 napos egyszerű mozgóátlag
            "Stoch.RSI.K",                # Stochastic RSI K
            "Stoch.RSI.D",                # Stochastic RSI D
            "Perf.W",                     # Heti teljesítmény %
            "Perf.Y",                     # Éves teljesítmény %
            "Perf.YTD",                   # Év eleji teljesítmény %
            "industry",                   # Iparág
            "Perf.All",                   # Teljes historikus teljesítmény %
            "description",                # Cég teljes neve
            "type",                       # Instrumentum típus
            "subtype",                    # Altípus
            "update_mode",                # Frissítési mód
            "pricescale",                 # Ár skála
            "minmov",                     # Minimális mozgás
            "fractional",                 # Töredék kereskedés
            "minmove2",                   # Alternatív min. mozgás
            "Mom[1]",                     # Momentum előző nap
            "RSI7[1]",                    # RSI előző nap
            "Rec.Stoch.RSI",              # Stochastic RSI ajánlás
            "currency",                   # Kereskedési deviza
            "fundamental_currency_code"    # Alapdeviza kód
        ]
        
        query = {
            "filter": [
                {"left": "type", "operation": "in_range", "right": ["stock", "dr", "fund"]},
                {"left": "subtype", "operation": "in_range", 
                 "right": ["common", "foreign-issuer", "", "etf", "etf,odd", "etf,otc", "etf,cfd"]},
                {"left": "exchange", "operation": "in_range", "right": ["AMEX", "NASDAQ", "NYSE"]},
                {"left": "is_primary", "operation": "equal", "right": True},
                {"left": "active_symbol", "operation": "equal", "right": True}
            ],
            "options": {"lang": "en"},
            "markets": ["america"],
            "symbols": {"query": {"types": []}, "tickers": []},
            "columns": stock_columns,
            "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
            "range": [0, 8000]
        }
        
        data_query = json.dumps(query)
        data = self._make_request('https://scanner.tradingview.com/america/scan', data_query)
        
        if data is None or 'data' not in data:
            logger.error("Nem sikerült letölteni a részvényadatokat")
            return False
        
        try:
            list_elements = list(map(lambda x: x['d'], data['data']))
            self.us_stock = pd.DataFrame(list_elements)
            self.us_stock.columns = stock_columns
            
            # Pont karakteres ticker-ek kiszűrése (pl. BRK.A, BRK.B)
            self.us_stock = self.us_stock[~self.us_stock['name'].str.contains('\\.', na=False)]
            self.us_stock.reset_index(inplace=True, drop=True)
            
            logger.info(f"Sikeresen betöltve {len(self.us_stock)} amerikai részvény")
            return True
            
        except (KeyError, ValueError) as e:
            logger.error(f"Hiba a részvényadatok feldolgozásakor: {str(e)}")
            return False
    
    def get_all_crypto(self) -> bool:
        """
        Letölti a top 300 kriptovaluta adatát a TradingView-ról, piaci kapitalizáció szerinti rangsorolásban.
        
        A függvény a TradingView coin scanner API-t használja, amely kriptovaluta-specifikus
        adatokat szolgáltat, mint például: alapvaluta, piaci kapitalizáció, 24 órás forgalom,
        forgalomban lévő mennyiség, blockchain ökoszisztémák és kategóriák.
        
        Returns:
        - True ha sikeres, False egyébként
        
        Működés:
        1. Query összeállítása kripto-specifikus mezőkkel
        2. API hívás a coin scanner végpontra
        3. Adatok feldolgozása és DataFrame létrehozása
        4. Stablecoin-ok kiszűrése (nem volatilis kriptók)
        5. USD párok ticker generálása (pl. BTC-USD)
        
        Speciális feldolgozás:
        - Automatikusan kiszűri a stablecoin-okat
        - Hozzáad egy 'ticker' oszlopot USD párral
        """
        
        # Kriptovaluta adatmezők definiálása
        crypto_columns = [
            "base_currency",              # Alap szimbólum (pl. BTC, ETH)
            "base_currency_desc",         # Teljes név (pl. Bitcoin, Ethereum)
            "base_currency_logoid",       # Logo azonosító
            "update_mode",                # Frissítési mód
            "type",                       # Instrumentum típus
            "typespecs",                  # Típus specifikáció
            "exchange",                   # Tőzsde/platform
            "crypto_total_rank",          # Általános rangsor
            "close",                      # Aktuális árfolyam USD-ben
            "pricescale",                 # Ár skála
            "minmov",                     # Minimális ármozgás
            "fractional",                 # Töredék kereskedés
            "minmove2",                   # Alternatív minimális mozgás
            "currency",                   # Jegyzési deviza (általában USD)
            "24h_close_change|5",         # 24 órás változás százalékban
            "market_cap_calc",            # Piaci kapitalizáció
            "fundamental_currency_code",   # Alap devizakód
            "24h_vol_cmc",                # 24 órás forgalom (CoinMarketCap)
            "circulating_supply",         # Forgalomban lévő mennyiség
            "crypto_common_categories",   # Kategóriák (pl. DeFi, layer-1)
            "crypto_blockchain_ecosystems" # Blockchain ökoszisztéma
        ]
        
        query = {
            "columns": crypto_columns,
            "ignore_unknown_fields": False,
            "options": {"lang": "en"},
            "range": [0, 300],
            "sort": {"sortBy": "crypto_total_rank", "sortOrder": "asc"},
            "markets": ["coin"]
        }
        
        data_query = json.dumps(query)
        data = self._make_request('https://scanner.tradingview.com/coin/scan', data_query)
        
        if data is None or 'data' not in data:
            logger.error("Nem sikerült letölteni a kripto adatokat")
            return False
        
        try:
            list_elements = list(map(lambda x: x['d'], data['data']))
            self.crypto = pd.DataFrame(list_elements)
            self.crypto.columns = crypto_columns
            
            # Stablecoin-ok kiszűrése
            filter_mask = self.crypto['crypto_common_categories'].fillna('-').apply(
                lambda x: 'stablecoins' not in x if isinstance(x, str) else True
            )
            self.crypto = self.crypto[filter_mask]
            
            # USD párok ticker generálása a könnyebb kereséshez
            self.crypto['ticker'] = self.crypto['base_currency'] + '-USD'
            
            self.crypto.reset_index(inplace=True, drop=True)
            
            logger.info(f"Sikeresen betöltve {len(self.crypto)} kriptovaluta")
            return True
            
        except (KeyError, ValueError) as e:
            logger.error(f"Hiba a kripto adatok feldolgozásakor: {str(e)}")
            return False
    
    def get_us_etfs(self) -> bool:
        """
        Letölti az amerikai ETF-ek (Exchange Traded Funds) adatait a TradingView-ról, AUM szerint rendezve.
        
        Az ETF-ek tőzsdén kereskedett alapok, amelyek index vagy árupiaci kosarakat követnek.
        A függvény körülbelül 3000 ETF adatát tölti le, beleértve az ETN-eket (Exchange Traded Notes) is.
        
        Returns:
        - True ha sikeres, False egyébként
        
        Működés:
        1. Komplex szűrő query építése ETF és ETN típusokra
        2. API hívás AUM (Assets Under Management) szerinti rendezéssel
        3. DataFrame létrehozása és oszlopnevek hozzárendelése
        4. Pont karaktert tartalmazó ticker-ek kiszűrése
        """
        
        # ETF adatmezők definiálása
        etf_columns = [
            "name",                      # Ticker szimbólum
            "description",               # ETF teljes neve
            "logoid",                    # Logo azonosító
            "update_mode",               # Frissítési mód
            "type",                      # Instrumentum típus
            "typespecs",                 # Típus specifikáció (ETF/ETN)
            "close",                     # Aktuális/záró árfolyam
            "pricescale",                # Ár skála
            "minmov",                    # Minimális ármozgás
            "fractional",                # Töredék kereskedés támogatott-e
            "minmove2",                  # Alternatív minimális mozgás
            "currency",                  # Kereskedési devizanem
            "change",                    # Árfolyamváltozás
            "Value.Traded",              # Forgalmazott érték
            "relative_volume_10d_calc",  # 10 napos relatív volumen
            "aum",                       # Assets Under Management (kezelt vagyon)
            "fundamental_currency_code",  # Alapdeviza kód
            "nav_total_return.5Y",       # 5 éves NAV teljes hozam
            "expense_ratio",             # Költségráta
            "asset_class.tr",            # Eszközosztály
            "focus.tr",                  # Befektetési fókusz
            "nav_discount_premium",      # NAV diszkont vagy prémium
            "category.tr",               # ETF kategória
            "brand.tr",                  # Kibocsátó márka
            "niche.tr"                   # Speciális piaci szegmens
        ]
        
        query = {
            "columns": etf_columns,
            "ignore_unknown_fields": False,
            "options": {"lang": "en"},
            "price_conversion": {"to_symbol": True},
            "range": [0, 3000],
            "sort": {"sortBy": "aum", "sortOrder": "desc"},
            "markets": ["america"],
            "filter2": {
                "operator": "and",
                "operands": [{
                    "operation": {
                        "operator": "or",
                        "operands": [
                            {"operation": {"operator": "and", 
                                         "operands": [{"expression": {"left": "typespecs", 
                                                                     "operation": "has", 
                                                                     "right": ["etn"]}}]}},
                            {"operation": {"operator": "and", 
                                         "operands": [{"expression": {"left": "typespecs", 
                                                                     "operation": "has", 
                                                                     "right": ["etf"]}}]}}
                        ]
                    }
                }]
            }
        }
        
        data_query = json.dumps(query)
        data = self._make_request('https://scanner.tradingview.com/america/scan', data_query)
        
        if data is None or 'data' not in data:
            logger.error("Nem sikerült letölteni az ETF adatokat")
            return False
        
        try:
            list_elements = list(map(lambda x: x['d'], data['data']))
            self.us_etf = pd.DataFrame(list_elements)
            self.us_etf.columns = etf_columns
            
            # Pont karakteres ticker-ek kiszűrése
            self.us_etf = self.us_etf[~self.us_etf['name'].str.contains('\\.', na=False)]
            self.us_etf.reset_index(inplace=True, drop=True)
            
            logger.info(f"Sikeresen betöltve {len(self.us_etf)} amerikai ETF")
            return True
            
        except (KeyError, ValueError) as e:
            logger.error(f"ETF adatok feldolgozási hiba: {str(e)}")
            return False
    
    def get_eu_stocks(self, markets: list = None, replace: bool = True) -> bool:
        """
        Letölti az európai tőzsdék részvényadatait a TradingView-ról.
        
        Az európai piacok külön scanner végpontokon érhetők el, minden országhoz
        külön API hívást kell végezni. Az eredmények egyetlen DataFrame-be kerülnek
        összefűzve.
        
        Parameters:
        - markets: európai piacok listája, alapértelmezetten ['uk', 'germany', 'poland']
        - replace: True esetén felülírja a meglévő adatokat, False esetén hozzáadja
        
        Returns:
        - True ha sikeres, False egyébként
        
        Támogatott piacok:
        - 'uk': London Stock Exchange (LSE, AIM)
        - 'germany': német tőzsdék (XETR, FSE, SWB, HAM, DUS, BER, STU, MUN)
        - 'poland': Warsaw Stock Exchange (WSE)
        
        Működés:
        1. Végigiterál a megadott piacokon
        2. Minden piachoz külön API hívást végez
        3. Összefűzi a DataFrame-eket
        4. Hozzáadja a régió információt
        5. Eltávolítja a pont karakteres ticker-eket
        6. Replace paraméter alapján felülír vagy hozzáad

        Hiányzó mezők az európai API-ból:
        - Technikai indikátorok:
            SMA50, SMA100, SMA200 (mozgóátlagok)
            EMA50, EMA100, EMA200 (exponenciális mozgóátlagok)
            RSI7 (Relative Strength Index)
            MACD.macd, MACD.signal
            Stoch.RSI.K, Stoch.RSI.D
            Bollinger sávok (BB.lower, BB.upper)
            Momentum indikátorok        
        - Historikus árak:
            High.1M, Low.1M (1 havi)
            High.3M, Low.3M (3 havi)
            High.6M, Low.6M (6 havi)
            High.All, Low.All (historikus)
            price_52_week_high, price_52_week_low
        """
        if markets is None:
            markets = ['uk', 'germany', 'poland']
        
        all_eu_stocks = []
        
        # Európai részvény adatmezők definiálása
        eu_stock_columns = [
            "logoid",                     # Logo azonosító
            "name",                       # Ticker szimbólum
            "close",                      # Záróárfolyam
            "change",                     # Árfolyamváltozás %
            "change_abs",                 # Árfolyamváltozás abszolút
            "Recommend.All",              # Összesített ajánlás
            "volume",                     # Forgalom
            "Value.Traded",               # Forgalmazott érték
            "market_cap_basic",           # Piaci kapitalizáció
            "price_earnings_ttm",         # P/E ráta (TTM)
            "earnings_per_share_basic_ttm", # EPS (TTM)
            "number_of_employees",        # Alkalmazottak száma
            "sector",                     # Szektor
            "Perf.3M",                    # 3 havi teljesítmény %
            "Perf.5Y",                    # 5 éves teljesítmény %
            "Perf.1M",                    # 1 havi teljesítmény %
            "Perf.6M",                    # 6 havi teljesítmény %
            "Perf.W",                     # Heti teljesítmény %
            "Perf.Y",                     # Éves teljesítmény %
            "Perf.YTD",                   # Év eleji teljesítmény %
            "industry",                   # Iparág
            "Perf.All",                   # Teljes historikus teljesítmény %
            "description",                # Cég teljes neve
            "type",                       # Instrumentum típus
            "currency",                   # Kereskedési deviza
            "exchange"                    # Tőzsde neve
        ]
        
        # Piaci beállítások
        market_configs = {
            'uk': {
                'url': 'https://scanner.tradingview.com/uk/scan',
                'exchanges': ['LSE', 'AIM'],
                'currency': 'GBP'
            },
            'germany': {
                'url': 'https://scanner.tradingview.com/germany/scan',
                'exchanges': ['XETR', 'FSE', 'SWB', 'HAM', 'DUS', 'BER', 'STU', 'MUN'],
                'currency': 'EUR'
            },
            'poland': {
                'url': 'https://scanner.tradingview.com/poland/scan',
                'exchanges': ['WSE', 'NEWCONNECT'],
                'currency': 'PLN'
            }
        }
        
        for market in markets:
            if market not in market_configs:
                logger.warning(f"Nem támogatott piac: {market}")
                continue
            
            config = market_configs[market]
            logger.info(f"Európai részvények letöltése: {market}")
            
            # Query összeállítása
            query = {
                "filter": [
                    {"left": "type", "operation": "in_range", "right": ["stock"]},
                    {"left": "exchange", "operation": "in_range", "right": config['exchanges']},
                    {"left": "is_primary", "operation": "equal", "right": True},
                    {"left": "active_symbol", "operation": "equal", "right": True}
                ],
                "options": {"lang": "en"},
                "markets": [market],
                "symbols": {"query": {"types": []}, "tickers": []},
                "columns": eu_stock_columns,
                "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
                "range": [0, 5000]
            }
            
            data_query = json.dumps(query)
            data = self._make_request(config['url'], data_query)
            
            if data is None or 'data' not in data:
                logger.error(f"Nem sikerült letölteni az adatokat: {market}")
                continue
            
            try:
                list_elements = list(map(lambda x: x['d'], data['data']))
                if list_elements:
                    market_df = pd.DataFrame(list_elements)
                    market_df.columns = eu_stock_columns
                    
                    # Régió és alapértelmezett deviza hozzáadása
                    market_df['region'] = market.upper()
                    market_df['default_currency'] = config['currency']
                    
                    all_eu_stocks.append(market_df)
                    logger.info(f"Sikeresen letöltve {market}: {len(market_df)} részvény")
                
            except (KeyError, ValueError) as e:
                logger.error(f"Hiba a {market} adatok feldolgozásakor: {str(e)}")
                continue
        
        if all_eu_stocks:
            # DataFrame-ek összefűzése
            new_data = pd.concat(all_eu_stocks, ignore_index=True)
            
            # Pont karakteres ticker-ek kiszűrése
            new_data = new_data[~new_data['name'].str.contains('\\.', na=False)]
            
            # Hozzáadás vagy felülírás
            if replace or self.eu_stock.empty:
                self.eu_stock = new_data
            else:
                # Hozzáadás a meglévőhöz, duplikátumok elkerülése
                self.eu_stock = pd.concat([self.eu_stock, new_data], ignore_index=True)
                # Duplikátumok eltávolítása ticker alapján (megtartja az újabbat)
                self.eu_stock = self.eu_stock.drop_duplicates(subset=['name'], keep='last')
            
            self.eu_stock.reset_index(inplace=True, drop=True)
            
            logger.info(f"Összesen {len(self.eu_stock)} európai részvény a DataFrame-ben")
            return True
        else:
            logger.error("Nem sikerült európai részvényadatokat letölteni")
            if replace:
                self.eu_stock = pd.DataFrame()
            return False
        
    def moneystring(self, money: float) -> str:
        """
        Pénzösszeget alakít át olvasható string formátumra megfelelő mértékegységgel.
        
        A függvény automatikusan választja ki a megfelelő mértékegységet (Million, Billion, Trillion)
        a pénzösszeg nagyságrendje alapján, hogy könnyen olvasható formátumot biztosítson.
        
        Parameters:
        - money: konvertálandó pénzösszeg (float vagy int)
        
        Returns: 
        - string mértékegységgel (pl. "45.67 Billion", "123.45 Million")
        - "N/A" ha érvénytelen bemenet
        
        Példák:
        - 1,234,567,890 -> "1.23 Billion"
        - 45,600,000 -> "45.6 Million"
        - 2,345,678,901,234 -> "2.35 Trillion"
        
        Működés:
        1. Input validáció (szám-e a bemenet)
        2. Nagyságrend meghatározása
        3. Megfelelő egységre konvertálás és kerekítés 2 tizedesre
        """
        if not isinstance(money, (int, float)):
            return "N/A"
        
        if money > 1_000_000_000_000:
            money_str = f"{round(money / 1_000_000_000_000, 2)} Trillion" 
        elif money > 1_000_000_000:
            money_str = f"{round(money / 1_000_000_000, 2)} Billion"
        elif money > 1_000_000:
            money_str = f"{round(money / 1_000_000, 2)} Million"
        else:
            money_str = f"{round(money, 2)}"
        
        return money_str

    def get_one_us_stock_info(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Egyetlen amerikai részvény részletes információit kéri le és dolgozza fel.
        
        A függvény megkeresi a megadott ticker-t a betöltött amerikai részvény adatokban,
        és visszaadja annak részletes információit, beleértve a szektor és iparági
        pozícióját is a piaci kapitalizáció alapján.
        
        Parameters: 
        - ticker: részvény szimbólum (pl. "AAPL", "MSFT")
        
        Returns: 
        - Dictionary a részvény infókkal vagy None ha nem található
        
        Visszatérési értékek:
        - ticker: részvény szimbólum
        - price: aktuális ár
        - market_cap: piaci kapitalizáció
        - n_emp: alkalmazottak száma
        - market_cap_text: formázott piaci kap. (pl. "45.6 Billion")
        - name: cég teljes neve
        - sector: szektor
        - industry: iparág
        - sec_loc: pozíció a szektorban (pl. "5/123")
        - ind_loc: pozíció az iparágban (pl. "2/45")
        - performance: teljesítmény különböző időtávokra
        
        Működés:
        1. Input validáció és ticker nagybetűsítése
        2. Ellenőrzi, hogy az adatok be vannak-e töltve
        3. Megkeresi a tickert a DataFrame-ben
        4. Kiszámítja a szektor és iparági pozíciót
        5. Összegyűjti és formázza az adatokat dictionary-be
        """
        if not ticker or not isinstance(ticker, str):
            logger.error("Érvénytelen ticker megadva")
            return None
        
        ticker = ticker.upper().strip()
        
        # Ellenőrzi hogy az adatok be vannak-e töltve
        if self.us_stock.empty:
            logger.warning("Amerikai részvényadatok nincsenek betöltve. Betöltés...")
            if not self.get_us_stocks():
                return None
        
        # Ticker keresése
        stock_rows = self.us_stock[self.us_stock['name'] == ticker]
        
        if stock_rows.empty:
            logger.warning(f"Ticker '{ticker}' nem található az amerikai részvény adatokban")
            return None
        
        try:
            one_row = stock_rows.iloc[0]
            
            # Szektor és iparági dataframe-ek lekérése
            tsec = self.us_stock[self.us_stock['sector'] == one_row['sector']].reset_index(drop=True)
            tind = self.us_stock[self.us_stock['industry'] == one_row['industry']].reset_index(drop=True)
            
            # Pozíciók megkeresése
            sec_position = tsec.index[tsec['name'] == ticker].tolist()
            ind_position = tind.index[tind['name'] == ticker].tolist()
            
            sec_loc = f"{sec_position[0] + 1}/{tsec.shape[0]}" if sec_position else "N/A"
            ind_loc = f"{ind_position[0] + 1}/{tind.shape[0]}" if ind_position else "N/A"
            
            return {
                'ticker': one_row['name'],
                'price': one_row['close'],
                'market_cap': one_row['market_cap_basic'],
                'n_emp': one_row['number_of_employees'],
                'market_cap_text': self.moneystring(one_row['market_cap_basic']),
                'name': one_row['description'],
                'sector': one_row['sector'],
                'industry': one_row['industry'],
                'sec_loc': sec_loc,
                'ind_loc': ind_loc,
                'performance': f"Teljesítmény | hét: {round(one_row.get('Perf.W', 0), 2)}% | "
                              f"hónap: {round(one_row.get('Perf.1M', 0), 2)}% | "
                              f"6 hónap: {round(one_row.get('Perf.6M', 0), 2)}% | "
                              f"év: {round(one_row.get('Perf.Y', 0), 2)}%"
            }
            
        except (KeyError, IndexError) as e:
            logger.error(f"Hiba a részvényinfó feldolgozásakor {ticker}: {str(e)}")
            return None

    def get_one_eu_stock_info(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Egyetlen európai részvény részletes információit kéri le és dolgozza fel.
        
        Hasonlóan működik mint a get_one_us_stock_info, de az európai részvények
        DataFrame-jében keres, és tartalmazza a régió és devizanem információkat is.
        
        Parameters:
        - ticker: részvény szimbólum (pl. "VOD" a Vodafone-hoz)
        
        Returns:
        - Dictionary a részvény infókkal vagy None ha nem található
        
        Visszatérési értékek:
        - ticker: részvény szimbólum
        - price: aktuális ár
        - currency: devizanem
        - region: régió (UK, GERMANY, POLAND)
        - market_cap: piaci kapitalizáció
        - market_cap_text: formázott piaci kap.
        - name: cég teljes neve
        - sector: szektor
        - industry: iparág
        - exchange: tőzsde
        - performance: teljesítmény különböző időtávokra
        
        Működés:
        1. Input validáció és ticker nagybetűsítése
        2. Ellenőrzi, hogy az európai adatok be vannak-e töltve
        3. Megkeresi a tickert a DataFrame-ben
        4. Összegyűjti és formázza az adatokat dictionary-be
        """
        if not ticker or not isinstance(ticker, str):
            logger.error("Érvénytelen ticker megadva")
            return None
        
        ticker = ticker.upper().strip()
        
        # Ellenőrzi hogy az adatok be vannak-e töltve
        if self.eu_stock.empty:
            logger.warning("Európai részvény adatok nincsenek betöltve. Betöltés...")
            if not self.get_eu_stocks():
                return None
        
        # Ticker keresése
        stock_rows = self.eu_stock[self.eu_stock['name'] == ticker]
        
        if stock_rows.empty:
            logger.warning(f"Ticker '{ticker}' nem található az európai adatokban")
            return None
        
        try:
            one_row = stock_rows.iloc[0]
            
            return {
                'ticker': one_row['name'],
                'price': one_row['close'],
                'currency': one_row.get('currency', one_row.get('default_currency', 'N/A')),
                'region': one_row['region'],
                'exchange': one_row.get('exchange', 'N/A'),
                'market_cap': one_row.get('market_cap_basic', 0),
                'market_cap_text': self.moneystring(one_row.get('market_cap_basic', 0)),
                'name': one_row.get('description', 'N/A'),
                'sector': one_row.get('sector', 'N/A'),
                'industry': one_row.get('industry', 'N/A'),
                'n_emp': one_row.get('number_of_employees', 0),
                'performance': f"Teljesítmény | hét: {round(one_row.get('Perf.W', 0), 2)}% | "
                              f"hónap: {round(one_row.get('Perf.1M', 0), 2)}% | "
                              f"6 hónap: {round(one_row.get('Perf.6M', 0), 2)}% | "
                              f"év: {round(one_row.get('Perf.Y', 0), 2)}%"
            }
            
        except (KeyError, IndexError) as e:
            logger.error(f"Hiba az európai részvényinfó feldolgozásakor {ticker}: {str(e)}")
            return None

    def get_top_n_us_stocks_by_sector(self, percent: float = 10) -> pd.DataFrame:
        """
        Szektoronként visszaadja a legnagyobb piaci kapitalizációjú amerikai részvényeket megadott százalékban.
        
        A függvény minden szektorban kiválasztja a legnagyobb amerikai cégeket piaci kapitalizáció alapján.
        Hasznos a szektor vezetők azonosítására és szektorok közötti összehasonlításra.
        
        Parameters: 
        - percent: visszaadandó részvények százaléka szektoronként (0-100)
                  pl.: 10 = minden szektor top 10%-a
        
        Returns: 
        - Pandas DataFrame a top részvényekkel szektoronként csoportosítva
        
        Példa:
        Ha egy szektorban 100 részvény van és percent=10:
        - Visszaadja a 10 legnagyobb piaci kap. részvényt
        
        Működés:
        1. Input validáció (0 < percent <= 100)
        2. Ellenőrzi hogy az adatok be vannak-e töltve
        3. GroupBy szektoronként
        4. Minden csoportból kiválasztja a top N%-ot
        5. Újraindexeli és visszaadja az eredményt
        
        Hibakezelés:
        - Invalid percent értéknél default 10% használata
        - Üres DataFrame visszaadása hiba esetén
        """
        if not 0 < percent <= 100:
            logger.warning(f"Érvénytelen százalék érték: {percent}. Alapértelmezett 10% használata")
            percent = 10
        
        if self.us_stock.empty:
            logger.warning("Amerikai részvényadatok nincsenek betöltve. Betöltés...")
            if not self.get_us_stocks():
                return pd.DataFrame()
        
        try:
            return (
                self.us_stock.groupby('sector')
                .apply(lambda x: x.nlargest(int(len(x) * (percent / 100)), 'market_cap_basic'))
                .reset_index(drop=True)
            )
        except Exception as e:
            logger.error(f"Hiba a top amerikai részvények lekérése során szektoronként: {str(e)}")
            return pd.DataFrame()

    def get_plotly_title(self, ticker: str) -> str:
        """
        Plotly grafikonokhoz generál informatív, egysoros címet a ticker típusától függően.
        
        A függvény automatikusan felismeri, hogy a ticker részvény, kripto vagy ETF-e,
        és ennek megfelelően formázza a címet a legfontosabb információkkal.
        Ez a cím jelenik meg a grafikonok tetején, gyors áttekintést nyújtva.
        
        Parameters: 
        - ticker: ticker szimbólum (részvény, kripto -USD végződéssel, vagy ETF)
        
        Returns: 
        - Formázott egysoros string a grafikon címéhez
        - Visszaadja magát a ticker-t ha nem található vagy hiba történik
        """
        if not ticker or not isinstance(ticker, str):
            return "Érvénytelen ticker"
        
        ticker = ticker.upper().strip()
        
        try:
            if '-USD' in ticker:
                # Kripto
                if self.crypto.empty:
                    self.get_all_crypto()
                
                crypto_rows = self.crypto[self.crypto['ticker'] == ticker]
                if not crypto_rows.empty:
                    coin = crypto_rows.iloc[0]
                    categories = coin.get('crypto_common_categories', [])
                    categories_str = ', '.join(categories) if isinstance(categories, list) else str(categories)
                    
                    return f"{coin['base_currency_desc']} ({coin['base_currency']}) - ${self.moneystring(coin.get('market_cap_calc', 0))} - {categories_str}"
            
            elif ticker in self.us_etf['name'].tolist():
                # ETF
                if self.us_etf.empty:
                    self.get_us_etfs()
                    
                etf_rows = self.us_etf[self.us_etf['name'] == ticker]
                if not etf_rows.empty:
                    t = etf_rows.iloc[0]
                    return f"{t['description']} ({t['name']}) - AUM: ${self.moneystring(t.get('aum', 0))} - Fókusz: {t.get('focus.tr', 'N/A')} - Költség: {t.get('expense_ratio', 'N/A')}%"
            
            else:
                # Részvény - először US, aztán EU
                # US részvény keresése
                stock_info = self.get_one_us_stock_info(ticker)
                if stock_info:
                    return f"{stock_info['name']} ({stock_info['ticker']}) [US] - ${stock_info['market_cap_text']} - {stock_info['sector']} ({stock_info['sec_loc']}) - {stock_info['industry']} ({stock_info['ind_loc']})"
                
                # EU részvény keresése ha US-ban nem található
                eu_info = self.get_one_eu_stock_info(ticker)
                if eu_info:
                    # Régió kód meghatározása
                    region_code = eu_info['region']
                    if region_code == 'UK':
                        region_tag = '[EU-UK]'
                        currency_symbol = '£'
                    elif region_code == 'GERMANY':
                        region_tag = '[EU-DE]'
                        currency_symbol = '€'
                    elif region_code == 'POLAND':
                        region_tag = '[EU-PL]'
                        currency_symbol = 'PLN '
                    else:
                        region_tag = f'[EU-{region_code}]'
                        currency_symbol = ''
                    
                    return f"{eu_info['name']} ({eu_info['ticker']}) {region_tag} - {currency_symbol}{eu_info['market_cap_text']} - {eu_info.get('sector', 'N/A')} - {eu_info.get('industry', 'N/A')}"
            
            return f"{ticker}"
            
        except Exception as e:
            logger.error(f"Hiba a plotly cím készítése során {ticker}: {str(e)}")
            return f"{ticker}"

    def get_us_sec_plot(self, ticker: str):
        """
        Létrehoz egy oszlopdiagramot, amely az amerikai részvény pozícióját mutatja a szektorán belül.
        
        A függvény vizualizálja, hogy egy adott amerikai részvény hol helyezkedik el a szektorában
        piaci kapitalizáció alapján. Az összes ugyanabban a szektorban lévő cég megjelenik
        oszlopdiagramként, a keresett részvény kiemelve annotációval.
        
        Parameters: 
        - ticker: amerikai részvény szimbólum (pl. "AAPL")
        
        Returns: 
        - Plotly figure objektum a szektor összehasonlító grafikonnal
        - None ha a ticker ETF vagy nem található
        """
        if not ticker or not isinstance(ticker, str):
            logger.error("Érvénytelen ticker megadva")
            return None
        
        ticker = ticker.upper().strip()
        
        if ticker in self.us_etf['name'].tolist():
            logger.info(f"{ticker} egy ETF, használja a get_us_etf_plot függvényt helyette")
            return None
        
        try:
            row_df = self.us_stock[self.us_stock['name'] == ticker]
            if row_df.empty:
                logger.warning(f"Ticker '{ticker}' nem található")
                return None
            
            row_df = row_df.copy()
            row_df.rename(columns={'description': 'Company'}, inplace=True)
            
            sector = row_df['sector'].iloc[0]
            secdf = self.us_stock[self.us_stock['sector'] == sector].reset_index(drop=True).copy()
            secdf.rename(columns={'description': 'Company'}, inplace=True)
            
            fig = px.bar(secdf, x='name', y='market_cap_basic', 
                        title=self.get_plotly_title(ticker),
                        labels={'market_cap_basic': 'Piaci kapitalizáció'}, 
                        text='Company')
            
            fig.add_annotation(
                x=row_df['name'].iloc[0], 
                y=row_df['market_cap_basic'].iloc[0],
                text=f"{self.moneystring(row_df['market_cap_basic'].iloc[0])}",
                showarrow=True, align="center", bordercolor="#c7c7c7",
                font=dict(family="Courier New, monospace", size=16, color="#214e34"),
                borderwidth=2, borderpad=4, bgcolor="#f4fdff", opacity=0.8,
                arrowhead=2, arrowsize=1, arrowwidth=1, ax=65, ay=-45
            )
            
            fig.update_layout(showlegend=False, plot_bgcolor='white', height=600)
            return fig
            
        except Exception as e:
            logger.error(f"Hiba a szektor grafikon készítése során {ticker}: {str(e)}")
            return None

    def get_us_ind_plot(self, ticker: str):
        """
        Létrehoz egy oszlopdiagramot, amely az amerikai részvény pozícióját mutatja az iparágán belül.
        
        Hasonló a get_us_sec_plot függvényhez, de szűkebb fókusszal: csak az azonos iparágban
        működő cégeket hasonlítja össze. Az iparág specifikusabb kategória mint a szektor
        (pl. "Semiconductors" iparág a "Technology" szektoron belül).
        
        Parameters: 
        - ticker: amerikai részvény szimbólum (pl. "NVDA")
        
        Returns: 
        - Plotly figure az iparági pozíciót mutató grafikonnal
        - None ha a ticker ETF vagy nem található
        """
        if not ticker or not isinstance(ticker, str):
            logger.error("Érvénytelen ticker megadva")
            return None
        
        ticker = ticker.upper().strip()
        
        if ticker in self.us_etf['name'].tolist():
            logger.info(f"{ticker} egy ETF, használja a get_us_etf_plot függvényt helyette")
            return None
        
        try:
            row_df = self.us_stock[self.us_stock['name'] == ticker]
            if row_df.empty:
                logger.warning(f"Ticker '{ticker}' nem található")
                return None
            
            row_df = row_df.copy()
            row_df.rename(columns={'description': 'Company'}, inplace=True)
            
            industry = row_df['industry'].iloc[0]
            inddf = self.us_stock[self.us_stock['industry'] == industry].reset_index(drop=True).copy()
            inddf.rename(columns={'description': 'Company'}, inplace=True)
            
            fig = px.bar(inddf, x='name', y='market_cap_basic',
                        title=self.get_plotly_title(ticker),
                        labels={'market_cap_basic': 'Piaci kapitalizáció'},
                        text='Company')
            
            fig.add_annotation(
                x=row_df['name'].iloc[0],
                y=row_df['market_cap_basic'].iloc[0],
                text=f"{self.moneystring(row_df['market_cap_basic'].iloc[0])}",
                showarrow=True, align="center", bordercolor="#c7c7c7",
                font=dict(family="Courier New, monospace", size=16, color="#214e34"),
                borderwidth=2, borderpad=4, bgcolor="#f4fdff", opacity=0.8,
                arrowhead=2, arrowsize=1, arrowwidth=1, ax=65, ay=-45
            )
            
            fig.update_layout(showlegend=False, plot_bgcolor='white', height=600)
            return fig
            
        except Exception as e:
            logger.error(f"Hiba az iparági grafikon készítése során {ticker}: {str(e)}")
            return None

    def get_us_etf_plot(self, ticker: str):
        """
        Létrehoz egy oszlopdiagramot amerikai ETF-ek összehasonlítására azonos befektetési fókusz alapján.
        
        Az ETF-ek esetében nem szektor vagy iparág, hanem befektetési fókusz alapján
        történik az összehasonlítás (pl. "Large Cap", "Emerging Markets", "Technology Sector").
        A diagram az AUM (Assets Under Management - kezelt vagyon) alapján rangsorolja őket.
        
        Parameters:
        - ticker: amerikai ETF szimbólum (pl. "SPY", "QQQ")
        
        Returns: 
        - Plotly figure az azonos fókuszú ETF-ek összehasonlításával
        - None ha nem található vagy hiba történik
        """
        if not ticker or not isinstance(ticker, str):
            logger.error("Érvénytelen ticker megadva")
            return None
        
        ticker = ticker.upper().strip()
        
        try:
            row_df = self.us_etf[self.us_etf['name'] == ticker]
            if row_df.empty:
                logger.warning(f"ETF '{ticker}' nem található")
                return None
            
            focus = row_df['focus.tr'].iloc[0]
            focdf = self.us_etf[self.us_etf['focus.tr'] == focus].reset_index(drop=True)
            
            fig = px.bar(focdf, x='name', y='aum',
                        title=self.get_plotly_title(ticker),
                        labels={'aum': 'Kezelt vagyon (AUM)'},
                        text='description')
            
            fig.add_annotation(
                x=row_df['name'].iloc[0],
                y=row_df['aum'].iloc[0],
                text=f"{self.moneystring(row_df['aum'].iloc[0])}",
                showarrow=True, align="center", bordercolor="#c7c7c7",
                font=dict(family="Courier New, monospace", size=16, color="#214e34"),
                borderwidth=2, borderpad=4, bgcolor="#f4fdff", opacity=0.8,
                arrowhead=2, arrowsize=1, arrowwidth=1, ax=65, ay=-45
            )
            
            fig.update_layout(showlegend=False, plot_bgcolor='white', height=600)
            return fig
            
        except Exception as e:
            logger.error(f"Hiba az ETF grafikon készítése során {ticker}: {str(e)}")
            return None


# Példa használat
if __name__ == "__main__":
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
