# SMA200 Strategy - Konzervatív Trendkövető Stratégia

## Áttekintés

Az SMA200 Strategy egy konzervatív, hosszú távú trendkövető stratégia, amely RSI szűréssel és breakout confirmation-nel dolgozik. A stratégia célja, hogy csak az erős trendekben lépjen piacra, és a volatilitás-adaptív kockázatkezeléssel védje a profitot.

## Stratégia Jellemzői

### Időkeret
- **Daily (D1)** - Minden számítás és kereskedés napi gyertyákon alapul

### Csak Long Pozíciók
- A stratégia csak felfelé irányuló trendeket követ
- Nincs short kereskedés

## Belépési Feltételek (ÖSSZES TELJESÜLNI KELL)

### 1. RSI Szűrő (Elsődleges)
- **RSI(14) < 65** a belépés napján
- Célja: Túlvett szintek elkerülése, fals kitörések szűrése
- Paraméter: `rsi_threshold` (default: 65)

### 2. Trend Szűrő
- **Záróár > 200 napos SMA**
- **SMA200 meredeksége pozitív** (mostani érték > 10 nappal ezelőtti érték)
- Paraméterek: 
  - `sma_long` (default: 200)
  - `slope_period` (default: 10)

### 3. Breakout Trigger
- **Záróár > 20 napos high**
- A breakout gyertya záróárának át kell törnie a korábbi 20 napos csúcsot
- Paraméter: `breakout_period` (default: 20)

### 4. ATR Test Méret
- **Gyertya testméret ≥ 1 × ATR(14)**
- Biztosítja, hogy erős momentum legyen a belépéskor
- Paraméter: `atr_multiplier_body` (default: 1.0)

### 5. Parabolikus Mozgás Szűrő
- **Max 15% emelkedés az elmúlt 20 napban**
- Elkerüli a túl gyors, fenntarthatatlan emelkedéseket
- Paraméterek:
  - `max_rise_period` (default: 20)
  - `max_rise_percent` (default: 15.0)

### 6. Doji / Hosszú Kanóc Szűrő
- **Nem doji**: test ≥ 10% a gyertya teljes tartományából
- **Nem hosszú felső kanóc**: felső kanóc ≤ 2 × test
- Automatikus, nincs külön paraméter

## Kockázatkezelés

### Stop Loss
- **Kezdeti stop**: belépő gyertya low - 2×ATR(14)
- Konzervatív, a volatilitáshoz igazodó stop
- Paraméter: `atr_multiplier_stop` (default: 2.0)

### Trailing Stop
- **2×ATR(14) távolság a legmagasabb ártól**
- Naponta frissül, ha új csúcsot ér el az ár
- Sosem megy lejjebb, csak feljebb
- Paraméter: `atr_multiplier_trail` (default: 2.0)

### Kilépési Feltételek (Bármelyik)

#### 1. Trailing Stop Hit
- Az ár eléri a trailing stop szintet

#### 2. SMA50 Alá Zárás
- A záróár az 50 napos SMA alá kerül
- Paraméter: `sma_short` (default: 50)

## Használat

### Alapvető Használat

```python
from tradingsuite.data.stocks import StockData
from tradingsuite.analysis.backtest import Backtest
from tradingsuite.strategies.sma200 import sma200_strategy

# Adat betöltés
stock = StockData('AAPL')
df = stock.df

# Backtest alapértelmezett paraméterekkel
backtest = Backtest(df, sma200_strategy)

# Eredmények
backtest.summarize_strategy()
```

### Testreszabott Paraméterekkel

```python
backtest = Backtest(
    df, 
    sma200_strategy,
    rsi_period=14,           # RSI számítási periódus
    rsi_threshold=65,        # RSI maximum belépéshez
    sma_long=200,            # Hosszú távú SMA
    sma_short=50,            # Rövid távú SMA (kilépés)
    slope_period=10,         # SMA meredekség periódus
    breakout_period=20,      # Breakout periódus
    atr_period=14,           # ATR számítási periódus
    atr_multiplier_body=1.0, # Min. gyertya test (ATR)
    atr_multiplier_stop=2.0, # Stop loss távolság (ATR)
    atr_multiplier_trail=2.0,# Trailing stop távolság (ATR)
    max_rise_period=20,      # Parabolikus ellenőrzési periódus
    max_rise_percent=15.0    # Max. emelkedés %
)
```

### Vizualizáció

```python
from tradingsuite.strategies.sma200 import show_indicator_sma200_strategy

# Alapértelmezett vizualizáció
fig = show_indicator_sma200_strategy('AAPL')
fig.show()

# Testreszabott vizualizáció
fig = show_indicator_sma200_strategy(
    'NVDA',
    rsi_threshold=70,
    ndays=500,              # Csak utolsó 500 nap
    plot_height=1400,
    add_strategy_summary=True
)
fig.show()
```

## Paraméter Optimalizálás

### Konzervatívabb Beállítás
```python
backtest = Backtest(
    df, 
    sma200_strategy,
    rsi_threshold=60,         # Szigorúbb RSI szűrő
    atr_multiplier_stop=2.5,  # Tágabb stop loss
    max_rise_percent=12.0     # Szigorúbb parabolikus szűrő
)
```

### Agresszívabb Beállítás
```python
backtest = Backtest(
    df, 
    sma200_strategy,
    rsi_threshold=70,         # Enyhébb RSI szűrő
    atr_multiplier_stop=1.5,  # Szűkebb stop loss
    atr_multiplier_trail=1.5, # Gyorsabb profit fixing
    max_rise_percent=18.0     # Enyhébb parabolikus szűrő
)
```

## Stratégia Előnyei

### ✅ Előnyök
1. **Konzervatív belépés**: Több szűrő biztosítja, hogy csak erős setupoknál lépjen be
2. **Volatilitás-adaptív**: ATR alapú stop-ok alkalmazkodnak a piaci környezethez
3. **Trend protection**: SMA200 és slope szűrő védi az ellentrendes belépésektől
4. **Profit protection**: Trailing stop és SMA50 kilépés védi a profitot
5. **Fals kitörés védelem**: RSI, ATR body size és parabolikus szűrők csökkentik a fals jelzéseket

### ⚠️ Korlátok
1. **Kevés trade**: A szigorú feltételek miatt kevés trade generálódik
2. **Lassú piacok**: Sideways vagy low volatility környezetben kevés lehetőség
3. **Késleltetett belépés**: A sok szűrő miatt lemaradhat a trend elejéről
4. **Whipsaw**: Choppy piacokon gyakran kiléphet korán

## Teljesítmény Metrikák

A backtest a következő metrikákat számítja:

- **Number of trades**: Trade-ek száma
- **Win ratio**: Nyerő trade-ek aránya
- **Average result**: Átlagos eredmény %
- **Median result**: Medián eredmény %
- **Cumulative result**: Összes trade összeszorzott eredménye
- **Average trade length**: Átlagos trade időtartam napokban
- **Max gain/loss**: Legnagyobb nyereség/veszteség
- **Hold result**: Buy & Hold stratégia eredménye összehasonlításként

## Példa Eredmények

```
Ticker: AAPL
Trades: 8
Win ratio: 75.0%
Average result: 12.5%
Cumulative result: 2.1x
Average trade length: 45 days
Hold result: 1.8x
```

## Ajánlott Használat

1. **Time frame**: Daily (D1) - nagyobb időkeretek nem ajánlottak
2. **Asset típus**: Részvények, ETF-ek (nagy likviditás)
3. **Piaci környezet**: Bull vagy erős uptrend periódusok
4. **Portfolio**: Több ticker párhuzamos kezelése ajánlott
5. **Paper trading**: Először tesztelj éles kereskedés előtt!

## Fejlesztési Lehetőségek

- [ ] Position sizing (fix pozícióméret vs. ATR alapú)
- [ ] Multiple timeframe confirmation
- [ ] Volume filter
- [ ] Sector strength filter
- [ ] Risk-reward ratio számítás belépés előtt
- [ ] Partial profit taking szintek

## Licenc

Lásd a fő TradingSuite LICENSE fájlt.

## Kapcsolat

Ha kérdésed van a stratégiával kapcsolatban, nyiss egy Issue-t a GitHub repositoryban.
