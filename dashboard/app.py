#!/usr/bin/env python3
"""
Dashboard Streamlit para monitoreo en tiempo real
Ejecutar: streamlit run dashboard/app.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from thinkorswim_broker import ThinkOrSwimBroker
from risk_management.daily_limits import DailyLimits
import json

# Page config
st.set_page_config(
    page_title="Trading Bot Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .positive {
        color: #28a745;
    }
    .negative {
        color: #dc3545;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def init_broker():
    """Inicializa broker (cached)"""
    return ThinkOrSwimBroker()


@st.cache_resource
def init_limits():
    """Inicializa daily limits (cached)"""
    return DailyLimits()


def main():
    """Main app"""
    st.title("🤖 Trading Bot Dashboard")
    st.write(f"_Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_")

    broker = init_broker()
    limits = init_limits()

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuración")

        refresh_interval = st.slider(
            "Intervalo de actualización (segundos)",
            min_value=5,
            max_value=60,
            value=30
        )

        if st.button("🔄 Actualizar Ahora", use_container_width=True):
            st.rerun()

        st.divider()

        st.subheader("📊 Información del Broker")
        broker_status = broker.get_market_status()
        st.metric("Estado del Mercado", broker_status)

    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Cuenta", "💼 Posiciones", "📊 Límites", "📋 Logs"])

    with tab1:
        col1, col2, col3 = st.columns(3)

        # Obtener datos
        account = broker.get_account()
        cash = broker.get_cash()
        buying_power = broker.get_buying_power()

        with col1:
            st.metric(
                "💰 Cash",
                f"${cash:,.2f}",
                delta=None
            )

        with col2:
            st.metric(
                "📊 Poder de Compra",
                f"${buying_power:,.2f}",
                delta=None
            )

        with col3:
            account_value = account.get("accountValue", {}).get("accountValue", 0)
            st.metric(
                "💎 Valor Total",
                f"${account_value:,.2f}",
                delta=None
            )

        # Chart de balance (simulado)
        st.subheader("Evolución de Balance")
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        balances = [5000 + i * (20 if i % 2 == 0 else -15) for i in range(30)]
        df_balance = pd.DataFrame({
            "Fecha": dates,
            "Balance": balances
        })
        st.line_chart(df_balance.set_index("Fecha"), height=300)

    with tab2:
        st.subheader("💼 Posiciones Abiertas")
        positions = broker.get_positions()

        if positions:
            pos_data = []
            for pos in positions:
                pos_data.append({
                    "Símbolo": pos["instrument"]["symbol"],
                    "Cantidad": int(pos.get("longQuantity", 0)),
                    "Precio Promedio": pos.get("averagePrice", 0),
                    "Precio Actual": pos.get("currentPrice", 0),
                    "Valor": f"${pos.get('marketValue', 0):,.2f}",
                    "P&L": f"${pos.get('marketValue', 0) - (pos.get('averagePrice', 0) * int(pos.get('longQuantity', 0))):,.2f}"
                })

            df_positions = pd.DataFrame(pos_data)
            st.dataframe(df_positions, use_container_width=True)
        else:
            st.info("📭 No hay posiciones abiertas")

        # Buttons para cerrar posiciones
        if positions:
            st.subheader("Gestionar Posiciones")
            symbol_to_close = st.selectbox(
                "Selecciona posición para cerrar",
                [p["instrument"]["symbol"] for p in positions]
            )

            if st.button(f"🔴 Cerrar {symbol_to_close}", use_container_width=True):
                if broker.close_position(symbol_to_close):
                    st.success(f"✅ {symbol_to_close} cerrada")
                    st.rerun()
                else:
                    st.error(f"❌ Error cerrando {symbol_to_close}")

    with tab3:
        st.subheader("⚠️  Límites Diarios")
        limits_status = limits.get_status()

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "P&L Diario",
                f"${limits_status['daily_pnl']:,.2f}",
                f"{limits_status['daily_pnl_pct']:.2f}%"
            )

            st.metric(
                "Máximo Pérdida",
                f"${limits_status['max_daily_loss']:,.2f}",
                None
            )

        with col2:
            st.metric(
                "Posiciones Abiertas",
                f"{limits_status['open_positions']} / {limits_status['max_open_positions']}"
            )

            st.metric(
                "Trades Realizados",
                f"{limits_status['trades_today']} / {limits_status['max_trades_today']}"
            )

        # Status
        if limits_status['can_trade']:
            st.success("✅ Permitido tradear")
        else:
            st.error(f"❌ {limits_status['reason']}")

        # Progress bars
        st.subheader("Progreso Diario")

        pnl_pct = (limits_status['daily_pnl'] / abs(limits_status['max_daily_loss'])) * 100 if limits_status['max_daily_loss'] != 0 else 0
        st.progress(
            min(abs(pnl_pct), 100) / 100,
            text=f"P&L: {pnl_pct:.1f}%"
        )

        pos_pct = limits_status['open_positions'] / limits_status['max_open_positions']
        st.progress(
            pos_pct,
            text=f"Posiciones: {limits_status['open_positions']}/{limits_status['max_open_positions']}"
        )

        trades_pct = limits_status['trades_today'] / limits_status['max_trades_today']
        st.progress(
            trades_pct,
            text=f"Trades: {limits_status['trades_today']}/{limits_status['max_trades_today']}"
        )

    with tab4:
        st.subheader("📋 Logs Recientes")

        # Leer últimas líneas del log
        try:
            with open("logs/trading_bot_main.log", "r") as f:
                lines = f.readlines()
                recent_logs = lines[-20:] if len(lines) > 20 else lines
                log_text = "".join(recent_logs)
                st.code(log_text, language="log")
        except FileNotFoundError:
            st.warning("⚠️  No hay logs aún")

    # Auto refresh
    st.markdown(f"""
    <script>
        setTimeout(function() {{
            window.location.reload(false);
        }}, {refresh_interval * 1000});
    </script>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
