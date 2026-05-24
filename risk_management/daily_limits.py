#!/usr/bin/env python3
"""
Daily Limits - Enforces límites diarios de riesgo
- Máximo pérdida diaria: 2% del capital
- Máximo posiciones abiertas: 3
- Máximo operaciones por día: 10
"""

import logging
from datetime import datetime, date
from typing import Dict, Tuple
from config_thinkorswim import (
    MAX_DAILY_LOSS_PCT,
    MAX_OPEN_POSITIONS,
    INITIAL_CAPITAL
)

logger = logging.getLogger(__name__)


class DailyLimits:
    """Gestiona límites diarios de trading"""

    def __init__(self):
        """Inicializa límites diarios"""
        self.max_daily_loss = INITIAL_CAPITAL * MAX_DAILY_LOSS_PCT
        self.max_open_positions = MAX_OPEN_POSITIONS
        self.max_trades_per_day = 10
        self.reset_daily()

    def reset_daily(self):
        """Reset de contadores diarios"""
        self.daily_pnl = 0.0
        self.open_positions = 0
        self.trades_today = 0
        self.last_reset = date.today()
        logger.info("📅 Límites diarios reset")

    def check_reset(self):
        """Verifica si hace falta reset (new day)"""
        if date.today() != self.last_reset:
            self.reset_daily()

    def can_trade(self, position_type: str = "entry") -> Tuple[bool, str]:
        """
        Verifica si se puede entrar en un nuevo trade

        Args:
            position_type: "entry" o "exit"

        Returns:
            (permitido: bool, razón: str)
        """
        self.check_reset()

        if position_type == "entry":
            # Verificar límite de posiciones abiertas
            if self.open_positions >= self.max_open_positions:
                return False, f"⚠️  Máximo {self.max_open_positions} posiciones abiertas"

            # Verificar límite de trades diarios
            if self.trades_today >= self.max_trades_per_day:
                return False, f"⚠️  Máximo {self.max_trades_per_day} trades por día"

            # Verificar pérdida diaria
            if self.daily_pnl < -self.max_daily_loss:
                return False, f"⚠️  Límite diario alcanzado: ${self.daily_pnl:,.2f}"

        return True, "✅ OK para operar"

    def add_trade(self, pnl: float = 0.0):
        """
        Registra un nuevo trade
        pnl: profit/loss del trade (puede ser 0 si entry, actualizar después)
        """
        self.trades_today += 1
        self.daily_pnl += pnl
        logger.info(f"📊 Trade #{self.trades_today} - P&L Diario: ${self.daily_pnl:,.2f}")

    def add_position(self):
        """Incrementa contador de posiciones abiertas"""
        self.open_positions += 1
        logger.info(f"📈 Posición abierta #{self.open_positions}")

    def close_position(self, pnl: float = 0.0):
        """
        Cierra una posición
        pnl: ganancia/pérdida de la posición
        """
        self.open_positions = max(0, self.open_positions - 1)
        self.daily_pnl += pnl
        logger.info(f"📉 Posición cerrada - P&L: ${pnl:,.2f} | P&L Diario: ${self.daily_pnl:,.2f}")

    def get_status(self) -> Dict:
        """Retorna status actual de límites"""
        self.check_reset()

        return {
            "date": date.today().isoformat(),
            "daily_pnl": self.daily_pnl,
            "daily_pnl_pct": (self.daily_pnl / INITIAL_CAPITAL) * 100,
            "max_daily_loss": -self.max_daily_loss,
            "open_positions": self.open_positions,
            "max_open_positions": self.max_open_positions,
            "trades_today": self.trades_today,
            "max_trades_today": self.max_trades_per_day,
            "can_trade": self.can_trade("entry")[0],
            "reason": self.can_trade("entry")[1]
        }

    def print_status(self):
        """Imprime status formateado"""
        status = self.get_status()

        print("\n" + "="*60)
        print("📊 DAILY LIMITS STATUS")
        print("="*60)
        print(f"Date: {status['date']}")
        print(f"\nP&L DIARIO:")
        print(f"  Ganancia/Pérdida: ${status['daily_pnl']:,.2f} ({status['daily_pnl_pct']:.2f}%)")
        print(f"  Máximo pérdida: ${status['max_daily_loss']:,.2f}")
        print(f"\nPOSICIONES:")
        print(f"  Abiertas: {status['open_positions']} / {status['max_open_positions']}")
        print(f"\nTRADES:")
        print(f"  Realizados: {status['trades_today']} / {status['max_trades_today']}")
        print(f"\nSTATUS:")
        print(f"  {status['reason']}")
        print("="*60 + "\n")


def main():
    """Test de daily limits"""
    limits = DailyLimits()

    print("\n" + "="*60)
    print("🧪 DAILY LIMITS TEST")
    print("="*60)

    # Test 1: Status inicial
    print("\nTest 1: Status Inicial")
    limits.print_status()

    # Test 2: Add positions
    print("Test 2: Agregando posiciones...")
    for i in range(3):
        can_trade, reason = limits.can_trade("entry")
        print(f"  Trade {i+1}: {reason}")
        if can_trade:
            limits.add_position()
            limits.add_trade()

    limits.print_status()

    # Test 3: Close position con pérdida
    print("Test 3: Cerrando posición con pérdida...")
    limits.close_position(pnl=-50.00)
    limits.print_status()

    # Test 4: Intentar exceder límite
    print("Test 4: Intentar exceder máximo de posiciones...")
    for i in range(3):
        can_trade, reason = limits.can_trade("entry")
        print(f"  Intento {i+1}: {reason}")
        if can_trade:
            limits.add_position()

    limits.print_status()

    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
