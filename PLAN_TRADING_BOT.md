# Plan Integral: Bot de Trading Automatizado para Bolsa USA

**Fecha:** 17 de Mayo 2026  
**Objetivo:** Crear un sistema de trading automatizado rentable con escaneo premarket y optimización continua  
**Capital:** < $5,000 (fase educativa/prueba)  
**Enfoque:** Prudente, escalable, educativo

---

## 1. ARQUITECTURA TÉCNICA

### 1.1 Stack Tecnológico Recomendado

```
Frontend:
- Dashboard: Python Dash o Streamlit (fácil de aprender)
- Visualización: Plotly, Matplotlib
  
Backend:
- Lenguaje: Python 3.10+
- Framework: FastAPI (para APIs)
- Base de datos: PostgreSQL (histórico de trades)
- Broker API: TD Ameritrade/Thinkorswim (API robusta con OAuth)
  
Data & Análisis:
- yfinance, pandas, numpy (datos de mercado)
- TA-Lib, pandas_ta (análisis técnico)
- BacktraderIO o VectorBT (backtesting)
  
Scheduling:
- APScheduler (ejecutar tareas programadas)
- Celery (si escalas a varias estrategias)
```

### 1.2 Componentes Principales

```
┌─────────────────────────────────────────────────────────┐
│                    TRADING BOT SYSTEM                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐   │
│  │   Scanner    │  │  Estrategias │  │  Riesgo    │   │
│  │ Premarket    │→ │  de Trading  │→ │  & Posiciones│ │
│  └──────────────┘  └──────────────┘  └────────────┘   │
│         ↓                                     ↓         │
│  ┌──────────────┐                  ┌──────────────┐   │
│  │  API Datos   │                  │ Ejecución    │   │
│  │ (yfinance)   │                  │ Órdenes      │   │
│  └──────────────┘                  └──────────────┘   │
│         ↓                                     ↓         │
│  ┌──────────────────────────────────────────────┐      │
│  │     BROKER (Thinkorswim/TD Ameritrade)     │      │
│  └──────────────────────────────────────────────┘      │
│                        ↓                               │
│  ┌──────────────────────────────────────────────┐      │
│  │  Database: PostgreSQL (logs, histórico)     │      │
│  │  Dashboard: Monitoreo en tiempo real        │      │
│  │  Optimizador: Análisis & ML                 │      │
│  └──────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────┘
```

---

## 2. FASE 1: FUNDAMENTOS (Semanas 1-3)

### 2.1 Configuración Inicial

**Objetivo:** Tener ambiente listo y entender básicos

```python
# Instalación de dependencias principales
pip install tda-api yfinance pandas numpy ta-lib
pip install plotly streamlit fastapi
pip install pandas-ta backtesting
pip install psycopg2-binary sqlalchemy
```

**Tareas:**
1. Registrarse en TD Ameritrade Developer (gratis, sin dinero real)
2. Obtener Consumer Key y Account ID de TD Ameritrade
3. Crear repositorio GitHub para versionamiento
4. Estructura de carpetas:
   ```
   trading-bot/
   ├── data/
   ├── strategies/
   ├── broker/
   ├── risk_management/
   ├── scanner/
   ├── backtesting/
   ├── dashboard/
   ├── config.py
   ├── main.py
   └── requirements.txt
   ```

### 2.2 Conectar API de Thinkorswim (Paper Trading)

```python
# thinkorswim_broker.py
import tda
from tda.client import Client
from tda.orders.generic import OrderBuilder
import json

class ThinkOrSwimBroker:
    def __init__(self, consumer_key, account_id, paper=True):
        self.consumer_key = consumer_key
        self.account_id = account_id
        self.paper = paper
        self.client = self._auth_client()
    
    def _auth_client(self):
        """Autentica con OAuth"""
        # Lee token.json (generado por setup_oauth.py)
        with open('token.json', 'r') as f:
            token_dict = json.load(f)
        return Client(self.consumer_key, redirect_uri='http://localhost:8000', 
                      token_dict=token_dict, account_id=self.account_id)
    
    def get_account(self):
        """Obtiene info de cuenta"""
        account_type = 'margin' if self.paper else 'cash'
        return self.client.get_account(self.account_id, fields=[
            tda.client.Client.Account.Fields.POSITIONS,
            tda.client.Client.Account.Fields.ORDERS
        ])
    
    def submit_order(self, symbol, qty, side, order_type="market"):
        """Coloca una orden"""
        order = OrderBuilder().add_equity_market_order(side, qty).build()
        return self.client.place_order(self.account_id, order)
    
    def get_positions(self):
        """Obtiene posiciones abiertas"""
        account = self.get_account()
        return account['positions'] if 'positions' in account else []
```

---

## 3. FASE 2: SCANNER PREMARKET (Semanas 3-5)

### 3.1 Módulo de Escaneo

El scanner busca acciones con:
- Volumen anómalo en premarket (vs promedio histórico)
- Gaps significativos (diferencia apertura vs cierre anterior)
- Breakouts técnicos
- Noticias/earnings próximas

```python
# scanner/premarket_scanner.py
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class PremarketScanner:
    def __init__(self, symbols_list=None):
        # Si no hay lista, escanea top 100 por volumen
        self.symbols = symbols_list or self._get_top_symbols()
    
    def _get_top_symbols(self):
        """Obtiene stocks más activos (puedes obtener del S&P 500)"""
        # Implementar lógica para obtener top símbolos
        pass
    
    def scan_for_opportunities(self):
        """Detecta setup interesantes en premarket"""
        opportunities = []
        
        for symbol in self.symbols:
            try:
                data = yf.download(symbol, period="5d", interval="1m", prepost=True)
                
                # Detectar gap
                gap = self._detect_gap(symbol)
                if gap and abs(gap['gap_pct']) > 2:  # Gap > 2%
                    opportunities.append({
                        'symbol': symbol,
                        'type': 'gap',
                        'gap_pct': gap['gap_pct'],
                        'strength': 'alta' if abs(gap['gap_pct']) > 5 else 'media'
                    })
                
                # Detectar volumen anómalo
                vol_anomaly = self._detect_volume_anomaly(symbol, data)
                if vol_anomaly:
                    opportunities.append({
                        'symbol': symbol,
                        'type': 'volume',
                        'vol_multiplier': vol_anomaly['multiplier']
                    })
            
            except Exception as e:
                print(f"Error escaneando {symbol}: {e}")
        
        return pd.DataFrame(opportunities)
    
    def _detect_gap(self, symbol):
        """Calcula gap entre cierre anterior y apertura premarket"""
        hist = yf.download(symbol, period="2d", progress=False)
        if len(hist) < 2:
            return None
        
        prev_close = hist.iloc[-2]['Close']
        current_premarket = hist.iloc[-1]['Open']
        gap_pct = ((current_premarket - prev_close) / prev_close) * 100
        
        return {'gap_pct': gap_pct, 'prev_close': prev_close}
    
    def _detect_volume_anomaly(self, symbol, data):
        """Detecta si volumen premarket es anómalo"""
        if len(data) < 20:
            return None
        
        recent_vol = data[-1]['Volume'] if 'Volume' in data.columns else 0
        avg_vol = data[:-1]['Volume'].mean()
        
        multiplier = recent_vol / avg_vol if avg_vol > 0 else 0
        return {'multiplier': multiplier} if multiplier > 2 else None
```

### 3.2 Criterios de Selección

Para reducir falsos positivos:
- Gap > 2% con volumen > 1.5x promedio
- Precio entre $5 y $500 (evitar penny stocks y mega caps volátiles)
- Liquidez: volumen promedio > 500k acciones/día
- Rango ATR < 30% (volatilidad razonable)

---

## 4. FASE 3: ESTRATEGIAS DE TRADING (Semanas 5-8)

### 4.1 Estrategia 1: Gap & Go (Premarket)

**Concepto:** Compra acciones con gap positivo + volumen anómalo, sale al 2-5% de ganancia

```python
# strategies/gap_and_go.py
class GapAndGoStrategy:
    def __init__(self, entry_gap_min=2, entry_gap_max=10, profit_target=0.03, 
                 stop_loss=0.02):
        self.entry_gap_min = entry_gap_min  # Gap mínimo
        self.entry_gap_max = entry_gap_max  # Gap máximo
        self.profit_target = profit_target  # 3% ganancia
        self.stop_loss = stop_loss          # 2% pérdida
    
    def check_setup(self, symbol, gap_pct, volume_multiplier):
        """Valida si cumple setup"""
        if (self.entry_gap_min <= gap_pct <= self.entry_gap_max and 
            volume_multiplier > 1.5):
            return True
        return False
    
    def generate_order(self, symbol, entry_price, position_size):
        """Genera orden con TP y SL"""
        tp_price = entry_price * (1 + self.profit_target)
        sl_price = entry_price * (1 - self.stop_loss)
        
        return {
            'symbol': symbol,
            'entry_price': entry_price,
            'tp_price': tp_price,
            'sl_price': sl_price,
            'position_size': position_size,
            'strategy': 'gap_and_go'
        }
```

### 4.2 Estrategia 2: Breakout (Intraday)

**Concepto:** Espera breakout de 20-período de resistencia, entra con stop y TP

```python
# strategies/breakout.py
class BreakoutStrategy:
    def __init__(self, lookback=20, profit_target_atr=2, stop_loss_atr=1):
        self.lookback = lookback
        self.profit_target_atr = profit_target_atr
        self.stop_loss_atr = stop_loss_atr
    
    def analyze(self, data):
        """Analiza si hay setup breakout"""
        if len(data) < self.lookback + 5:
            return None
        
        # Calcula ATR
        high_20 = data['High'].tail(self.lookback).max()
        low_20 = data['Low'].tail(self.lookback).min()
        atr = self._calculate_atr(data)
        
        current_price = data['Close'].iloc[-1]
        
        # Setup alcista: precio rompe la resistencia
        if current_price > high_20 and data['Close'].iloc[-2] <= high_20:
            return {
                'direction': 'long',
                'entry': current_price,
                'resistance': high_20,
                'tp': current_price + (atr * self.profit_target_atr),
                'sl': current_price - (atr * self.stop_loss_atr)
            }
        
        return None
    
    def _calculate_atr(self, data, period=14):
        """Calcula Average True Range"""
        high_low = data['High'] - data['Low']
        high_close = abs(data['High'] - data['Close'].shift())
        low_close = abs(data['Low'] - data['Close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        return true_range.rolling(period).mean().iloc[-1]
```

### 4.3 Estrategia 3: Media Móvil Cruce (Swing Trading)

**Concepto:** Compra cuando SMA rápida cruza por arriba de SMA lenta

```python
# strategies/ma_crossover.py
class MACrossoverStrategy:
    def __init__(self, fast_ma=9, slow_ma=21, profit_target_pct=5, 
                 stop_loss_pct=2):
        self.fast_ma = fast_ma
        self.slow_ma = slow_ma
        self.profit_target_pct = profit_target_pct
        self.stop_loss_pct = stop_loss_pct
    
    def analyze(self, data):
        """Busca cruces de medias móviles"""
        data['sma_fast'] = data['Close'].rolling(self.fast_ma).mean()
        data['sma_slow'] = data['Close'].rolling(self.slow_ma).mean()
        
        # Necesita al menos 2 velas para detectar cruce
        if len(data) < self.slow_ma + 2:
            return None
        
        prev_fast = data['sma_fast'].iloc[-2]
        prev_slow = data['sma_slow'].iloc[-2]
        curr_fast = data['sma_fast'].iloc[-1]
        curr_slow = data['sma_slow'].iloc[-1]
        
        # Cruce alcista: fast cruza por arriba de slow
        if prev_fast <= prev_slow and curr_fast > curr_slow:
            entry = data['Close'].iloc[-1]
            return {
                'direction': 'long',
                'entry': entry,
                'tp': entry * (1 + self.profit_target_pct / 100),
                'sl': entry * (1 - self.stop_loss_pct / 100)
            }
        
        return None
```

---

## 5. FASE 4: GESTIÓN DE RIESGO (Semana 5, paralela)

### 5.1 Position Sizing

```python
# risk_management/position_sizing.py
class PositionSizer:
    def __init__(self, account_size, risk_per_trade=0.01):
        """
        account_size: Capital total de la cuenta
        risk_per_trade: % del capital a arriesgar por trade (1% recomendado)
        """
        self.account_size = account_size
        self.risk_per_trade = risk_per_trade
    
    def calculate_position_size(self, entry_price, stop_loss_price):
        """Calcula cuántas acciones comprar basado en riesgo"""
        max_risk = self.account_size * self.risk_per_trade
        price_diff = abs(entry_price - stop_loss_price)
        
        if price_diff == 0:
            return 0
        
        position_size = max_risk / price_diff
        return int(position_size)
    
    def update_account_size(self, new_size):
        """Actualiza tamaño de cuenta tras ganancias/pérdidas"""
        self.account_size = new_size
```

### 5.2 Límites Diarios

```python
# risk_management/daily_limits.py
class DailyLimits:
    def __init__(self, max_daily_loss_pct=2, max_trades_per_day=10):
        self.max_daily_loss_pct = max_daily_loss_pct
        self.max_trades_per_day = max_trades_per_day
        self.daily_pnl = 0
        self.trades_today = 0
    
    def can_trade(self, account_value):
        """Verifica si puede abrir más posiciones"""
        max_loss = account_value * (self.max_daily_loss_pct / 100)
        
        if self.daily_pnl <= -max_loss:
            return False, "Límite de pérdida diaria alcanzado"
        
        if self.trades_today >= self.max_trades_per_day:
            return False, "Máximo de trades diarios alcanzado"
        
        return True, "OK"
    
    def reset_daily(self):
        """Reset al inicio del día"""
        self.daily_pnl = 0
        self.trades_today = 0
```

---

## 6. FASE 5: BACKTESTING (Semanas 7-9)

### 6.1 Framework de Backtesting

```python
# backtesting/backtest_engine.py
from backtesting import Backtest, Strategy
import pandas as pd

class TradingBotStrategy(Strategy):
    def init(self):
        self.strategy = GapAndGoStrategy()
    
    def next(self):
        """Se ejecuta para cada barra de datos"""
        # Lógica de entrada/salida
        pass

# Ejecutar backtest
def run_backtest(strategy_class, symbol, start_date, end_date, initial_cash=10000):
    data = yf.download(symbol, start=start_date, end=end_date)
    
    bt = Backtest(data, strategy_class, cash=initial_cash, commission=0.002)
    results = bt.run()
    
    return {
        'return_pct': results['Return [%]'],
        'sharpe': results['Sharpe Ratio'],
        'max_drawdown': results['Max. Drawdown [%]'],
        'win_rate': results['Win Rate [%]'],
        'trades': results['# Trades']
    }
```

**Métricas clave a monitorear:**
- Return %: Ganancia total del período
- Sharpe Ratio: Retorno ajustado por riesgo (>1.0 es bueno)
- Max Drawdown: Peor caída del equity (queremos < 15%)
- Win Rate: % de trades ganadores (> 50% es bueno)
- Profit Factor: Ganancia total / Pérdida total (> 1.5 es bueno)

---

## 7. FASE 6: INTEGRACIÓN BROKER (Semanas 9-11)

### 7.1 Paper Trading (Con dinero simulado)

```python
# main.py - Modo paper trading
from thinkorswim_broker import ThinkOrSwimBroker
from scanner.premarket_scanner import PremarketScanner
from strategies.gap_and_go import GapAndGoStrategy

def run_paper_trading():
    broker = ThinkOrSwimBroker(CONSUMER_KEY, ACCOUNT_ID, paper=True)
    scanner = PremarketScanner()
    strategy = GapAndGoStrategy()
    
    while True:
        # Escanear oportunidades premarket
        opportunities = scanner.scan_for_opportunities()
        
        for _, opp in opportunities.iterrows():
            if strategy.check_setup(
                opp['symbol'], 
                opp['gap_pct'], 
                opp.get('vol_multiplier', 1)
            ):
                # Generar y ejecutar orden
                order = strategy.generate_order(
                    opp['symbol'], 
                    entry_price=opp['entry_price'],
                    position_size=position_sizer.calculate_position_size(...)
                )
                
                # Ejecutar (paper trading)
                broker.submit_order(order['symbol'], order['position_size'], 'buy')
                
                # Registrar en base de datos para análisis
                log_trade(order)
        
        time.sleep(60)  # Rescanear cada minuto
```

### 7.2 Transición a Dinero Real

Solo después de:
- ✅ Backtest positivo (Sharpe > 1.0, Max DD < 15%)
- ✅ 2-4 semanas de paper trading exitoso
- ✅ Ganancias consistentes (al menos 3 trades ganadores por 1 perdedor)
- ✅ Entiendes completamente cada trade

**Pasos:**
1. Comenzar con capital mínimo ($500-$1,000)
2. Misma estrategia que en paper
3. Máximo 1-2 trades por día inicialmente
4. Aumentar capital solo después de 4-6 semanas de ganancias consistentes

---

## 8. FASE 7: DASHBOARD & MONITOREO (Semanas 10-12)

### 8.1 Dashboard con Streamlit

```python
# dashboard/app.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Trading Bot Dashboard", layout="wide")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Account Balance", f"${account_balance:,.2f}")

with col2:
    daily_pnl = calculate_daily_pnl()
    st.metric("Daily P&L", f"${daily_pnl:,.2f}")

with col3:
    st.metric("Win Rate", f"{win_rate:.1f}%")

# Trades recientes
st.subheader("Últimos Trades")
trades_df = get_recent_trades()
st.dataframe(trades_df)

# Gráfico de equity curve
st.subheader("Equity Curve")
equity = get_equity_history()
st.line_chart(equity)

# Estatus de posiciones abiertas
st.subheader("Posiciones Abiertas")
positions = broker.get_positions()
st.table(positions)
```

---

## 9. FASE 8: OPTIMIZACIÓN CONTINUA (Semanas 12+)

### 9.1 Análisis Post-Trade

```python
# optimization/trade_analyzer.py
class TradeAnalyzer:
    def analyze_trades(self, trades_df):
        """Analiza trades para encontrar patrones"""
        
        # Ganancias vs Pérdidas
        winning_trades = trades_df[trades_df['pnl'] > 0]
        losing_trades = trades_df[trades_df['pnl'] < 0]
        
        # Por qué ganan los trades ganadores?
        print("Patrones en trades ganadores:")
        print(winning_trades[['symbol', 'entry_time', 'exit_time', 'reason']].groupby('reason').count())
        
        # Horarios mejores
        trades_df['hour'] = pd.to_datetime(trades_df['entry_time']).dt.hour
        best_hours = trades_df.groupby('hour')['pnl'].mean().sort_values(ascending=False)
        
        print(f"Mejores horas para operar: {best_hours.head()}")
        
        # Símbolos más rentables
        best_symbols = trades_df.groupby('symbol')['pnl'].mean().sort_values(ascending=False)
        print(f"Mejores símbolos: {best_symbols.head()}")
```

### 9.2 Optimización Automática de Parámetros

```python
# optimization/parameter_optimizer.py
from itertools import product

class ParameterOptimizer:
    def optimize_strategy(self, strategy_class, symbol, date_range, params_grid):
        """Grid search para encontrar parámetros óptimos"""
        
        results = []
        
        for param_combo in product(*params_grid.values()):
            param_dict = dict(zip(params_grid.keys(), param_combo))
            
            strategy = strategy_class(**param_dict)
            backtest_result = run_backtest(strategy, symbol, *date_range)
            
            results.append({
                'params': param_dict,
                'sharpe': backtest_result['sharpe'],
                'return': backtest_result['return_pct'],
                'max_dd': backtest_result['max_drawdown']
            })
        
        # Retorna parámetros con mejor Sharpe ratio
        best = max(results, key=lambda x: x['sharpe'])
        return best['params']
```

---

## 10. ROADMAP DETALLADO

| Semana | Objetivo | Deliverables |
|--------|----------|--------------|
| 1-3 | Setup & Fundamentos | Thinkorswim conectado, código base |
| 3-5 | Scanner Premarket | Scanner funcional, lista de setups |
| 5-8 | Estrategias | 3 estrategias codificadas |
| 7-9 | Backtesting | Validación histórica, parámetros óptimos |
| 9-11 | Paper Trading | 2-4 semanas exitosas |
| 10-12 | Dashboard | Monitoreo completo |
| 12+ | Dinero Real | Inicio gradual con $500-1k |
| 12+ | Optimización | Mejora continua de estrategias |

---

## 11. REGLAS DE ORO PARA NO PERDER DINERO

1. **Riesgo fijo:** Nunca arriesgues > 1% del capital por trade
2. **Stop Loss obligatorio:** Todo trade TIENE un stop loss, sin excepciones
3. **Backtesting primero:** Nunca trades algo que no pasó backtest
4. **Paper Trading:** Mínimo 2-4 semanas antes de dinero real
5. **Journal de trades:** Documenta CADA trade: por qué entraste, qué pasó
6. **Límites diarios:** Si pierdes 2% del capital en un día, STOP
7. **Aprende de pérdidas:** Cada pérdida es una lección, no una tragedia
8. **Emociones:** Si empiezas a feel greedy/scared, cierra todo y respira
9. **Diversificación:** No pongas todo en una estrategia/símbolo
10. **Evoluciona:** Tu estrategia debe mejorar cada mes

---

## 12. HERRAMIENTAS Y RECURSOS

### APIs & Brokers:
- **TD Ameritrade/Thinkorswim** (recomendado): developer.tdameritrade.com
- **Interactive Brokers**: ibkr.com
- **Polygon.io**: Datos de mercado en tiempo real

### Librerías Python:
- pandas, numpy: Análisis de datos
- ta-lib: Indicadores técnicos
- backtesting: Framework de backtesting
- streamlit: Dashboard interactivo
- sqlalchemy: ORM para base de datos

### Comunidades:
- r/algotrading: Reddit
- QuantConnect: Plataforma de backtesting
- TradingView: Gráficos y análisis

---

## PRÓXIMOS PASOS

1. **Hoy:** Registra en TD Ameritrade Developer, obtén Consumer Key
2. **Esta semana:** Entiende la arquitectura, prepara el repositorio
3. **Próximas 3 semanas:** Implementa scanner + 1 estrategia
4. **Semanas 4-8:** Backtest, optimize, paper trade
5. **Semana 9+:** Dinero real (si todo va bien)

¿Empezamos con la Fase 1?
