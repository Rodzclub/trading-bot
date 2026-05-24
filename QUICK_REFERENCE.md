# ⚡ Quick Reference - Thinkorswim Bot

## Inicio Rápido (5 pasos)

```bash
# 1. Obtener Consumer Key en https://developer.tdameritrade.com/
# 2. Editar .env
echo "TD_CONSUMER_KEY=PK_..." >> .env
echo "TD_ACCOUNT_ID=123456789" >> .env

# 3. Instalar dependencias
pip install tda-api

# 4. Setup OAuth (abre navegador automáticamente)
python setup_oauth.py

# 5. Verificar conexión
python thinkorswim_broker.py
```

**Resultado esperado:** ✓ Cash: $10,000.00

---

## Archivos Principales

| Archivo | Propósito |
|---------|-----------|
| `thinkorswim_broker.py` | Conector con TD Ameritrade API |
| `config_thinkorswim.py` | Configuración (parámetros de estrategias) |
| `scanner_premarket.py` | Scanner de oportunidades |
| `strategies/*.py` | Lógica de estrategias |
| `dashboard/app.py` | Dashboard Streamlit |

---

## Comandos Útiles

```bash
# Ver conexión
python thinkorswim_broker.py

# Ejecutar scanner
python scanner_premarket.py

# Ver dashboard
streamlit run dashboard/app.py

# Ver logs
tail -f logs/trading_bot_thinkorswim.log

# Verificar sintaxis Python
python -m py_compile thinkorswim_broker.py
```

---

## Métodos Principales - Broker

```python
from thinkorswim_broker import ThinkOrSwimBroker
import config_thinkorswim as config

broker = ThinkOrSwimBroker()

# Account Info
account = broker.get_account()  # Dict con cash, buying_power, etc
cash = broker.get_cash()        # Float: dinero disponible
bp = broker.get_buying_power()  # Float: poder de compra

# Posiciones
positions = broker.get_positions()  # List[Dict]
pos = broker.get_position("AAPL")   # Dict o None
broker.close_position("AAPL")       # Cierra posición completa

# Órdenes
broker.submit_market_order("AAPL", 10, "BUY")
broker.submit_limit_order("AAPL", 10, "BUY", 150.50)
broker.cancel_order(order_id)
broker.get_orders()  # Lista de órdenes abiertas

# Datos
quote = broker.get_quote("AAPL")    # Dict: bid, ask, last, etc
bars = broker.get_price_history(
    "AAPL",
    period_type='day',
    period=10,
    frequency_type='minute',
    frequency=1
)
```

---

## Parámetros de Estrategias

```python
# Gap and Go (Premarket)
config_thinkorswim.GAP_AND_GO = {
    'entry_gap_min': 2,        # Gap mínimo 2%
    'entry_gap_max': 10,       # Gap máximo 10%
    'profit_target_pct': 3,    # Tomar ganancia al 3%
    'stop_loss_pct': 2,        # Stop loss al 2%
}

# Breakout (Intraday)
config_thinkorswim.BREAKOUT = {
    'lookback_period': 20,
    'profit_target_atr': 2.0,
    'stop_loss_atr': 1.0,
}

# MA Crossover (Swing)
config_thinkorswim.MA_CROSSOVER = {
    'fast_ma': 9,
    'slow_ma': 21,
    'profit_target_pct': 5,
    'stop_loss_pct': 2.5,
}
```

---

## Configuración Crítica

```python
# config_thinkorswim.py

RISK_PER_TRADE = 0.01  # 🔴 NUNCA CAMBIES: 1% máximo
MAX_DAILY_LOSS_PCT = 0.02  # 2% de pérdida diaria = STOP
MAX_OPEN_POSITIONS = 3  # Máximo 3 posiciones simultáneas

# Símbolos a escanear
WATCHLIST = "AAPL,MSFT,TSLA,AMZN,GOOGL"

# Horarios (EST)
PREMARKET_OPEN = "04:00"
MARKET_OPEN_TIME = "09:30"
MARKET_CLOSE_TIME = "16:00"
```

---

## Debugging Rápido

```python
# Test conexión
python -c "from thinkorswim_broker import ThinkOrSwimBroker; \
           b = ThinkOrSwimBroker(); \
           print(b.get_account())"

# Ver posiciones
python -c "from thinkorswim_broker import ThinkOrSwimBroker; \
           b = ThinkOrSwimBroker(); \
           print(b.get_positions())"

# Ver órdenes abiertas
python -c "from thinkorswim_broker import ThinkOrSwimBroker; \
           b = ThinkOrSwimBroker(); \
           print(b.get_orders())"

# Ver quote
python -c "from thinkorswim_broker import ThinkOrSwimBroker; \
           b = ThinkOrSwimBroker(); \
           print(b.get_quote('AAPL'))"
```

---

## Error Troubleshooting

| Error | Solución |
|-------|----------|
| ModuleNotFoundError: tda | `pip install tda-api` |
| TD_CONSUMER_KEY not found | Revisar `.env` tiene el valor |
| OAuth token not found | Ejecutar `python setup_oauth.py` |
| Permission denied | Token expirado, re-ejecutar OAuth |
| No data available | Aumentar `period` en `get_price_history()` |
| Insufficient buying power | Reducir `RISK_PER_TRADE` en config |

---

## Flujo de Operación

```
1. Scanner busca gaps/setups (cada 30-60 seg)
   ↓
2. Estrategia valida si cumple reglas
   ↓
3. Risk management calcula posición
   ↓
4. Broker coloca orden (market o limit)
   ↓
5. Database registra trade
   ↓
6. Monitor busca TP/SL
   ↓
7. Cuando se alcanza → orden de salida
   ↓
8. Log y estadísticas actualizadas
```

---

## Paper Trading Checklist

Antes de dinero real, valida:

- [ ] 50+ trades completados
- [ ] Win rate > 50%
- [ ] Profit factor > 1.5
- [ ] Max drawdown < 15%
- [ ] Consistencia en ganancias (últimas 2-3 semanas)
- [ ] Entiendes cada parámetro
- [ ] Logs documentan cada trade
- [ ] Sin emociones (sin cambios de parámetros al azar)

---

## Fórmulas de Riesgo

```python
# Position Size
max_risk_per_trade = account_size * 0.01  # 1%
position_size = max_risk_per_trade / (entry_price - stop_loss)

# Ejemplo: Account $5,000, Entry $100, SL $98
max_risk = 5000 * 0.01 = $50
pos_size = 50 / (100 - 98) = 50 / 2 = 25 acciones

# Pérdida máxima: 25 * $2 = $50 (1% de $5,000) ✓
# Ganancia si sube a $103: 25 * $3 = $75 (1.5% de $5,000) ✓
```

---

## Horarios USA EST

```
04:00 - 09:30   Premarket (low volume, high volatility)
09:30 - 16:00   Regular (normal trading hours)
16:00 - 20:00   Afterhours (low volume)

Best for gap_and_go:     04:00 - 10:30
Best for breakout:       09:30 - 15:30
Best for ma_crossover:   09:30 - 15:30
```

---

## Símbolos Recomendados para Testing

**Líquidos y predecibles:**
- AAPL (Apple)
- MSFT (Microsoft)
- TSLA (Tesla)
- AMZN (Amazon)
- GOOGL (Google)

**Volátiles (aprende):**
- AMD (Advanced Micro)
- PLTR (Palantir)
- NVDA (Nvidia)

---

## Seguridad

```
❌ NUNCA:
- Guardar API keys en código
- Compartir token.json
- Usar dinero que no puedas perder
- Arriesgar > 1% por trade
- Operar sin stop loss

✅ SIEMPRE:
- Usar .env para credenciales
- .gitignore para token.json
- Paper trading 2-4 semanas primero
- Log cada trade
- Risk management automático
```

---

## Archivos Importantes

```
.env                           ← Credenciales (NUNCA en Git)
token.json                     ← OAuth token (NUNCA en Git)
config_thinkorswim.py         ← Parámetros de bot
thinkorswim_broker.py         ← Conexión broker
trading_bot_thinkorswim.db    ← Base de datos trades
logs/trading_bot_thinkorswim.log  ← Log operaciones
```

---

## Próximos Pasos

1. **Hoy:** Completar `THINKORSWIM_SETUP.md`
2. **Mañana:** Probar conexión (`python thinkorswim_broker.py`)
3. **Día 3:** Adaptar scanner para Thinkorswim
4. **Día 4-5:** Adaptar estrategias
5. **Día 6-7:** Paper trading inicial

---

## Recursos Rápidos

- [TD Ameritrade API Docs](https://developer.tdameritrade.com/)
- [TDA Python Client](https://github.com/td-ameritrade/tda-api)
- [Thinkorswim Help](https://www.tdameritrade.com/tools-and-platforms/thinkorswim/features.html)
- [r/thinkorswim](https://reddit.com/r/thinkorswim)

---

## Última Línea de Defensa

Si algo falla:

1. Revisa logs: `tail -f logs/trading_bot_thinkorswim.log`
2. Verifica .env: `cat .env` (busca errores)
3. Re-ejecuta OAuth: `python setup_oauth.py`
4. Reinicia bot: (CTRL+C, luego ejecuta de nuevo)

---

**Creado:** Mayo 2026  
**Última actualización:** Hoy  
**Versión:** Thinkorswim Edition

¡Suerte! 💪
