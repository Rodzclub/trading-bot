# config.py - Configuración centralizada del bot

import os
from dotenv import load_dotenv

load_dotenv()

# ============ BROKER CONFIGURATION ============
BROKER_TYPE = "alpaca"  # alpaca, ib, etc
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "YOUR_API_KEY_HERE")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "YOUR_SECRET_KEY_HERE")
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"  # Paper trading URL
# ALPACA_BASE_URL = "https://api.alpaca.markets"  # Live trading URL (CUIDADO!)

PAPER_TRADING = True  # Cambiar a False solo después de validar todo

# ============ ACCOUNT CONFIGURATION ============
INITIAL_CAPITAL = 5000  # $ iniciales en la cuenta
RISK_PER_TRADE = 0.01  # 1% del capital por trade
MAX_DAILY_LOSS_PCT = 0.02  # Máximo 2% de pérdida diaria antes de STOP
MAX_TRADES_PER_DAY = 10  # Máximo trades por día
MAX_OPEN_POSITIONS = 3  # Máximo posiciones simultáneas

# ============ MARKET CONFIGURATION ============
MARKET_OPEN_TIME = "09:30"  # Apertura mercado USA
MARKET_CLOSE_TIME = "16:00"  # Cierre mercado USA
PREMARKET_OPEN = "04:00"  # Apertura premarket
PREMARKET_CLOSE = "09:30"  # Cierre premarket

# Horarios para trading (formato 24h)
TRADING_HOURS = {
    'gap_and_go': ('04:00', '10:30'),  # Premarket y primeros 60 min
    'breakout': ('09:30', '15:30'),     # Horario regular
    'ma_crossover': ('09:30', '15:30')  # Swing, horario regular
}

# ============ SCANNER CONFIGURATION ============
SCANNER_ENABLED = True
SCANNER_INTERVAL = 60  # Segundos entre scans
MIN_PRICE = 5  # Precio mínimo de acción
MAX_PRICE = 500  # Precio máximo
MIN_VOLUME = 500000  # Volumen promedio mínimo
MIN_GAP_PCT = 2  # Gap mínimo para considerarse (%)
MAX_GAP_PCT = 10  # Gap máximo (evita extremos)
MIN_VOLUME_MULTIPLIER = 1.5  # Volumen premarket vs promedio

# ============ STRATEGY CONFIGURATION ============
STRATEGIES_ENABLED = {
    'gap_and_go': True,
    'breakout': True,
    'ma_crossover': True
}

# Gap and Go Strategy
GAP_AND_GO = {
    'entry_gap_min': 2,
    'entry_gap_max': 10,
    'profit_target_pct': 3,  # Take profit 3%
    'stop_loss_pct': 2,      # Stop loss 2%
}

# Breakout Strategy
BREAKOUT = {
    'lookback_period': 20,
    'profit_target_atr': 2.0,  # TP = entry + (ATR * 2)
    'stop_loss_atr': 1.0,      # SL = entry - ATR
    'min_atr': 0.20,  # ATR mínimo en $
}

# MA Crossover Strategy
MA_CROSSOVER = {
    'fast_ma': 9,
    'slow_ma': 21,
    'profit_target_pct': 5,
    'stop_loss_pct': 2.5,
    'min_price_for_entry': 5,
}

# ============ COMMISSION & FEES ============
COMMISSION_PCT = 0.001  # 0.1% por orden (Alpaca es $0, pero dejamos para simulación)
SLIPPAGE_PCT = 0.002  # Slippage simulado 0.2%

# ============ DATABASE CONFIGURATION ============
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/trading_bot"
)
# Para desarrollo rápido, usar SQLite:
# DATABASE_URL = "sqlite:///./trading_bot.db"

# ============ LOGGING CONFIGURATION ============
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "logs/trading_bot.log"
LOG_TO_CONSOLE = True

# ============ BACKTESTING CONFIGURATION ============
BACKTEST_INITIAL_CASH = 10000
BACKTEST_COMMISSION = 0.002  # 0.2%
BACKTEST_START_DATE = "2024-01-01"
BACKTEST_END_DATE = "2025-01-01"

# ============ OPTIMIZATION CONFIGURATION ============
OPTIMIZATION_ENABLED = True
OPTIMIZATION_FREQUENCY = "weekly"  # daily, weekly, monthly
OPTIMIZATION_LOOKBACK_DAYS = 60  # Usar últimos 60 días para optimizar

# ============ DASHBOARD CONFIGURATION ============
DASHBOARD_PORT = 8501
DASHBOARD_HOST = "localhost"
DASHBOARD_AUTO_REFRESH = 60  # Segundos entre updates

# ============ NOTIFICATIONS ============
SEND_ALERTS = True
ALERT_EMAIL = os.getenv("ALERT_EMAIL", "guityrodriguez@gmail.com")
ALERT_ON_TRADE = True  # Alertar cuando entra/sale
ALERT_ON_ERROR = True  # Alertar si hay errores

# ============ DEVELOPMENT SETTINGS ============
DEBUG_MODE = False
VERBOSE_LOGGING = False
DRY_RUN = False  # Si True, simula órdenes sin ejecutarlas

print("✓ Configuración cargada exitosamente")
