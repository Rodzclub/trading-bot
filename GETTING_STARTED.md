# 🚀 GUÍA DE INICIO RÁPIDO - THINKORSWIM

## ⭐ LEE PRIMERO: THINKORSWIM_SETUP.md

Esta es la guía rápida. Para setup completo y detallado:
👉 **Lee:** `THINKORSWIM_SETUP.md`

---

## Paso 1: Obtener Consumer Key TD Ameritrade (10 minutos)

```bash
# 1. Ve a: https://developer.tdameritrade.com/
# 2. Registrate con tu email
# 3. En "My Apps" → "Create App"
#    - App Name: TradingBot
#    - Callback URL: http://localhost:8000
# 4. Copia tu Consumer Key (API Key)
# 5. Copia tu Account ID (de tu login TD)
```

## Paso 2: Instalar Dependencias (5 minutos)

```bash
# Abrir terminal/PowerShell en la carpeta del proyecto

# Crear ambiente virtual
python -m venv venv

# Activar ambiente
# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate

# Instalar librerías (IMPORTANTE: tda-api, no alpaca)
pip install -r requirements.txt
```

## Paso 3: Configurar Variables de Entorno (5 minutos)

```bash
# En la carpeta raíz, copia el archivo template
cp .env.example .env

# Abre .env en un editor de texto y rellena:
TD_CONSUMER_KEY=PK_YOUR_KEY_HERE
TD_ACCOUNT_ID=123456789
ALERT_EMAIL=tu_email@gmail.com
```

## Paso 4: Setup OAuth (Una sola vez - 5 minutos)

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

## Paso 5: Probar la Conexión (2 minutos)

```bash
# Cambia de broker.py a thinkorswim_broker.py
python thinkorswim_broker.py
```

**Resultado esperado:**
```
✓ Conectado a TD Ameritrade Thinkorswim
✓ Acceso a 1 cuenta(s)
   - [NOMBRE]: $10,000.00

Cuenta:
  Cash: $10,000.00
  Buying Power: $40,000.00

Posiciones (0):

Mercado: CERRADO
```

Si ves esto → **¡Estás listo!** ✅

## Paso 5: Ejecutar el Scanner (En Premarket: 04:00-09:30 EST)

```bash
python scanner_premarket.py
```

**Qué verás:**
```
Escaneando premarket...
[04:15] TSLA: Gap +5.2%, Vol 2.1x → OPORTUNIDAD
[04:16] NVDA: Gap +3.1%, Vol 1.8x → OPORTUNIDAD
[04:17] AMD: Gap -1.5%, Vol 1.2x → No cumple
...
Total oportunidades: 4
```

## Paso 6: Ver Dashboard (Opcional, pero recomendado)

En otra terminal:
```bash
streamlit run dashboard/app.py
```

Abre: http://localhost:8501

## 🎯 Próximos Pasos (Orden de Importancia)

### Esta Semana:

**Día 1-2: Entender la arquitectura**
- [ ] Lee `PLAN_TRADING_BOT.md` (estrategia general)
- [ ] Lee `README.md` (estructura del proyecto)
- [ ] Prueba conexión a Thinkorswim

**Día 3-4: Explorar el código**
- [ ] Abre `thinkorswim_broker.py` y entiende cada función
- [ ] Revisa `config_thinkorswim.py` y ajusta parámetros según tus necesidades
- [ ] Ejecuta scanner en horario premarket

**Día 5-7: Primeras órdenes de prueba**
- [ ] Ejecuta `python thinkorswim_broker.py` y coloca orden test (1 acción)
- [ ] Observa que aparece en posiciones
- [ ] Ciérrala manualmente en Thinkorswim

### Próximas 2 Semanas:

**Semana 2: Implementar estrategias**
- [ ] Estudia `strategies/gap_and_go.py`
- [ ] Estudia `strategies/breakout.py`
- [ ] Entiende los parámetros de cada una

**Semana 3: Backtesting**
- [ ] Ejecuta backtesting de cada estrategia
- [ ] Ajusta parámetros basado en resultados
- [ ] Verifica que Sharpe > 1.0

**Semana 4: Paper Trading Automatizado**
- [ ] Ejecuta bot automático en modo simulado
- [ ] Observa mínimo 50 trades antes de dinero real
- [ ] Documenta qué funciona y qué no

## 🔧 Configuración Esencial (5 minutos)

Edita `config_thinkorswim.py` y ajusta estos valores según TU situación:

```python
# CRÍTICO: Tu capital inicial
INITIAL_CAPITAL = 5000  # ← CAMBIAR si es diferente

# CRÍTICO: Tu tolerancia al riesgo
RISK_PER_TRADE = 0.01   # 1% es lo recomendado para principiantes
MAX_DAILY_LOSS_PCT = 0.02  # 2% es máximo permisible

# IMPORTANTE: Estrategias a usar
STRATEGIES_ENABLED = {
    'gap_and_go': True,      # Premarket - MÁS ARRIESGADO
    'breakout': True,        # Intraday - MODERADO
    'ma_crossover': True,    # Swing - MÁS SEGURO
}

# OPCIONAL: Parámetros de estrategias
GAP_AND_GO = {
    'profit_target_pct': 3,   # Tomar ganancia al 3%
    'stop_loss_pct': 2,       # Stop loss al 2%
}
```

## ⚠️ ADVERTENCIAS CRÍTICAS

### ❌ NO HAGAS ESTO:

```
❌ Invertir dinero real sin backtest
❌ Arriesgar > 1% del capital por trade
❌ Operar sin stop loss
❌ Cambiar parámetros durante la operación
❌ Ignorar el drawdown máximo
❌ Operar por emoción (miedo/avaricia)
❌ Guardar API keys en el código
❌ Operar acciones que no conozcas
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
```

## 🆘 Errores Comunes y Soluciones

### Error: "ModuleNotFoundError: No module named 'tda'"
```bash
pip install tda-api --upgrade
```

### Error: "Authentication failed"
- Verifica que copiastes bien el Consumer Key
- Confirma que está en el archivo `.env` (no en `config_thinkorswim.py`)
- Re-ejecuta `python setup_oauth.py` para refrescar el token

### Error: "No data available"
- El símbolo debe existir (AAPL, MSFT, TSLA)
- Verifica que esté correctamente escrito (mayúsculas)
- Prueba con simbolos más populares primero

### Error: "Insufficient buying power"
```
Significa que no tienes suficiente cash para la posición
Soluciones:
1. Reduce RISK_PER_TRADE en config.py
2. Reduce el precio de la acción (menos dinero)
3. Espera a tener más capital
```

## 📊 Órdenes de Magnitud - Qué Esperar

### Premarket (Gap & Go) - Capital: $5,000
```
Risk per trade: $50 (1% de $5,000)
Precio típico: $50
Posición típica: 1 acción
Ganancia objetivo: $1.50 (3%)
Pérdida máxima: $1.00 (2%)
Duración: 15-60 minutos
```

### Intraday (Breakout) - Capital: $5,000
```
Risk per trade: $50
Precio típico: $100
Posición típica: 0.5 acciones (1 acción = $100)
Ganancia objetivo: $2-3 (2-3%)
Pérdida máxima: $50
Duración: 30 minutos - 2 horas
```

### Swing Trading (MA Crossover) - Capital: $5,000
```
Risk per trade: $50
Precio típico: $150
Posición típica: 1 acción
Ganancia objetivo: $7.50 (5%)
Pérdida máxima: $3.75 (2.5%)
Duración: 1-5 días
```

## 📈 Progresión Esperada

| Fase | Duración | Actividad | Meta |
|------|----------|-----------|------|
| **Learning** | Semana 1 | Estudio + pruebas | Entender el código |
| **Paper 1** | Semana 2-3 | Scanner + primeras órdenes | Familiaridad |
| **Paper 2** | Semana 4-5 | Bot automático simulado | 50+ trades |
| **Analysis** | Semana 6 | Revisar todos los trades | Identificar patrones |
| **Optimization** | Semana 7 | Ajustar parámetros | Mejorar Sharpe ratio |
| **Live Start** | Semana 8 | Dinero real inicial | $500-1,000 |
| **Scale** | Semana 12+ | Aumentar capital gradualmente | Rentabilidad consistente |

## 💡 Tips de Oro

1. **Documenta TODO**
   - Por qué entraste en cada trade
   - Por qué saliste
   - Qué salió bien/mal
   - Esto es tu mayor herramienta de aprendizaje

2. **Mantén expectativas reales**
   - 50-60% de trades ganadores es EXCELENTE
   - Pérdidas pequeñas y ganancias medianas es lo ideal
   - El objetivo es ser rentable en el tiempo, no en cada trade

3. **Emociones = Enemigo Principal**
   - Si sientes ansia de recuperar pérdidas → STOP
   - Si sientes avaricia de más ganancias → STOP
   - Si no puedes dormir por las posiciones → Posiciones muy grandes

4. **Escala gradualmente**
   - No dupliques capital hasta mínimo 4 semanas de ganancias
   - Comienza con 10-20% del capital, no el 100%
   - Aumenta solo si las ganancias son consistentes

5. **Mantén backup y documentación**
   - Guarda logs de todos los trades
   - Haz backup de tu código en GitHub
   - Documente parámetros óptimos de cada estrategia

## 🎓 Recursos para Aprender

### Gratis:
- Investopedia.com (guías sobre trading)
- YouTube: "Algorithmic Trading for Beginners"
- r/algotrading en Reddit
- TradingView (gráficos gratuitos)

### De Pago (Pero Valen la Pena):
- "A Beginner's Guide to Day Trading" - $20
- QuantConnect Course - $99
- "Algorithmic Trading" por Ernie Chan - $30

## 🚦 Checklist Antes de Dinero Real

- [ ] Instalé todas las dependencias
- [ ] Conecté exitosamente a Thinkorswim
- [ ] Ejecuté scanner y lo entendí
- [ ] Backtesté al menos 1 estrategia
- [ ] Paper traded mínimo 50 trades
- [ ] Mis ganancias promedio > mis pérdidas promedio
- [ ] Tengo win rate > 50%
- [ ] He documentado mis trades
- [ ] He identificado mis mejores horarios
- [ ] Tengo límites diarios configurados
- [ ] Entiendo completamente cada parámetro en config.py
- [ ] Tengo stop loss en 100% de mis trades
- [ ] He pasado 4+ semanas sin obtener ganancias = mejora esperada
- [ ] Estoy emocionalmente preparado para perder dinero

Si marcaste TODOS los items → ¡Estás listo para dinero real!

---

## 📞 ¿Preguntas?

1. **Sobre el código:** Abre una issue en el repositorio
2. **Sobre trading:** r/algotrading en Reddit
3. **Sobre estrategias:** TradingView comunidad
4. **Sobre Python:** Stack Overflow

## ¡Adelante! 💪

Ahora que tienes todo configurado, es momento de:

1. Ejecutar `python broker.py` para verificar conexión
2. Leer `PLAN_TRADING_BOT.md` para entender la estrategia
3. Explorar el código en `broker.py`
4. Ejecutar scanner: `python scanner_premarket.py`

**¡Que comience el aprendizaje!** 📚
