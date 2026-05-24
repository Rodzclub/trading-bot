# Trading Bot Automatizado - Thinkorswim (TD Ameritrade)

Sistema de trading automatizado profesional para escanear y operar en el mercado de valores estadounidense con **Thinkorswim/TD Ameritrade**, con enfoque en premarket gaps, breakouts y estrategias de momentum.

**⭐ DOCUMENTATION PRINCIPAL: Lee [THINKORSWIM_COMPLETE.md](THINKORSWIM_COMPLETE.md) para toda la información necesaria.**

## 🎯 Objetivos

- ✅ Automatizar entrada y salida de posiciones
- ✅ Escanear premarket en busca de oportunidades
- ✅ Ejecutar múltiples estrategias de forma simultánea
- ✅ Gestionar riesgo automáticamente
- ✅ Optimizar estrategias continuamente
- ✅ Proporcionar dashboard de monitoreo en tiempo real
- ✅ Acceso desde iPhone/iPad
- ✅ Ejecutar 24/7 en Cloud (sin PC prendida)

## 🚀 Quick Start (5 minutos)

Para setup rápido: Ve a [THINKORSWIM_COMPLETE.md → Quick Start](THINKORSWIM_COMPLETE.md#quick-start)

```bash
# 1. Obtener Consumer Key: https://developer.tdameritrade.com/
# 2. Configurar .env con TD_CONSUMER_KEY y TD_ACCOUNT_ID
# 3. python setup_oauth.py
# 4. python thinkorswim_broker.py  (verificar conexión)
# 5. python scanner_premarket.py   (ejecutar scanner)
```

## 📁 Estructura del Proyecto

```
trading-bot/
├── thinkorswim_broker.py      # Conector con TD Ameritrade (PRINCIPAL)
├── config_thinkorswim.py      # Configuración para Thinkorswim (USA)
├── setup_oauth.py             # Setup OAuth (ejecutar una sola vez)
├── broker.py                  # Conector Alpaca (referencia deprecada)
├── config.py                  # Configuración Alpaca (referencia deprecada)
├── scanner_premarket.py       # Scanner de oportunidades
├── strategies/
│   ├── gap_and_go.py         # Estrategia Gap & Go
│   ├── breakout.py           # Estrategia Breakout
│   └── ma_crossover.py       # Estrategia Media Móvil
├── risk_management/
│   ├── position_sizing.py    # Cálculo de posición
│   └── daily_limits.py       # Límites diarios
├── backtesting/
│   └── backtest_engine.py    # Framework backtesting
├── dashboard/
│   └── app.py                # Dashboard Streamlit
├── database/
│   └── models.py             # Modelos SQLAlchemy
├── logs/                      # Archivos de log
├── requirements.txt           # Dependencias Python
├── THINKORSWIM_SETUP.md      # Guía de setup (IMPORTANTE)
├── MIGRACION_ALPACA_A_THINKORSWIM.md
├── DEPLOYMENT_PC_CLOUD.md    # Cloud deployment guide
├── RESPUESTAS_RAPIDAS.md     # FAQ rápido
└── README.md                  # Este archivo
```

⭐ **Archivos clave:**
- `thinkorswim_broker.py` - Tu broker (TD Ameritrade)
- `config_thinkorswim.py` - Tus parámetros
- `THINKORSWIM_SETUP.md` - Lee primero

## 🔧 Configuración

Ver [THINKORSWIM_COMPLETE.md → Configuración Inicial](THINKORSWIM_COMPLETE.md#configuración-inicial) para detalles completos.

Parámetros principales en `config_thinkorswim.py`:
```python
RISK_PER_TRADE = 0.01      # 1% del capital por trade
MAX_DAILY_LOSS_PCT = 0.02  # Máximo 2% pérdida diaria
MAX_OPEN_POSITIONS = 3     # Máximo 3 posiciones abiertas
```

## 📊 Estrategias Disponibles

Ver [THINKORSWIM_COMPLETE.md → Estrategias de Trading](THINKORSWIM_COMPLETE.md#estrategias-de-trading) para ejemplos y parámetros completos.

**1. Gap and Go** - Premarket gaps con volumen anómalo (3-5% riesgo)  
**2. Breakout** - Ruptura de máximos en intraday (2-3% riesgo)  
**3. Media Móvil Cruce** - SMA 9/21 crossover swing (1-2% riesgo)

## 🎓 Hoja de Ruta

Ver [THINKORSWIM_COMPLETE.md → Próximos Pasos](THINKORSWIM_COMPLETE.md#próximos-pasos) para detalles semanales.

| Fase | Semana | Objetivo |
|------|--------|----------|
| 1 | 1-3 | Setup inicial + Thinkorswim ✅ |
| 2 | 3-5 | Scanner premarket |
| 3 | 5-8 | Estrategias + Backtesting |
| 4 | 9-11 | Paper Trading (2-4 semanas) |
| 5 | 12+ | Dinero Real ($500-1k) |

## 🧪 Testing & Backtesting

```bash
python backtesting/backtest_engine.py
```

Métricas viables: Sharpe > 1.0, Win Rate > 50%, Max DD < 15%

Detalles en [THINKORSWIM_COMPLETE.md](THINKORSWIM_COMPLETE.md)

## 📈 Monitoreo en Tiempo Real

```bash
python main.py                          # Bot automatizado
streamlit run dashboard/app.py          # Dashboard web
tail -f logs/trading_bot_thinkorswim.log # Logs
```

## ⚠️ Reglas de Oro

1. ✅ **Riesgo máximo 1%** por trade
2. ✅ **Stop loss obligatorio** en CADA posición
3. ✅ **Backtest primero** antes de operar
4. ✅ **Paper trading 2-4 semanas** mínimo
5. ✅ **Dinero real gradualmente** ($500-1k inicial)

[Ver reglas completas](THINKORSWIM_COMPLETE.md#seguridad---reglas-de-oro)

## 🔐 Seguridad

- **Credenciales:** En `.env`, NUNCA en código
- **OAuth Token:** `token.json` en `.gitignore`
- **Paper Trading:** Activado por defecto
- **Límites:** Conservadores por defecto

[Configuración de seguridad completa](THINKORSWIM_COMPLETE.md#seguridad---reglas-de-oro)

## 📚 Recursos

- [TD Ameritrade API Docs](https://developer.tdameritrade.com/apis)
- [TDA Python Client](https://github.com/td-ameritrade/tda-api)
- [Thinkorswim Manual](https://www.tdameritrade.com/tools-and-platforms/thinkorswim/features.html)
- [r/algotrading](https://reddit.com/r/algotrading)
- [QuantConnect.com](https://www.quantconnect.com/)

## 🐛 Troubleshooting

Errores comunes y soluciones en [THINKORSWIM_COMPLETE.md → Troubleshooting](THINKORSWIM_COMPLETE.md#troubleshooting)

Comandos útiles:
```bash
tail -f logs/trading_bot_thinkorswim.log  # Ver logs
grep ERROR logs/trading_bot_thinkorswim.log  # Buscar errores
```

## 📞 Soporte

1. Revisa [THINKORSWIM_COMPLETE.md](THINKORSWIM_COMPLETE.md)
2. Ver logs: `tail -f logs/trading_bot_thinkorswim.log`
3. Troubleshooting: [Sección de errores](THINKORSWIM_COMPLETE.md#troubleshooting)
4. Comunidad: [r/algotrading](https://reddit.com/r/algotrading)

## ⚖️ Disclaimer

**ESTE SOFTWARE SE PROPORCIONA COMO ESTÁ, SIN GARANTÍA.**

- El trading implica riesgo de pérdida de capital
- Comienza con dinero simulado (paper trading)
- Consulta con un asesor financiero antes de invertir dinero real
- No te conviertas en deuda por tradear

## 📝 License

MIT License - Siéntete libre de usar, modificar y distribuir.

---

**Creado:** Mayo 2026  
**Última actualización:** Mayo 2026  
**Versión:** 1.0 (Thinkorswim Edition)

**📖 [VER DOCUMENTACIÓN COMPLETA →](THINKORSWIM_COMPLETE.md)**

¡Buena suerte con tus trades! 📈💪
