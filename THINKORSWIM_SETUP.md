# 🎯 Configuración Thinkorswim + Bot Automatizado

**Thinkorswim es SUPERIOR a Alpaca** para lo que quieres porque:
- ✅ API nativa robusta (TD Ameritrade API)
- ✅ Paper trading automático completamente funcional
- ✅ Datos de mercado en tiempo real
- ✅ Comisiones $0 por acción
- ✅ Sin restrictriciones de Pattern Day Trading (PDT) en simulado
- ✅ Comunidad amplia de traders algorítmicos

---

## FASE 1: OBTENER ACCESO API THINKORSWIM (Hoy)

### Paso 1: Crear Cuenta de Desarrollador en TD Ameritrade

1. **Ve a:** https://developer.tdameritrade.com/
2. **Haz clic en:** "Register for a Free Account"
3. **Completa:**
   - Email (usa el mismo de tu cuenta Robinhood si es diferente)
   - Contraseña
   - Información personal
4. **Verifica email**

### Paso 2: Crear Aplicación para Obtener API Keys

1. Logueate en https://developer.tdameritrade.com/
2. Ve a **"My Apps"**
3. Haz clic en **"Create App"**
4. Rellena:
   - **App Name:** `TradingBot` (o el que prefieras)
   - **Description:** `Automated trading bot for gap trading`
   - **Callback URL:** `http://localhost:8000` (importante para OAuth)
5. **Haz clic en "Create"**
6. **Copia tu Consumer Key (API Key)** - la usaremos luego

### Paso 3: Habilitar OAuth en Tu Cuenta TD Ameritrade

1. Logueate en tu cuenta principal de TD Ameritrade: https://www.tdameritrade.com/
2. Ve a **Account → Settings → Security → API Settings**
3. Habilita **"OAuth Applications"**
4. Autoriza la aplicación que acabas de crear

### Paso 4: Configurar Variables de Entorno

```bash
# Edita .env y añade:
TD_CONSUMER_KEY=YOUR_CONSUMER_KEY_HERE
TD_ACCOUNT_ID=YOUR_ACCOUNT_ID_HERE
TD_ACCESS_TOKEN_REFRESH_TOKEN=WILL_GET_THIS_AFTER_OAUTH

# Tu account ID lo encuentras en TD Ameritrade login (mostrará algo como: 123456789)
```

---

## FASE 2: INSTALAR THINKORSWIM DESKTOP (20 minutos)

### Paso 1: Descargar Thinkorswim

1. Ve a: https://www.tdameritrade.com/tools-and-platforms/thinkorswim/features
2. **Descarga → Thinkorswim Desktop**
3. Instala en tu computadora

### Paso 2: Logueate con Tus Credenciales TD Ameritrade

1. Abre Thinkorswim
2. Ingresa tu usuario/contraseña de TD Ameritrade
3. Selecciona **Paper Trading Mode** (importante para pruebas)

### Paso 3: Habilitar Scripting en Thinkorswim (Opcional pero Poderoso)

1. En Thinkorswim → **Monitor Tab**
2. **Add Studies → Custom...**
3. Aquí puedes crear scripts en **ThinkScript**
4. ThinkScript es similar a Pine Script (TradingView) pero más poderoso

---

## FASE 3: CONECTAR API CON PYTHON

### Instalación

```bash
# Instalar librería TD Ameritrade API para Python
pip install tda-api

# Alternativas:
# pip install python-td-ameritrade  (opción alternativa)
```

### Archivo: thinkorswim_broker.py

Crea este archivo para conectar Python con TD Ameritrade:

```python
# thinkorswim_broker.py - Conector con TD Ameritrade API

import os
import json
from datetime import datetime, timedelta
import logging
from typing import Optional, List, Dict
import pandas as pd

try:
    from tda import auth, client
    from tda.orders.common import OrderType, Session, Duration, SpecialInstruction
    from tda.orders.generic import OrderBuilder
    TDA_AVAILABLE = True
except ImportError:
    TDA_AVAILABLE = False
    logging.warning("TDA SDK no disponible. Install: pip install tda-api")

import config

logger = logging.getLogger(__name__)


class ThinkOrSwimBroker:
    """
    Conector con TD Ameritrade Thinkorswim
    Soporta paper trading y live trading
    """

    def __init__(self, consumer_key: str = None, account_id: str = None):
        """
        Inicializa conexión con TD Ameritrade

        Args:
            consumer_key: API Consumer Key de TD Ameritrade
            account_id: Tu Account ID (ej: 123456789)
        """
        if not TDA_AVAILABLE:
            raise ImportError("TDA SDK no disponible")

        self.consumer_key = consumer_key or config.TD_CONSUMER_KEY
        self.account_id = account_id or config.TD_ACCOUNT_ID

        # Primera vez necesita OAuth
        try:
            self.client = self._get_client()
        except Exception as e:
            logger.error(f"Error de autenticación: {e}")
            logger.info("Ejecuta primero: python setup_oauth.py")
            raise

        logger.info("✓ Conectado a TD Ameritrade Thinkorswim")
        self._verify_connection()

    def _get_client(self):
        """Obtiene cliente TD Ameritrade con OAuth"""
        token_path = "token.json"

        # Si existe token guardado, úsalo
        if os.path.exists(token_path):
            with open(token_path, 'r') as f:
                token = json.load(f)
                logger.info("✓ Usando token OAuth guardado")
                return client.Client(
                    self.consumer_key,
                    access_token=token['access_token'],
                    refresh_token=token['refresh_token'],
                    token_metadata=token['token_metadata']
                )
        else:
            # Primera vez: hacer OAuth
            logger.error("❌ No hay token OAuth. Ejecuta: python setup_oauth.py")
            raise ValueError("Se requiere OAuth. Ejecuta setup_oauth.py primero")

    def _verify_connection(self):
        """Verifica que la conexión funciona"""
        try:
            accounts = self.client.get_accounts()
            logger.info(f"✓ Acceso a {len(accounts)} cuenta(s)")
            for account in accounts:
                balance = account['securitiesAccount']['initialBalances']['cashBalance']
                logger.info(f"  - {account['name']}: ${float(balance):.2f}")
        except Exception as e:
            logger.error(f"✗ Error de conexión: {e}")
            raise

    # ============ ACCOUNT INFO ============

    def get_account(self) -> Dict:
        """Obtiene información detallada de la cuenta"""
        try:
            account_data = self.client.get_account(
                self.account_id,
                fields=['positions', 'orders']
            )['securitiesAccount']

            balances = account_data['initialBalances']
            return {
                'cash': float(balances['cashBalance']),
                'buying_power': float(balances['buyingPower']),
                'net_liquidation': float(balances['netLiquidation']),
                'margin_balance': float(balances.get('marginBalance', 0)),
                'account_type': account_data['accountType'],
                'is_day_trader': account_data.get('isDayTrader', False),
            }
        except Exception as e:
            logger.error(f"Error obteniendo información de cuenta: {e}")
            return None

    def get_cash(self) -> float:
        """Obtiene cash disponible"""
        account = self.get_account()
        return account['cash'] if account else 0.0

    def get_buying_power(self) -> float:
        """Obtiene poder de compra"""
        account = self.get_account()
        return account['buying_power'] if account else 0.0

    # ============ POSITIONS ============

    def get_positions(self) -> List[Dict]:
        """Obtiene todas las posiciones abiertas"""
        try:
            account_data = self.client.get_account(
                self.account_id,
                fields=['positions']
            )

            positions = account_data['securitiesAccount'].get('positions', [])
            result = []

            for pos in positions:
                instrument = pos['instrument']
                result.append({
                    'symbol': instrument['symbol'],
                    'qty': float(pos['longQuantity']) - float(pos['shortQuantity']),
                    'avg_price': float(pos['averagePrice']),
                    'current_price': float(pos['currentPrice']),
                    'market_value': float(pos['marketValue']),
                    'unrealized_gain': float(pos.get('currentPrice', 0)) * (
                        float(pos['longQuantity']) - float(pos['shortQuantity'])
                    ) - float(pos['averagePrice']) * (
                        float(pos['longQuantity']) - float(pos['shortQuantity'])
                    ),
                    'unrealized_gain_pct': float(pos.get('longQuantity', 0)) > 0 and (
                        ((float(pos['currentPrice']) - float(pos['averagePrice'])) / float(pos['averagePrice'])) * 100
                    ) or 0,
                })
            return result
        except Exception as e:
            logger.error(f"Error obteniendo posiciones: {e}")
            return []

    def get_position(self, symbol: str) -> Optional[Dict]:
        """Obtiene posición específica"""
        positions = self.get_positions()
        for pos in positions:
            if pos['symbol'] == symbol:
                return pos
        return None

    def close_position(self, symbol: str) -> Dict:
        """Cierra posición completa"""
        position = self.get_position(symbol)
        if not position:
            logger.warning(f"No hay posición abierta en {symbol}")
            return None

        qty = abs(position['qty'])
        side = 'SELL' if position['qty'] > 0 else 'BUY'

        try:
            order_spec = {
                'orderType': 'MARKET',
                'session': 'NORMAL',
                'duration': 'DAY',
                'orderStrategyType': 'SINGLE',
                'orderLegCollection': [
                    {
                        'instruction': side,
                        'quantity': qty,
                        'instrument': {
                            'symbol': symbol,
                            'assetType': 'EQUITY'
                        }
                    }
                ]
            }

            order = self.client.place_order(self.account_id, order_spec)
            logger.info(f"Cierre de posición {symbol} ejecutado")
            return {'status': 'success', 'symbol': symbol}
        except Exception as e:
            logger.error(f"Error cerrando posición {symbol}: {e}")
            return None

    # ============ ORDERS ============

    def submit_market_order(self, symbol: str, qty: int, side: str) -> Dict:
        """
        Coloca una orden de mercado

        Args:
            symbol: Símbolo (ej: AAPL)
            qty: Cantidad de acciones
            side: 'BUY' o 'SELL'
        """
        try:
            order_spec = {
                'orderType': 'MARKET',
                'session': 'NORMAL',
                'duration': 'DAY',
                'orderStrategyType': 'SINGLE',
                'orderLegCollection': [
                    {
                        'instruction': side.upper(),
                        'quantity': qty,
                        'instrument': {
                            'symbol': symbol,
                            'assetType': 'EQUITY'
                        }
                    }
                ]
            }

            order_id = self.client.place_order(self.account_id, order_spec)
            logger.info(f"Orden {side} {symbol} x{qty} colocada. ID: {order_id}")

            return {
                'status': 'success',
                'order_id': order_id,
                'symbol': symbol,
                'qty': qty,
                'side': side,
                'type': 'MARKET'
            }
        except Exception as e:
            logger.error(f"Error colocando orden: {e}")
            return {'status': 'error', 'message': str(e)}

    def submit_limit_order(self, symbol: str, qty: int, side: str,
                          limit_price: float) -> Dict:
        """Coloca una orden límite"""
        try:
            order_spec = {
                'orderType': 'LIMIT',
                'price': limit_price,
                'session': 'NORMAL',
                'duration': 'GTC',  # Good Till Canceled
                'orderStrategyType': 'SINGLE',
                'orderLegCollection': [
                    {
                        'instruction': side.upper(),
                        'quantity': qty,
                        'instrument': {
                            'symbol': symbol,
                            'assetType': 'EQUITY'
                        }
                    }
                ]
            }

            order_id = self.client.place_order(self.account_id, order_spec)
            logger.info(f"Orden límite {side} {symbol}: {qty} @ ${limit_price}")

            return {
                'status': 'success',
                'order_id': order_id,
                'symbol': symbol,
                'qty': qty,
                'limit_price': limit_price
            }
        except Exception as e:
            logger.error(f"Error en orden límite: {e}")
            return {'status': 'error', 'message': str(e)}

    def cancel_order(self, order_id: str) -> bool:
        """Cancela una orden pendiente"""
        try:
            self.client.cancel_order(self.account_id, order_id)
            logger.info(f"Orden {order_id} cancelada")
            return True
        except Exception as e:
            logger.error(f"Error cancelando orden: {e}")
            return False

    def get_orders(self) -> List[Dict]:
        """Obtiene órdenes abiertas"""
        try:
            account_data = self.client.get_account(
                self.account_id,
                fields=['orders']
            )

            orders = account_data['securitiesAccount'].get('orderStrategies', [])
            result = []

            for order in orders:
                result.append({
                    'order_id': order['orderId'],
                    'status': order['status'],
                    'order_type': order['orderType'],
                    'session': order['session'],
                    'quantity': order['quantity'],
                    'filled_quantity': order.get('filledQuantity', 0),
                    'created_time': order['createTime'],
                })
            return result
        except Exception as e:
            logger.error(f"Error obteniendo órdenes: {e}")
            return []

    # ============ MARKET DATA ============

    def get_quote(self, symbol: str) -> Optional[Dict]:
        """Obtiene cotización en tiempo real"""
        try:
            quotes = self.client.get_quotes(symbol)
            quote = quotes[symbol]

            return {
                'symbol': symbol,
                'bid': float(quote['bidPrice']),
                'ask': float(quote['askPrice']),
                'last': float(quote['lastPrice']),
                'high_52w': float(quote.get('52WkHigh', 0)),
                'low_52w': float(quote.get('52WkLow', 0)),
                'bid_size': int(quote.get('bidSize', 0)),
                'ask_size': int(quote.get('askSize', 0)),
                'volume': int(quote.get('totalVolume', 0)),
                'pe_ratio': float(quote.get('peRatio', 0)),
                'dividend_yield': float(quote.get('divYield', 0)),
            }
        except Exception as e:
            logger.debug(f"Error obteniendo quote para {symbol}: {e}")
            return None

    def get_price_history(self, symbol: str, period_type: str = 'day',
                         period: int = 10, frequency_type: str = 'minute',
                         frequency: int = 1) -> pd.DataFrame:
        """
        Obtiene histórico de precios

        Args:
            symbol: Símbolo (ej: AAPL)
            period_type: 'day', 'month', 'year', 'ytd'
            period: Cantidad de períodos (ej: 10 días)
            frequency_type: 'minute', 'daily', 'weekly', 'monthly'
            frequency: 1, 5, 10, 15, 30 (minutos) o 1 (días)
        """
        try:
            history = self.client.get_price_history(
                symbol,
                period_type=period_type,
                period=period,
                frequency_type=frequency_type,
                frequency=frequency
            )

            candles = history['candles']
            df = pd.DataFrame(candles)

            # Convertir timestamps a datetime
            df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')

            return df[['datetime', 'open', 'high', 'low', 'close', 'volume']]
        except Exception as e:
            logger.error(f"Error obteniendo histórico: {e}")
            return pd.DataFrame()


# ============ UTILITY ============

def create_broker() -> ThinkOrSwimBroker:
    """Factory function para crear broker"""
    return ThinkOrSwimBroker()


if __name__ == "__main__":
    broker = create_broker()

    # Test
    account = broker.get_account()
    print(f"\nCuenta:")
    print(f"  Cash: ${account['cash']:.2f}")
    print(f"  Buying Power: ${account['buying_power']:.2f}")

    positions = broker.get_positions()
    print(f"\nPosiciones ({len(positions)}):")
    for pos in positions:
        print(f"  {pos['symbol']}: {pos['qty']} @ ${pos['avg_price']:.2f}")
```

---

## FASE 4: CONFIGURAR OAUTH (Importante!)

Crea este archivo: `setup_oauth.py`

```python
# setup_oauth.py - Configura OAuth una sola vez

import json
import os
import sys
from tda import auth, client

def setup_oauth():
    """
    Configura OAuth y guarda token para uso futuro
    Solo necesitas hacer esto UNA VEZ
    """

    # Obtener valores del .env
    from dotenv import load_dotenv
    load_dotenv()

    consumer_key = os.getenv("TD_CONSUMER_KEY")
    account_id = os.getenv("TD_ACCOUNT_ID")

    if not consumer_key:
        print("❌ TD_CONSUMER_KEY no encontrado en .env")
        sys.exit(1)

    print("🔐 Configurando OAuth...")
    print(f"Consumer Key: {consumer_key[:20]}...")

    try:
        # Esto abre tu navegador para autorizar
        c = auth.easy_client(
            api_key=consumer_key,
            redirect_uri='http://localhost:8000',
            token_path='token.json'
        )

        print("✅ OAuth configurado exitosamente!")
        print("   Token guardado en: token.json")
        print("   (Nunca compartas este archivo)")

        # Test conexión
        accounts = c.get_accounts()
        print(f"\n✓ Conectado a {len(accounts)} cuenta(s)")

    except Exception as e:
        print(f"❌ Error en OAuth: {e}")
        sys.exit(1)


if __name__ == "__main__":
    setup_oauth()
```

**Ejecutar una sola vez:**
```bash
python setup_oauth.py

# Se abrirá un navegador pidiendo autorización
# Haz clic en "Allow"
# Se guardará token.json automáticamente
```

---

## COMPARATIVA: Alpaca vs Thinkorswim

| Característica | Alpaca | Thinkorswim |
|---|---|---|
| **Comisiones** | $0 | $0 |
| **Paper Trading** | ✅ Automático | ✅ Automático |
| **API Robustez** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Datos en Tiempo Real** | ✅ | ✅ |
| **Documentación** | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Scripting Avanzado** | No | ✅ ThinkScript |
| **Comunidad** | Creciente | Amplia |
| **Estabilidad** | Buena | Excelente |
| **Facilidad de Uso** | Muy fácil | Moderada |

**Veredicto:** Para trading automatizado serio, **Thinkorswim es superior**.

---

## PRÓXIMOS PASOS

1. **Hoy:**
   - [ ] Crear cuenta desarrollador en https://developer.tdameritrade.com/
   - [ ] Crear aplicación y obtener Consumer Key
   - [ ] Editar .env con Consumer Key y Account ID

2. **Mañana:**
   - [ ] `pip install tda-api`
   - [ ] Ejecutar `python setup_oauth.py` (Una sola vez)
   - [ ] Ejecutar `python thinkorswim_broker.py` para verificar conexión

3. **Esta semana:**
   - [ ] Mantener el resto del código (scanner, estrategias)
   - [ ] Simplemente cambiar importación de `broker.py` a `thinkorswim_broker.py`
   - [ ] Todo funciona igual pero más robusto

---

## VENTAJAS ADICIONALES DE THINKORSWIM

### 1. ThinkScript (Scripting Nativo)
Puedes crear scripts directamente en Thinkorswim:
```thinkscript
# Ejemplo: Alert cuando hay gap > 3%
def gap = close[1] != 0 and (open - close[1]) / close[1] * 100;
Alert(gap > 3, "GAP GRANDE DETECTADO: " + AsPercent(gap));
```

### 2. Watchlists Automáticas
Crear watchlists que se actualizan automáticamente basadas en criterios.

### 3. Estudios Personalizados
Muchos estudios pre-construidos que puedes modificar.

### 4. Mobile App
Trading desde iPhone/Android con sincronización perfecta.

### 5. Comunidad ThinkOrSwim
Acceso a scripts, estrategias y comunidad de traders avanzados.

---

## ¿Y QUÉ PASA CON ROBINHOOD Y ETRADE?

Puedes mantenerlos abiertos para:
- **Robinhood:** Operaciones manuales quick trades (interfaz simple)
- **Etrade:** Operaciones más complejas manualmente
- **Thinkorswim:** Todo automatizado + análisis técnico avanzado

La mayoría de traders profesionales usan TD Ameritrade/Thinkorswim como principal precisamente por esto.

---

## RECOMENDACIÓN FINAL

**Mantén ambas estrategias:**
1. **Thinkorswim + Bot Automatizado** (tu máquina)
2. **Manual en Robinhood** (trades rápidos manualmente)

Así tienes lo mejor de ambos mundos.

¿Necesitas ayuda con algún paso? Dime dónde te estancas.
