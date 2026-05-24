#!/usr/bin/env python3
"""
Gap and Go Strategy
Busca gaps > 2% en premarket y los opera al abrir el mercado
- Entry: Ruptura del gap con volumen
- Exit: Profit target o stop loss
- Riesgo: 3-5% por trade (más arriesgado pero rápido)
- Duración: 15-60 minutos
"""

import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class GapAndGoStrategy:
    """Gap and Go - Estrategia premarket"""

    def __init__(self):
        """Inicializa parámetros de la estrategia"""
        # Parámetros de entrada
        self.min_gap = 2.0  # Gap mínimo 2%
        self.min_volume_ratio = 1.5  # Volumen mínimo 1.5x
        self.entry_confirmation_bars = 2  # Esperar 2 velas de confirmación

        # Parámetros de salida
        self.profit_target_pct = 3.0  # Target 3% ganancia
        self.stop_loss_pct = 2.0  # Stop 2% pérdida
        self.trailing_stop_pct = 1.0  # Trailing stop 1%

        # Control de estado
        self.active_positions = {}  # {symbol: {entry_price, shares, entry_time}}

    def check_entry_signal(self, symbol: str, market_data: Dict) -> Dict:
        """
        Verifica señal de entrada

        Args:
            symbol: símbolo a analizar
            market_data: {price, gap, volume_ratio, previous_close, bid, ask}

        Returns:
            {
                'signal': 'BUY' | 'SELL' | 'HOLD',
                'confidence': 0-100,
                'reason': str,
                'entry_price': float,
                'stop_loss': float,
                'profit_target': float
            }
        """
        price = market_data.get("price", 0)
        gap = market_data.get("gap", 0)
        volume_ratio = market_data.get("volume_ratio", 0)
        previous_close = market_data.get("previous_close", 0)

        # Validación básica
        if not price or not previous_close:
            return {"signal": "HOLD", "confidence": 0, "reason": "Datos incompletos"}

        # Gap positivo
        if gap >= self.min_gap and volume_ratio >= self.min_volume_ratio:
            # Entrada: en el bid (a favor del gap)
            entry_price = market_data.get("bid", price)
            stop_loss = round(entry_price * (1 - self.stop_loss_pct / 100), 2)
            profit_target = round(entry_price * (1 + self.profit_target_pct / 100), 2)

            confidence = min(
                (abs(gap) / 2) * 50 +  # Gap contribuye 50%
                (volume_ratio - 1) * 50,  # Volumen contribuye 50%
                100
            )

            return {
                "signal": "BUY",
                "confidence": int(confidence),
                "reason": f"Gap {gap:.1f}% + Vol {volume_ratio:.1f}x",
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "profit_target": profit_target,
                "gap": gap,
                "volume_ratio": volume_ratio
            }

        # Gap negativo (short)
        elif gap <= -self.min_gap and volume_ratio >= self.min_volume_ratio:
            entry_price = market_data.get("ask", price)
            stop_loss = round(entry_price * (1 + self.stop_loss_pct / 100), 2)
            profit_target = round(entry_price * (1 - self.profit_target_pct / 100), 2)

            confidence = min(
                (abs(gap) / 2) * 50 +
                (volume_ratio - 1) * 50,
                100
            )

            return {
                "signal": "SELL",
                "confidence": int(confidence),
                "reason": f"Gap {gap:.1f}% + Vol {volume_ratio:.1f}x",
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "profit_target": profit_target,
                "gap": gap,
                "volume_ratio": volume_ratio
            }

        return {
            "signal": "HOLD",
            "confidence": 0,
            "reason": f"Gap {gap:.1f}% no cumple criterio ({self.min_gap}%)"
        }

    def check_exit_signal(
        self,
        symbol: str,
        current_price: float,
        entry_data: Dict
    ) -> Dict:
        """
        Verifica señal de salida

        Args:
            symbol: símbolo
            current_price: precio actual
            entry_data: {entry_price, stop_loss, profit_target, signal}

        Returns:
            {
                'signal': 'CLOSE' | 'HOLD',
                'reason': str,
                'exit_price': float,
                'pnl': float,
                'pnl_pct': float
            }
        """
        entry_price = entry_data.get("entry_price", 0)
        stop_loss = entry_data.get("stop_loss", 0)
        profit_target = entry_data.get("profit_target", 0)
        signal = entry_data.get("signal", "BUY")

        if signal == "BUY":
            # Profit target
            if current_price >= profit_target:
                pnl = current_price - entry_price
                pnl_pct = (pnl / entry_price) * 100
                return {
                    "signal": "CLOSE",
                    "reason": "Profit target alcanzado",
                    "exit_price": profit_target,
                    "pnl": pnl,
                    "pnl_pct": pnl_pct,
                    "type": "PROFIT"
                }

            # Stop loss
            if current_price <= stop_loss:
                pnl = current_price - entry_price
                pnl_pct = (pnl / entry_price) * 100
                return {
                    "signal": "CLOSE",
                    "reason": "Stop loss hit",
                    "exit_price": stop_loss,
                    "pnl": pnl,
                    "pnl_pct": pnl_pct,
                    "type": "LOSS"
                }

        elif signal == "SELL":
            # Profit target (short)
            if current_price <= profit_target:
                pnl = entry_price - current_price
                pnl_pct = (pnl / entry_price) * 100
                return {
                    "signal": "CLOSE",
                    "reason": "Profit target alcanzado (short)",
                    "exit_price": profit_target,
                    "pnl": pnl,
                    "pnl_pct": pnl_pct,
                    "type": "PROFIT"
                }

            # Stop loss (short)
            if current_price >= stop_loss:
                pnl = entry_price - current_price
                pnl_pct = (pnl / entry_price) * 100
                return {
                    "signal": "CLOSE",
                    "reason": "Stop loss hit (short)",
                    "exit_price": stop_loss,
                    "pnl": pnl,
                    "pnl_pct": pnl_pct,
                    "type": "LOSS"
                }

        return {"signal": "HOLD"}

    def get_parameters(self) -> Dict:
        """Retorna parámetros de la estrategia"""
        return {
            "name": "Gap and Go",
            "min_gap": f"{self.min_gap}%",
            "min_volume_ratio": f"{self.min_volume_ratio}x",
            "profit_target": f"{self.profit_target_pct}%",
            "stop_loss": f"{self.stop_loss_pct}%",
            "risk_level": "High (3-5%)",
            "duration": "15-60 minutes",
            "best_time": "04:00-09:30 EST (Premarket)",
            "confidence_needed": "60%+"
        }


def main():
    """Test de la estrategia"""
    strategy = GapAndGoStrategy()

    print("\n" + "="*80)
    print("🎯 GAP AND GO STRATEGY TEST")
    print("="*80)

    # Test 1: Parámetros
    print("\nParámetros:")
    for key, value in strategy.get_parameters().items():
        print(f"  {key}: {value}")

    # Test 2: Señal de entrada (gap positivo)
    print("\nTest 1: Gap Positivo")
    market_data = {
        "price": 50.50,
        "gap": 2.5,
        "volume_ratio": 1.8,
        "previous_close": 49.27,
        "bid": 50.48,
        "ask": 50.52
    }
    entry = strategy.check_entry_signal("TSLA", market_data)
    print(f"  Signal: {entry['signal']}")
    print(f"  Confidence: {entry['confidence']}%")
    print(f"  Reason: {entry.get('reason', 'N/A')}")
    print(f"  Entry: ${entry.get('entry_price', 0):.2f}")
    print(f"  SL: ${entry.get('stop_loss', 0):.2f}")
    print(f"  PT: ${entry.get('profit_target', 0):.2f}")

    # Test 3: Señal de salida (profit)
    if entry["signal"] == "BUY":
        print("\nTest 2: Profit Target")
        exit_signal = strategy.check_exit_signal(
            "TSLA",
            entry["profit_target"] + 0.01,  # Precio al target
            entry
        )
        print(f"  Signal: {exit_signal['signal']}")
        print(f"  Reason: {exit_signal.get('reason', 'N/A')}")
        print(f"  P&L: ${exit_signal.get('pnl', 0):.2f} ({exit_signal.get('pnl_pct', 0):.2f}%)")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
