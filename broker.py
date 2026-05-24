# broker.py - Conector con Alpaca Broker

import os
from datetime import datetime, timedelta
import logging
from typing import Optional, List, Dict
import pandas as pd

try:
    from alpaca.trading.client import TradingClient
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest, StockLatestBarRequest
    from alpaca.trading.requests import (
        MarketOrderRequest,
        StopOrderRequest,
        LimitOrderRequest,
        TrailingStopOrderRequest
    )
    from alpaca.trading.enums import OrderSide, TimeInForce, OrderStatus
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    logging.warning("Alpaca SDK no disponible. Install: pip install alpaca-trade-api")

import config

logger = logging.getLogger(__name__)


class AlpacaBroker:
    """
    Conector con Alpaca Broker
    Soporta paper trading y live trading
    """

    def __init__(self, api_key: str = None, secret_key: str = None, paper: bool = True):
        """
        Inicializa conexión con Alpaca

        Args:
            api_key: API key de Alpaca
            secret_key: Secret key de Alpaca
            paper: Si True, usa paper trading (simulado sin dinero real)
        """
        if not ALPACA_AVAILABLE:
            raise ImportError("Alpaca SDK no disponible")

        self.api_key = api_key or config.ALPACA_API_KEY
        self.secret_key = secret_key or config.ALPACA_SECRET_KEY
        self.paper = paper

        # Conectar con Alpaca
        self.client = TradingClient(
            api_key=self.api_key,
            secret_key=self.secret_key,
            paper_trading=paper
        )

        self.data_client = StockHistoricalDataClient(
            api_key=self.api_key,
            secret_key=self.secret_key
        )

        logger.info(f"Conectado a Alpaca ({'Paper Trading' if paper else 'LIVE TRADING'})")
        self._verify_connection()

    def _verify_connection(self):
        """Verifica que la conexión funciona"""
        try:
            account = self.client.get_account()
            logger.info(f"✓ Conexión exitosa. Cash disponible: ${float(account.cash):.2f}")
        except Exception as e:
            logger.error(f"✗ Error de conexión: {e}")
            raise

    # ============ ACCOUNT INFO ============

    def get_account(self) -> Dict:
        """Obtiene información de la cuenta"""
        try:
            account = self.client.get_account()
            return {
                'cash': float(account.cash),
                'portfolio_value': float(account.portfolio_value),
                'equity': float(account.equity),
                'multiplier': account.multiplier,
                'buying_power': float(account.buying_power),
                'day_trade_buying_power': float(account.daytrade_buying_power),
                'status': account.status,
                'created_at': account.created_at,
                'updated_at': account.updated_at,
            }
        except Exception as e:
            logger.error(f"Error obteniendo información de cuenta: {e}")
            return None

    def get_portfolio_value(self) -> float:
        """Obtiene valor total del portafolio"""
        account = self.get_account()
        return account['portfolio_value'] if account else 0.0

    def get_cash(self) -> float:
        """Obtiene cash disponible"""
        account = self.get_account()
        return account['cash'] if account else 0.0

    # ============ POSITIONS ============

    def get_positions(self) -> List[Dict]:
        """Obtiene todas las posiciones abiertas"""
        try:
            positions = self.client.get_all_positions()
            result = []
            for pos in positions:
                result.append({
                    'symbol': pos.symbol,
                    'qty': float(pos.qty),
                    'avg_fill_price': float(pos.avg_fill_price),
                    'current_price': float(pos.current_price) if pos.current_price else None,
                    'unrealized_gain': float(pos.unrealized_gain) if pos.unrealized_gain else None,
                    'unrealized_gain_pct': float(pos.unrealized_gainpct) if pos.unrealized_gainpct else None,
                    'side': pos.side,
                    'asset_id': pos.asset_id,
                })
            return result
        except Exception as e:
            logger.error(f"Error obteniendo posiciones: {e}")
            return []

    def get_position(self, symbol: str) -> Optional[Dict]:
        """Obtiene posición específica"""
        try:
            position = self.client.get_open_position(symbol)
            return {
                'symbol': position.symbol,
                'qty': float(position.qty),
                'avg_fill_price': float(position.avg_fill_price),
                'current_price': float(position.current_price) if position.current_price else None,
                'unrealized_gain': float(position.unrealized_gain) if position.unrealized_gain else None,
                'unrealized_gain_pct': float(position.unrealized_gainpct) if position.unrealized_gainpct else None,
            }
        except:
            return None

    def close_position(self, symbol: str) -> Dict:
        """Cierra posición completa de un símbolo"""
        try:
            order = self.client.close_position(symbol)
            logger.info(f"Orden de cierre para {symbol} ejecutada: ID {order.id}")
            return {
                'order_id': order.id,
                'symbol': order.symbol,
                'qty': float(order.qty),
                'status': order.status,
            }
        except Exception as e:
            logger.error(f"Error cerrando posición {symbol}: {e}")
            return None

    # ============ ORDERS ============

    def submit_market_order(self, symbol: str, qty: int, side: str,
                           time_in_force: str = "day") -> Dict:
        """
        Coloca una orden de mercado

        Args:
            symbol: Símbolo (ej: AAPL)
            qty: Cantidad de acciones
            side: buy o sell
            time_in_force: day, gtc, opg, cls, ioc

        Returns:
            Dict con detalles de la orden
        """
        try:
            order_data = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL,
                time_in_force=TimeInForce(time_in_force.upper())
            )

            order = self.client.submit_order(order_data)

            logger.info(f"Orden {side.upper()} colocada: {symbol} x{qty} (ID: {order.id})")

            return {
                'order_id': order.id,
                'symbol': order.symbol,
                'qty': float(order.qty),
                'side': order.side,
                'order_type': order.order_type,
                'status': order.status,
                'created_at': order.created_at,
                'filled_at': order.filled_at,
                'filled_avg_price': float(order.filled_avg_price) if order.filled_avg_price else None,
                'filled_qty': float(order.filled_qty) if order.filled_qty else None,
            }
        except Exception as e:
            logger.error(f"Error colocando orden {side} {symbol}: {e}")
            return None

    def submit_limit_order(self, symbol: str, qty: int, side: str,
                          limit_price: float) -> Dict:
        """Coloca una orden límite"""
        try:
            order_data = LimitOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL,
                limit_price=limit_price,
                time_in_force=TimeInForce.GTC  # Good Till Canceled
            )

            order = self.client.submit_order(order_data)
            logger.info(f"Orden límite {side.upper()} {symbol}: {qty} @ ${limit_price}")
            return self._format_order(order)
        except Exception as e:
            logger.error(f"Error colocando orden límite: {e}")
            return None

    def submit_bracket_order(self, symbol: str, qty: int, entry_price: float,
                           take_profit: float, stop_loss: float) -> List[Dict]:
        """
        Coloca una orden bracket (entrada + TP + SL)

        Args:
            symbol: Símbolo
            qty: Cantidad
            entry_price: Precio de entrada (límite)
            take_profit: Precio para cerrar ganancia
            stop_loss: Precio para cerrar pérdida
        """
        try:
            # Orden entrada
            entry = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.GTC
            )

            order = self.client.submit_order(entry)
            logger.info(f"Bracket order {symbol}: Entry {qty}, TP ${take_profit}, SL ${stop_loss}")
            return [self._format_order(order)]
        except Exception as e:
            logger.error(f"Error en bracket order: {e}")
            return []

    def cancel_order(self, order_id: str) -> bool:
        """Cancela una orden pendiente"""
        try:
            self.client.cancel_order_by_id(order_id)
            logger.info(f"Orden {order_id} cancelada")
            return True
        except Exception as e:
            logger.error(f"Error cancelando orden: {e}")
            return False

    def get_orders(self, status: str = "open") -> List[Dict]:
        """Obtiene órdenes (open, closed, all)"""
        try:
            orders = self.client.get_orders(status=status)
            result = []
            for order in orders:
                result.append(self._format_order(order))
            return result
        except Exception as e:
            logger.error(f"Error obteniendo órdenes: {e}")
            return []

    def get_order(self, order_id: str) -> Dict:
        """Obtiene detalles de orden específica"""
        try:
            order = self.client.get_order_by_id(order_id)
            return self._format_order(order)
        except Exception as e:
            logger.error(f"Error obteniendo orden {order_id}: {e}")
            return None

    def _format_order(self, order) -> Dict:
        """Formatea objeto de orden a Dict"""
        return {
            'order_id': order.id,
            'symbol': order.symbol,
            'qty': float(order.qty),
            'side': order.side,
            'order_type': order.order_type,
            'status': order.status,
            'created_at': order.created_at,
            'filled_at': order.filled_at,
            'filled_avg_price': float(order.filled_avg_price) if order.filled_avg_price else None,
            'filled_qty': float(order.filled_qty) if order.filled_qty else None,
        }

    # ============ MARKET DATA ============

    def get_latest_bar(self, symbol: str) -> Optional[Dict]:
        """Obtiene la barra más reciente de un símbolo"""
        try:
            request = StockLatestBarRequest(symbol_or_symbols=symbol)
            bar = self.data_client.get_stock_latest_bar(request)

            if bar and symbol in bar:
                b = bar[symbol]
                return {
                    'symbol': symbol,
                    'open': float(b.open),
                    'high': float(b.high),
                    'low': float(b.low),
                    'close': float(b.close),
                    'volume': int(b.volume),
                    'timestamp': b.timestamp,
                }
            return None
        except Exception as e:
            logger.debug(f"Error obteniendo última barra para {symbol}: {e}")
            return None

    def get_bars(self, symbol: str, timeframe: str = "1Day",
                limit: int = 100) -> pd.DataFrame:
        """
        Obtiene barras históricas

        Args:
            symbol: Símbolo
            timeframe: 1Min, 5Min, 15Min, 1Hour, 1Day
            limit: Cantidad de barras
        """
        try:
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=timeframe,
                limit=limit,
                start=datetime.now() - timedelta(days=365)
            )

            bars = self.data_client.get_stock_bars(request)

            if symbol in bars:
                df = bars[symbol].df
                return df
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error obteniendo barras para {symbol}: {e}")
            return pd.DataFrame()

    def get_clock(self) -> Dict:
        """Obtiene estado del mercado (abierto/cerrado)"""
        try:
            clock = self.client.get_clock()
            return {
                'timestamp': clock.timestamp,
                'is_open': clock.is_open,
                'next_open': clock.next_open,
                'next_close': clock.next_close,
            }
        except Exception as e:
            logger.error(f"Error obteniendo reloj del mercado: {e}")
            return None


# ============ UTILITY FUNCTIONS ============

def create_broker(paper: bool = True) -> AlpacaBroker:
    """Factory function para crear broker"""
    return AlpacaBroker(paper=paper)


if __name__ == "__main__":
    # Test connection
    broker = create_broker(paper=True)

    # Get account info
    account = broker.get_account()
    print(f"\nCuenta (Paper Trading):")
    print(f"  Cash: ${account['cash']:.2f}")
    print(f"  Portfolio Value: ${account['portfolio_value']:.2f}")
    print(f"  Buying Power: ${account['buying_power']:.2f}")

    # Get positions
    positions = broker.get_positions()
    print(f"\nPosiciones ({len(positions)}):")
    for pos in positions:
        print(f"  {pos['symbol']}: {pos['qty']} @ ${pos['avg_fill_price']:.2f} (Gain: {pos['unrealized_gain_pct']:.1f}%)")

    # Get clock
    clock = broker.get_clock()
    print(f"\nMercado: {'ABIERTO' if clock['is_open'] else 'CERRADO'}")
