"""
Revolution Stock Selector Dashboard
A Streamlit dashboard implementing the Sentiment + Catalyst Convergence strategy
to identify 3 US stocks with explosive short-term growth potential.
"""

import sys
import os

print("🚀 STARTING APP.PY (TOP)...", flush=True)

print("📦 Importing streamlit...", flush=True)
import streamlit as st
print("📦 Importing pandas...", flush=True)
import pandas as pd
print("📦 Importing numpy...", flush=True)
import numpy as np
print("📦 Importing plotly...", flush=True)
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

print("🚀 STARTING APP.PY (AFTER IMPORTS)...", flush=True)

# Add current directory AND 'Competition' subdirectory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, "Competition"))
print(f"📂 Added to path: {sys.path}", flush=True)

# ─── NLTK Setup (MUST BE FIRST) ──────────────────────────────────────────────
print("🔧 Initializing NLTK...", flush=True)
import nltk
try:
    nltk.data.find('tokenizers/punkt')
    print("✅ Found punkt", flush=True)
except LookupError:
    print("⬇️ Downloading punkt...", flush=True)
    nltk.download('punkt')
try:
    nltk.data.find('tokenizers/punkt_tab')
    print("✅ Found punkt_tab", flush=True)
except LookupError:
    try:
        print("⬇️ Downloading punkt_tab...", flush=True)
        nltk.download('punkt_tab')
    except Exception as e:
        print(f"⚠️ Failed punkt_tab: {e}", flush=True)

print("📦 Importing custom modules...", flush=True)


# ─── Custom Imports ──────────────────────────────────────────────────────────
try:
    from config import SECTOR_MAP, DEFAULT_WEIGHTS, COLORS, PLOTLY_TEMPLATE, FULL_US_UNIVERSE
    print("✅ Imported config", flush=True)
    from data_engine import analyze_ticker, fetch_price_data, generate_market_summary
    print("✅ Imported data_engine", flush=True)
    from scoring import rank_candidates, get_top_picks, format_market_cap, compute_composite_score
    print("✅ Imported scoring", flush=True)
except Exception as e:
    print(f"❌ IMPORT ERROR: {e}", flush=True)
    raise e

print("🎨 Setting page config...", flush=True)
# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Revolution Stock Selector",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)
print("✅ Page config set!", flush=True)


# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* Global */
    .stApp {
        background: linear-gradient(135deg, #0a0a1a 0%, #0d0d2b 50%, #0a0a1a 100%);
        font-family: 'Inter', sans-serif;
    }

    /* Hide default header */
    header[data-testid="stHeader"] {
        background: transparent;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111128 0%, #0d0d2b 100%);
        border-right: 1px solid #222255;
    }

    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #e8e8f0;
    }

    /* Hero header */
    .hero-header {
        background: linear-gradient(135deg, #1a1a3e 0%, #2d1b69 50%, #1a1a3e 100%);
        border: 1px solid rgba(108, 99, 255, 0.3);
        border-radius: 16px;
        padding: 30px 40px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .hero-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(108,99,255,0.15) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero-header h1 {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6c63ff, #00d4aa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .hero-header p {
        color: #8888aa;
        font-size: 1rem;
        margin-top: 8px;
    }

    /* Score cards */
    .score-card {
        background: linear-gradient(135deg, #1a1a3e, #222255);
        border: 1px solid rgba(108, 99, 255, 0.2);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .score-card:hover {
        border-color: rgba(108, 99, 255, 0.5);
        transform: translateY(-2px);
    }
    .score-card .value {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6c63ff, #00d4aa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .score-card .label {
        color: #8888aa;
        font-size: 0.85rem;
        margin-top: 4px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Ticker chip */
    .ticker-chip {
        display: inline-block;
        background: linear-gradient(135deg, #6c63ff, #8b5cf6);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
        margin: 2px;
    }

    /* Rank badge */
    .rank-1 { color: #ffd700; font-weight: 800; font-size: 1.2rem; }
    .rank-2 { color: #c0c0c0; font-weight: 700; font-size: 1.1rem; }
    .rank-3 { color: #cd7f32; font-weight: 700; font-size: 1.0rem; }

    /* Metric styling */
    [data-testid="stMetricValue"] {
        color: #e8e8f0;
    }
    [data-testid="stMetricDelta"] > div {
        font-weight: 600;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #111128;
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #8888aa;
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6c63ff, #8b5cf6);
        color: white;
    }

    /* DataFrames */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Divider */
    hr {
        border-color: #222255;
    }

    /* Button */
    .stButton > button {
        background: linear-gradient(135deg, #6c63ff, #8b5cf6);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        padding: 10px 24px;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #5a52e0, #7c4dff);
        box-shadow: 0 4px 20px rgba(108, 99, 255, 0.4);
    }
</style>
""", unsafe_allow_html=True)


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚀 Revolution Selector")
    
    # Navigation
    page = st.radio("📍 Navigation", ["Dashboard", "💼 Portfolio Monitor"])
    st.markdown("---")

    if page == "Dashboard":
        # Sector selection
        st.markdown("### 📊 Stock Universe")
        sector = st.selectbox("Select Sector", list(SECTOR_MAP.keys()), index=4)
        preset_tickers = SECTOR_MAP[sector]

        # Custom ticker input
        custom_tickers = st.text_input(
            "Add Custom Tickers (comma-separated)",
            placeholder="e.g. TSLA, NVDA, AMD"
        )

        # Combine tickers
        tickers = list(preset_tickers)
        if custom_tickers:
            extras = [t.strip().upper() for t in custom_tickers.split(",") if t.strip()]
            tickers = list(set(tickers + extras))

        st.markdown(f"**Analyzing {len(tickers)} stocks**")

        st.markdown("---")

        # Scoring weights
        st.markdown("### ⚖️ Factor Weights")
        w_sentiment = st.slider("📰 News Sentiment", 0, 100, 30, 5, help="Weight for news headline sentiment analysis")
        w_catalyst = st.slider("🎯 Catalyst Proximity", 0, 100, 25, 5, help="Weight for proximity to earnings/events")
        w_insider = st.slider("👤 Insider Buying", 0, 100, 15, 5, help="Weight for insider trading activity")
        w_options = st.slider("📊 Options Flow", 0, 100, 15, 5, help="Weight for put/call ratio sentiment")
        w_technical = st.slider("📈 Technical Setup", 0, 100, 15, 5, help="Weight for SMA/RSI technical indicators")

        total_w = w_sentiment + w_catalyst + w_insider + w_options + w_technical
        if total_w > 0:
            weights = {
                "sentiment": w_sentiment / total_w,
                "catalyst": w_catalyst / total_w,
                "insider": w_insider / total_w,
                "options": w_options / total_w,
                "technical": w_technical / total_w,
            }
        else:
            weights = DEFAULT_WEIGHTS

        st.markdown(f"*Total: {total_w}% → Normalized to 100%*")

        st.markdown("---")

        # Top N selection
        top_n = st.slider("🏆 Number of Picks", 1, 5, 3)

        # Analyze button
        analyze_btn = st.button("🔍 Analyze Selected", use_container_width=True, type="primary")
        
        st.markdown("---")
        
        # Auto-Select Top 10 Button
        auto_select_btn = st.button("✨ Auto-Select Top 10", use_container_width=True, help="Scan 100+ stocks and find the absolute best")

    else:
        # Portfolio Sidebar - Keep it clean
        from portfolio_config import PORTFOLIO_HOLDINGS
        st.markdown(f"**Tracking {len(PORTFOLIO_HOLDINGS)} Holdings**")
        
        # Calculate Quick Total
        # (This is just a sidebar preview, detailed logic is in main panel)
        
        st.info("Strategy: ATR Trailing Stops + Sentiment Monitoring")
        
        # Recommendation Logic Button
        find_opps_btn = st.button("🔎 Scan for Better Opportunities", type="primary", use_container_width=True)
        
        # Define these as False so Main Logic doesn't break
        analyze_btn = False
        auto_select_btn = False
        weights = DEFAULT_WEIGHTS
        top_n = 3


# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <h1>🚀 Revolution Stock Selector</h1>
    <p>Sentiment + Catalyst Convergence Strategy · Identify high-potential stocks for explosive short-term growth</p>
</div>
""", unsafe_allow_html=True)


# ─── Main Logic ───────────────────────────────────────────────────────────────

if page == "Dashboard":
    if analyze_btn or auto_select_btn or "analyses" in st.session_state:
        # Run analysis
        if analyze_btn:
            analyses = []
            progress = st.progress(0, text="Analyzing stocks...")
            for i, ticker in enumerate(tickers):
                progress.progress((i + 1) / len(tickers), text=f"Analyzing {ticker}... ({i+1}/{len(tickers)})")
                result = analyze_ticker(ticker)
                analyses.append(result)

            st.session_state["analyses"] = analyses
            progress.empty()

        # Auto-Select Logic
        if auto_select_btn:
            analyses = []
            target_universe = FULL_US_UNIVERSE
            progress = st.progress(0, text="Scanning full US universe (120+ stocks)...")
            
            # Batch processing to show progress
            total = len(target_universe)
            for i, ticker in enumerate(target_universe):
                progress.progress((i + 1) / total, text=f"Scanning {ticker}... ({i+1}/{total})")
                result = analyze_ticker(ticker)
                analyses.append(result)
                
            st.session_state["analyses"] = analyses
            progress.empty()
            
            # Set top_n to 10 automatically
            top_n = 10
            st.toast("✅ Auto-Select Complete! Showing Top 10 Revolution Stocks")

        analyses = st.session_state["analyses"]

        # Compute rankings
        ranked_df = rank_candidates(analyses, weights)
        
        # If using Auto-Select, force top 10
        display_top_n = top_n
        if "auto_select" in st.session_state or auto_select_btn: # Better flag check needed ideally but auto_select_btn works for immediate
             if auto_select_btn: display_top_n = 10
            
        top_picks_df = get_top_picks(ranked_df, display_top_n)

        # ─── Market Summary (Auto-Select Only) ──────────────────────────────
        if auto_select_btn or (len(analyses) > 50):
            st.markdown("### 📝 AI Market Pulse")
            summary_text = generate_market_summary(top_picks_df.to_dict("records"))
            st.info(summary_text, icon="🤖")
            st.markdown("---")

        # ─── Summary Metrics ─────────────────────────────────────────────────
        cols = st.columns(4)
        with cols[0]:
            st.markdown(f"""
            <div class="score-card">
                <div class="value">{len(analyses)}</div>
                <div class="label">Stocks Analyzed</div>
            </div>
            """, unsafe_allow_html=True)
        with cols[1]:
            avg_score = ranked_df["Composite"].mean()
            st.markdown(f"""
            <div class="score-card">
                <div class="value">{avg_score:.1f}</div>
                <div class="label">Avg Composite Score</div>
            </div>
            """, unsafe_allow_html=True)
        with cols[2]:
            top_score = ranked_df["Composite"].max()
            st.markdown(f"""
            <div class="score-card">
                <div class="value">{top_score:.1f}</div>
                <div class="label">Top Score</div>
            </div>
            """, unsafe_allow_html=True)
        with cols[3]:
            top_ticker = ranked_df.iloc[0]["Ticker"]
            st.markdown(f"""
            <div class="score-card">
                <div class="value">{top_ticker}</div>
                <div class="label">Top Pick</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ─── Tabs ─────────────────────────────────────────────────────────────
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 Screener & Rankings",
            "📰 Sentiment Analysis",
            "📈 Technical Setup",
            "🏆 Final Picks",
            "🛡️ Risk Monitor",
        ])

        # ─── TAB 1: Screener ──────────────────────────────────────────────────
        with tab1:
            st.markdown("### 📋 Stock Rankings")
            st.markdown("All candidates scored and ranked by composite score. Higher is better.")

            # Format display DataFrame
            display_df = ranked_df.copy()
            display_df["Market Cap"] = display_df["Market Cap"].apply(format_market_cap)
            try:
                display_df["P/E"] = display_df["P/E"].apply(lambda x: f"{x:.1f}" if pd.notna(x) and x else "N/A")
            except:
                pass

            st.dataframe(
                display_df,
                use_container_width=True,
                height=min(400, 40 * len(display_df) + 40),
                column_config={
                    "Composite": st.column_config.ProgressColumn(
                        "Composite Score",
                        min_value=0,
                        max_value=10,
                        format="%.1f",
                    ),
                    "Sentiment": st.column_config.ProgressColumn(
                        "Sentiment",
                        min_value=0,
                        max_value=10,
                        format="%.1f",
                    ),
                    "Catalyst": st.column_config.ProgressColumn(
                        "Catalyst",
                        min_value=0,
                        max_value=10,
                        format="%.1f",
                    ),
                    "Insider": st.column_config.ProgressColumn(
                        "Insider",
                        min_value=0,
                        max_value=10,
                        format="%.1f",
                    ),
                    "Options": st.column_config.ProgressColumn(
                        "Options",
                        min_value=0,
                        max_value=10,
                        format="%.1f",
                    ),
                    "Technical": st.column_config.ProgressColumn(
                        "Technical",
                        min_value=0,
                        max_value=10,
                        format="%.1f",
                    ),
                },
            )

            # Score Distribution Chart
            st.markdown("### 📊 Score Distribution")
            fig_dist = go.Figure()

            factors = ["Sentiment", "Catalyst", "Insider", "Options", "Technical"]
            colors_list = [COLORS["accent_1"], COLORS["accent_2"], COLORS["accent_3"],
                           COLORS["accent_4"], "#a78bfa"]

            for i, factor in enumerate(factors):
                fig_dist.add_trace(go.Bar(
                    name=factor,
                    x=ranked_df["Ticker"],
                    y=ranked_df[factor],
                    marker_color=colors_list[i],
                    opacity=0.85,
                ))

            fig_dist.update_layout(
                barmode="group",
                paper_bgcolor=COLORS["bg_primary"],
                plot_bgcolor=COLORS["bg_secondary"],
                font=dict(color=COLORS["text_primary"], family="Inter"),
                xaxis=dict(gridcolor="#222244"),
                yaxis=dict(gridcolor="#222244", title="Score (0-10)"),
                legend=dict(orientation="h", y=-0.15),
                height=400,
                margin=dict(t=20, b=60),
            )
            st.plotly_chart(fig_dist, use_container_width=True)

        # ─── TAB 2: Sentiment ─────────────────────────────────────────────────
        with tab2:
            st.markdown("### 📰 News Sentiment Analysis")

            # Sentiment overview bar chart
            sent_data = []
            for a in analyses:
                sent_data.append({
                    "Ticker": a["ticker"],
                    "Avg Sentiment": a["sentiment_data"]["avg_sentiment"],
                    "Positive %": a["sentiment_data"]["positive_pct"],
                    "Headlines": a["sentiment_data"]["count"],
                })
            sent_df = pd.DataFrame(sent_data).sort_values("Avg Sentiment", ascending=True)

            fig_sent = go.Figure()
            colors_sent = [COLORS["positive"] if v > 0.05 else
                           (COLORS["negative"] if v < -0.05 else COLORS["neutral"])
                           for v in sent_df["Avg Sentiment"]]

            fig_sent.add_trace(go.Bar(
                x=sent_df["Avg Sentiment"],
                y=sent_df["Ticker"],
                orientation="h",
                marker_color=colors_sent,
                text=sent_df["Avg Sentiment"].apply(lambda x: f"{x:.3f}"),
                textposition="outside",
            ))
            fig_sent.update_layout(
                paper_bgcolor=COLORS["bg_primary"],
                plot_bgcolor=COLORS["bg_secondary"],
                font=dict(color=COLORS["text_primary"], family="Inter"),
                xaxis=dict(title="Sentiment Polarity (-1 to +1)", gridcolor="#222244",
                           zeroline=True, zerolinecolor="#444466"),
                yaxis=dict(gridcolor="#222244"),
                height=max(300, len(analyses) * 35),
                margin=dict(t=20, l=80, r=80),
            )
            st.plotly_chart(fig_sent, use_container_width=True)

            # Detailed headlines per ticker
            st.markdown("### 📝 Recent Headlines")
            selected_ticker = st.selectbox(
                "Select ticker to view headlines",
                [a["ticker"] for a in analyses],
            )

            for a in analyses:
                if a["ticker"] == selected_ticker:
                    headlines = a["sentiment_data"]["headlines"]
                    if headlines:
                        for h in headlines[:15]:
                            sentiment = h["sentiment"]
                            icon = "🟢" if sentiment > 0.05 else ("🔴" if sentiment < -0.05 else "⚪")
                            st.markdown(f"{icon} **{sentiment:+.3f}** — {h['headline']}")
                    else:
                        st.info("No headlines found for this ticker.")
                    break

        # ─── TAB 3: Technical ─────────────────────────────────────────────────
        with tab3:
            st.markdown("### 📈 Technical Analysis")

            tech_ticker = st.selectbox(
                "Select ticker for technical analysis",
                [a["ticker"] for a in analyses],
                key="tech_select",
            )

            for a in analyses:
                if a["ticker"] == tech_ticker:
                    tech = a["technical_data"]
                    price_df = a["price_data"]

                    # Tech summary
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Current Price", f"${tech.get('price', 0):.2f}")
                    with col2:
                        rsi = tech.get('rsi', 50)
                        st.metric("RSI (14)", f"{rsi:.1f}",
                                  delta="Overbought" if rsi > 70 else ("Oversold" if rsi < 30 else "Normal"))
                    with col3:
                        st.metric("50-day SMA", f"${tech.get('sma_50', 0):.2f}")
                    with col4:
                        signal_color = "🟢" if tech["signal"] == "Bullish" else ("🔴" if tech["signal"] == "Bearish" else "⚪")
                        st.metric("Signal", f"{signal_color} {tech['signal']}")

                    # Price chart with SMAs
                    if not price_df.empty and len(price_df) > 20:
                        fig_price = make_subplots(
                            rows=2, cols=1,
                            shared_xaxes=True,
                            vertical_spacing=0.05,
                            row_heights=[0.7, 0.3],
                            subplot_titles=("Price & Moving Averages", "Volume"),
                        )

                        # Candlestick
                        fig_price.add_trace(go.Candlestick(
                            x=price_df.index,
                            open=price_df["Open"],
                            high=price_df["High"],
                            low=price_df["Low"],
                            close=price_df["Close"],
                            name="Price",
                            increasing_line_color=COLORS["positive"],
                            decreasing_line_color=COLORS["negative"],
                        ), row=1, col=1)

                        # SMA 50
                        sma50 = price_df["Close"].rolling(50).mean()
                        fig_price.add_trace(go.Scatter(
                            x=price_df.index, y=sma50,
                            name="SMA 50",
                            line=dict(color=COLORS["accent_1"], width=2),
                        ), row=1, col=1)

                        # SMA 200
                        if len(price_df) >= 200:
                            sma200 = price_df["Close"].rolling(200).mean()
                            fig_price.add_trace(go.Scatter(
                                x=price_df.index, y=sma200,
                                name="SMA 200",
                                line=dict(color=COLORS["accent_3"], width=2),
                            ), row=1, col=1)

                        # Volume
                        vol_colors = [COLORS["positive"] if price_df["Close"].iloc[i] >= price_df["Open"].iloc[i]
                                      else COLORS["negative"] for i in range(len(price_df))]
                        fig_price.add_trace(go.Bar(
                            x=price_df.index, y=price_df["Volume"],
                            name="Volume",
                            marker_color=vol_colors,
                            opacity=0.5,
                        ), row=2, col=1)

                        fig_price.update_layout(
                            paper_bgcolor=COLORS["bg_primary"],
                            plot_bgcolor=COLORS["bg_secondary"],
                            font=dict(color=COLORS["text_primary"], family="Inter"),
                            xaxis=dict(gridcolor="#222244", rangeslider=dict(visible=False)),
                            xaxis2=dict(gridcolor="#222244"),
                            yaxis=dict(gridcolor="#222244"),
                            yaxis2=dict(gridcolor="#222244"),
                            height=600,
                            margin=dict(t=40),
                            showlegend=True,
                            legend=dict(orientation="h", y=1.02),
                        )
                        st.plotly_chart(fig_price, use_container_width=True)

                        # Technical indicators summary
                        st.markdown("#### Indicators Summary")
                        ind_cols = st.columns(3)
                        with ind_cols[0]:
                            above_sma = "✅ Above" if tech["above_sma50"] else "❌ Below"
                            st.info(f"**Price vs SMA-50:** {above_sma}")
                        with ind_cols[1]:
                            gc = "✅ Yes (Bullish)" if tech["golden_cross"] else "❌ No"
                            st.info(f"**Golden Cross:** {gc}")
                        with ind_cols[2]:
                            st.info(f"**Technical Score:** {tech['score']:.1f} / 10")

                    break

        # ─── TAB 4: Final Picks ───────────────────────────────────────────────
        with tab4:
            st.markdown("### 🏆 Your Revolution Picks")
            st.markdown(f"Top **{display_top_n}** stocks ranked by composite score")

            # Top picks cards - Grid Layout
            # Create rows of 4
            for i in range(0, min(display_top_n, len(top_picks_df)), 4):
                # Determine how many columns in this row (max 4)
                cols_count = min(4, min(display_top_n, len(top_picks_df)) - i)
                pick_cols = st.columns(4) # Always create 4 to keep size consistent, but use only cols_count

                for j in range(cols_count):
                    idx = i + j
                    if idx >= len(top_picks_df): break
                    
                    row = top_picks_df.iloc[idx]
                    medals = ["🥇", "🥈", "🥉"]
                    medal = medals[idx] if idx < 3 else f"#{idx+1}"

                    # Find matching analysis
                    matching = [a for a in analyses if a["ticker"] == row["Ticker"]]
                    
                    with pick_cols[j]:
                        st.markdown(f"""
                        <div class="score-card">
                            <div class="value">{medal} {row['Ticker']}</div>
                            <div class="label">{row['Company'][:20]}</div>
                            <hr style="border-color:#333366; margin:10px 0;">
                            <div style="font-size:1.5rem; font-weight:800; color:#00d4aa;">
                                {row['Composite']:.1f} <span style="font-size:0.8rem; color:#8888aa;">/10</span>
                            </div>
                            <div class="label">Composite Score</div>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown(f"""
                        | Factor | Score |
                        |--------|-------|
                        | 📰 Sent | **{row['Sentiment']:.1f}** |
                        | 🎯 Cat | **{row['Catalyst']:.1f}** |
                        | 👤 Ins | **{row['Insider']:.1f}** |
                        | 📊 Opt | **{row['Options']:.1f}** |
                        | 📈 Tech | **{row['Technical']:.1f}** |
                        """
                        )

                        # Volatility / Risk Section
                        vol = matching[0]["volatility_data"]
                        if vol["atr"] > 0:
                            st.markdown(f"""
                            <div style="background-color:rgba(108, 99, 255, 0.1); padding:10px; border-radius:8px; margin-top:10px;">
                                <div style="font-size:0.85rem; color:#e8e8f0; font-weight:700; margin-bottom:5px;">🛡️ Trade Setup (ATR Method)</div>
                                <div style="display:flex; justify-content:space-between; font-size:0.8rem;">
                                    <span style="color:#ff4b4b;">🛑 Stop: ${vol['stop_atr']}</span>
                                    <span style="color:#00d4aa;">🎯 Target: ${vol['profit_atr']}</span>
                                </div>
                                <div style="font-size:0.75rem; color:#8888aa; margin-top:4px;">
                                    ATR: ${vol['atr']} • σ15: ±{vol['sigma_15_pct']}%
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("---")

            # Radar chart comparison
            st.markdown("### 🕸️ Factor Comparison (Radar)")

            fig_radar = go.Figure()
            categories = ["Sentiment", "Catalyst", "Insider", "Options", "Technical"]
            radar_colors = [COLORS["accent_1"], COLORS["accent_2"], COLORS["accent_3"],
                            COLORS["accent_4"], "#a78bfa"]

            for i in range(min(top_n, len(top_picks_df))):
                row = top_picks_df.iloc[i]
                values = [row[c] for c in categories]
                values.append(values[0])  # close the polygon

                fig_radar.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories + [categories[0]],
                    fill="toself",
                    name=f"{row['Ticker']}",
                    line=dict(color=radar_colors[i % len(radar_colors)], width=2),
                    fillcolor=radar_colors[i % len(radar_colors)],
                    opacity=0.3,
                ))

            fig_radar.update_layout(
                polar=dict(
                    bgcolor=COLORS["bg_secondary"],
                    radialaxis=dict(
                        visible=True, range=[0, 10],
                        gridcolor="#333366",
                        linecolor="#333366",
                    ),
                    angularaxis=dict(
                        gridcolor="#333366",
                        linecolor="#333366",
                    ),
                ),
                paper_bgcolor=COLORS["bg_primary"],
                font=dict(color=COLORS["text_primary"], family="Inter"),
                height=500,
                margin=dict(t=40, b=40),
                showlegend=True,
                legend=dict(orientation="h", y=-0.1),
            )
            st.plotly_chart(fig_radar, use_container_width=True)

            # Final recommendation table
            st.markdown("### 📋 Final Recommendation")
            final_display = top_picks_df[["Ticker", "Company", "Sector", "Price",
                                           "Composite", "Sentiment", "Catalyst",
                                           "Technical"]].copy()
            st.dataframe(final_display, use_container_width=True)

            st.success(f"✅ **{top_n} Revolution picks selected!** "
                       f"Top choice: **{top_picks_df.iloc[0]['Ticker']}** "
                       f"with composite score **{top_picks_df.iloc[0]['Composite']:.1f}/10**")

        # ─── TAB 5: Risk Monitor ──────────────────────────────────────────────
        with tab5:
            st.markdown("### 🛡️ ATR Strategy Monitor")
            st.markdown("Real-time risk management levels based on volatility (14-day ATR).")

            # Build Risk DataFrame
            risk_data = []
            for a in analyses:
                vol = a["volatility_data"]
                if vol["atr"] > 0:
                    # Safety Check: Is ATR stop wider than statistical noise?
                    stop_dist_pct = (vol["price"] - vol["stop_atr"]) / vol["price"]
                    sigma_15 = vol["sigma_15_pct"] / 100
                    
                    # If Stop Distance > Sigma15, it's outside normal noise -> Safe
                    # If Stop Distance < Sigma15, it's inside normal noise -> Tight
                    is_safe = stop_dist_pct > sigma_15
                    safety_icon = "✅ Optimal" if is_safe else "⚠️ Tight"
                    
                    risk_data.append({
                        "Ticker": a["ticker"],
                        "Price": vol["price"],
                        "ATR ($)": vol["atr"],
                        "🛑 Stop (ATR)": vol["stop_atr"],
                        "Safety": safety_icon, 
                        "🎯 Target (ATR)": vol["profit_atr"],
                        "Reward/Risk": "2.0x",
                        "Sigma15": f"±{vol['sigma_15_pct']}%"
                    })
            
            risk_df = pd.DataFrame(risk_data)
            
            if not risk_df.empty:
                # Sort by Ticker or Risk %? Let's sort by Ticker for monitoring
                risk_df = risk_df.sort_values("Ticker")

                st.dataframe(
                    risk_df,
                    use_container_width=True,
                    height=min(500, 40 * len(risk_df) + 40),
                    column_config={
                        "Price": st.column_config.NumberColumn(format="$%.2f"),
                        "ATR ($)": st.column_config.NumberColumn(format="$%.2f"),
                        "🛑 Stop (ATR)": st.column_config.NumberColumn(format="$%.2f"),
                        "🎯 Target (ATR)": st.column_config.NumberColumn(format="$%.2f"),
                    },
                    hide_index=True
                )

                st.markdown("""
                > **🛡️ Stop Loss Decision Guide:**
                > * **✅ Optimal:** The ATR stop is **wider** than the 3-week statistical noise (Sigma15). This is a statistically sound stop.
                > * **⚠️ Tight:** The ATR stop is **inside** the expected volatility noise. consider placing your stop slightly wider (e.g., at `-1.0 x Sigma15`).
                """)
            else:
                st.info("No volatility data available. Run analysis first.")

    else:
        # Landing state
        st.markdown("---")

        col_left, col_right = st.columns([2, 1])
        with col_left:
            st.markdown("""
            ### 🎯 How It Works

            1. **Select a sector** or add custom tickers in the sidebar
            2. **Adjust factor weights** to match your investment thesis
            3. **Click "Analyze Stocks"** to run the full analysis pipeline
            4. **Review results** across 4 tabs: Screener, Sentiment, Technical, Final Picks

            ### 📊 Five-Factor Scoring Model

            | Factor | Default Weight | What It Measures |
            |--------|---------------|------------------|
            | 📰 News Sentiment | 30% | TextBlob polarity of FinViz headlines |
            | 🎯 Catalyst Proximity | 25% | Days until next earnings/event |
            | 👤 Insider Buying | 15% | Net insider purchase activity |
            | 📊 Options Flow | 15% | Put/call ratio sentiment |
            | 📈 Technical Setup | 15% | SMA crossover, RSI, breakout |
            """)

        with col_right:
            st.markdown("""
            ### 🏷️ Preset Sectors

            - 🤖 **AI & Technology**
            - 🧬 **Biotech & Healthcare**
            - 💳 **Fintech & Disruptive Finance**
            - ⚡ **Clean Energy & Tech**
            - 🌐 **All Sectors** (32 stocks)

            ### ⏱️ Timeline
            Designed for the **3-week** asset allocation competition.
            """)

elif page == "💼 Portfolio Monitor":
    st.markdown("## 💼 Portfolio Monitor & Action Center")
    
    # 1. Load Holdings & Define tickers (Fixes NameError)
    try:
        from portfolio_config import PORTFOLIO_HOLDINGS
    except ImportError:
        st.error("Configuration file not found.")
        st.stop()
        
    pf_tickers = [p["Ticker"] for p in PORTFOLIO_HOLDINGS]

    # 2. Run Analysis if needed
    if "portfolio_analyses" not in st.session_state:
        st.info("🔄 Running live analysis on your portfolio...")
        
        pf_analyses = []
        progress = st.progress(0, text="Analyzing portfolio...")
        for i, ticker in enumerate(pf_tickers):
            progress.progress((i + 1) / len(pf_tickers), text=f"Analyzing {ticker}...")
            # Use data_engine directly
            result = analyze_ticker(ticker)
            pf_analyses.append(result)
        progress.empty()
        st.session_state["portfolio_analyses"] = pf_analyses
        st.rerun()

    pf_analyses = st.session_state["portfolio_analyses"]
    
    # ─── Portfolio Metrics & Signals ──────────────────────────────────────────
    
    pf_data = []
    total_val = 0
    total_cost = 0
    
    for holding in PORTFOLIO_HOLDINGS:
        ticker = holding["Ticker"]
        # Find analysis
        analysis = next((a for a in pf_analyses if a["ticker"] == ticker), None)
        
        if analysis:
            curr_price = analysis["price"]
            vol = analysis["volatility_data"]
            tech = analysis["technical_data"]
            sentiment_score = analysis["sentiment_score"]
            
            # P&L
            mkt_val = curr_price * holding["Qty"]
            cost_val = holding["Avg_Cost"] * holding["Qty"]
            total_val += mkt_val
            total_cost += cost_val
            unrealized_pl = mkt_val - cost_val
            unrealized_pct = (unrealized_pl / cost_val) * 100
            
            # ATR Levels
            trailing_stop = curr_price - (2 * vol["atr"])
            hard_stop = holding["Avg_Cost"] - (2 * vol["atr"])
            
            # Action Logic
            action = "HOLD"
            reason = "Stable"
            
            if curr_price < hard_stop:
                action = "🛑 STOP LOSS"
                reason = "Price < Entry - 2ATR"
            elif sentiment_score < 4.0:
                action = "🔻 REDUCE"
                reason = "Sentiment Negative"
            elif tech["rsi"] > 75:
                action = "💰 TAKE PROFIT"
                reason = "RSI Overbought (>75)"
            elif sentiment_score > 7.5 and tech["signal"] == "Bullish":
                action = "🟢 ADD"
                reason = "High Sentiment + Bullish Tech"
            elif curr_price < trailing_stop:
                 action = "⚠️ WATCH"
                 reason = "Below Trailing Stop"
            
            pf_data.append({
                "Ticker": ticker,
                "Qty": holding["Qty"],
                "Avg Cost": holding["Avg_Cost"],
                "Price": curr_price,
                "P&L ($)": unrealized_pl,
                "P&L %": unrealized_pct,
                "ATR Stop": trailing_stop,
                "Action": action,
                "Reason": reason,
                "Score": sentiment_score
            })

    # Portfolio Summary Headers
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Value", f"${total_val:,.2f}", delta=f"${total_val-total_cost:,.2f}")
    with col2:
        tot_ret = ((total_val - total_cost) / total_cost) * 100 if total_cost > 0 else 0
        st.metric("Total Return", f"{tot_ret:.2f}%")
    with col3:
        st.metric("Holdings", len(pf_data))

    # Portfolio Table
    st.markdown("### 📊 Holdings Status")
    
    # Iterate through holdings to display detailed cards instead of just a table
    # This allows for the "Evidence" requested
    for holding in PORTFOLIO_HOLDINGS:
        ticker = holding["Ticker"]
        analysis = next((a for a in pf_analyses if a["ticker"] == ticker), None)
        p_dat = next((d for d in pf_data if d["Ticker"] == ticker), None)
        
        if not analysis or not p_dat: continue
        
        # Create a card for each stock
        with st.container():
            # Card Header
            c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1.5])
            c1.markdown(f"### {ticker}")
            c2.metric("Price", f"${p_dat['Price']:.2f}", f"{p_dat['P&L %']:.2f}%")
            
            # Action Badge
            act_color = "#8888aa"
            if "STOP" in p_dat["Action"]: act_color = "#ff4757"
            elif "ADD" in p_dat["Action"]: act_color = "#00d4aa"
            elif "TAKE" in p_dat["Action"]: act_color = "#ffa502"
            
            c3.markdown(f"""
            <div style="background-color:{act_color}; color:white; padding:5px 10px; border-radius:5px; text-align:center; font-weight:bold;">
                {p_dat['Action']}
            </div>
            """, unsafe_allow_html=True)
            
            c4.metric("ATR Stop", f"${p_dat['ATR Stop']:.2f}")
            c5.progress(min(1.0, max(0.0, analysis['composite_score'] if 'composite_score' in analysis else analysis['sentiment_score']/10)), text=f"AI Score: {analysis.get('composite_score', analysis['sentiment_score']):.1f}/10")
            
            # Expander for 5-Factor Evidence
            with st.expander(f"🔍 5-Factor Analysis & Evidence for {ticker}"):
                sc1, sc2, sc3, sc4, sc5 = st.columns(5)
                sc1.metric("📰 Sentiment (30%)", f"{analysis['sentiment_score']:.1f}")
                sc2.metric("🎯 Catalyst (25%)", f"{analysis['catalyst_score']:.1f}")
                sc3.metric("👤 Insider (15%)", f"{analysis['insider_score']:.1f}")
                sc4.metric("📊 Options (15%)", f"{analysis['options_score']:.1f}")
                sc5.metric("📈 Technical (15%)", f"{analysis['technical_score']:.1f}")
                
                st.markdown("---")
                e1, e2 = st.columns(2)
                
                with e1:
                    st.markdown("**📰 Top Headlines (Sentiment Evidence)**")
                    headlines = analysis["sentiment_data"]["headlines"]
                    if headlines:
                        for h in headlines[:3]:
                            s_icon = "🟢" if h['sentiment'] > 0 else ("🔴" if h['sentiment'] < 0 else "⚪")
                            st.markdown(f"- {s_icon} {h['headline']}")
                    else:
                        st.write("No recent headlines found.")
                        
                    st.markdown("**📈 Technical Signals**")
                    tech = analysis["technical_data"]
                    st.write(f"- **RSI:** {tech['rsi']} ({'Overbought' if tech['rsi']>70 else 'Neutral' if tech['rsi']>30 else 'Oversold'})")
                    st.write(f"- **SMA50:** {'Above (Bullish)' if tech['above_sma50'] else 'Below (Bearish)'}")
                
                with e2:
                    st.markdown("**👤 Insider Activity (Evidence)**")
                    ins = analysis["insider_data"]
                    st.write(f"- **Net Activity:** {ins.get('net_activity', 'Neutral')}")
                    # Show transactions if available (from new data_engine)
                    txs = ins.get("recent_transactions", [])
                    if txs:
                        st.table(pd.DataFrame(txs)[["date", "name", "type", "shares"]])
                    else:
                        st.write(f"- **Ownership Change:** {ins.get('insider_trans', 'N/A')}")
                        st.caption("(Detailed transaction rows not available via public feed)")

                    st.markdown("**🎯 Catalyst**")
                    st.write(f"- **Next Earnings:** {analysis['earnings_date']}")
            
            st.markdown("---")

    
    # ─── Opportunity Finder ───────────────────────────────────────────────────
    st.markdown("### 🧠 AI Recommendations (Upgrade Candidates)")
    
    if find_opps_btn:
        with st.spinner("🤖 Scanning market for superior candidates..."):
            # Use data_engine.FULL_US_UNIVERSE
            target_univ = FULL_US_UNIVERSE 
            
            # Filter out existing portfolio using pf_tickers defined above
            candidates = [t for t in target_univ if t not in pf_tickers]
            
            # Limit scan for speed
            candidates = candidates[:30] 
            
            opp_analyses = []
            prog_bar = st.progress(0)
            for i, tick in enumerate(candidates):
                prog_bar.progress((i+1)/len(candidates))
                opp_analyses.append(analyze_ticker(tick))
            prog_bar.empty()
            
            # Rank them
            ranked_opps = rank_candidates(opp_analyses, DEFAULT_WEIGHTS)
            
            # Compare against weakest portfolio holding
            # We need to score the portfolio first
            pf_scored = rank_candidates(pf_analyses, DEFAULT_WEIGHTS)
            lowest_pf_stock = pf_scored.iloc[-1]
            lowest_score = lowest_pf_stock["Composite"]
            
            # Filter opportunities significantly better
            better_opps = ranked_opps[ranked_opps["Composite"] > (lowest_score + 1.0)] 
            
            col_a, col_b = st.columns([2, 1])
            
            with col_a:
                if not better_opps.empty:
                    st.success(f"🔍 Found {len(better_opps)} stocks with stronger signals than your weakest holding (**{lowest_pf_stock['Ticker']}**: {lowest_score:.1f})")
                    
                    top_upgrade = better_opps.iloc[0]
                    st.markdown(f"""
                    <div style="padding:15px; border:1px solid #00d4aa; border-radius:10px; background:rgba(0,212,170,0.1)">
                        <h3 style="margin:0; color:#00d4aa">✨ Top Upgrade: {top_upgrade['Ticker']}</h3>
                        <p style="margin:5px 0 0 0; color:#e8e8f0">{top_upgrade['Company']}</p>
                        <hr style="border-color:#00d4aa; opacity:0.3">
                        <div style="display:flex; justify-content:space-between">
                            <div>Composite Score: <strong style="font-size:1.2rem">{top_upgrade['Composite']:.1f}</strong></div>
                            <div>Sentiment: <strong>{top_upgrade['Sentiment']:.1f}</strong></div>
                            <div>Tech: <strong>{top_upgrade['Technical']:.1f}</strong></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("#### All Candidates")
                    st.dataframe(
                        better_opps[["Ticker", "Composite", "Sentiment", "Technical", "Price"]].head(5),
                        use_container_width=True
                    )
                else:
                    st.info("✅ Your portfolio is strong! No significantly better candidates found in this scan.")
            
            with col_b:
                st.markdown("#### 📉 Weakest Link")
                st.warning(f"Consider reducing: **{lowest_pf_stock['Ticker']}**")
                st.metric("Current Score", f"{lowest_score:.1f}/10")
                st.markdown(f"Sentiment: **{lowest_pf_stock['Sentiment']:.1f}**")
                st.markdown(f"Technical: **{lowest_pf_stock['Technical']:.1f}**")
