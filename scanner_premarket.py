#!/usr/bin/env python3
"""
Scanner Premarket - Escanea gaps y oportunidades 04:00-09:30 EST
Busca:
- Gaps > 2%
- Volumen anómalo (> 1.5x promedio)
- Precios entre $5-$500
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd
from dotenv import load_dotenv
from thinkorswim_broker import ThinkOrSwimBroker

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/scanner_premarket.log"),
        logging.StreamHandler()
    ]
)

# Parámetros del scanner
MIN_GAP = 2.0  # Gap mínimo 2%
MIN_VOLUME_RATIO = 1.5  # Volumen mínimo 1.5x el promedio
MIN_PRICE = 5.0  # Precio mínimo
MAX_PRICE = 500.0  # Precio máximo
MIN_LIQUIDITY = 100000  # Volumen mínimo diario


class PremarketScanner:
    """Scanner para oportunidades en premarket"""

    def __init__(self, watchlist: List[str] = None):
        """
        Inicializa el scanner
        watchlist: lista de símbolos a escanear
        """
        self.broker = ThinkOrSwimBroker()
        self.watchlist = watchlist or self._get_default_watchlist()
        self.opportunities = []
        logger.info(f"📊 Scanner iniciado con {len(self.watchlist)} símbolos")

    def _get_default_watchlist(self) -> List[str]:
        """Obtiene la lista de símbolos del .env o usa defaults"""
        watchlist_str = os.getenv("WATCHLIST", "")
        if watchlist_str:
            return [s.strip().upper() for s in watchlist_str.split(",")]
        else:
            # Top S&P 500 por liquidez
            return [
                "AAPL", "MSFT", "TSLA", "AMZN", "GOOGL", "META", "NVDA", "AMD",
                "PLTR", "RIVN", "LUCID", "NFLX", "SQ", "CRWD", "ZM", "DASH",
                "NIO", "XPEV", "LI", "SAIC", "ACHR", "APRN", "SOFI", "UPST"
            ]

    def scan(self) -> List[Dict]:
        """Escanea todos los símbolos y retorna oportunidades"""
        print("\n" + "="*80)
        print("🔍 ESCANEO PREMARKET")
        print("="*80)
        print(f"Iniciando: {datetime.now().strftime('%H:%M:%S')}")
        print(f"Símbolos: {len(self.watchlist)}")
        print("-"*80)

        self.opportunities = []

        for symbol in self.watchlist:
            try:
                opportunity = self._analyze_symbol(symbol)
                if opportunity:
                    self.opportunities.append(opportunity)
                    print(f"✅ {opportunity['symbol']}: "
                          f"Gap {opportunity['gap']:.1f}% | "
                          f"Vol {opportunity['volume_ratio']:.1f}x | "
                          f"Score: {opportunity['score']:.0f}")

            except Exception as e:
                logger.warning(f"⚠️  Error escaneando {symbol}: {e}")
                continue

        # Ordenar por score
        self.opportunities.sort(key=lambda x: x["score"], reverse=True)

        print("-"*80)
        print(f"Completado: {datetime.now().strftime('%H:%M:%S')}")
        print(f"Oportunidades encontradas: {len(self.opportunities)}")
        print("="*80 + "\n")

        return self.opportunities

    def _analyze_symbol(self, symbol: str) -> Dict:
        """
        Analiza un símbolo individual
        Retorna Dict con oportunidad o None
        """
        try:
            # Obtener quote actual
            quote = self.broker.get_quote(symbol)
            if not quote:
                return None

            current_price = quote.get("lastPrice", 0)
            bid = quote.get("bidPrice", current_price)
            ask = quote.get("askPrice", current_price)

            # Validaciones básicas
            if current_price < MIN_PRICE or current_price > MAX_PRICE:
                return None

            # Obtener historial (últimos 10 días)
            history = self.broker.get_price_history(
                symbol,
                period=10,
                period_type="day",
                frequency=1,
                frequency_type="minute"  # Última vela del día anterior
            )

            if not history or len(history) < 2:
                return None

            # Último cierre (ayer)
            last_close = history[-2]["close"] if len(history) >= 2 else history[-1]["close"]

            # Gap calculado
            gap = ((current_price - last_close) / last_close) * 100

            # Filtrar por gap mínimo
            if abs(gap) < MIN_GAP:
                return None

            # Obtener volumen
            today_candles = [c for c in history if c["datetime"] >= (datetime.now() - timedelta(days=1)).timestamp() * 1000]
            if not today_candles:
                return None

            today_volume = sum(c.get("volume", 0) for c in today_candles)
            historical_volume = sum(c.get("volume", 0) for c in history[:-1]) / len(history[:-1])
            volume_ratio = today_volume / historical_volume if historical_volume > 0 else 0

            # Filtrar por volumen
            if volume_ratio < MIN_VOLUME_RATIO:
                return None

            if today_volume < MIN_LIQUIDITY:
                return None

            # Calcular score
            gap_score = min(abs(gap) / 2, 50)  # Max 50 puntos por gap
            volume_score = min(volume_ratio * 10, 50)  # Max 50 puntos por volumen
            score = gap_score + volume_score

            return {
                "symbol": symbol,
                "price": current_price,
                "gap": gap,
                "volume_ratio": volume_ratio,
                "bid": bid,
                "ask": ask,
                "score": score,
                "last_close": last_close,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error analizando {symbol}: {e}")
            return None

    def export_csv(self, filename: str = "opportunities.csv"):
        """Exporta oportunidades a CSV"""
        if not self.opportunities:
            print("No hay oportunidades para exportar")
            return

        df = pd.DataFrame(self.opportunities)
        df.to_csv(filename, index=False)
        logger.info(f"Oportunidades exportadas a {filename}")
        print(f"📁 Guardado: {filename}")

    def filter_by_score(self, min_score: float = 80.0) -> List[Dict]:
        """Filtra oportunidades por score mínimo"""
        return [opp for opp in self.opportunities if opp["score"] >= min_score]

    def filter_by_price_range(self, min_price: float, max_price: float) -> List[Dict]:
        """Filtra oportunidades por rango de precio"""
        return [
            opp for opp in self.opportunities
            if min_price <= opp["price"] <= max_price
        ]


def main():
    """Ejecuta el scanner"""
    try:
        scanner = PremarketScanner()
        opportunities = scanner.scan()

        if opportunities:
            print("\n🎯 TOP OPORTUNIDADES:")
            print("-"*80)
            for i, opp in enumerate(opportunities[:5], 1):
                print(f"\n{i}. {opp['symbol']}")
                print(f"   Precio: ${opp['price']:.2f}")
                print(f"   Gap: {opp['gap']:.2f}%")
                print(f"   Volumen: {opp['volume_ratio']:.2f}x")
                print(f"   Score: {opp['score']:.0f}")
                print(f"   Bid/Ask: ${opp['bid']:.2f} / ${opp['ask']:.2f}")

            # Exportar CSV
            scanner.export_csv("opportunities.csv")

        else:
            print("\n⚠️  No se encontraron oportunidades que cumplan los criterios")

    except Exception as e:
        logger.error(f"Error en scanner: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
