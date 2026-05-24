# 🔄 Plan de Migración: Alpaca → Thinkorswim

Buena noticia: **Ya tienes Alpaca configurado**, así que convertir a Thinkorswim es fácil.

## Por Qué Cambiar a Thinkorswim

| Aspecto | Alpaca | Thinkorswim | Ganancia |
|--------|--------|-------------|----------|
| **API Robustez** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | +1 |
| **Datos Tiempo Real** | ✅ | ✅ | 0 |
| **Comisiones** | $0 | $0 | 0 |
| **Paper Trading** | ✅ | ✅ | 0 |
| **Documentación** | Buena | Excelente | +1 |
| **Scripting** | No | ThinkScript | +1 |
| **Estabilidad** | Buena | Excelente | +1 |
| **Comunidad Trading** | Pequeña | AMPLIA | +1 |
| **Datos Históricos** | Limitados | Completos | +1 |
| **Análisis Técnico** | Básico | Avanzado | +1 |

**Conclusión:** Thinkorswim es superior para tu caso de uso.

---

## ✅ CHECKLIST DE MIGRACIÓN

### Fase 1: Preparación (Hoy - 30 minutos)

- [ ] Leer `THINKORSWIM_SETUP.md` completo
- [ ] Crear cuenta TD Ameritrade (si no tienes)
- [ ] Registrarse en https://developer.tdameritrade.com/
- [ ] Crear aplicación para obtener Consumer Key
- [ ] Editar `.env` con Consumer Key y Account ID

### Fase 2: Instalación (Mañana - 1 hora)

- [ ] `pip install tda-api` (nueva librería)
- [ ] Copiar `thinkorswim_broker.py` a carpeta del proyecto
- [ ] Copiar `config_thinkorswim.py` a carpeta del proyecto
- [ ] Crear `setup_oauth.py` (para autenticación)
- [ ] Ejecutar `python setup_oauth.py` (Una sola vez)

### Fase 3: Validación (Esta semana - 30 minutos)

- [ ] Ejecutar `python thinkorswim_broker.py` 
- [ ] Verificar conexión y datos de cuenta
- [ ] Probar obtener posiciones
- [ ] Probar obtener cotizaciones

### Fase 4: Adaptación del Código (Esta semana - 2 horas)

- [ ] Cambiar importaciones en `main.py`:
  ```python
  # Cambiar de:
  from broker import AlpacaBroker
  
  # A:
  from thinkorswim_broker import ThinkOrSwimBroker
  ```
- [ ] Cambiar configuración en `config.py`:
  ```python
  # Cambiar de:
  import config
  
  # A:
  import config_thinkorswim as config
  ```
- [ ] Probar scanner con Thinkorswim
- [ ] Probar órdenes test (paper trading)

### Fase 5: Migración Completa (Semana siguiente)

- [ ] Todos los scanners funcionando
- [ ] Todas las estrategias funcionando
- [ ] Dashboard funcionando
- [ ] Paper trading por 2-4 semanas con Thinkorswim

---

## 🔧 CAMBIOS TÉCNICOS NECESARIOS

### 1. Cambio de Importación en main.py

**Antes (Alpaca):**
```python
from broker import AlpacaBroker, create_broker

broker = create_broker(paper=True)
```

**Después (Thinkorswim):**
```python
from thinkorswim_broker import ThinkOrSwimBroker, create_broker

broker = create_broker()  # Sin parámetro paper
```

### 2. Cambio de Configuración

**Antes (Alpaca):**
```python
import config
from broker import AlpacaBroker

api_key = config.ALPACA_API_KEY
secret_key = config.ALPACA_SECRET_KEY
```

**Después (Thinkorswim):**
```python
import config_thinkorswim as config
from thinkorswim_broker import ThinkOrSwimBroker

consumer_key = config.TD_CONSUMER_KEY
account_id = config.TD_ACCOUNT_ID
```

### 3. Métodos de Órdenes (SON IGUALES)

¡Buena noticia! Los métodos principales son idénticos:

```python
# AMBOS usan:
broker.submit_market_order(symbol, qty, side)
broker.submit_limit_order(symbol, qty, side, price)
broker.get_positions()
broker.get_account()
broker.close_position(symbol)
```

### 4. Cambios en Data

**Alpaca:**
```python
bars = broker.get_bars(symbol, timeframe="1Min", limit=100)
```

**Thinkorswim:**
```python
bars = broker.get_price_history(
    symbol, 
    period_type='day',
    period=10,
    frequency_type='minute',
    frequency=1
)
```

---

## 📋 PASOS DETALLADOS

### Step 1: Obtener Consumer Key

```
1. Ve a: https://developer.tdameritrade.com/
2. "Register for a Free Account"
3. Completa formulario
4. Verifica email
5. "My Apps" → "Create App"
   - App Name: TradingBot
   - Callback URL: http://localhost:8000
6. Copia tu Consumer Key (API Key)
7. Edita .env:
   TD_CONSUMER_KEY=PK_...
   TD_ACCOUNT_ID=123456789  (lo ves en TD Ameritrade)
```

### Step 2: Instalar Dependencias

```bash
# Agregar a requirements.txt:
tda-api==2.2.0

# O instalar directamente:
pip install tda-api
```

### Step 3: Ejecutar OAuth Setup

```bash
# Esto abre un navegador para autorizar
python setup_oauth.py

# Resultado:
# ✅ OAuth configurado exitosamente!
# Token guardado en: token.json
```

### Step 4: Probar Conexión

```bash
python thinkorswim_broker.py

# Esperado:
# ✓ Conectado a TD Ameritrade Thinkorswim
# ✓ Acceso a 1 cuenta(s)
#   - [NOMBRE]: $10,000.00
```

### Step 5: Adaptar Scanner

**Antes:**
```python
from broker import create_broker
import config

broker = create_broker(paper=True)
data = broker.get_bars(symbol, timeframe="1Min")
```

**Después:**
```python
from thinkorswim_broker import create_broker
import config_thinkorswim as config

broker = create_broker()
data = broker.get_price_history(
    symbol,
    period_type='day',
    period=10,
    frequency_type='minute',
    frequency=1
)
```

---

## ⚠️ COSAS QUE NO CAMBIAN

- ✅ Lógica de estrategias (gap_and_go.py, breakout.py, ma_crossover.py)
- ✅ Risk management (position_sizing.py, daily_limits.py)
- ✅ Backtesting (mismos indicadores técnicos)
- ✅ Dashboard (mismo Streamlit)
- ✅ Database (mismo SQLAlchemy)
- ✅ Logs y monitoreo

Solo cambia la capa de conexión al broker.

---

## 🎯 TIMELINE RECOMENDADO

| Día | Tarea | Tiempo |
|-----|-------|--------|
| **Hoy** | Setup Consumer Key + .env | 20 min |
| **Mañana** | Instalar tda-api + OAuth | 30 min |
| **Mañana (tarde)** | Probar conexión | 10 min |
| **Día 3** | Adaptar scanner | 1 hora |
| **Día 4-5** | Adaptar estrategias | 2 horas |
| **Día 6-7** | Paper trading inicial | - |

**Total: ~4 horas de trabajo**

---

## 🚨 PROBLEMAS COMUNES Y SOLUCIONES

### Error: "ModuleNotFoundError: tda"
```bash
pip install tda-api --upgrade
```

### Error: "TD_CONSUMER_KEY not in .env"
```bash
# Verifica que .env tiene:
TD_CONSUMER_KEY=PK_...
TD_ACCOUNT_ID=123456789
```

### Error: "OAuth token not found"
```bash
# Ejecuta:
python setup_oauth.py

# Esto abrirá navegador y guardará token.json
```

### Error: "Account ID incorrect"
- Abre tu cuenta TD Ameritrade
- Ve a Settings
- Copia el Account ID exacto (puede tener guiones)
- Pégalo en .env sin espacios

### Falta de datos históricos
```python
# Thinkorswim necesita más tiempo para datos
# Aumenta el period:
broker.get_price_history(
    symbol,
    period_type='day',
    period=20,  # En vez de 10
    frequency_type='minute',
    frequency=1
)
```

---

## ✨ VENTAJAS DESPUÉS DE MIGRAR

### 1. Acceso a Thinkorswim Desktop
- Interfaz profesional
- Gráficos avanzados
- Watchlists
- Alertas
- ThinkScript

### 2. Mejor Documentación
- Ejemplos de código en Python
- Comunidad grande
- Stack Overflow tiene respuestas

### 3. Más Confiabilidad
- TD Ameritrade = broker profesional (desde 1971)
- Alpaca = broker nuevo y joven
- Para dinero real, TD es más seguro

### 4. Sincronización con Desktop
- Órdenes colocadas por bot → visibles en Thinkorswim
- Datos sincronizados en tiempo real
- Puedes monitorear en desktop mientras bot corre

---

## 📊 COMPARATIVA DE CÓDIGO

### Obtener Cotización

**Alpaca:**
```python
quote = broker.get_latest_bar("AAPL")
print(quote['close'])
```

**Thinkorswim:**
```python
quote = broker.get_quote("AAPL")
print(quote['last'])
```

### Colocar Orden

**Ambos IGUALES:**
```python
broker.submit_market_order("AAPL", 10, "BUY")
```

### Obtener Posiciones

**Ambos IGUALES:**
```python
positions = broker.get_positions()
for pos in positions:
    print(f"{pos['symbol']}: {pos['qty']}")
```

---

## 🎓 RECURSOS

### Documentación Oficial
- [TD Ameritrade API Docs](https://developer.tdameritrade.com/apis)
- [TDA Python Client](https://github.com/td-ameritrade/tda-api)
- [Thinkorswim Manual](https://www.tdameritrade.com/tools-and-platforms/thinkorswim/features.html)

### Comunidades
- r/thinkorswim (Reddit)
- ThinkorSwim Lounge (TD Ameritrade)
- QuantShare Forum

---

## ❓ PREGUNTAS FRECUENTES

**P: ¿Pierdo mi cuenta Alpaca si cambio?**
No. Ambas pueden coexistir. Alpaca seguirá ahí.

**P: ¿Se pierden los datos de trades anteriores?**
No. Usa base de datos separada (thinkorswim vs alpaca).

**P: ¿Puedo tener ambos ejecutándose simultáneamente?**
Sí, pero necesitarías instancias separadas (complicado).

**P: ¿Cuál es el token.json? ¿Es seguro?**
Es tu OAuth token. NUNCA lo compartas. Gitignore automáticamente.

**P: ¿Si cierro sesión se borra el token?**
No. El token persiste hasta que lo revokes manualmente.

**P: ¿Puedo usar esto en múltiples computadoras?**
Sí, pero compartir el token.json es problemático. Mejor hacer OAuth en cada máquina.

---

## 🎉 DESPUÉS DE MIGRACIÓN

Tendrás:
- ✅ Bot más robusto
- ✅ Datos mejores
- ✅ Comunidad más grande
- ✅ Scripting nativo en Thinkorswim
- ✅ Acceso a más herramientas

Pero seguirás manteniendo:
- ✅ Mismo código Python
- ✅ Mismas estrategias
- ✅ Mismo paper trading
- ✅ Misma lógica

---

## 🚀 COMIENZA AHORA

1. Abre `THINKORSWIM_SETUP.md`
2. Sigue el Paso 1-3 hoy
3. Mañana ejecuta `setup_oauth.py`
4. Esta semana adapta el código

¿Preguntas? Dime en qué paso te atascas y te ayudo.
