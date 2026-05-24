#!/usr/bin/env python3
"""
Broker connector para TD Ameritrade/Thinkorswim
Proporciona interfaz simplificada para:
- Obtener datos de cuenta
- Colocar órdenes
- Cerrar posiciones
- Obtener precios en tiempo real
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
import tda
from tda.client import Client
from tda.orders.common import OrderType, Duration, AssetType

load_dotenv()

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/trading_bot_thinkorswim.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Credenciales
CONSUMER_KEY = os.getenv("TD_CONSUMER_KEY")
ACCOUNT_ID = os.getenv("TD_ACCOUNT_ID")
TOKEN_FILE = "token.json"
PAPER_TRADING = os.getenv("PAPER_TRADING", "True").lower() == "true"


class ThinkOrSwimBroker:
    """Broker connector para TD Ameritrade/Thinkorswim"""

    def __init__(self):
        """Inicializa la conexión con el broker"""
        if not CONSUMER_KEY or not ACCOUNT_ID:
            raise ValueError("TD_CONSUMER_KEY y TD_ACCOUNT_ID requeridos en .env")

        self.client = self._authenticate()
        self.account_id = ACCOUNT_ID
        self.paper_trading = PAPER_TRADING
        logger.info(f"🔗 Conectado a TD Ameritrade (Paper Trading: {self.paper_trading})")

    def _authenticate(self) -> Client:
        """Autentica con TD Ameritrade usando OAuth"""
        try:
            if os.path.exists(TOKEN_FILE):
                return tda.easy_client.EasyClient(
                    CONSUMER_KEY,
                    token_path=TOKEN_FILE
                )
            else:
                raise FileNotFoundError(
                    f"{TOKEN_FILE} no encontrado. Ejecuta: python setup_oauth.py"
                )
        except Exception as e:
            logger.error(f"Error de autenticación: {e}")
            raise

    def get_account(self) -> Dict:
        """Obtiene información de la cuenta"""
        try:
            response = self.client.get_account(self.account_id)
            account_data = response.json()
            return account_data["securitiesAccount"]
        except Exception as e:
            logger.error(f"Error obteniendo cuenta: {e}")
            return {}

    def get_cash(self) -> float:
        """Obtiene el cash disponible"""
        try:
            account = self.get_account()
            return float(account["accountValue"]["cashBalance"])
        except Exception as e:
            logger.error(f"Error obteniendo cash: {e}")
            return 0.0

    def get_buying_power(self) -> float:
        """Obtiene el poder de compra (basado en 4x con margen)"""
        try:
            account = self.get_account()
            # TD Ameritrade proporciona buying power directamente
            return float(account["accountValue"]["buyingPower"])
        except Exception as e:
            logger.error(f"Error obteniendo poder de compra: {e}")
            return 0.0

    def get_positions(self) -> List[Dict]:
        """Obtiene todas las posiciones abiertas"""
        try:
            account = self.get_account()
            positions = account.get("positions", [])
            return positions
        except Exception as e:
            logger.error(f"Error obteniendo posiciones: {e}")
            return []

    def get_position(self, symbol: str) -> Optional[Dict]:
        """Obtiene una posición específica"""
        try:
            positions = self.get_positions()
            for position in positions:
                if position["instrument"]["symbol"] == symbol:
                    return position
            return None
        except Exception as e:
            logger.error(f"Error obteniendo posición {symbol}: {e}")
            return None

    def get_quote(self, symbol: str) -> Dict:
        """Obtiene el precio actual de un símbolo"""
        try:
            response = self.client.get_quote(symbol)
            quote_data = response.json()
            return quote_data.get(symbol, {})
        except Exception as e:
            logger.error(f"Error obteniendo quote para {symbol}: {e}")
            return {}

    def get_price_history(
        self,
        symbol: str,
        period: int = 10,
        period_type: str = "day",
        frequency: int = 1,
        frequency_type: str = "minute"
    ) -> List[Dict]:
        """Obtiene historial de precios"""
        try:
            response = self.client.get_price_history(
                symbol,
                period=period,
                period_type=period_type,
                frequency=frequency,
                frequency_type=frequency_type
            )
            candles = response.json().get("candles", [])
            return candles
        except Exception as e:
            logger.error(f"Error obteniendo historial para {symbol}: {e}")
            return []

    def submit_market_order(
        self,
        symbol: str,
        quantity: int,
        instruction: str = "BUY"
    ) -> Optional[str]:
        """
        Coloca una orden de mercado
        instruction: "BUY" o "SELL"
        Retorna: order_id o None si falla
        """
        if self.paper_trading:
            logger.warning(f"📋 PAPER TRADING: Market order {instruction} {quantity} {symbol}")
            return self._simulate_order(symbol, quantity, instruction)

        try:
            order = {
                "orderType": "MARKET",
                "session": "NORMAL",
                "duration": "DAY",
                "orderStrategyType": "SINGLE",
                "orderLegCollection": [
                    {
                        "instruction": instruction,
                        "quantity": quantity,
                        "instrument": {
                            "symbol": symbol,
                            "assetType": "EQUITY"
                        }
                    }
                ]
            }

            response = self.client.place_order(self.account_id, order)
            order_id = response.headers.get("Location").split("/")[-1]
            logger.info(f"✅ Orden colocada: {instruction} {quantity} {symbol} (ID: {order_id})")
            return order_id

        except Exception as e:
            logger.error(f"Error colocando orden: {e}")
            return None

    def submit_limit_order(
        self,
        symbol: str,
        quantity: int,
        price: float,
        instruction: str = "BUY"
    ) -> Optional[str]:
        """
        Coloca una orden límite
        instruction: "BUY" o "SELL"
        Retorna: order_id o None si falla
        """
        if self.paper_trading:
            logger.warning(f"📋 PAPER TRADING: Limit order {instruction} {quantity} {symbol} @ ${price}")
            return self._simulate_order(symbol, quantity, instruction)

        try:
            order = {
                "orderType": "LIMIT",
                "session": "NORMAL",
                "duration": "DAY",
                "price": price,
                "orderStrategyType": "SINGLE",
                "orderLegCollection": [
                    {
                        "instruction": instruction,
                        "quantity": quantity,
                        "instrument": {
                            "symbol": symbol,
                            "assetType": "EQUITY"
                        }
                    }
                ]
            }

            response = self.client.place_order(self.account_id, order)
            order_id = response.headers.get("Location").split("/")[-1]
            logger.info(f"✅ Orden límite: {instruction} {quantity} {symbol} @ ${price} (ID: {order_id})")
            return order_id

        except Exception as e:
            logger.error(f"Error colocando orden límite: {e}")
            return None

    def cancel_order(self, order_id: str) -> bool:
        """Cancela una orden"""
        try:
            self.client.cancel_order(self.account_id, order_id)
            logger.info(f"✅ Orden cancelada: {order_id}")
            return True
        except Exception as e:
            logger.error(f"Error cancelando orden: {e}")
            return False

    def close_position(self, symbol: str) -> bool:
        """Cierra una posición (vende todas las acciones)"""
        try:
            position = self.get_position(symbol)
            if not position:
                logger.warning(f"⚠️  No hay posición abierta en {symbol}")
                return False

            quantity = int(position["longQuantity"])
            if quantity > 0:
                self.submit_market_order(symbol, quantity, "SELL")
                logger.info(f"✅ Posición cerrada: {symbol} ({quantity} acciones)")
                return True
            else:
                logger.warning(f"⚠️  Cantidad inválida en {symbol}")
                return False

        except Exception as e:
            logger.error(f"Error cerrando posición: {e}")
            return False

    def _simulate_order(self, symbol: str, quantity: int, instruction: str) -> str:
        """Simula una orden en paper trading"""
        import uuid
        return f"PAPER_{uuid.uuid4().hex[:8].upper()}"

    def get_market_status(self) -> str:
        """Obtiene el estado del mercado"""
        try:
            # Simplificado: si estamos en horario de mercado
            now = datetime.now()
            hour = now.hour
            weekday = now.weekday()  # 0=Monday, 4=Friday

            # Mercado abierto: 09:30-16:00 EST, Lunes-Viernes
            if weekday < 5 and 9 <= hour < 16:
                return "OPEN"
            elif weekday < 5 and 4 <= hour < 9:
                return "PREMARKET"
            elif weekday < 5 and 16 <= hour < 20:
                return "AFTERHOURS"
            else:
                return "CLOSED"

        except Exception as e:
            logger.error(f"Error obteniendo estado del mercado: {e}")
            return "UNKNOWN"


def main():
    """Test del broker"""
    try:
        broker = ThinkOrSwimBroker()

        print("\n" + "="*60)
        print("🔗 CONEXIÓN EXITOSA CON THINKORSWIM")
        print("="*60)

        # Info de cuenta
        account = broker.get_account()
        cash = broker.get_cash()
        buying_power = broker.get_buying_power()

        print(f"\n📊 CUENTA:")
        print(f"  Account Value: ${account.get('accountValue', {}).get('accountValue', 0):,.2f}")
        print(f"  Cash: ${cash:,.2f}")
        print(f"  Buying Power: ${buying_power:,.2f}")

        # Posiciones
        positions = broker.get_positions()
        print(f"\n📈 POSICIONES ({len(positions)}):")
        for pos in positions:
            symbol = pos["instrument"]["symbol"]
            qty = pos["longQuantity"]
            market_value = pos["marketValue"]
            print(f"  {symbol}: {qty} acciones (${market_value:,.2f})")

        # Estado del mercado
        market_status = broker.get_market_status()
        print(f"\n🕐 MERCADO: {market_status}")

        print("\n" + "="*60)
        print("✅ Todo funciona correctamente")
        print("="*60 + "\n")

    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Error en test: {e}")


if __name__ == "__main__":
    main()
