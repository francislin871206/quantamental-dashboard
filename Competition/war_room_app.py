
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from datetime import datetime
import yfinance as yf
from textblob import TextBlob
import requests
from bs4 import BeautifulSoup

# ─── CONFIGURATION ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Macro War Room",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for "Pro Max" UI
st.markdown("""
<style>
    /* Dark Theme Optimization */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Console Style */
    .console-box {
        background-color: #1e1e1e;
        color: #00ff00;
        font-family: 'Courier New', Courier, monospace;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #333;
        height: 300px;
        overflow-y: auto;
    }
    
    /* Audit Log Entry */
    .log-entry {
        margin-bottom: 5px;
        border-bottom: 1px solid #333;
        padding-bottom: 2px;
    }
    
    /* Agent Badges */
    .badge-analyst { color: #00d4aa; font-weight: bold; }
    .badge-quant { color: #f2a900; font-weight: bold; }
    .badge-risk { color: #ff4b4b; font-weight: bold; }
    
    /* Kill Switch */
    .kill-switch-active {
        background-color: #333 !important;
        color: #666 !important;
        border: 1px solid #444 !important;
        cursor: not-allowed;
    }
</style>
""", unsafe_allow_html=True)


# ─── AGENT LOGIC (DATA ENGINE LITE) ──────────────────────────────────────────

@st.cache_data(ttl=3600)
def fetch_spy_ma200():
    """Quant Agent: Fetches SPY and calculates 200D Moving Average."""
    try:
        spy = yf.Ticker("SPY").history(period="1y")
        if spy.empty: return None, None
        
        current_price = spy["Close"].iloc[-1]
        ma200 = spy["Close"].rolling(200).mean().iloc[-1]
        
        return current_price, ma200
    except Exception as e:
        return None, None

def fetch_fomc_sentiment_sim():
    """Analyst Agent: Simulates FOMC sentiment scraping."""
    # In a real app, this would use the scraping logic from data_engine.py
    # Here we simulate varying conditions for testing the "Kill Switch"
    
    # Randomly generate a scenario for demonstration unless override
    # score: -10 (Hawkish/Bearish) to +10 (Dovish/Bullish)
    import random
    scenarios = [
        {"score": -5, "label": "Hawkish 🦅", "evidence": "Fed signals 'higher for longer' indefinitely."},
        {"score": 8, "label": "Dovish 🕊️", "evidence": "Powell hints at rate cuts next meeting."},
        {"score": 0, "label": "Neutral ⚖️", "evidence": "Fed awaiting more CPI data."}
    ]
    return random.choice(scenarios)

def fetch_risk_level_sim():
    """Risk Agent: Simulates Geopolitical Risk analysis."""
    import random
    levels = ["Low 🟢", "Medium 🟡", "High 🔴"]
    return random.choice(levels)


# ─── STATE MANAGEMENT ────────────────────────────────────────────────────────

if "agent_state" not in st.session_state:
    st.session_state.agent_state = "IDLE" # IDLE, SCANNING, COMPLETE

if "logs" not in st.session_state:
    st.session_state.logs = []

if "results" not in st.session_state:
    st.session_state.results = {
        "hawk_score": 0,
        "price_vs_ma": "Neutral",
        "risk_level": "Low",
        "consensus": "Neutral"
    }

def add_log(agent, message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append({"time": timestamp, "agent": agent, "msg": message})


# ─── UI LAYOUT ───────────────────────────────────────────────────────────────

st.title("🌍 Global Macro War Room")
st.caption("autonomous_agent_orchestrator__v1.2 // session_id: " + str(id(st.session_state))[:8])

# Top Controls
c1, c2, c3 = st.columns([2, 1, 1])

with c1:
    if st.session_state.agent_state == "IDLE":
        if st.button("🚀 INITIALIZE GLOBAL SCAN", type="primary", use_container_width=True):
            st.session_state.agent_state = "SCANNING"
            st.session_state.logs = [] # Clear logs on new run
            st.rerun()
    elif st.session_state.agent_state == "SCANNING":
        st.button("⏳ AGENTS RUNNING...", disabled=True, use_container_width=True)
    else:
        if st.button("🔄 RE-SCAN MARKET", type="primary", use_container_width=True):
            st.session_state.agent_state = "SCANNING"
            st.session_state.logs = []
            st.rerun()

with c2:
    if st.button("🗑️ Clear Console", use_container_width=True):
        st.session_state.logs = []
        st.rerun()
        
with c3:
    if st.button("💥 Reset System", use_container_width=True):
        st.session_state.clear()
        st.rerun()


# ─── ORCHESTRATION ENGINE ────────────────────────────────────────────────────

if st.session_state.agent_state == "SCANNING":
    placeholder = st.empty()
    
    # 1. Analyst Agent
    with placeholder.container():
        st.info("🕵️ Analyst Agent: Connecting to Federal Reserve News Stream...")
    time.sleep(1.5)
    fomc = fetch_fomc_sentiment_sim()
    st.session_state.results["hawk_score"] = fomc["score"]
    add_log("Analyst", f"FOMC Sentiment: {fomc['label']} (Score: {fomc['score']})")
    add_log("Analyst", f"Evidence: {fomc['evidence']}")
    
    # 2. Quant Agent
    with placeholder.container():
        st.info("🧮 Quant Agent: Calculating Technical Structure ($SPY)...")
    time.sleep(1.5)
    price, ma200 = fetch_spy_ma200()
    if price and ma200:
        trend = "Bullish" if price > ma200 else "Bearish"
        st.session_state.results["price_vs_ma"] = trend
        add_log("Quant", f"SPY Price: ${price:.2f} | MA200: ${ma200:.2f}")
        add_log("Quant", f"Technical Structure: {trend} (Price {'Above' if trend == 'Bullish' else 'Below'} MA200)")
    else:
        st.session_state.results["price_vs_ma"] = "Error"
        add_log("Quant", "Failed to fetch market data.")
        
    # 3. Risk Agent
    with placeholder.container():
        st.info("🌍 Risk Agent: Scanning Geopolitical Wires...")
    time.sleep(1.5)
    risk = fetch_risk_level_sim()
    st.session_state.results["risk_level"] = risk
    add_log("Risk", f"Geopolitical Threat Level: {risk}")
    
    # Completion
    st.session_state.agent_state = "COMPLETE"
    st.rerun()


# ─── DASHBOARD ───────────────────────────────────────────────────────────────

col_viz, col_console = st.columns([1.5, 2])

with col_viz:
    st.markdown("#### 🧭 Aggregate Confidence")
    
    # Calculate Confidence Logic
    res = st.session_state.results
    
    # Normalize inputs to 0-100
    # Hawk: -10 to +10 -> Map to 0-100
    s1 = max(0, min(100, (res["hawk_score"] + 10) * 5))
    
    s2 = 100 if res["price_vs_ma"] == "Bullish" else 0
    
    s3 = 100 if "Low" in res["risk_level"] else 50 if "Medium" in res["risk_level"] else 0
    
    confidence = (s1 + s2 + s3) / 3
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = confidence,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Bullish Conviction"},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "#00d4aa"},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "#333",
            'steps': [
                {'range': [0, 30], 'color': 'rgba(255, 75, 75, 0.3)'},
                {'range': [30, 70], 'color': 'rgba(255, 255, 0, 0.3)'},
                {'range': [70, 100], 'color': 'rgba(0, 212, 170, 0.3)'}],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': confidence
            }
        }
    ))
    fig.update_layout(height=350, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
    st.plotly_chart(fig, use_container_width=True)
    
    # KILL SWITCH LOGIC
    # Kill if: (Hawk < -2) AND (Price < MA200) -> Consensus High Risk
    is_hawkish = res["hawk_score"] < -2
    is_bearish_trend = res["price_vs_ma"] == "Bearish"
    is_high_risk = "High" in res["risk_level"]
    
    kill_switch = (is_hawkish and is_bearish_trend) or is_high_risk
    
    st.markdown("---")
    st.markdown("#### 🚦 Trade Execution Protocol")
    
    if kill_switch:
        st.error("⛔ KILL SWITCH ACTIVATED")
        reason = []
        if is_hawkish: reason.append("Hawkish Fed")
        if is_bearish_trend: reason.append("Bearish Trend")
        if is_high_risk: reason.append("Geopolitical Instability")
        
        st.caption(f"Consensus: HIGH RISK ({', '.join(reason)})")
        
        st.button("EXECUTE LONG TRADE", disabled=True, key="btn_exec_disabled")
    else:
        st.success("✅ SYSTEM OPERATIONAL")
        st.caption("Consensus: Conditions Favorable for Deployment")
        if st.button("⚡ EXECUTE LONG TRADE", type="primary"):
            st.toast("🚀 Order Sent to Broker API!", icon="✅")

with col_console:
    st.markdown("#### 📟 Live Agent Transcript")
    
    # Render Console
    log_html = '<div class="console-box">'
    if not st.session_state.logs:
        log_html += '<div style="color:#666; font-style:italic;">System Initialized. Awaiting manual trigger...</div>'
    else:
        for log in st.session_state.logs[::-1]: # Newest top
            color = "#00d4aa" if log['agent'] == "Analyst" else "#f2a900" if log['agent'] == "Quant" else "#ff4b4b"
            icon = "🕵️" if log['agent'] == "Analyst" else "🧮" if log['agent'] == "Quant" else "🌍"
            
            log_html += f"""
            <div class="log-entry">
                <span style="color:#666">[{log['time']}]</span> 
                <span style="color:{color}">{icon} {log['agent']}:</span> 
                {log['msg']}
            </div>
            """
    log_html += '</div>'
    
    st.markdown(log_html, unsafe_allow_html=True)
