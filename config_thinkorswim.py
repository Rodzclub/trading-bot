# config_thinkorswim.py - Configuración para Thinkorswim/TD Ameritrade

import os
from dotenv import load_dotenv

load_dotenv()

# ============ BROKER CONFIGURATION ============
BROKER_TYPE = "thinkorswim"  # Cambió de "alpaca" a "thinkorswim"
TD_CONSUMER_KEY = os.getenv("TD_CONSUMER_KEY", "YOUR_CONSUMER_KEY_HERE")
TD_ACCOUNT_ID = os.getenv("TD_ACCOUNT_ID", "YOUR_ACCOUNT_ID_HERE")

# OAuth token (se genera automáticamente después de setup_oauth.py)
TD_ACCESS_TOKEN = os.getenv("TD_ACCESS_TOKEN", None)
TD_REFRESH_TOKEN = os.getenv("TD_REFRESH_TOKEN", None)

# ============ PAPER vs LIVE TRADING ============
# En Thinkorswim necesitas cambiar esto desde la app
# Pero aquí puedes configurar comportamiento del bot
TRADING_MODE = "PAPER"  # "PAPER" o "LIVE"
LIVE_TRADING_ENABLED = False  # NUNCA cambies a True sin validación completa

if TRADING_MODE == "LIVE" and not LIVE_TRADING_ENABLED:
    raise ValueError("❌ LIVE TRADING NO HABILITADO. Revisa config.")

# ============ ACCOUNT CONFIGURATION ============
INITIAL_CAPITAL = 5000  # Tu capital inicial
RISK_PER_TRADE = 0.01  # 1% del capital por trade (MUY IMPORTANTE)
MAX_DAILY_LOSS_PCT = 0.02  # Máximo 2% pérdida diaria antes de STOP
MAX_TRADES_PER_DAY = 10  # Máximo trades por día
MAX_OPEN_POSITIONS = 3  # Máximo posiciones simultáneas

# ============ MARKET CONFIGURATION ============
MARKET_OPEN_TIME = "09:30"  # Apertura mercado USA (EST)
MARKET_CLOSE_TIME = "16:00"  # Cierre mercado USA
PREMARKET_OPEN = "04:00"  # Apertura premarket
PREMARKET_CLOSE = "09:30"  # Cierre premarket

# Horarios para cada estrategia (formato 24h EST)
TRADING_HOURS = {
    'gap_and_go': ('04:00', '10:30'),  # Premarket + primeros 60 min
    'breakout': ('09:30', '15:30'),     # Horario regular
    'ma_crossover': ('09:30', '15:30')  # Swing, horario regular
}

# ============ SCANNER CONFIGURATION ============
SCANNER_ENABLED = True
SCANNER_INTERVAL = 60  # Segundos entre scans
PREMARKET_SCAN_INTERVAL = 30  # Más frecuente en premarket

# Filtros de scan
MIN_PRICE = 5  # Precio mínimo de acción
MAX_PRICE = 500  # Precio máximo
MIN_VOLUME = 500000  # Volumen promedio mínimo
MIN_GAP_PCT = 2  # Gap mínimo para considerarse (%)
MAX_GAP_PCT = 10  # Gap máximo (evita extremos volatilidad)
MIN_VOLUME_MULTIPLIER = 1.5  # Volumen premarket vs promedio
MIN_PE_RATIO = 5  # PE mínimo (evita empresas sin ganancias)
MAX_PE_RATIO = 50  # PE máximo (evita sobrevaluadas)

# ============ STRATEGY CONFIGURATION ============
STRATEGIES_ENABLED = {
    'gap_and_go': True,
    'breakout': True,
    'ma_crossover': True
}

# Ponderación de estrategias (% de capital a usar en cada una)
STRATEGY_ALLOCATION = {
    'gap_and_go': 0.4,      # 40% en gap & go (más arriesgado, más rápido)
    'breakout': 0.35,       # 35% en breakout
    'ma_crossover': 0.25,   # 25% en swing (más seguro)
}

# ============ GAP AND GO STRATEGY ============
GAP_AND_GO = {
    'entry_gap_min': 2,           # Gap mínimo 2%
    'entry_gap_max': 10,          # Gap máximo 10%
    'profit_target_pct': 3,       # Tomar ganancia al 3%
    'stop_loss_pct': 2,           # Stop loss al 2%
    'time_to_close': 60,          # Cerrar si no ha ganado en X minutos
    'min_volume_multiplier': 1.5, # Volumen mínimo
    'best_hours': ('04:00', '10:30'),  # Mejores horarios
}

# ============ BREAKOUT STRATEGY ============
BREAKOUT = {
    'lookback_period': 20,         # Máximo de últimos 20 períodos
    'profit_target_atr': 2.0,      # TP = entry + (ATR * 2)
    'stop_loss_atr': 1.0,          # SL = entry - ATR
    'min_atr': 0.20,               # ATR mínimo en $
    'volume_confirmation': True,   # Requiere volumen para breakout
    'min_volume_increase': 1.5,    # Volumen 1.5x del promedio
}

# ============ MA CROSSOVER STRATEGY ============
MA_CROSSOVER = {
    'fast_ma': 9,
    'slow_ma': 21,
    'profit_target_pct': 5,        # 5% ganancia
    'stop_loss_pct': 2.5,          # 2.5% pérdida
    'rsi_filter': True,            # Usar RSI para filtrar
    'rsi_oversold': 30,            # RSI < 30 = oversold
    'rsi_overbought': 70,          # RSI > 70 = overbought
    'min_price_for_entry': 5,      # Precio mínimo
}

# ============ COMMISSION & FEES ============
# Thinkorswim/TD Ameritrade = $0 comisiones en USA stocks
COMMISSION_PCT = 0.0  # Sin comisiones
SLIPPAGE_PCT = 0.001  # Slippage simulado 0.1%

# ============ DATABASE CONFIGURATION ============
# Para desarrollo: SQLite (más fácil)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./trading_bot_thinkorswim.db"
)

# Para producción: PostgreSQL
# DATABASE_URL = "postgresql://user:password@localhost:5432/trading_bot"

# ============ LOGGING CONFIGURATION ============
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "logs/trading_bot_thinkorswim.log"
LOG_TO_CONSOLE = True
LOG_MAX_SIZE = 10485760  # 10 MB antes de rotar logs

# ============ BACKTESTING CONFIGURATION ============
BACKTEST_INITIAL_CASH = 10000
BACKTEST_COMMISSION = 0.0  # TD Ameritrade = $0
BACKTEST_START_DATE = "2023-01-01"  # 2 años de datos
BACKTEST_END_DATE = "2025-01-01"
BACKTEST_SLIPPAGE = 0.001

# ============ OPTIMIZATION CONFIGURATION ============
OPTIMIZATION_ENABLED = True
OPTIMIZATION_FREQUENCY = "weekly"  # daily, weekly, monthly
OPTIMIZATION_LOOKBACK_DAYS = 60  # Usar últimos 60 días
OPTIMIZATION_METHOD = "sharpe_ratio"  # sharpe_ratio, max_return, max_winning_rate

# ============ DASHBOARD CONFIGURATION ============
DASHBOARD_PORT = 8501
DASHBOARD_HOST = "localhost"
DASHBOARD_AUTO_REFRESH = 60  # Segundos entre updates

# ============ NOTIFICATIONS ============
SEND_ALERTS = True
ALERT_EMAIL = os.getenv("ALERT_EMAIL", "tu_email@gmail.com")
ALERT_ON_TRADE = True  # Alertar cuando entra/sale
ALERT_ON_ERROR = True  # Alertar si hay errores
ALERT_ON_DAILY_LOSS = True  # Alertar si alcanza límite de pérdida

# ============ SYMBOLS CONFIGURATION ============
# Símbolos a escanear (separa con comas)
WATCHLIST = os.getenv("WATCHLIST", "AAPL,MSFT,TSLA,AMZN,GOOGL,META,NVDA,AMD")

# Puedes obtener watchlist del .env o hardcodear aquí
if isinstance(WATCHLIST, str):
    WATCHLIST = [s.strip().upper() for s in WATCHLIST.split(',')]

# ============ DEVELOPMENT SETTINGS ============
DEBUG_MODE = False
VERBOSE_LOGGING = False
DRY_RUN = False  # Si True, simula órdenes sin ejecutarlas
TEST_MODE = True  # Modo test - más logs, menos riesgo

# ============ THINKORSWIM SPECIFIC ============
# Cambios de setup según el broker
BROKER_NAME = "TD Ameritrade (Thinkorswim)"
API_TYPE = "TDA"  # TD Ameritrade
OAUTH_ENABLED = True

# Parámetro de sesión de mercado
MARKET_SESSION = "NORMAL"  # NORMAL, EXTENDED (para premarket/afterhours)

# Duraciones de órdenes
ORDER_DURATION = "DAY"  # DAY, GTC (Good Till Canceled), GTD (Good Till Date)

print("✓ Configuración Thinkorswim cargada exitosamente")
print(f"  Modo: {TRADING_MODE}")
print(f"  Broker: {BROKER_NAME}")
print(f"  Símbolos: {len(WATCHLIST)}")
print(f"  Estrategias activas: {sum(1 for v in STRATEGIES_ENABLED.values() if v)}/3")
