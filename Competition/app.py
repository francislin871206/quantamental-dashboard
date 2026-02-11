"""
Revolution Stock Selector Dashboard
A Streamlit dashboard implementing the Sentiment + Catalyst Convergence strategy
to identify 3 US stocks with explosive short-term growth potential.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import SECTOR_MAP, DEFAULT_WEIGHTS, COLORS, PLOTLY_TEMPLATE, FULL_US_UNIVERSE
from data_engine import analyze_ticker, fetch_price_data, generate_market_summary
from scoring import rank_candidates, get_top_picks, format_market_cap, compute_composite_score

# ─── NLTK Setup (Prevent Cloud Crash) ────────────────────────────────────────
import nltk
try:
    nltk.classes
except AttributeError:
    pass  # NLTK not loaded properly?

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    try:
        nltk.download('punkt_tab')
    except Exception:
        pass # Older nltk might not need this


# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Revolution Stock Selector",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
    st.markdown("---")

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


# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <h1>🚀 Revolution Stock Selector</h1>
    <p>Sentiment + Catalyst Convergence Strategy · Identify high-potential stocks for explosive short-term growth</p>
</div>
""", unsafe_allow_html=True)


# ─── Main Logic ───────────────────────────────────────────────────────────────

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
    if auto_select_btn:
        display_top_n = 10
        
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
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Screener & Rankings",
        "📰 Sentiment Analysis",
        "📈 Technical Setup",
        "🏆 Final Picks",
    ])

    # ─── TAB 1: Screener ──────────────────────────────────────────────────
    with tab1:
        st.markdown("### 📋 Stock Rankings")
        st.markdown("All candidates scored and ranked by composite score. Higher is better.")

        # Format display DataFrame
        display_df = ranked_df.copy()
        display_df["Market Cap"] = display_df["Market Cap"].apply(format_market_cap)
        display_df["P/E"] = display_df["P/E"].apply(lambda x: f"{x:.1f}" if pd.notna(x) and x else "N/A")

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
                    """)
            
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

    st.markdown("---")
    st.markdown(
        "<p style='text-align:center; color:#555577;'>"
        "Revolution Stock Selector · Quantamental Investment Competition · Feb 2026"
        "</p>",
        unsafe_allow_html=True,
    )
