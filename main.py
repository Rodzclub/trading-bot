#!/usr/bin/env python3
"""
Trading Bot Principal
Orquesta: Scanner → Estrategias → Risk Check → Orders
Ejecutar: python main.py
"""

import os
import sys
import time
import logging
from datetime import datetime, time as dt_time
from dotenv import load_dotenv

from thinkorswim_broker import ThinkOrSwimBroker
from scanner_premarket import PremarketScanner
from strategies.gap_and_go import GapAndGoStrategy
from strategies.breakout import BreakoutStrategy
from strategies.ma_crossover import MovingAverageCrossoverStrategy
from risk_management.position_sizing import PositionSizer
from risk_management.daily_limits import DailyLimits
from config_thinkorswim import INITIAL_CAPITAL

load_dotenv()

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/trading_bot_main.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TradingBot:
    """Bot principal de trading automatizado"""

    def __init__(self):
        """Inicializa el bot"""
        self.broker = ThinkOrSwimBroker()
        self.scanner = PremarketScanner()
        self.gap_and_go = GapAndGoStrategy()
        self.breakout = BreakoutStrategy()
        self.ma_crossover = MovingAverageCrossoverStrategy()
        self.position_sizer = PositionSizer(account_value=INITIAL_CAPITAL)
        self.daily_limits = DailyLimits()
        self.active_trades = {}  # {symbol: {strategy, entry_price, entry_time}}

        logger.info("✅ Bot inicializado")

    def is_trading_hours(self) -> bool:
        """Verifica si estamos en horario de trading"""
        now = datetime.now()
        hour = now.hour

        # Premarket: 04:00-09:30
        if 4 <= hour < 9:
            return True
        # Normal market: 09:30-16:00
        elif 9 <= hour < 16:
            return True
        # After hours: 16:00-20:00
        elif 16 <= hour < 20:
            return True

        return False

    def scan_and_trade(self):
        """Main loop: Escanea y ejecuta trades"""
        print("\n" + "="*80)
        print(f"🤖 TRADING BOT INICIADO - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        if not self.is_trading_hours():
            logger.warning("⚠️  Fuera de horario de trading")
            return

        market_status = self.broker.get_market_status()
        logger.info(f"📊 Estado del mercado: {market_status}")

        # FASE 1: Escanear oportunidades
        logger.info("📍 FASE 1: Escaneando oportunidades...")
        opportunities = self.scanner.scan()

        if not opportunities:
            logger.info("⚠️  No hay oportunidades")
            return

        # FASE 2: Evaluar estrategias
        logger.info("📍 FASE 2: Evaluando estrategias...")

        for opp in opportunities[:5]:  # Top 5 oportunidades
            symbol = opp["symbol"]
            logger.info(f"\n📌 Analizando: {symbol}")

            # Verificar límites diarios
            can_trade, reason = self.daily_limits.can_trade("entry")
            if not can_trade:
                logger.warning(f"⚠️  {reason}")
                break

            # Obtener datos actuales
            quote = self.broker.get_quote(symbol)
            if not quote:
                logger.warning(f"⚠️  No se pudo obtener quote para {symbol}")
                continue

            price_history = self.broker.get_price_history(symbol, period=10)
            if not price_history:
                logger.warning(f"⚠️  No hay historial para {symbol}")
                continue

            # Evaluar estrategias
            strategies_results = {
                "gap_and_go": self.gap_and_go.check_entry_signal(
                    symbol,
                    {
                        "price": quote.get("lastPrice", 0),
                        "gap": opp.get("gap", 0),
                        "volume_ratio": opp.get("volume_ratio", 0),
                        "previous_close": quote.get("closePrice", 0),
                        "bid": quote.get("bidPrice", quote.get("lastPrice", 0)),
                        "ask": quote.get("askPrice", quote.get("lastPrice", 0))
                    }
                ),
                "breakout": self.breakout.check_entry_signal(
                    symbol,
                    quote.get("lastPrice", 0),
                    opp.get("volume", 0),
                    price_history
                ),
                "ma_crossover": self.ma_crossover.check_entry_signal(
                    symbol,
                    price_history
                )
            }

            # Elegir mejor estrategia
            best_strategy = max(
                strategies_results.items(),
                key=lambda x: x[1].get("confidence", 0)
            )

            if best_strategy[1].get("signal") != "HOLD":
                logger.info(f"✅ Señal de entrada: {best_strategy[0]} "
                            f"(Confidence: {best_strategy[1].get('confidence', 0)}%)")

                # FASE 3: Risk Management
                self.execute_trade(symbol, best_strategy)

    def execute_trade(self, symbol: str, strategy_result: tuple):
        """
        Ejecuta un trade

        Args:
            symbol: símbolo
            strategy_result: (strategy_name, entry_data)
        """
        strategy_name, entry_data = strategy_result
        signal = entry_data.get("signal")
        entry_price = entry_data.get("entry_price", 0)
        stop_loss = entry_data.get("stop_loss", 0)
        profit_target = entry_data.get("profit_target", 0)

        logger.info(f"\n📍 FASE 3: Risk Management para {symbol}")

        # Calcular position size
        shares = self.position_sizer.calculate_shares(entry_price, stop_loss)
        if shares < 1:
            logger.warning(f"⚠️  Position size inválido: {shares} acciones")
            return

        # Calcular dinero en riesgo
        risk_dollars = abs(entry_price - stop_loss) * shares
        logger.info(f"  Risk: ${risk_dollars:,.2f}")
        logger.info(f"  Shares: {shares}")

        # FASE 4: Colocar orden
        logger.info(f"\n📍 FASE 4: Colocando orden...")

        if signal == "BUY":
            order_id = self.broker.submit_market_order(symbol, shares, "BUY")
        elif signal == "SELL":
            order_id = self.broker.submit_market_order(symbol, shares, "SELL")
        else:
            logger.warning(f"⚠️  Signal inválido: {signal}")
            return

        if not order_id:
            logger.error(f"❌ Error colocando orden para {symbol}")
            return

        # Registrar trade
        logger.info(f"✅ Orden colocada: {order_id}")

        self.active_trades[symbol] = {
            "strategy": strategy_name,
            "signal": signal,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "profit_target": profit_target,
            "shares": shares,
            "order_id": order_id,
            "entry_time": datetime.now().isoformat()
        }

        # Actualizar límites
        self.daily_limits.add_position()
        self.daily_limits.add_trade()

    def monitor_positions(self):
        """Monitorea posiciones abiertas y cierra si es necesario"""
        if not self.active_trades:
            return

        logger.info(f"\n📍 MONITOREO: {len(self.active_trades)} posiciones abiertas")

        for symbol, trade_info in list(self.active_trades.items()):
            quote = self.broker.get_quote(symbol)
            current_price = quote.get("lastPrice", 0)

            if not current_price:
                continue

            # Verificar exit signal
            strategy = self._get_strategy(trade_info["strategy"])
            exit_signal = strategy.check_exit_signal(current_price, trade_info)

            if exit_signal.get("signal") == "CLOSE":
                logger.info(f"🔴 Cerrando {symbol}: {exit_signal.get('reason')}")

                # Cerrar posición
                self.broker.close_position(symbol)

                # Actualizar límites
                pnl = exit_signal.get("pnl", 0)
                self.daily_limits.close_position(pnl=pnl)

                # Remover de trades activos
                del self.active_trades[symbol]

    def _get_strategy(self, strategy_name: str):
        """Retorna la instancia de estrategia"""
        if strategy_name == "gap_and_go":
            return self.gap_and_go
        elif strategy_name == "breakout":
            return self.breakout
        elif strategy_name == "ma_crossover":
            return self.ma_crossover

    def print_summary(self):
        """Imprime resumen del bot"""
        print("\n" + "="*80)
        print("📊 RESUMEN DEL BOT")
        print("="*80)

        # Cuenta
        cash = self.broker.get_cash()
        buying_power = self.broker.get_buying_power()
        positions = self.broker.get_positions()

        print(f"\n💰 CUENTA:")
        print(f"  Cash: ${cash:,.2f}")
        print(f"  Poder de compra: ${buying_power:,.2f}")

        # Posiciones
        print(f"\n📈 POSICIONES: {len(positions)}")
        for pos in positions:
            symbol = pos["instrument"]["symbol"]
            qty = pos["longQuantity"]
            market_value = pos["marketValue"]
            print(f"  {symbol}: {qty} acciones (${market_value:,.2f})")

        # Límites diarios
        limits_status = self.daily_limits.get_status()
        print(f"\n⚠️  LÍMITES DIARIOS:")
        print(f"  P&L: ${limits_status['daily_pnl']:,.2f} ({limits_status['daily_pnl_pct']:.2f}%)")
        print(f"  Posiciones: {limits_status['open_positions']} / {limits_status['max_open_positions']}")
        print(f"  Trades: {limits_status['trades_today']} / {limits_status['max_trades_today']}")
        print(f"  Puedo tradear: {limits_status['can_trade']}")

        print("\n" + "="*80 + "\n")


def main():
    """Main entry point"""
    try:
        bot = TradingBot()

        # Loop principal
        while True:
            try:
                # Verificar horario
                if not bot.is_trading_hours():
                    logger.warning("⚠️  Fuera de horario")
                    time.sleep(60)
                    continue

                # Scan and trade
                bot.scan_and_trade()

                # Monitor positions
                bot.monitor_positions()

                # Print summary
                bot.print_summary()

                # Wait before next scan
                logger.info("⏳ Esperando próximo ciclo...")
                time.sleep(60)  # Scan cada minuto

            except KeyboardInterrupt:
                logger.info("🛑 Interrumpido por usuario")
                break
            except Exception as e:
                logger.error(f"❌ Error en loop principal: {e}")
                time.sleep(5)

    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
