# 📚 THINKORSWIM TRADING BOT - DOCUMENTACIÓN COMPLETA

**Versión:** 1.0  
**Última actualización:** 17 de Mayo 2026  
**Broker:** TD Ameritrade / Thinkorswim  
**Objetivo:** Bot de trading automatizado con escaneo premarket, múltiples estrategias y gestión de riesgo

---

## 📑 TABLA DE CONTENIDOS

1. [Quick Start (5 minutos)](#quick-start)
2. [Configuración Inicial (30 minutos)](#configuración-inicial)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [API Thinkorswim](#api-thinkorswim)
5. [Estrategias de Trading](#estrategias-de-trading)
6. [Ejecución del Bot](#ejecución-del-bot)
7. [Deployment en Cloud](#deployment-en-cloud)
8. [Preguntas Frecuentes](#preguntas-frecuentes)
9. [Troubleshooting](#troubleshooting)
10. [Próximos Pasos](#próximos-pasos)

---

## QUICK START

### Paso 1: Obtener Consumer Key (10 minutos)

```bash
# 1. Ve a: https://developer.tdameritrade.com/
# 2. Registrate con tu email
# 3. En "My Apps" → "Create App"
#    - App Name: TradingBot
#    - Callback URL: http://localhost:8000
# 4. Copia tu Consumer Key (API Key)
# 5. Copia tu Account ID (de tu login TD)
```

### Paso 2: Instalar Dependencias (5 minutos)

```bash
# Crear ambiente virtual
python -m venv venv

# Activar ambiente
# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate

# Instalar librerías
pip install tda-api pandas numpy ta-lib streamlit plotly

# O todo junto:
pip install -r requirements.txt
```

### Paso 3: Configurar Variables de Entorno (5 minutos)

```bash
# Copiar template
cp .env.example .env

# Editar .env y rellenar:
TD_CONSUMER_KEY=PK_YOUR_KEY_HERE
TD_ACCOUNT_ID=123456789
ALERT_EMAIL=tu_email@gmail.com
```

### Paso 4: Setup OAuth (Una sola vez - 5 minutos)

```bash
# Esto abre tu navegador para autorizar
python setup_oauth.py

# Se abrirá navegador pidiendo autorización
# Haz clic en "Allow"
# Se guardará token.json automáticamente

# Resultado esperado:
# ✅ OAuth configurado exitosamente!
# Token guardado en: token.json
```

### Paso 5: Probar la Conexión (2 minutos)

```bash
python thinkorswim_broker.py

# Resultado esperado:
# ✓ Conectado a TD Ameritrade Thinkorswim
# ✓ Acceso a 1 cuenta(s)
#    - [NOMBRE]: $10,000.00
# Cash: $10,000.00
# Buying Power: $40,000.00
```

Si ves esto → **¡Estás listo!** ✅

---

## CONFIGURACIÓN INICIAL

### 1. Crear Cuenta Demo en TD Ameritrade

```
1. Ve a: https://www.tdameritrade.com/
2. Abre una cuenta de práctica (paper trading)
3. Recibirás $100,000 en dinero simulado
4. No necesita depositar dinero real
```

### 2. Registrarse en TD Developer

```
1. Ve a: https://developer.tdameritrade.com/
2. Haz clic en "Login" con tus credenciales de TD
3. Ve a "My Apps"
4. Crea una nueva aplicación:
   - Nombre: TradingBot
   - Descripción: Bot automatizado para gap trading
   - Callback URL: http://localhost:8000
5. Copia el Consumer Key (API Key)
```

### 3. Configurar Proyecto Python

```bash
# Clonar o descargar
git clone <tu-repo>
cd trading-bot

# Crear ambiente
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env
cp .env.example .env
```

### 4. Editar .env

```bash
# Abre .env en tu editor favorito
TD_CONSUMER_KEY=PK_abc123xyz789...  # Copia tu Consumer Key
TD_ACCOUNT_ID=123456789            # Tu Account ID (ej: en login TD)
ALERT_EMAIL=tu@email.com           # Para notificaciones
```

### 5. Ejecutar OAuth Setup

```bash
python setup_oauth.py

# Se abrirá un navegador automáticamente
# Haz clic en "Allow" para autorizar
# Cierra el navegador cuando veas "Authorization Successful"
# Se crea token.json automáticamente (NO COMITEAR A GIT)
```

### 6. Verificar Conexión

```bash
python thinkorswim_broker.py

# Deberías ver tu información de cuenta
```

---

## ESTRUCTURA DEL PROYECTO

```
trading-bot/
├── thinkorswim_broker.py           # ⭐ Conector principal con TD Ameritrade
├── config_thinkorswim.py           # ⭐ Configuración de parámetros
├── setup_oauth.py                  # Setup de autorización (ejecutar una sola vez)
├── scanner_premarket.py            # Escanea oportunidades en premarket
├── main.py                         # Punto de entrada del bot
│
├── strategies/
│   ├── gap_and_go.py              # Gap & Go (premarket)
│   ├── breakout.py                # Breakout (intraday)
│   └── ma_crossover.py            # Media Móvil Crossover (swing)
│
├── risk_management/
│   ├── position_sizing.py         # Calcula tamaño de posición
│   └── daily_limits.py            # Límites de riesgo diario
│
├── backtesting/
│   └── backtest_engine.py         # Framework de backtesting
│
├── database/
│   └── models.py                  # Modelos SQLAlchemy
│
├── dashboard/
│   └── app.py                     # Dashboard Streamlit
│
├── logs/                          # Archivos de log
├── .env                           # Variables de entorno (NO COMITEAR)
├── .env.example                   # Template de .env
├── token.json                     # OAuth token (NO COMITEAR)
├── requirements.txt               # Dependencias Python
└── README.md                      # Overview del proyecto
```

---

## API THINKORSWIM

### ThinkOrSwimBroker - Métodos Principales

```python
from thinkorswim_broker import ThinkOrSwimBroker
import config_thinkorswim as config

broker = ThinkOrSwimBroker()

# ============ INFORMACIÓN DE CUENTA ============
account = broker.get_account()      # Dict con toda la info
cash = broker.get_cash()            # Float: dinero disponible
bp = broker.get_buying_power()      # Float: poder de compra

# ============ POSICIONES ============
positions = broker.get_positions()  # List[Dict] de todas las posiciones
pos = broker.get_position("AAPL")   # Dict de una posición específica o None
broker.close_position("AAPL")       # Cierra posición completa

# ============ ÓRDENES ============
broker.submit_market_order("AAPL", 10, "BUY")
broker.submit_limit_order("AAPL", 10, "BUY", 150.50)
broker.cancel_order(order_id)
orders = broker.get_orders()        # Lista de órdenes abiertas

# ============ DATOS DE MERCADO ============
quote = broker.get_quote("AAPL")    # Dict: bid, ask, last, etc
bars = broker.get_price_history(
    "AAPL",
    period_type='day',
    period=10,
    frequency_type='minute',
    frequency=1
)
```

### Ejemplo Completo

```python
from thinkorswim_broker import ThinkOrSwimBroker
import config_thinkorswim as config

def main():
    broker = ThinkOrSwimBroker()
    
    # Obtener cuenta
    account = broker.get_account()
    print(f"Cash: ${account['cash']}")
    print(f"Buying Power: ${account['buying_power']}")
    
    # Colocar orden
    order = broker.submit_market_order("AAPL", 1, "BUY")
    print(f"Orden colocada: {order}")
    
    # Verificar posición
    position = broker.get_position("AAPL")
    print(f"Posición AAPL: {position}")
    
    # Cerrar posición
    broker.close_position("AAPL")
    print("Posición cerrada")

if __name__ == "__main__":
    main()
```

---

## ESTRATEGIAS DE TRADING

### 1. Gap and Go (Premarket)

**Concepto:** Compra acciones con gap significativo + volumen anómalo, sale rápido al 2-5%

**Parámetros en config_thinkorswim.py:**
```python
GAP_AND_GO = {
    'entry_gap_min': 2,           # Gap mínimo 2%
    'entry_gap_max': 10,          # Gap máximo 10%
    'volume_multiplier_min': 1.5, # Volumen 1.5x
    'profit_target_pct': 3,       # Tomar ganancia al 3%
    'stop_loss_pct': 2,           # Stop loss al 2%
    'max_holding_time': 60        # Máximo 60 minutos
}
```

**Cuándo usar:**
- ⏰ Premarket: 04:00 - 10:30 EST
- 💰 Capital: $5,000+
- 📊 Riesgo: Alto (3-5% por trade)
- ⏱️ Duración: 15-60 minutos

**Ejemplo:**
```
[04:15] TSLA: Gap +5.2%, Vol 2.1x → COMPRAR
Entry: $140 | TP: $144.20 (3%) | SL: $137.20 (2%)
[04:45] Target alcanzado → VENDER
Ganancia: $420 (3% de $14,000)
```

---

### 2. Breakout (Intraday)

**Concepto:** Compra cuando precio rompe máximo de 20 períodos, usa ATR para TP/SL

**Parámetros:**
```python
BREAKOUT = {
    'lookback_period': 20,        # Máximo de últimas 20 velas
    'atr_period': 14,
    'profit_target_atr': 2.0,     # TP = Entrada + (2 x ATR)
    'stop_loss_atr': 1.0,         # SL = Entrada - (1 x ATR)
}
```

**Cuándo usar:**
- ⏰ Intraday: 09:30 - 15:30 EST
- 💰 Capital: $5,000+
- 📊 Riesgo: Medio (2-3% por trade)
- ⏱️ Duración: 30 min - 2 horas

---

### 3. Media Móvil Crossover (Swing)

**Concepto:** Compra cuando SMA 9 cruza por arriba de SMA 21

**Parámetros:**
```python
MA_CROSSOVER = {
    'fast_ma': 9,                 # Media móvil rápida
    'slow_ma': 21,                # Media móvil lenta
    'profit_target_pct': 5,       # Tomar ganancia al 5%
    'stop_loss_pct': 2.5,         # Stop loss al 2.5%
}
```

**Cuándo usar:**
- ⏰ Intraday + Swing: 09:30 - 16:00 EST
- 💰 Capital: $5,000+
- 📊 Riesgo: Bajo-Medio (1-2% por trade)
- ⏱️ Duración: 1-5 días

---

## EJECUCIÓN DEL BOT

### Modo 1: Escaneo Manual (Testing)

```bash
# Terminal 1: Ejecutar scanner
python scanner_premarket.py

# Verás:
# Escaneando premarket...
# [04:15] TSLA: Gap +5.2%, Vol 2.1x → OPORTUNIDAD
# [04:16] NVDA: Gap +3.1%, Vol 1.8x → OPORTUNIDAD
# [04:17] AMD: Gap -1.5%, Vol 1.2x → No cumple
# Total oportunidades: 4

# Terminal 2: Verificar conexión
python thinkorswim_broker.py

# Terminal 3: Ver dashboard
streamlit run dashboard/app.py
# Abre: http://localhost:8501
```

### Modo 2: Bot Automatizado (Paper Trading)

```bash
# En terminal única
python main.py

# El bot:
# 1. Escanea cada 60 segundos
# 2. Genera órdenes automáticas
# 3. Monitorea TP/SL
# 4. Registra logs en logs/trading_bot_thinkorswim.log
# 5. Actualiza dashboard en tiempo real

# Para detener:
# CTRL+C
```

### Modo 3: Bot en Background (Cloud)

```bash
# En servidor remoto (DigitalOcean, AWS, etc)
tmux new-session -d -s bot "python main.py"

# Ver si corre:
tmux list-sessions

# Ver logs:
tmux attach-session -t bot
# Salir sin detener: CTRL+B, D
```

---

## DEPLOYMENT EN CLOUD

### Opción Recomendada: DigitalOcean ($5/mes)

#### Paso 1: Crear Droplet

```
1. Ve a: https://www.digitalocean.com
2. "Create" → "Droplets"
3. Selecciona:
   - OS: Ubuntu 22.04
   - Plan: Basic ($5/month)
   - Region: NYC o SFO
4. Crea el droplet
5. Recibirás email con contraseña root
```

#### Paso 2: Conectar SSH

```bash
# En tu PC
ssh root@TU_IP_DROPLET

# Cambia contraseña
passwd
```

#### Paso 3: Instalar Dependencias

```bash
apt update
apt install python3-pip python3-venv git -y

# Clonar proyecto
git clone https://github.com/tuusuario/trading-bot.git
cd trading-bot

# Crear ambiente
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

#### Paso 4: Ejecutar Bot en Background

```bash
# Opción 1: tmux (mejor)
apt install tmux
tmux new-session -d -s bot "python main.py"

# Opción 2: nohup (más simple)
nohup python main.py > bot.log 2>&1 &
tail -f bot.log  # Ver logs
```

#### Paso 5: Acceder Dashboard desde iPhone

```
1. En servidor: El bot corre en puerto 8501
2. En iPhone (WiFi o remoto):
   Safari → http://TU_IP:8501
```

#### Costos Mensuales
```
- DigitalOcean Droplet: $5/mes
- Dominio (opcional): $10-15/año
- Total: $5/mes = $0.16/día = 1 café por semana
```

---

## PREGUNTAS FRECUENTES

### P1: ¿La PC tiene que estar prendida 24/7?

**Respuesta:** ❌ NO si usas Cloud (DigitalOcean $5/mes)

Con Cloud:
- ✅ Bot corre 24/7 sin tu PC
- ✅ PC apagada = bot sigue funcionando
- ✅ Monitorea desde iPhone en cualquier parte
- ✅ Uptime 99.99% (45 minutos down/año)

---

### P2: ¿Se puede usar en iPhone?

**Respuesta:** ✅ SÍ pero no como crees

**Lo que SÍ funciona en iPhone:**
```
Dashboard Streamlit
→ Ver gráficos de ganancias/pérdidas
→ Ver operaciones abiertas
→ Ver P&L en tiempo real
→ Monitorear alertas

= Acceso completo a estadísticas (READ-ONLY)
```

**Lo que NO funciona:**
```
Ejecutar el bot en iPhone
→ iPhone no tiene Python instalado
→ Pantalla se apaga = todo se detiene
→ Consumo brutal de batería

= Imposible de usar como servidor
```

**Flujo Correcto:**
```
Thinkorswim API
     ↓
Bot Python (Cloud o PC)
     ↓
Dashboard Streamlit
     ↓
iPhone Safari (solo visualiza)
```

---

### P3: ¿Cómo accedo desde iPhone?

#### Opción A: WiFi Local (Sin Cloud)

```
1. En tu PC: python main.py
2. Encuentra IP de PC:
   Windows: ipconfig → IPv4 Address
   Mac: System Preferences → Network
3. En iPhone (WiFi MISMA RED):
   Safari → http://192.168.1.100:8501
```

#### Opción B: Cloud (Sin necesidad de WiFi)

```
1. Crea DigitalOcean ($5/mes)
2. Despliega bot en servidor
3. En iPhone (desde cualquier lugar):
   Safari → http://TU_IP_SERVIDOR:8501
```

---

### P4: ¿Cuánto cuesta Cloud?

```
DigitalOcean: $5/mes = $0.16/día = 1 café/semana

Comparativa:
| Servicio | Costo | PC Encendida |
|----------|-------|--------------|
| DigitalOcean | $5/mes | ❌ NO |
| AWS Lambda | $0-5/mes | ❌ NO |
| Replit | $7/mes | ❌ NO |
| PC Local | $0+electricidad | ✅ 24/7 |

Veredicto: Cloud es mejor + más barato
```

---

### P5: ¿Es seguro poner credenciales en Cloud?

**Respuesta:** ✅ SÍ, es MÁS seguro

**En Cloud:**
- ✅ Encriptadas y aisladas
- ✅ Aseguradas profesionalmente
- ✅ Backups automáticos
- ✅ Acceso controlado

**En PC Local:**
- ⚠️ En tu disco duro
- ⚠️ Si PC se compromete = todo se va
- ⚠️ Backup manual

**Dinero:**
- TD Ameritrade tiene el dinero (no el servidor)
- Servidor solo ejecuta órdenes
- TD verifica cada transacción
```

---

## TROUBLESHOOTING

### Error: "ModuleNotFoundError: No module named 'tda'"

```bash
pip install tda-api --upgrade
```

### Error: "TD_CONSUMER_KEY not found"

```bash
# Verifica que .env existe y tiene la key:
cat .env

# Debe verse:
# TD_CONSUMER_KEY=PK_...
# TD_ACCOUNT_ID=123456789
```

### Error: "OAuth token not found"

```bash
# Re-ejecuta setup OAuth:
python setup_oauth.py

# Te abrirá navegador para autorizar
# Haz clic en "Allow"
# Se creará token.json automáticamente
```

### Error: "Permission denied"

```bash
# Token expirado, re-ejecuta OAuth:
python setup_oauth.py
```

### Error: "No data available"

```bash
# El símbolo debe existir (AAPL, MSFT, TSLA)
# Verifica que esté correctamente escrito (mayúsculas)
# Prueba con símbolos populares primero
```

### Error: "Insufficient buying power"

```bash
# No tienes suficiente cash para la posición

# Soluciones:
1. Reduce RISK_PER_TRADE en config_thinkorswim.py
2. Reduce el precio de la acción (menos dinero)
3. Espera a tener más capital
```

### Ver logs para debuggear

```bash
# En tiempo real:
tail -f logs/trading_bot_thinkorswim.log

# Buscar errores:
grep ERROR logs/trading_bot_thinkorswim.log
```

---

## SEGURIDAD - REGLAS DE ORO

### ❌ NUNCA HAGAS ESTO:

```
❌ Invertir dinero real sin backtest
❌ Arriesgar > 1% del capital por trade
❌ Operar sin stop loss
❌ Cambiar parámetros durante la operación
❌ Ignorar el drawdown máximo
❌ Operar por emoción (miedo/avaricia)
❌ Guardar API keys en el código
❌ Operar acciones que no conozcas
❌ Comitear token.json o .env a Git
❌ Usar dinero que no puedas perder
```

### ✅ SIEMPRE HAZ ESTO:

```
✅ Paper trading primero (mínimo 2-4 semanas)
✅ Backtest antes de cualquier operación real
✅ Riesgo fijo de 1% máximo
✅ Stop loss en CADA posición
✅ Logs detallados de cada trade
✅ Seguimiento emocional
✅ Credenciales en .env, nunca en código
✅ Dinero real gradualmente (pequeñas cantidades)
✅ Agregar .env y token.json a .gitignore
✅ Documentar por qué entraste/saliste cada trade
```

### Configuración de .gitignore

```bash
# .gitignore
.env
token.json
*.db
*.log
__pycache__/
.venv/
venv/
.DS_Store
*.pyc
```

---

## PRÓXIMOS PASOS

### Hoy (Semana 1):

- [ ] Lee esta documentación completa
- [ ] Obtén Consumer Key de TD Developer
- [ ] Instala Python y dependencias
- [ ] Ejecuta `python setup_oauth.py`
- [ ] Verifica conexión: `python thinkorswim_broker.py`

### Esta Semana (Semana 1-2):

- [ ] Lee `PLAN_TRADING_BOT.md` (estrategia general)
- [ ] Entiende `thinkorswim_broker.py`
- [ ] Revisa `config_thinkorswim.py` y ajusta parámetros
- [ ] Ejecuta scanner: `python scanner_premarket.py`

### Próximas 2 Semanas (Semana 2-4):

- [ ] Estudia las 3 estrategias en detail
- [ ] Ejecuta backtesting de cada una
- [ ] Comienza paper trading manual
- [ ] Documenta CADA trade

### Semana 5+ (Producción):

- [ ] 50+ trades en paper trading exitosos
- [ ] Win rate > 50%
- [ ] Ganancias consistentes
- [ ] Considera DigitalOcean Cloud ($5/mes)
- [ ] Dinero real gradualmente ($500-1k inicial)

---

## INFORMACIÓN ADICIONAL

### Archivos Importantes

```
.env                           ← Credenciales (NUNCA en Git)
token.json                     ← OAuth token (NUNCA en Git)
config_thinkorswim.py         ← Parámetros del bot
thinkorswim_broker.py         ← Conexión con TD Ameritrade
requirements.txt              ← Dependencias Python
```

### Comandos Útiles

```bash
# Ver conexión y cuenta
python thinkorswim_broker.py

# Ejecutar scanner
python scanner_premarket.py

# Ver dashboard
streamlit run dashboard/app.py

# Ver logs
tail -f logs/trading_bot_thinkorswim.log

# Verificar sintaxis
python -m py_compile thinkorswim_broker.py
```

### Recursos Externos

- [TD Ameritrade API Docs](https://developer.tdameritrade.com/apis)
- [TDA Python Client](https://github.com/td-ameritrade/tda-api)
- [Thinkorswim Manual](https://www.tdameritrade.com/tools-and-platforms/thinkorswim/features.html)
- [TA-Lib Indicators](https://github.com/mrjbq7/ta-lib)
- [r/thinkorswim (Reddit)](https://reddit.com/r/thinkorswim)
- [r/algotrading (Reddit)](https://reddit.com/r/algotrading)

### Horarios USA (EST)

```
04:00 - 09:30   Premarket (low volume, high volatility)
09:30 - 16:00   Regular (normal trading hours)
16:00 - 20:00   Afterhours (low volume)

Best for gap_and_go:    04:00 - 10:30
Best for breakout:      09:30 - 15:30
Best for ma_crossover:  09:30 - 15:30
```

---

## RESUMEN RÁPIDO

| Pregunta | Respuesta |
|----------|-----------|
| **¿PC prendida 24/7?** | ❌ No si usas Cloud ($5/mes) |
| **¿Funciona en iPhone?** | ✅ Sí dashboard (no el bot) |
| **¿Dónde ejecutar?** | Cloud (DigitalOcean recomendado) |
| **¿Acceso desde iPhone?** | ✅ Sí vía dashboard web |
| **¿Costo Cloud?** | $5/mes = $0.16/día |
| **¿Complejidad setup?** | Media (30 minutos) |
| **¿Paper trading primero?** | ✅ Sí mínimo 2-4 semanas |
| **¿Dinero real cuándo?** | Después de 50+ trades exitosos |
| **¿1% riesgo por trade?** | ✅ Máximo absoluto |
| **¿Stop loss obligatorio?** | ✅ SÍ en CADA posición |

---

## ÚLTIMA LÍNEA DE DEFENSA

Si algo falla:

1. **Revisa logs:** `tail -f logs/trading_bot_thinkorswim.log`
2. **Verifica .env:** `cat .env` (busca errores de tipeo)
3. **Re-ejecuta OAuth:** `python setup_oauth.py`
4. **Reinicia bot:** CTRL+C, luego ejecuta de nuevo
5. **Busca en r/algotrading:** Comunidad muy activa

---

**¡Adelante con tu trading bot! 💪📈**

Versión Thinkorswim Edition v1.0  
Última actualización: 17 Mayo 2026
