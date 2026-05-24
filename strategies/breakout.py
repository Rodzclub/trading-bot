#!/usr/bin/env python3
"""
Breakout Strategy
Busca rupturas de máximos intraday con volumen
- Entry: Ruptura de la resistencia del día anterior
- Exit: Profit target o stop loss
- Riesgo: 2-3% por trade (moderado)
- Duración: 30 minutos - 2 horas
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class BreakoutStrategy:
    """Breakout - Estrategia intraday"""

    def __init__(self):
        """Inicializa parámetros de la estrategia"""
        # Parámetros de entrada
        self.lookback_bars = 20  # Máximo de los últimos 20 días
        self.min_volume_ratio = 1.3  # Volumen mínimo 1.3x
        self.entry_offset_pct = 0.2  # Entry 0.2% arriba del high

        # Parámetros de salida
        self.profit_target_pct = 2.5  # Target 2.5% ganancia
        self.stop_loss_pct = 1.5  # Stop 1.5% pérdida
        self.trailing_stop_pct = 0.8  # Trailing stop 0.8%

    def check_entry_signal(
        self,
        symbol: str,
        current_price: float,
        current_volume: float,
        price_history: List[Dict]
    ) -> Dict:
        """
        Verifica señal de entrada de breakout

        Args:
            symbol: símbolo
            current_price: precio actual
            current_volume: volumen actual
            price_history: lista de candles recientes

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
        if not price_history or len(price_history) < 5:
            return {"signal": "HOLD", "confidence": 0, "reason": "Datos insuficientes"}

        # Calcular resistance y support de los últimos lookback_bars
        lookback = min(self.lookback_bars, len(price_history) - 1)
        recent_candles = price_history[-lookback:-1]  # Excluyendo la vela actual

        resistance = max([c.get("high", 0) for c in recent_candles])
        support = min([c.get("low", 0) for c in recent_candles])
        avg_volume = sum([c.get("volume", 0) for c in recent_candles]) / len(recent_candles)

        # Calcular volume ratio
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0

        # Búsqueda de breakout alcista
        if current_price > resistance * (1 + self.entry_offset_pct / 100):
            if volume_ratio >= self.min_volume_ratio:
                entry_price = round(current_price, 2)
                stop_loss = round(support, 2)
                profit_target = round(entry_price * (1 + self.profit_target_pct / 100), 2)

                # Confidence basado en volumen
                confidence = min(
                    (volume_ratio - 1) * 50 +  # Volumen contribuye 50%
                    ((current_price - resistance) / resistance * 100) * 0.5,  # Distancia contribuye 50%
                    100
                )

                return {
                    "signal": "BUY",
                    "confidence": int(confidence),
                    "reason": f"Ruptura {(current_price - resistance) / resistance * 100:.1f}% + Vol {volume_ratio:.1f}x",
                    "entry_price": entry_price,
                    "stop_loss": stop_loss,
                    "profit_target": profit_target,
                    "resistance": resistance,
                    "support": support
                }

        # Búsqueda de breakout bajista
        elif current_price < support * (1 - self.entry_offset_pct / 100):
            if volume_ratio >= self.min_volume_ratio:
                entry_price = round(current_price, 2)
                stop_loss = round(resistance, 2)
                profit_target = round(entry_price * (1 - self.profit_target_pct / 100), 2)

                confidence = min(
                    (volume_ratio - 1) * 50 +
                    ((resistance - current_price) / resistance * 100) * 0.5,
                    100
                )

                return {
                    "signal": "SELL",
                    "confidence": int(confidence),
                    "reason": f"Ruptura bajista {(resistance - current_price) / resistance * 100:.1f}% + Vol {volume_ratio:.1f}x",
                    "entry_price": entry_price,
                    "stop_loss": stop_loss,
                    "profit_target": profit_target,
                    "resistance": resistance,
                    "support": support
                }

        return {
            "signal": "HOLD",
            "confidence": 0,
            "reason": f"Sin ruptura clara. Resistance: ${resistance:.2f}, Support: ${support:.2f}",
            "resistance": resistance,
            "support": support
        }

    def check_exit_signal(
        self,
        current_price: float,
        entry_data: Dict
    ) -> Dict:
        """
        Verifica señal de salida

        Args:
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
            "name": "Breakout",
            "lookback_bars": f"{self.lookback_bars} days",
            "min_volume_ratio": f"{self.min_volume_ratio}x",
            "profit_target": f"{self.profit_target_pct}%",
            "stop_loss": f"{self.stop_loss_pct}%",
            "risk_level": "Medium (2-3%)",
            "duration": "30 minutes - 2 hours",
            "best_time": "09:30-12:00 EST (Morning)",
            "confidence_needed": "50%+"
        }


def main():
    """Test de la estrategia"""
    strategy = BreakoutStrategy()

    print("\n" + "="*80)
    print("🎯 BREAKOUT STRATEGY TEST")
    print("="*80)

    # Test 1: Parámetros
    print("\nParámetros:")
    for key, value in strategy.get_parameters().items():
        print(f"  {key}: {value}")

    # Test 2: Historial simulado
    print("\nTest 1: Breakout Detection")
    price_history = [
        {"high": 100, "low": 98, "close": 99.5, "volume": 1000000},
        {"high": 101, "low": 99, "close": 100.2, "volume": 1100000},
        {"high": 100.5, "low": 99, "close": 99.8, "volume": 950000},
        {"high": 102, "low": 99.5, "close": 101.5, "volume": 1500000},  # Breakout
    ]

    entry = strategy.check_entry_signal(
        "AAPL",
        current_price=102.1,
        current_volume=1600000,
        price_history=price_history
    )

    print(f"  Signal: {entry['signal']}")
    print(f"  Confidence: {entry['confidence']}%")
    print(f"  Reason: {entry.get('reason', 'N/A')}")
    print(f"  Entry: ${entry.get('entry_price', 0):.2f}")
    print(f"  SL: ${entry.get('stop_loss', 0):.2f}")
    print(f"  PT: ${entry.get('profit_target', 0):.2f}")

    # Test 3: Exit signal
    if entry["signal"] == "BUY":
        print("\nTest 2: Profit Target Exit")
        exit_signal = strategy.check_exit_signal(
            entry["profit_target"] + 0.01,
            entry
        )
        print(f"  Signal: {exit_signal['signal']}")
        print(f"  P&L: ${exit_signal.get('pnl', 0):.2f} ({exit_signal.get('pnl_pct', 0):.2f}%)")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
