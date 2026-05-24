# 🖥️ ¿PC Prendida? ¿iPhone? Soluciones de Deployment

Pregunta muy importante. La respuesta es **NO**, tu PC NO necesita estar prendida 24/7.

---

## El Problema

Si ejecutas el bot en tu PC:
```bash
python main.py
```

Tienes 3 problemas:

1. **PC debe estar prendida 24/7** ❌
2. **Si falla conexión de internet → bot muere** ❌
3. **Si reinicia Windows → bot se detiene** ❌
4. **No puedes acceder desde iPhone** ❌

Esto es **ineficiente e inseguro**.

---

## La Solución: Desplegar en Cloud

### Opción 1: Cloud Barato ($5-15/mes) ⭐ RECOMENDADO

**Plataformas:**
- DigitalOcean ($5/mes droplet)
- Linode ($5/mes)
- AWS Free Tier ($0-12/mes)
- Google Cloud ($300 crédito gratis)

**Ventajas:**
- ✅ PC no necesita estar prendida
- ✅ Servidor ejecuta 24/7 sin interrupciones
- ✅ Acceso desde cualquier dispositivo
- ✅ iPhone/Android accede al dashboard
- ✅ Más seguro (no tu wifi)

**Costo:** $5-15/mes = menos que una pizza

---

## Comparativa: Local vs Cloud

| Aspecto | PC Local | Cloud |
|---------|----------|-------|
| **PC encendida 24/7** | ❌ Sí, necesaria | ✅ NO |
| **Confiabilidad** | ⭐⭐ (interrupciones) | ⭐⭐⭐⭐⭐ (99.99% uptime) |
| **Acceso remoto** | ❌ Complicado | ✅ Fácil |
| **Dashboard en iPhone** | ❌ No | ✅ Sí |
| **Costo** | $0 (electricidad) | $5-15/mes |
| **Seguridad** | ⭐⭐ (red local) | ⭐⭐⭐⭐⭐ |
| **Escalabilidad** | Limitada | Ilimitada |

**Veredicto:** Cloud es mejor en 6 de 7 aspectos.

---

## OPCIÓN 1: DigitalOcean (La más fácil) - $5/mes

### Paso 1: Crear Droplet (Servidor)

1. Ve a: https://www.digitalocean.com
2. Haz clic en "Sign Up"
3. Completa información (credit card necesaria)
4. "Create" → "Droplets"
5. Selecciona:
   - **OS:** Ubuntu 22.04
   - **Plan:** Basic ($5/month)
   - **Region:** NYC o SFO (cercano a USA markets)
6. Haz clic en "Create Droplet"
7. Recibirás email con contraseña root

### Paso 2: Conectar a Tu Servidor

```bash
# En tu PC, abre terminal/PowerShell
ssh root@YOUR_DROPLET_IP

# Te pedirá contraseña (la del email)
# Luego:
passwd  # Cambia contraseña a una fuerte
```

### Paso 3: Instalar Python y Dependencias

```bash
# Una sola vez en el servidor
apt update
apt install python3-pip python3-venv git

# Clonar tu proyecto (si está en GitHub)
git clone https://github.com/tuusuario/trading-bot.git
cd trading-bot

# Crear ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 4: Ejecutar Bot en Segundo Plano

```bash
# Opción A: tmux (mejor)
apt install tmux
tmux new-session -d -s bot "python main.py"

# Ver si corre:
tmux list-sessions
# Resultado: bot: 1 windows (created ...)

# Ver output:
tmux attach-session -t bot

# Salir sin detener: CTRL+B, D

# Opción B: nohup (más simple)
nohup python main.py > bot.log 2>&1 &

# Ver logs:
tail -f bot.log
```

### Paso 5: Acceder al Dashboard desde iPhone

```bash
# En el servidor, Streamlit escucha en puerto 8501
# Necesitas exponer el puerto (cuidado con seguridad)

# Opción 1: Nginx (recomendado)
apt install nginx

# Configurar Nginx como proxy (un poco técnico)
# O Opción 2: Ngrok (más fácil)
```

**Acceso desde iPhone:**
1. Abre navegador en iPhone
2. Ve a: `http://TU_IP_SERVIDOR:8501`
3. Ves el dashboard en tiempo real

---

## OPCIÓN 2: AWS Lambda (Serverless) - $0-5/mes

Más avanzado pero muy barato:

```python
# main_lambda.py
def lambda_handler(event, context):
    # Tu código de bot aquí
    # Se ejecuta cada X minutos
    return {'statusCode': 200}
```

**Ventajas:**
- ✅ Pagas solo por tiempo de ejecución (muy barato)
- ✅ Sin servidor que mantener
- ✅ Escalable automáticamente

**Desventaja:**
- ❌ Más complejo de configurar

---

## OPCIÓN 3: Replit (Más Fácil para Principiantes) - Free + $7/mes

### Paso 1: Crear Cuenta

1. Ve a: https://replit.com
2. Registra con GitHub/Google
3. "Create Repl"
4. Selecciona Python
5. Pega tu código

### Paso 2: Ejecutar

```bash
# En Replit, solo:
python main.py

# O configura Always On ($7/mes)
# Dashboard accesible por URL pública
```

**Ventajas:**
- ✅ Muy fácil
- ✅ Ambiente listo (sin instalar nada)
- ✅ URL pública automática

**Desventaja:**
- ❌ Menos control
- ❌ Más limitaciones

---

## OPCIÓN 4: Ejecutar en iPhone Directamente

Técnicamente posible pero **NO recomendado** porque:

1. ❌ Python en iPhone es muy limitado
2. ❌ No puedes instalar todas las librerías
3. ❌ Screen se apaga = bot se detiene
4. ❌ Consumo brutal de batería

**Mejor:** Usar iPhone solo para **ver** el dashboard (Cloud + Streamlit)

---

## MI RECOMENDACIÓN (Para Ti)

### Fase 1: Desarrollo (Semanas 1-4)
**Ejecuta en tu PC local** (es más fácil para debuggear)
```bash
python main.py
```

### Fase 2: Paper Trading (Semanas 5-8)
**Despliega en Cloud** (DigitalOcean $5/mes)
- Bot corre 24/7 sin tu PC
- Dashboard accesible desde iPhone
- Más confiable para testing

### Fase 3: Dinero Real (Semana 9+)
**Mantén en Cloud** (aunque ganes dinero)
- Servidor profesional
- Múltiples bots posibles
- Monitoreo desde iPhone

---

## SETUP RÁPIDO: DigitalOcean (Mi recomendación)

### Costo Total: $5/mes (menos que Netflix)

### Pasos (30 minutos):

1. **Registrarse:** https://digitalocean.com ($5/mes)
2. **Crear Droplet:** Ubuntu 22.04 Basic
3. **Conectar:**
   ```bash
   ssh root@YOUR_IP
   ```
4. **Instalar:**
   ```bash
   apt update && apt install python3-pip git -y
   git clone TU_REPO
   cd trading-bot
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
5. **Ejecutar:**
   ```bash
   tmux new-session -d -s bot "python main.py"
   ```
6. **Dashboard en iPhone:**
   ```
   http://TU_IP_SERVIDOR:8501
   ```

---

## ACCESO DESDE iPHONE: Paso a Paso

### Opción A: Acceso Directo (Simple)

```
1. En tu PC:
   python -m streamlit run dashboard/app.py --server.port=8501

2. En iPhone (WiFi misma red):
   Safari → http://192.168.1.100:8501

   (Reemplaza 192.168.1.100 por IP de tu PC)
```

### Opción B: Acceso Remoto desde Cloud

```
1. Servidor en Cloud ejecuta:
   python main.py

2. iPhone en cualquier parte:
   Safari → https://mibot.example.com

   (DNS configurado apuntando a tu servidor)
```

### Opción C: App Nativa (Avanzado)

Crea app iOS simple con:
- SwiftUI (interfaz)
- Conecta a API de tu bot
- Ver estadísticas en tiempo real

---

## COMPARATIVA: Ejecutar el Bot

| Método | Localización | PC Encendida | iPhone | Costo | Complejidad |
|--------|-------------|--------------|--------|-------|------------|
| **Local PC** | Casa | ✅ 24/7 | ❌ Difícil | $0 | Baja |
| **DigitalOcean** | Cloud | ❌ NO | ✅ Fácil | $5 | Media |
| **AWS Lambda** | Cloud | ❌ NO | ✅ Fácil | $0-5 | Alta |
| **Replit** | Cloud | ❌ NO | ✅ Muy Fácil | $7 | Baja |
| **iPhone Local** | iPhone | ❌ Pantalla | ⚠️ Limitado | $0 | Media |

---

## SEGURIDAD: ¿Y Si Alguien Accede al Dashboard?

**Importante:** Protege el dashboard

### Con Cloud (Recomendado)

```bash
# En el servidor, edita config_thinkorswim.py
# Añade autenticación

# O usa Nginx con contraseña:
apt install apache2-utils
htpasswd -c /etc/nginx/.htpasswd admin
# Contraseña: TuContraseñaFuerte
```

### En PC Local

```bash
# Solo acceso desde tu wifi local
# Pero aún así, protege:
STREAMLIT_SERVER_PASSWORD=TuPassword
python -m streamlit run dashboard/app.py
```

---

## RECOMENDACIÓN FINAL

### Para Empezar (Semanas 1-4):
```bash
# En tu PC
python main.py

# Dashboard: http://localhost:8501
# Solo desde tu PC
```

### Para Producción (Semana 5+):
```bash
# En DigitalOcean ($5/mes)
ssh root@TU_IP
tmux new-session -d -s bot "python main.py"

# Dashboard: http://TU_IP:8501 (desde iPhone)
```

**Costo total:** $5/mes = 0.16/día = un café a la semana

---

## RESPUESTA A TUS PREGUNTAS

### P: ¿La PC tiene que estar prendida 24/7?

**Respuesta:** 
- ✅ **NO si usas Cloud** (DigitalOcean, AWS, etc)
- ❌ **SÍ si ejecutas en PC local**

**Recomendación:** Cloud es mejor. $5/mes = sin problemas.

### P: ¿Se puede usar en iPhone?

**Respuesta:**
- ✅ **SÍ el Dashboard** (ver gráficos, operaciones, ganancias)
- ❌ **NO ejecutar el bot** (requiere Python, librerías, etc)
- ⚠️ **El bot corre en Cloud/PC, iPhone solo ve el dashboard**

**Flujo correcto:**
```
Bot Thinkorswim → Server Cloud (24/7) → Dashboard Streamlit → iPhone (ve en tiempo real)
```

---

## PRÓXIMO PASO

**Semanas 1-4 (Desarrollo):**
```bash
# En tu PC local
python main.py
# Dashboard: localhost:8501
```

**Semana 5+ (Producción):**
```bash
# En Cloud (DigitalOcean)
# Bot corre 24/7
# iPhone accede a dashboard
# Costo: $5/mes
```

---

## Preguntas Frecuentes

**P: ¿Es seguro tener dinero en un servidor Cloud?**
R: Sí. TD Ameritrade es quien tiene el dinero, no el servidor. El servidor solo ejecuta órdenes.

**P: ¿Qué pasa si el servidor falla?**
R: DigitalOcean tiene 99.99% uptime. Antes de dinero real, valida con paper trading.

**P: ¿Puedo monitorearlo desde iPhone sin Cloud?**
R: Sí con Ngrok (herramienta gratuita que expone tu PC). Pero Cloud es mejor.

**P: ¿Necesito saber Linux para Cloud?**
R: No mucho. Los pasos arriba son copy-paste. Si te atascas, avísame.

**P: ¿Se me va a cobrar algo sin querer?**
R: DigitalOcean cobra exactamente $5/mes. Puedes poner límite para no gastar más.

---

## Resumen Ejecutivo

| Pregunta | Respuesta |
|----------|-----------|
| **¿PC prendida 24/7?** | ❌ No si usas Cloud ($5/mes) |
| **¿Funciona en iPhone?** | ✅ Sí el dashboard (no el bot) |
| **¿Dónde ejecutar el bot?** | Cloud (DigitalOcean) |
| **¿Acceso desde iPhone?** | ✅ Sí, vía dashboard web |
| **¿Costo?** | $5/mes Cloud + $0 código |
| **¿Complejidad?** | Media (setup 30 min) |

---

## Ahora Qué Haces

### Opción A: Comienza Local (Fácil ahora, Cloud después)
1. Desarrollo en tu PC (semanas 1-4)
2. Cuando entre en producción, migra a DigitalOcean

### Opción B: Usa Cloud desde el inicio
1. Crea DigitalOcean hoy ($5)
2. Configura servidor en 30 minutos
3. Bot corre 24/7
4. Dashboard en iPhone desde el inicio

**Mi recomendación:** Opción A (más simple para empezar)

---

¿Alguna duda sobre Cloud o iPhone? Dime y te ayudo.
