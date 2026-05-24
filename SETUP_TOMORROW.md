# 🚀 SETUP PARA MAÑANA - PASO A PASO

**Fecha:** 17 Mayo 2026  
**Estado:** ✅ Todo está listo para operar

---

## PASO 1: Configurar variables de entorno (5 minutos)

1. Abre `.env` (o cópialo de `.env.example`):
   ```bash
   cp .env.example .env
   ```

2. Rellena tus credenciales TD Ameritrade:
   ```
   TD_CONSUMER_KEY=PK_...              # De developer.tdameritrade.com
   TD_ACCOUNT_ID=123456789             # Tu account ID de TD
   ALERT_EMAIL=tu_email@gmail.com      # Tu email para alertas
   ```

3. Guarda el archivo. **NO COMITAS A GIT**

---

## PASO 2: Instalar dependencias (5 minutos)

```bash
# Crear ambiente virtual
python -m venv venv

# Activar ambiente
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# Instalar librerías
pip install -r requirements.txt
```

---

## PASO 3: Setup OAuth (5 minutos - UNA SOLA VEZ)

```bash
python setup_oauth.py
```

**Qué sucede:**
1. Se abre tu navegador automáticamente
2. Haz clic en "Allow" para autorizar la app
3. Se cierra el navegador automáticamente
4. Se genera `token.json` (NO COMITEAR)

**Resultado esperado:**
```
✨ OAUTH CONFIGURADO EXITOSAMENTE
✓ Access Token válido por: 1800 segundos
✓ Token guardado en: token.json
```

---

## PASO 4: Verificar conexión al broker (2 minutos)

```bash
python thinkorswim_broker.py
```

**Resultado esperado:**
```
🔗 CONEXIÓN EXITOSA CON THINKORSWIM
========================================

📊 CUENTA:
  Account Value: $10,000.00
  Cash: $10,000.00
  Buying Power: $40,000.00

📈 POSICIONES (0):

🕐 MERCADO: CLOSED

========================================
✅ Todo funciona correctamente
```

Si ves esto → **¡Estás listo!** ✅

---

## PASO 5: Ejecutar el bot (Elige UNO)

### Opción A: Bot Automático (Recomendado)
```bash
python main.py
```

Esto:
- ✅ Escanea oportunidades continuamente
- ✅ Ejecuta estrategias automáticamente
- ✅ Monitorea posiciones abiertas
- ✅ Loguea cada operación en `logs/trading_bot_main.log`

### Opción B: Scanner Manual
```bash
python scanner_premarket.py
```

Esto escanea UNA VEZ y muestra oportunidades en CSV.

### Opción C: Dashboard (Otra terminal)
```bash
streamlit run dashboard/app.py
```

Abre en: http://localhost:8501

---

## ⏰ HORARIOS OPERATIVOS

### Premarket (04:00-09:30 EST)
- Estrategia: **Gap and Go**
- Mejor: 5% gaps + volumen anómalo
- Riesgo: 3-5%
- Duración: 15-60 minutos

### Mercado Regular (09:30-16:00 EST)
- Estrategias: **Breakout + MA Crossover**
- Mejor: Rupturas de máximos/mínimos
- Riesgo: 1-3%
- Duración: 30 min - 5 días

### After Hours (16:00-20:00 EST)
- Monitoreo de posiciones abiertas

---

## 🎯 QUÉ ESPERAR MAÑANA

### Primer Trade:
```
Símbolo:         TSLA
Entry:           $50.00
Stop Loss:       $49.00
Profit Target:   $51.50
Duración:        45 minutos
Ganancias:       $75 (3%)
```

### Parámetros de Riesgo:
```
Capital:         $5,000
Riesgo/trade:    $50 (1%)
Max Pérdida/día: $100 (2%)
Max Posiciones:  3
Max Trades/día:  10
```

### Logs en Tiempo Real:
```
tail -f logs/trading_bot_main.log
```

---

## ⚠️ CHECKLIST ANTES DE EJECUTAR

- [ ] `.env` configurado con TD_CONSUMER_KEY y TD_ACCOUNT_ID
- [ ] `setup_oauth.py` ejecutado → `token.json` generado
- [ ] `thinkorswim_broker.py` conecta exitosamente
- [ ] Carpeta `logs/` existe
- [ ] `requirements.txt` instalado (`pip install -r requirements.txt`)
- [ ] Tengo $5k+ en la cuenta (simulada en paper trading)
- [ ] Horario: 04:00-20:00 EST (mañana por la mañana)

---

## 🆘 Si algo falla

### "ModuleNotFoundError: No module named 'tda'"
```bash
pip install tda-api --upgrade
```

### "Authentication failed"
```bash
# Ejecutar OAuth de nuevo
python setup_oauth.py
```

### "No se conecta al broker"
1. Verifica `.env` tiene TD_CONSUMER_KEY y TD_ACCOUNT_ID
2. Verifica `token.json` existe
3. Re-ejecuta `setup_oauth.py`
4. Verifica firewall/proxy

### "Insufficient buying power"
- Reduce RISK_PER_TRADE en `config_thinkorswim.py` (cambiar 0.01 a 0.005)
- O aumenta INITIAL_CAPITAL si es simulado

---

## 📊 MONITORES NECESARIOS

Abre 3-4 terminales:

1. **Terminal 1**: Bot Principal
   ```bash
   python main.py
   ```

2. **Terminal 2**: Dashboard (Opcional pero recomendado)
   ```bash
   streamlit run dashboard/app.py
   ```

3. **Terminal 3**: Monitoreo de logs
   ```bash
   tail -f logs/trading_bot_main.log
   ```

4. **Navegador**: Thinkorswim web/app (opcional, para ver órdenes)

---

## ✅ RESULTADO ESPERADO

Después de 1 hora de ejecución deberías ver:

```
📊 RESUMEN DEL BOT
========================================
💰 CUENTA:
  Cash: $4,950.00
  Poder de compra: $39,800.00

📈 POSICIONES: 1
  TSLA: 1 acción ($50.50)

⚠️  LÍMITES DIARIOS:
  P&L: $50.00 (1.00%)
  Posiciones: 1 / 3
  Trades: 1 / 10
  Puedo tradear: ✅

🕐 ESTADO: OPERATIVO
========================================
```

---

## 💡 TIPS

1. **Primer día**: Usa paper trading (está activado por defecto)
2. **Observa**: Mira los trades y entiende por qué se ejecutan
3. **Documenta**: Copia los logs a un documento (para aprender)
4. **No cambies parámetros**: Deja que haga 20-50 trades primero
5. **Emociones**: Si sientes ansias, STOP - no está permitido tradear

---

## 🚀 PRÓXIMOS PASOS (Después de mañana)

1. **Observa 50 trades** en paper trading
2. **Analiza ganancias**: Win rate, sharpe ratio, drawdown
3. **Optimiza**: Ajusta parámetros basado en resultados
4. **Backtesting**: Ejecuta `backtesting/backtest_engine.py`
5. **Dinero real**: Solo después de 4 semanas consistentes

---

## 📞 SOPORTE RÁPIDO

```bash
# Ver errores
grep ERROR logs/trading_bot_main.log

# Ver últimos 100 trades
tail -100 logs/trading_bot_main.log | grep "✅ Orden colocada"

# Ver todos los stops
grep "Stop loss" logs/trading_bot_main.log

# Ver todas las ganancias
grep "Profit target" logs/trading_bot_main.log
```

---

**¡Que tengas excelente sesión de trading mañana! 🚀📈**

Recuerda: **Consistencia > Velocidad**

Cualquier duda: Lee [THINKORSWIM_COMPLETE.md](THINKORSWIM_COMPLETE.md)
