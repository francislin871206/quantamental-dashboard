
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from datetime import datetime
import random

# ─── AGENT LOGIC ─────────────────────────────────────────────────────────────

def run_analyst(ticker):
    """Simulates Analyst Agent: Scrapes 10-K and FOMC."""
    time.sleep(1.5) # Simulate browsing
    
    # Mock data for demonstration
    base_sentiment = random.uniform(2, 9)
    if ticker in ["TSLA", "NVDA", "AMD"]: base_sentiment += 1
    
    return {
        "agent": "ANALYST",
        "status": "Success",
        "score": min(10, max(0, base_sentiment)),
        "output": f"Analyzed latest 10-K for ${ticker}. Revenue growth robust (+15% YoY). FOMC minutes suggest 'neutral-dovish' pivot.",
        "quotes": [
            "\"Steady expansion in core operating margins...\"", 
            "\"AI-driven demand remains a primary tailwind...\"",
            "\"Fed Governor Waller: 'No rush to hike further.'\""
        ]
    }

def run_quant(ticker):
    """Simulates Quant Agent: Calculates RSI, SMA, Volatility."""
    time.sleep(1.5)
    
    # Random metrics
    rsi = random.randint(30, 80)
    sma_diff = random.uniform(-5, 10)
    volatility = random.uniform(10, 35)
    
    score = 5
    if rsi > 50: score += 1
    if sma_diff > 0: score += 2
    if volatility < 20: score += 1
    
    return {
        "agent": "QUANT",
        "status": "Success",
        "score": score,
        "metrics": {
            "RSI (14)": f"{rsi}",
            "200d SMA": f"{'+' if sma_diff>0 else ''}{sma_diff:.1f}% vs Price",
            "Implied Vol": f"{volatility:.1f}%"
        },
        "output": f"RSI is {rsi}. Price is {abs(sma_diff):.1f}% {'above' if sma_diff>0 else 'below'} the 200-day moving average."
    }

def run_risk_guardian(analyst_score, quant_score):
    """Simulates Risk Agent: Adversarial check."""
    time.sleep(1.5)
    
    risk_level = random.choice(["Low", "Medium", "Critical"])
    risk_score = 10 if risk_level == "Low" else 5 if risk_level == "Medium" else 0
    
    adversarial_note = "None."
    if risk_level == "Critical":
        adversarial_note = "Yield Curve Inversion (2s10s) creates recession risk that negates bullish technicals."
    elif risk_level == "Medium":
        adversarial_note = "upcoming CPI print introduces binary event risk."
        
    return {
        "agent": "RISK GUARDIAN",
        "status": "Warning" if risk_level != "Low" else "Clean",
        "score": risk_score, # High score = Low Risk
        "risk_level": risk_level,
        "output": f"Risk Level: {risk_level}. Check: {adversarial_note}"
    }

# ─── UI RENDERER ─────────────────────────────────────────────────────────────

def render_terminal():
    # ─── CSS PRO MAX ─────────────────────────────────────────────────────────
    st.markdown("""
    <style>
        /* Midnight Emerald Theme */
        .stApp {
            background-color: #050505 !important;
            color: #e0e0e0;
        }
        
        /* Neon Colors */
        :root {
            --neon-green: #A3FF12;
            --neon-blue: #00F3FF;
            --neon-red: #FF0055;
            --glass-bg: rgba(20, 20, 30, 0.8);
        }
        
        /* Marquee */
        .marquee-container {
            width: 100%;
            overflow: hidden;
            background: #111;
            border-bottom: 1px solid #333;
            white-space: nowrap;
            padding: 5px 0;
            margin-bottom: 20px;
        }
        .marquee-content {
            display: inline-block;
            animation: marquee 20s linear infinite;
            color: var(--neon-green);
            font-family: 'Courier New', monospace;
            font-weight: bold;
        }
        @keyframes marquee {
            0% { transform: translateX(100%); }
            100% { transform: translateX(-100%); }
        }
        
        /* Live Clock & Heartbeat */
        .system-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .heartbeat {
            width: 10px;
            height: 10px;
            background-color: var(--neon-green);
            border-radius: 50%;
            display: inline-block;
            animation: pulse 1s infinite;
            margin-right: 10px;
        }
        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(163, 255, 18, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(163, 255, 18, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(163, 255, 18, 0); }
        }
        
        /* Terminal Console */
        .terminal-window {
            background-color: #0a0a0a;
            border: 1px solid #333;
            border-radius: 5px;
            padding: 15px;
            font-family: 'Courier New', monospace;
            color: #ccc;
            height: 400px;
            overflow-y: auto;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
        }
        .term-line { margin-bottom: 8px; border-bottom: 1px solid #1a1a1a; padding-bottom: 4px; }
        .term-time { color: #666; margin-right: 10px; }
        .term-agent { font-weight: bold; margin-right: 10px; }
        .agent-analyst { color: var(--neon-blue); }
        .agent-quant { color: #ffbd2e; }
        .agent-risk { color: var(--neon-red); }
        
        /* Gauge Container */
        .gauge-container {
            background: var(--glass-bg);
            border: 1px solid #333;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 0 30px rgba(0,243,255,0.05);
        }
        
    </style>
    """, unsafe_allow_html=True)

    # ─── STATE INITIALIZATION ────────────────────────────────────────────────
    if "term_state" not in st.session_state:
        st.session_state.term_state = "IDLE" # IDLE, RUNNING, DONE
    if "term_logs" not in st.session_state:
        st.session_state.term_logs = []
    if "term_ticker" not in st.session_state:
        st.session_state.term_ticker = "SPY"
    if "term_confidence" not in st.session_state:
        st.session_state.term_confidence = 0
    if "term_risk_score" not in st.session_state:
        st.session_state.term_risk_score = 0 # 0-10 (10 is safe)

    # ─── HEADER ──────────────────────────────────────────────────────────────
    
    # Marquee
    st.markdown(f"""
    <div class="marquee-container">
        <div class="marquee-content">
            LIVE: SPY $502.45 (+0.12%) | QQQ $428.90 (-0.05%) | VIX 13.45 (-1.2%) | 
            FED WATCH: 25bps cut probability 65% | 
            OIL $78.50 | GOLD $2035.10 | 
            SYSTEM STATUS: OPERATIONAL
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # System Header
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(f"""
        <div class="system-header">
            <h1 style="margin:0; font-size:2rem; color:#fff;">
                <span class="heartbeat"></span>AGENTIC TRADING TERMINAL <span style="color:#A3FF12; font-size:1rem;">PRO</span>
            </h1>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.caption(f"SERVER TIME: {datetime.utcnow().strftime('%H:%M:%S UTC')}")
        st.caption("LATENCY: 12ms")

    # ─── MAIN DOCK ───────────────────────────────────────────────────────────
    
    col_ctrl, col_main, col_logs = st.columns([1, 2, 2])
    
    # --- 1. CONTROL DOCK ---
    with col_ctrl:
        st.markdown("### 🎛️ COMMAND")
        with st.container(border=True):
            ticker_input = st.text_input("TICKER SYMBOL", value=st.session_state.term_ticker)
            if ticker_input != st.session_state.term_ticker:
                st.session_state.term_ticker = ticker_input
            
            st.markdown("---")
            
            # Buttons
            if st.session_state.term_state == "IDLE":
                if st.button("🚀 INITIALIZE SCAN", type="primary", use_container_width=True):
                    st.session_state.term_state = "RUNNING"
                    st.session_state.term_logs = []
                    st.rerun()
            elif st.session_state.term_state == "RUNNING":
                st.button("⚙️ PROCESSING...", disabled=True, use_container_width=True)
            else:
                if st.button("🔄 RE-SCAN", type="primary", use_container_width=True):
                    st.session_state.term_state = "RUNNING"
                    st.session_state.term_logs = []
                    st.rerun()
            
            if st.button("⛔ EMERGENCY STOP", use_container_width=True):
                st.session_state.term_state = "IDLE"
                st.rerun()

    # --- 2. LOGIC ENGINE (Hidden State Machine) ---
    if st.session_state.term_state == "RUNNING":
        # ANALYST
        with st.spinner("Analyst Agent fetching 10-K..."):
            res_analyst = run_analyst(st.session_state.term_ticker)
            st.session_state.term_logs.insert(0, res_analyst)
            time.sleep(0.5)
        
        # QUANT
        with st.spinner("Quant Agent calculating Volatility..."):
            res_quant = run_quant(st.session_state.term_ticker)
            st.session_state.term_logs.insert(0, res_quant)
            time.sleep(0.5)
            
        # RISK
        with st.spinner("Risk Guardian simulating Adversarial scenarios..."):
            res_risk = run_risk_guardian(res_analyst['score'], res_quant['score'])
            st.session_state.term_logs.insert(0, res_risk)
            time.sleep(0.5)
            
        # Calculate Consensus
        # Confidence % = (Analyst/10 + Quant/10) / 2 * 100
        # Multiplied by Risk Factor (0.0 if Critical, 0.5 Medium, 1.0 Low) ?? 
        # User requested separate Logic Gate.
        
        raw_conf = (res_analyst['score'] + res_quant['score']) / 20 * 100
        st.session_state.term_confidence = raw_conf
        st.session_state.term_risk_score = res_risk['score'] # 0, 5, 10
        
        st.session_state.term_state = "DONE"
        st.rerun()

    # --- 3. CENTERPIECE (Gauge & Action) ---
    with col_main:
        # Gauge
        conf_val = st.session_state.term_confidence
        risk_val = st.session_state.term_risk_score # 0, 5, 10. We want Risk% < 30%. 
        # Map Risk Score (0-10) to Risk % (100-0). 10(Safe) -> 0% Risk. 0(Bad) -> 100% Risk.
        risk_pct = (10 - risk_val) * 10
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = conf_val,
            title = {'text': "GLOBAL CONFIDENCE", 'font': {'size': 20, 'color': '#A3FF12'}},
            number = {'suffix': "%", 'font': {'color': 'white'}},
            gauge = {
                'axis': {'range': [0, 100], 'tickcolor': "white"},
                'bar': {'color': "#A3FF12"},
                'bgcolor': "rgba(0,0,0,0)",
                'steps': [
                    {'range': [0, 50], 'color': '#333'},
                    {'range': [50, 75], 'color': '#444'},
                    {'range': [75, 100], 'color': '#555'}
                ]
            }
        ))
        fig.update_layout(height=250, margin=dict(l=30, r=30, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)")
        
        st.markdown('<div class="gauge-container">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Smart Execute Button Logic
        # Enable if Confidence > 75% AND Risk < 30%
        can_execute = (conf_val > 75) and (risk_pct < 30.0)
        
        st.markdown("### 🚀 EXECUTION GATE")
        if can_execute:
            st.success("✅ GATES OPEN: ALPHA DETECTED")
            st.button("⚡ SMART EXECUTE (ALGO)", type="primary", use_container_width=True)
        else:
            st.warning("🔒 SAFETY INTERLOCK ENGAGED")
            reasons = []
            if conf_val <= 75: reasons.append(f"Confidence too low ({conf_val:.1f}% < 75%)")
            if risk_pct >= 30: reasons.append(f"Risk too high ({risk_pct}% > 30%)")
            
            for r in reasons:
                st.caption(f"❌ {r}")
                
            st.button("🚫 BLOCKED BY SENTINEL", disabled=True, use_container_width=True)

    # --- 4. LIVE CONSOLE ---
    with col_logs:
        st.markdown("### 📟 SYSTEM LOGS")
        
        log_html = '<div class="terminal-window">'
        if not st.session_state.term_logs:
            log_html += '<div style="color:#555">System Idle. Waiting for trigger...</div>'
        else:
            for log in st.session_state.term_logs:
                # Log structure: {time, agent, msg, output...}
                agent_class = f"agent-{log['agent'].split()[0].lower()}" # agent-analyst
                
                log_html += f"""
                <div class="term-line">
                    <span class="term-time">[{datetime.now().strftime('%H:%M:%S')}]</span>
                    <span class="term-agent {agent_class}">{log['agent']}:</span>
                    {log.get('output', 'Processing...')}
                </div>
                """
                # If there are sub-details
                if 'quotes' in log:
                    for q in log['quotes']:
                        log_html += f"<div style='color:#888; margin-left:20px;'>&gt; {q}</div>"
                if 'metrics' in log:
                    for k,v in log['metrics'].items():
                        log_html += f"<div style='color:#ccc; margin-left:20px;'>• {k}: <span style='color:#A3FF12'>{v}</span></div>"
                        
        log_html += '</div>'
        st.markdown(log_html, unsafe_allow_html=True)

