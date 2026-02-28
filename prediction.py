# ==========================================
# 🔮 AI FOREX DASHBOARD (INDIA TIME BASED FUTURE PREDICTION)
# ==========================================

import streamlit as st
import pandas as pd
import numpy as np
import MetaTrader5 as mt5
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(layout="wide")

# ---------------------------
# PLAIN LOGIN PAGE (ANY USERNAME/PASSWORD)
# ---------------------------
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🔐 Login (Any Username/Password)")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        # ANY input logs in successfully
        st.session_state.login = True
        st.success(f"Login Successful! Welcome, {username}")
        st.rerun()

    st.stop()

# ---------------------------
# SIDEBAR
# ---------------------------
st.sidebar.title("Currency Pairs")

pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"]
selected_pair = st.sidebar.selectbox("Select Pair", pairs)

# ---------------------------
# MT5 CONNECT
# ---------------------------
if not mt5.initialize():
    st.error("MT5 Initialization Failed")
    st.stop()

# ---------------------------
# GET DATA FUNCTION
# ---------------------------
def get_data(symbol, timeframe, bars=200):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

# ---------------------------
# INDIA TIME (IST)
# ---------------------------
ist = pytz.timezone("Asia/Kolkata")
now_ist = datetime.now(ist)

# ---------------------------
# FUTURE TIME CALCULATION
# ---------------------------
future_1h_time = now_ist + timedelta(hours=1)
future_1d_time = now_ist + timedelta(days=1)

# ---------------------------
# DUMMY PREDICTION LOGIC
# (Replace with your TFT/XGB model)
# ---------------------------
def predict_next_price(df):
    last_price = df['close'].iloc[-1]
    predicted = last_price + np.random.uniform(-0.001, 0.001)
    return predicted

# ---------------------------
# 1 HOUR PREDICTION
# ---------------------------
st.subheader("📈 1 Hour Prediction")

df_1h = get_data(selected_pair, mt5.TIMEFRAME_H1, bars=30)
df_1h['time'] = df_1h['time'].dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
last_candle = df_1h.iloc[-1]

pred_close = predict_next_price(df_1h)
pred_open = last_candle['close']
pred_high = max(pred_open, pred_close) + 0.0005
pred_low = min(pred_open, pred_close) - 0.0005
future_time = future_1h_time

fig1 = go.Figure()
fig1.add_trace(go.Candlestick(
    x=df_1h['time'],
    open=df_1h['open'],
    high=df_1h['high'],
    low=df_1h['low'],
    close=df_1h['close'],
    name="Actual"
))
fig1.add_trace(go.Candlestick(
    x=[future_time],
    open=[pred_open],
    high=[pred_high],
    low=[pred_low],
    close=[pred_close],
    name="Predicted"
))
fig1.update_layout(
    title=f"{selected_pair} - Next Hour Prediction",
    xaxis_title="Time (IST)",
    yaxis_title="Price",
    xaxis=dict(tickformat="%d-%m %H:%M"),
)
st.plotly_chart(fig1, use_container_width=True)

# ---------------------------
# 1 DAY PREDICTION
# ---------------------------
st.subheader("📊 1 Day Prediction")

df_1d = get_data(selected_pair, mt5.TIMEFRAME_D1)
last_price = df_1d['close'].iloc[-1]
pred_1d = predict_next_price(df_1d)

x_values = [now_ist, future_1d_time]
y_values = [last_price, pred_1d]

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=x_values,
    y=y_values,
    mode='lines+markers+text',
    text=["Current", "Predicted"],
    textposition="top center",
    name="1D Prediction"
))
fig2.update_layout(
    title=f"{selected_pair} - Next Day Prediction",
    xaxis_title="Time (IST)",
    yaxis_title="Price",
    xaxis=dict(
        tickformat="%d-%m-%Y %H:%M",
        type='date'
    )
)
st.plotly_chart(fig2, use_container_width=True)

st.write("🕒 Current IST:", now_ist.strftime("%d-%m-%Y %H:%M"))
st.write("➡️ Next Day Prediction Time:", future_1d_time.strftime("%d-%m-%Y %H:%M"))
st.write("💰 Predicted Price:", round(pred_1d, 5))

# ---------------------------
# SIGNAL SECTION
# ---------------------------
st.sidebar.subheader("📢 Signals Comparison")
signals = {}

for pair in pairs:
    df_temp = get_data(pair, mt5.TIMEFRAME_H1)
    pred_temp = predict_next_price(df_temp)
    last_price = df_temp['close'].iloc[-1]

    if pred_temp > last_price:
        signals[pair] = "BUY"
    elif pred_temp < last_price:
        signals[pair] = "SELL"
    else:
        signals[pair] = "HOLD"

for pair, signal in signals.items():
    st.sidebar.write(f"{pair} → {signal}")

# ---------------------------
# SHUTDOWN MT5
# ---------------------------
mt5.shutdown()
