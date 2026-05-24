#!/usr/bin/env python3
"""
Moving Average Crossover Strategy
Swing trading usando SMA 9/21 crossover
- Entry: SMA9 cruza arriba de SMA21 (alcista) o abajo (bajista)
- Exit: Profit target o stop loss
- Riesgo: 1-2% por trade (más seguro)
- Duración: 1-5 días
"""

import logging
from typing import Dict, List
import numpy as np

logger = logging.getLogger(__name__)


class MovingAverageCrossoverStrategy:
    """MA Crossover - Estrategia swing trading"""

    def __init__(self):
        """Inicializa parámetros de la estrategia"""
        # Parámetros de media móvil
        self.sma_short = 9  # SMA rápido
        self.sma_long = 21  # SMA lento
        self.min_bars_for_ma = max(self.sma_short, self.sma_long) + 5

        # Parámetros de salida
        self.profit_target_pct = 4.0  # Target 4% ganancia
        self.stop_loss_pct = 1.5  # Stop 1.5% pérdida
        self.atr_multiplier = 2.0  # Stop basado en ATR

    def calculate_sma(self, prices: List[float], period: int) -> float:
        """Calcula Simple Moving Average"""
        if len(prices) < period:
            return 0
        return np.mean(prices[-period:])

    def calculate_atr(self, candles: List[Dict], period: int = 14) -> float:
        """
        Calcula Average True Range
        Usado para dynamic stop loss
        """
        if len(candles) < period:
            return 0

        trs = []
        for i in range(len(candles)):
            high = candles[i].get("high", 0)
            low = candles[i].get("low", 0)
            close_prev = candles[i-1].get("close", high) if i > 0 else high

            tr = max(
                high - low,
                abs(high - close_prev),
                abs(low - close_prev)
            )
            trs.append(tr)

        return np.mean(trs[-period:]) if len(trs) >= period else np.mean(trs)

    def check_entry_signal(
        self,
        symbol: str,
        candle_history: List[Dict]
    ) -> Dict:
        """
        Verifica señal de entrada de MA crossover

        Args:
            symbol: símbolo
            candle_history: lista de candles (debe tener close, high, low)

        Returns:
            {
                'signal': 'BUY' | 'SELL' | 'HOLD',
                'confidence': 0-100,
                'reason': str,
                'entry_price': float,
                'stop_loss': float,
                'profit_target': float,
                'sma_short': float,
                'sma_long': float
            }
        """
        if len(candle_history) < self.min_bars_for_ma:
            return {"signal": "HOLD", "confidence": 0, "reason": "Datos insuficientes"}

        closes = [c.get("close", 0) for c in candle_history]

        # Calcular SMAs
        sma_short = self.calculate_sma(closes, self.sma_short)
        sma_long = self.calculate_sma(closes, self.sma_long)
        sma_short_prev = self.calculate_sma(closes[:-1], self.sma_short)

        if sma_short == 0 or sma_long == 0:
            return {"signal": "HOLD", "confidence": 0, "reason": "SMAs no calculadas"}

        current_price = closes[-1]
        atr = self.calculate_atr(candle_history, period=14)

        # Señal alcista: SMA9 cruza arriba de SMA21
        if sma_short > sma_long and sma_short_prev <= sma_long:
            entry_price = current_price
            stop_loss = round(current_price - (atr * self.atr_multiplier), 2)
            profit_target = round(entry_price * (1 + self.profit_target_pct / 100), 2)

            # Confidence basado en distancia entre SMAs
            ma_distance = ((sma_short - sma_long) / sma_long) * 100
            confidence = min(
                50 +  # Base 50%
                min(ma_distance * 5, 50),  # Distancia contribuye hasta 50%
                100
            )

            return {
                "signal": "BUY",
                "confidence": int(confidence),
                "reason": f"SMA{self.sma_short} cruzó SMA{self.sma_long} al alza",
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "profit_target": profit_target,
                "sma_short": round(sma_short, 2),
                "sma_long": round(sma_long, 2),
                "distance": round(ma_distance, 2)
            }

        # Señal bajista: SMA9 cruza abajo de SMA21
        elif sma_short < sma_long and sma_short_prev >= sma_long:
            entry_price = current_price
            stop_loss = round(current_price + (atr * self.atr_multiplier), 2)
            profit_target = round(entry_price * (1 - self.profit_target_pct / 100), 2)

            ma_distance = ((sma_long - sma_short) / sma_long) * 100
            confidence = min(
                50 +
                min(ma_distance * 5, 50),
                100
            )

            return {
                "signal": "SELL",
                "confidence": int(confidence),
                "reason": f"SMA{self.sma_short} cruzó SMA{self.sma_long} a la baja",
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "profit_target": profit_target,
                "sma_short": round(sma_short, 2),
                "sma_long": round(sma_long, 2),
                "distance": round(ma_distance, 2)
            }

        return {
            "signal": "HOLD",
            "confidence": 0,
            "reason": f"Sin crossover. SMA9: ${sma_short:.2f}, SMA21: ${sma_long:.2f}",
            "sma_short": round(sma_short, 2),
            "sma_long": round(sma_long, 2)
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
            "name": "MA Crossover",
            "fast_ma": f"SMA{self.sma_short}",
            "slow_ma": f"SMA{self.sma_long}",
            "profit_target": f"{self.profit_target_pct}%",
            "stop_loss": f"{self.stop_loss_pct}% (Dynamic ATR)",
            "risk_level": "Low-Medium (1-2%)",
            "duration": "1-5 days",
            "best_time": "Daily (todas las horas)",
            "confidence_needed": "50%+",
            "description": "Swing trading con cruces de medias móviles"
        }


def main():
    """Test de la estrategia"""
    strategy = MovingAverageCrossoverStrategy()

    print("\n" + "="*80)
    print("🎯 MOVING AVERAGE CROSSOVER STRATEGY TEST")
    print("="*80)

    # Test 1: Parámetros
    print("\nParámetros:")
    for key, value in strategy.get_parameters().items():
        print(f"  {key}: {value}")

    # Test 2: Historial simulado (tendencia alcista)
    print("\nTest 1: Alcista Crossover")
    candle_history = [
        {"close": 100, "high": 101, "low": 99},
        {"close": 100.5, "high": 101.5, "low": 100},
        {"close": 101, "high": 102, "low": 100.5},
        {"close": 101.5, "high": 102.5, "low": 101},
        {"close": 102, "high": 103, "low": 101.5},
        {"close": 102.5, "high": 103.5, "low": 102},
        {"close": 103, "high": 103.8, "low": 102.5},
        {"close": 103.5, "high": 104, "low": 103},
        {"close": 104, "high": 104.5, "low": 103.5},
        {"close": 104.5, "high": 105, "low": 104},
        {"close": 105, "high": 105.5, "low": 104.5},
        {"close": 105.5, "high": 106, "low": 105},
        {"close": 106, "high": 106.5, "low": 105.5},
        {"close": 106.5, "high": 107, "low": 106},
        {"close": 107, "high": 107.5, "low": 106.5},
        {"close": 107.5, "high": 108, "low": 107},  # Crossover esperado
    ]

    entry = strategy.check_entry_signal("AAPL", candle_history)

    print(f"  Signal: {entry['signal']}")
    print(f"  Confidence: {entry.get('confidence', 0)}%")
    print(f"  Reason: {entry.get('reason', 'N/A')}")
    print(f"  SMA9: ${entry.get('sma_short', 0):.2f}")
    print(f"  SMA21: ${entry.get('sma_long', 0):.2f}")
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
