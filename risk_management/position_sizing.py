#!/usr/bin/env python3
"""
Position Sizing - Calcula tamaño de posición basado en riesgo
Sigue regla: Riesgo máximo 1% del capital por trade
"""

import logging
from typing import Tuple
from config_thinkorswim import RISK_PER_TRADE, INITIAL_CAPITAL

logger = logging.getLogger(__name__)


class PositionSizer:
    """Calcula tamaño de posición automáticamente"""

    def __init__(self, account_value: float = INITIAL_CAPITAL):
        """
        Inicializa position sizer
        account_value: valor actual de la cuenta
        """
        self.account_value = account_value
        self.risk_per_trade = RISK_PER_TRADE

    def calculate_shares(
        self,
        entry_price: float,
        stop_loss_price: float
    ) -> int:
        """
        Calcula número de acciones a comprar
        Basado en: (riesgo $ / riesgo por acción) = número de acciones

        Args:
            entry_price: precio de entrada
            stop_loss_price: precio del stop loss

        Returns:
            Número de acciones a comprar
        """
        # Riesgo en dólares (1% del capital)
        risk_dollars = self.account_value * self.risk_per_trade

        # Riesgo por acción
        risk_per_share = abs(entry_price - stop_loss_price)

        if risk_per_share <= 0:
            logger.warning("⚠️  Stop loss inválido")
            return 0

        # Acciones = Riesgo $ / Riesgo por acción
        shares = int(risk_dollars / risk_per_share)

        # Validación mínima
        if shares < 1:
            logger.warning(f"⚠️  Posición muy pequeña: {shares} acciones")
            return 1

        logger.info(f"📊 Position Size: {shares} acciones "
                    f"(Riesgo: ${risk_dollars:.2f})")

        return shares

    def calculate_profit_target(
        self,
        entry_price: float,
        risk_amount: float,
        reward_ratio: float = 2.0
    ) -> float:
        """
        Calcula target de ganancia basado en riesgo/ganancia

        Args:
            entry_price: precio de entrada
            risk_amount: $ en riesgo
            reward_ratio: ratio riesgo/ganancia (ej: 2 = 2:1)

        Returns:
            Precio objetivo de ganancia
        """
        potential_profit = risk_amount * reward_ratio
        target_price = entry_price + (potential_profit / 100 * entry_price / risk_amount)
        return round(target_price, 2)

    def calculate_stop_loss(
        self,
        entry_price: float,
        stop_loss_pct: float = 2.0
    ) -> float:
        """
        Calcula stop loss porcentaje

        Args:
            entry_price: precio de entrada
            stop_loss_pct: porcentaje de stop loss (ej: 2 = 2%)

        Returns:
            Precio del stop loss
        """
        stop_loss = entry_price * (1 - stop_loss_pct / 100)
        return round(stop_loss, 2)

    def get_kelly_fraction(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float
    ) -> float:
        """
        Calcula Kelly Fraction para posición sizing óptimo
        Fórmula: (bp - q) / b
        Donde: b = avg_win/avg_loss, p = win_rate, q = 1-win_rate

        Args:
            win_rate: porcentaje de trades ganadores (0-1)
            avg_win: ganancia promedio
            avg_loss: pérdida promedio

        Returns:
            Fracción Kelly (0-1, multiplicar por riesgo_pct)
        """
        if avg_loss <= 0:
            return 0

        b = avg_win / avg_loss
        p = win_rate
        q = 1 - win_rate

        kelly = (b * p - q) / b

        # Limitar a máximo 25% para conservador
        kelly = min(max(kelly, 0), 0.25)

        logger.info(f"🔢 Kelly Fraction: {kelly:.2%}")

        return kelly


def main():
    """Test del position sizer"""
    sizer = PositionSizer(account_value=5000)

    # Test 1: Calcular shares
    print("\n" + "="*60)
    print("📊 POSITION SIZING TEST")
    print("="*60)

    entry = 50.00
    stop = 48.00
    shares = sizer.calculate_shares(entry, stop)

    print(f"\nTest 1: Position Shares")
    print(f"  Entry: ${entry:.2f}")
    print(f"  Stop Loss: ${stop:.2f}")
    print(f"  Risk per share: ${abs(entry - stop):.2f}")
    print(f"  Shares to buy: {shares}")

    # Test 2: Profit target
    print(f"\nTest 2: Profit Target (2:1 Ratio)")
    risk_dollars = 5000 * 0.01
    target = sizer.calculate_profit_target(entry, abs(entry - stop), reward_ratio=2.0)
    print(f"  Entry: ${entry:.2f}")
    print(f"  Target: ${target:.2f}")
    print(f"  Profit if hit: ${(target - entry) * shares:.2f}")

    # Test 3: Kelly Fraction
    print(f"\nTest 3: Kelly Fraction")
    kelly = sizer.get_kelly_fraction(win_rate=0.55, avg_win=150, avg_loss=100)
    print(f"  Win rate: 55%")
    print(f"  Avg win: $150")
    print(f"  Avg loss: $100")
    print(f"  Kelly: {kelly:.2%}")

    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
