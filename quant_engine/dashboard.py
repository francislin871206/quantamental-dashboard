"""
Quantamental Trading Dashboard - Premium Edition
Design inspired by Cathay Bank & Tesla: Clean, white, minimal, premium.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import yfinance as yf
import streamlit.components.v1 as components
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quant_engine.strategy_factory import StrategyFactory
from quant_engine.ai_report import AIReportGenerator

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Quantamental | 量化投資平台",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════════════
# LANGUAGE TRANSLATIONS
# ═══════════════════════════════════════════════════════════════════════════════
TRANSLATIONS = {
    'en': {
        'title': 'QUANTAMENTAL',
        'subtitle': 'Intelligent Trading Platform',
        'asset_selection': 'Asset Selection',
        'asset_class': 'Asset Class',
        'symbol': 'Symbol',
        'custom_symbol': 'Custom Symbol',
        'date_range': 'Date Range',
        'from': 'From',
        'to': 'To',
        'strategy': 'Strategy',
        'model': 'Model',
        'risk_controls': 'Risk Controls',
        'vix_filter': 'VIX Filter',
        'vix_threshold': 'VIX Threshold',
        'capital': 'Capital',
        'initial': 'Initial Amount',
        'net_pnl': 'Net P&L',
        'max_drawdown': 'Max Drawdown',
        'total_trades': 'Total Trades',
        'win_rate': 'Win Rate',
        'vix_protected': 'VIX Protected',
        'final_value': 'Final Value',
        'peak_to_trough': 'Peak-to-Trough',
        'executed': 'Executed',
        'success': 'Success',
        'sessions': 'Sessions',
        'portfolio': 'Portfolio',
        'chart_analysis': 'Chart Analysis',
        'strategy_insights': 'Strategy Insights',
        'price_signals': 'Price Action & Signals',
        'performance_analysis': 'Performance Analysis',
        'summary': 'Summary',
        'contributing_factors': 'Contributing Factors',
        'recommendations': 'Recommendations',
        'risk_active': 'Risk Management Active',
        'vix_protected_msg': 'VIX filter protected capital during {0} high-volatility sessions.',
        'current_vix': 'Current VIX',
        'no_data': 'No data available for',
        'ai_analysis': 'AI Analysis',
        'backtest_analysis': 'Backtest Analysis',
        'strategy_perspective': 'Strategy Perspective',
        'technical_perspective': 'Technical Perspective',
        'fundamental_perspective': 'Fundamental Perspective',
        'news_sentiment': 'News & Sentiment',
        'strategy_summary': 'Strategy Performance Summary',
        'signal_quality': 'Signal Quality Analysis',
        'market_regime': 'Market Regime Detection',
        'risk_adjusted': 'Risk-Adjusted Metrics',
        'categories': {
            'US Equities - Technology': 'US Equities - Technology',
            'US Equities - Financials': 'US Equities - Financials',
            'US Equities - Healthcare': 'US Equities - Healthcare',
            'US Equities - Consumer': 'US Equities - Consumer',
            'US Equities - Energy': 'US Equities - Energy',
            'Indices': 'Indices',
            'International ETFs': 'International ETFs',
            'Digital Assets': 'Digital Assets',
            'Commodities': 'Commodities',
        }
    },
    'zh': {
        'title': '量化投資',
        'subtitle': '智能交易平台',
        'asset_selection': '資產選擇',
        'asset_class': '資產類別',
        'symbol': '標的代碼',
        'custom_symbol': '自訂代碼',
        'date_range': '日期範圍',
        'from': '開始日期',
        'to': '結束日期',
        'strategy': '策略',
        'model': '模型',
        'risk_controls': '風險控制',
        'vix_filter': 'VIX 過濾器',
        'vix_threshold': 'VIX 閾值',
        'capital': '資金',
        'initial': '初始資金',
        'net_pnl': '淨損益',
        'max_drawdown': '最大回撤',
        'total_trades': '交易次數',
        'win_rate': '勝率',
        'vix_protected': 'VIX 保護',
        'final_value': '最終價值',
        'peak_to_trough': '峰值至谷底',
        'executed': '已執行',
        'success': '成功率',
        'sessions': '交易日',
        'portfolio': '投資組合',
        'chart_analysis': '圖表分析',
        'strategy_insights': '策略洞察',
        'price_signals': '價格走勢與訊號',
        'performance_analysis': '績效分析',
        'summary': '摘要',
        'contributing_factors': '影響因素',
        'recommendations': '建議',
        'risk_active': '風險管理已啟動',
        'vix_protected_msg': 'VIX 過濾器在 {0} 個高波動交易日保護了您的資金。',
        'current_vix': '當前 VIX',
        'no_data': '無法取得數據：',
        'ai_analysis': 'AI 智能分析',
        'backtest_analysis': '回測分析',
        'strategy_perspective': '策略面分析',
        'technical_perspective': '技術面分析',
        'fundamental_perspective': '基本面分析',
        'news_sentiment': '新聞消息面',
        'strategy_summary': '策略績效摘要',
        'signal_quality': '訊號品質分析',
        'market_regime': '市場狀態偵測',
        'risk_adjusted': '風險調整指標',
        'categories': {
            'US Equities - Technology': '美股 - 科技',
            'US Equities - Financials': '美股 - 金融',
            'US Equities - Healthcare': '美股 - 醫療',
            'US Equities - Consumer': '美股 - 消費',
            'US Equities - Energy': '美股 - 能源',
            'Indices': '指數',
            'International ETFs': '國際ETF',
            'Digital Assets': '加密貨幣',
            'Commodities': '商品',
        }
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# TICKER DATABASE
# ═══════════════════════════════════════════════════════════════════════════════
TICKER_CATEGORIES = {
    "US Equities - Technology": ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "AMD", "INTC", "CRM"],
    "US Equities - Financials": ["JPM", "BAC", "GS", "MS", "V", "MA", "AXP", "BLK", "C", "WFC"],
    "US Equities - Healthcare": ["JNJ", "UNH", "PFE", "ABBV", "MRK", "TMO", "ABT", "DHR", "BMY", "LLY"],
    "US Equities - Consumer": ["WMT", "HD", "MCD", "NKE", "SBUX", "TGT", "COST", "LOW", "TJX", "DG"],
    "US Equities - Energy": ["XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HAL"],
    "Indices": ["^GSPC", "^DJI", "^IXIC", "^RUT", "^VIX"],
    "International ETFs": ["EFA", "EEM", "VEA", "VWO", "IEFA", "ACWI"],
    "Digital Assets": ["BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "SOL-USD"],
    "Commodities": ["GC=F", "SI=F", "CL=F", "NG=F"],
}

# ═══════════════════════════════════════════════════════════════════════════════
# PREMIUM CATHAY/TESLA STYLE CSS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --white: #ffffff;
        --snow: #fafbfc;
        --pearl: #f4f5f7;
        --silver: #e8eaed;
        --grey-light: #d1d5db;
        --grey: #9ca3af;
        --grey-dark: #6b7280;
        --charcoal: #374151;
        --slate: #1f2937;
        --black: #111827;
        --accent-green: #10b981;
        --accent-red: #ef4444;
        --accent-teal: #14b8a6;
        --accent-emerald: #059669;
    }
    
    .stApp {
        background: linear-gradient(135deg, var(--snow) 0%, var(--white) 50%, var(--pearl) 100%);
        font-family: 'Inter', 'Noto Sans TC', sans-serif;
    }
    
    /* CRITICAL: Force dark text color for all main content */
    .stApp .main .block-container,
    .stApp .main .block-container *,
    .stApp .main .stMarkdown,
    .stApp .main .stMarkdown *,
    .stApp .main p,
    .stApp .main span,
    .stApp .main li,
    .stApp .main ul,
    .stApp .main div {
        color: #1f2937;
    }
    
    /* Override for colored spans */
    .stApp .main span[style*="color:"] {
        color: inherit !important;
    }
    
    /* Animated background shapes */
    .stApp::before {
        content: '';
        position: fixed;
        top: -50%;
        right: -20%;
        width: 80%;
        height: 120%;
        background: radial-gradient(ellipse at center, rgba(20, 184, 166, 0.03) 0%, transparent 70%);
        animation: float1 20s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }
    
    .stApp::after {
        content: '';
        position: fixed;
        bottom: -30%;
        left: -10%;
        width: 60%;
        height: 80%;
        background: radial-gradient(ellipse at center, rgba(16, 185, 129, 0.04) 0%, transparent 60%);
        animation: float2 25s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }
    
    @keyframes float1 {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        33% { transform: translate(30px, -30px) rotate(5deg); }
        66% { transform: translate(-20px, 20px) rotate(-3deg); }
    }
    
    @keyframes float2 {
        0%, 100% { transform: translate(0, 0) scale(1); }
        50% { transform: translate(40px, -20px) scale(1.1); }
    }
    
    .main .block-container {
        padding: 1.5rem 3rem;
        max-width: 100%;
        position: relative;
        z-index: 1;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--white) 0%, var(--snow) 100%);
        border-right: 1px solid var(--silver);
    }
    
    section[data-testid="stSidebar"] * {
        font-family: 'Inter', 'Noto Sans TC', sans-serif !important;
    }
    
    /* Sidebar text colors - make labels visible */
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] h5,
    section[data-testid="stSidebar"] h6 {
        color: var(--slate) !important;
    }
    
    /* Sidebar input/select styling */
    section[data-testid="stSidebar"] .stSelectbox > div > div,
    section[data-testid="stSidebar"] .stTextInput > div > div > input,
    section[data-testid="stSidebar"] .stNumberInput > div > div > input,
    section[data-testid="stSidebar"] .stDateInput > div > div > input {
        background-color: var(--white) !important;
        color: var(--slate) !important;
        border: 1px solid var(--silver) !important;
    }
    
    /* Dropdown text */
    section[data-testid="stSidebar"] [data-baseweb="select"] span {
        color: var(--slate) !important;
    }
    
    /* Slider labels */
    section[data-testid="stSidebar"] .stSlider label {
        color: var(--charcoal) !important;
    }
    
    /* Checkbox text */
    section[data-testid="stSidebar"] .stCheckbox label span {
        color: var(--slate) !important;
    }
    
    /* Premium Header */
    .premium-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1.5rem 0;
        margin-bottom: 2rem;
        position: relative;
    }
    
    .premium-header::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--silver), transparent);
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .logo-icon {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, var(--accent-teal) 0%, var(--accent-emerald) 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.5rem;
        font-weight: 700;
        box-shadow: 0 4px 20px rgba(20, 184, 166, 0.25);
    }
    
    .logo-text {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--slate);
        letter-spacing: 2px;
    }
    
    .logo-sub {
        font-size: 0.75rem;
        color: var(--grey-dark);
        font-weight: 400;
        letter-spacing: 1px;
    }
    
    .header-right {
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }
    
    .lang-toggle {
        display: flex;
        background: var(--pearl);
        border-radius: 8px;
        padding: 4px;
        gap: 4px;
    }
    
    .lang-btn {
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 500;
        border: none;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .lang-btn.active {
        background: var(--white);
        color: var(--slate);
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    .lang-btn:not(.active) {
        background: transparent;
        color: var(--grey-dark);
    }
    
    .timestamp {
        font-size: 0.75rem;
        color: var(--grey-dark);
        text-align: right;
    }
    
    /* Floating Decorative Shapes */
    .floating-shape {
        position: fixed;
        border-radius: 50%;
        opacity: 0.5;
        pointer-events: none;
        z-index: 0;
    }
    
    .shape-1 {
        width: 300px;
        height: 300px;
        top: 10%;
        right: 5%;
        background: linear-gradient(135deg, rgba(20, 184, 166, 0.05) 0%, rgba(16, 185, 129, 0.02) 100%);
        animation: morph1 15s ease-in-out infinite;
    }
    
    .shape-2 {
        width: 200px;
        height: 200px;
        bottom: 20%;
        left: 10%;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.03) 0%, rgba(20, 184, 166, 0.02) 100%);
        animation: morph2 20s ease-in-out infinite;
    }
    
    @keyframes morph1 {
        0%, 100% { border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; }
        50% { border-radius: 30% 60% 70% 40% / 50% 60% 30% 60%; }
    }
    
    @keyframes morph2 {
        0%, 100% { border-radius: 40% 60% 60% 40% / 60% 40% 60% 40%; }
        50% { border-radius: 60% 40% 30% 70% / 40% 70% 30% 60%; }
    }
    
    /* Metrics Cards */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .metric-card {
        background: var(--white);
        border-radius: 16px;
        padding: 1.25rem;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04);
        border: 1px solid var(--silver);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--accent-teal), var(--accent-emerald));
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    .metric-label {
        font-size: 0.7rem;
        font-weight: 600;
        color: var(--grey-dark);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        font-family: 'Inter', monospace;
    }
    
    .metric-value.positive { color: var(--accent-green); }
    .metric-value.negative { color: var(--accent-red); }
    .metric-value.neutral { color: var(--slate); }
    
    .metric-delta {
        font-size: 0.7rem;
        font-weight: 500;
        margin-top: 0.25rem;
        color: var(--grey);
    }
    
    /* Section Headers */
    .section-header {
        font-size: 0.7rem;
        font-weight: 600;
        color: var(--grey-dark);
        text-transform: uppercase;
        letter-spacing: 1.5px;
        padding: 1rem 0 0.75rem 0;
        margin-top: 1rem;
        border-bottom: 1px solid var(--silver);
    }
    
    /* Info Cards */
    .info-card {
        background: var(--white);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04);
        border: 1px solid var(--silver);
        margin: 1rem 0;
    }
    
    .info-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--slate);
        margin-bottom: 0.75rem;
    }
    
    .info-text {
        font-size: 0.9rem;
        color: var(--charcoal);
        line-height: 1.7;
    }
    
    /* Alert Card */
    .alert-card {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(20, 184, 166, 0.04) 100%);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .alert-icon {
        width: 40px;
        height: 40px;
        background: var(--accent-emerald);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.2rem;
    }
    
    .alert-content {
        flex: 1;
    }
    
    .alert-title {
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--accent-emerald);
    }
    
    .alert-text {
        font-size: 0.8rem;
        color: var(--charcoal);
        margin-top: 0.25rem;
    }
    
    /* Ticker Badge */
    .ticker-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: linear-gradient(135deg, var(--accent-teal) 0%, var(--accent-emerald) 100%);
        color: white;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        margin-right: 0.75rem;
        box-shadow: 0 2px 12px rgba(20, 184, 166, 0.25);
    }
    
    .strategy-badge {
        display: inline-flex;
        align-items: center;
        background: var(--pearl);
        color: var(--slate);
        font-size: 0.7rem;
        font-weight: 600;
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Hide Streamlit Elements */
    #MainMenu, footer, header { visibility: hidden; }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: var(--snow); }
    ::-webkit-scrollbar-thumb { background: var(--grey-light); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--grey); }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: var(--pearl);
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--white) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    /* ═══════════════════════════════════════════════════════════════════
       INCEPTION SPINNING TOP - Dynamic Quality Animation (3D Enhanced)
    ═══════════════════════════════════════════════════════════════════ */
    .inception-container {
        position: fixed;
        top: 100px;
        right: 40px;
        z-index: 1000;
        perspective: 800px;
        transform-style: preserve-3d;
    }
    
    .spinning-top {
        width: 70px;
        height: 70px;
        position: relative;
        transform-style: preserve-3d;
        animation: topSpin 3s linear infinite;
        filter: drop-shadow(0 15px 25px rgba(0, 0, 0, 0.3));
    }
    
    .spinning-top::before {
        content: '';
        position: absolute;
        width: 100%;
        height: 100%;
        background: conic-gradient(
            from 0deg,
            #2dd4bf 0deg,
            #14b8a6 45deg,
            #0d9488 90deg,
            #0f766e 135deg,
            #115e59 180deg,
            #0f766e 225deg,
            #0d9488 270deg,
            #14b8a6 315deg,
            #2dd4bf 360deg
        );
        border-radius: 50%;
        box-shadow: 
            0 0 30px rgba(20, 184, 166, 0.6),
            0 0 60px rgba(16, 185, 129, 0.4),
            0 10px 30px rgba(0, 0, 0, 0.3),
            inset 0 -10px 20px rgba(0, 0, 0, 0.3),
            inset 0 10px 20px rgba(255, 255, 255, 0.4),
            inset 5px 0 15px rgba(255, 255, 255, 0.2),
            inset -5px 0 15px rgba(0, 0, 0, 0.2);
        transform: rotateX(75deg);
        transform-style: preserve-3d;
    }
    
    .spinning-top::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%) rotateX(75deg);
        width: 20px;
        height: 20px;
        background: radial-gradient(circle at 30% 30%, #fff 0%, #a7f3d0 30%, #14b8a6 70%, #0d9488 100%);
        border-radius: 50%;
        box-shadow: 
            0 0 15px rgba(255, 255, 255, 0.9),
            inset 0 -3px 6px rgba(0, 0, 0, 0.2);
    }
    
    .top-stem {
        position: absolute;
        bottom: 75%;
        left: 50%;
        transform: translateX(-50%) rotateX(0deg);
        width: 10px;
        height: 35px;
        background: linear-gradient(90deg, 
            #0d9488 0%, 
            #14b8a6 20%, 
            #5eead4 40%, 
            #14b8a6 60%, 
            #0d9488 100%
        );
        border-radius: 5px 5px 0 0;
        box-shadow: 
            2px 0 5px rgba(0, 0, 0, 0.3),
            -2px 0 5px rgba(0, 0, 0, 0.1),
            inset 2px 0 3px rgba(255, 255, 255, 0.3);
    }
    
    .top-point {
        position: absolute;
        top: 85%;
        left: 50%;
        transform: translateX(-50%);
        width: 0;
        height: 0;
        border-left: 12px solid transparent;
        border-right: 12px solid transparent;
        border-top: 40px solid;
        border-top-color: #0f766e;
        filter: drop-shadow(0 8px 15px rgba(0, 0, 0, 0.4));
        background: linear-gradient(180deg, #14b8a6 0%, #0f766e 50%, #115e59 100%);
        clip-path: polygon(50% 100%, 0 0, 100% 0);
    }
    
    .top-point::before {
        content: '';
        position: absolute;
        top: -40px;
        left: -6px;
        width: 12px;
        height: 40px;
        background: linear-gradient(90deg, 
            rgba(255,255,255,0.3) 0%, 
            transparent 50%, 
            rgba(0,0,0,0.2) 100%
        );
        clip-path: polygon(50% 100%, 0 0, 100% 0);
    }
    
    .top-shadow {
        position: absolute;
        bottom: -60px;
        left: 50%;
        transform: translateX(-50%) rotateX(80deg);
        width: 60px;
        height: 20px;
        background: radial-gradient(ellipse, rgba(0,0,0,0.4) 0%, rgba(0,0,0,0.2) 40%, transparent 70%);
        animation: shadowPulse 3s ease-in-out infinite;
        filter: blur(3px);
    }
    
    @keyframes topSpin {
        from { transform: rotateY(0deg) rotateZ(-3deg); }
        to { transform: rotateY(360deg) rotateZ(-3deg); }
    }
    
    @keyframes shadowPulse {
        0%, 100% { opacity: 0.5; transform: translateX(-50%) rotateX(80deg) scale(1); }
        50% { opacity: 0.7; transform: translateX(-50%) rotateX(80deg) scale(0.85); }
    }
    
    .inception-container:hover .spinning-top {
        animation: topSpin 0.8s linear infinite;
    }
    
    .inception-container:hover .top-shadow {
        animation: shadowPulse 0.8s ease-in-out infinite;
    }
    
    /* ═══════════════════════════════════════════════════════════════════
       ENHANCED SIDEBAR - Gradient Labels & Better Visibility
    ═══════════════════════════════════════════════════════════════════ */
    
    /* Section headers with gradient and icons */
    section[data-testid="stSidebar"] h5 {
        background: linear-gradient(135deg, #1f2937 0%, #374151 50%, #4b5563 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        letter-spacing: 1px;
        padding: 0.75rem 0;
        margin-top: 0.5rem;
        position: relative;
        display: flex;
        align-items: center;
    }
    
    section[data-testid="stSidebar"] h5::before {
        content: '◈';
        margin-right: 8px;
        -webkit-text-fill-color: #14b8a6;
        font-size: 1rem;
    }
    
    /* Labels with gradient effect */
    section[data-testid="stSidebar"] label {
        background: linear-gradient(135deg, #374151 0%, #1f2937 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.3px;
        transition: all 0.3s ease;
    }
    
    section[data-testid="stSidebar"] label:hover {
        background: linear-gradient(135deg, #14b8a6 0%, #059669 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Slider value with enhanced visibility */
    section[data-testid="stSidebar"] .stSlider > div > div > div > div {
        color: var(--slate) !important;
        font-weight: 600 !important;
    }
    
    /* Select boxes with icons */
    section[data-testid="stSidebar"] .stSelectbox > label::before {
        content: '▸';
        margin-right: 6px;
        color: #14b8a6;
    }
    
    /* Input fields with gradient border on focus */
    section[data-testid="stSidebar"] .stSelectbox > div > div,
    section[data-testid="stSidebar"] .stTextInput > div > div > input,
    section[data-testid="stSidebar"] .stNumberInput > div > div > input,
    section[data-testid="stSidebar"] .stDateInput > div > div > input {
        background-color: var(--white) !important;
        color: var(--slate) !important;
        border: 2px solid var(--silver) !important;
        border-radius: 10px !important;
        transition: all 0.3s ease;
    }
    
    section[data-testid="stSidebar"] .stSelectbox > div > div:hover,
    section[data-testid="stSidebar"] .stTextInput > div > div > input:hover,
    section[data-testid="stSidebar"] .stNumberInput > div > div > input:hover,
    section[data-testid="stSidebar"] .stDateInput > div > div > input:hover {
        border-color: #14b8a6 !important;
        box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.1) !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox > div > div:focus-within,
    section[data-testid="stSidebar"] .stTextInput > div > div > input:focus,
    section[data-testid="stSidebar"] .stNumberInput > div > div > input:focus,
    section[data-testid="stSidebar"] .stDateInput > div > div > input:focus {
        border-color: #10b981 !important;
        box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.15) !important;
    }
    
    /* Slider track with gradient */
    section[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] [role="slider"] {
        background: linear-gradient(135deg, #14b8a6 0%, #10b981 100%) !important;
        box-shadow: 0 2px 8px rgba(20, 184, 166, 0.4) !important;
    }
    
    section[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] > div > div {
        background: linear-gradient(90deg, #14b8a6 0%, #10b981 100%) !important;
    }
    
    /* Checkbox with gradient checkmark */
    section[data-testid="stSidebar"] .stCheckbox [data-testid="stCheckbox"] {
        transition: all 0.3s ease;
    }
    
    section[data-testid="stSidebar"] .stCheckbox [data-testid="stCheckbox"]:hover {
        transform: scale(1.02);
    }
    
    /* Dividers with gradient */
    section[data-testid="stSidebar"] hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #14b8a6, #10b981, transparent);
        margin: 1.5rem 0;
    }
    
    /* ═══════════════════════════════════════════════════════════════════
       AI ANALYSIS CARDS - Premium Design
    ═══════════════════════════════════════════════════════════════════ */
    .ai-analysis-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1.25rem;
        margin: 1.5rem 0;
    }
    
    .analysis-card {
        background: linear-gradient(145deg, var(--white) 0%, var(--snow) 100%);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid var(--silver);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .analysis-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .analysis-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.1);
    }
    
    .analysis-card:hover::before {
        opacity: 1;
    }
    
    .analysis-card.strategy::before {
        background: linear-gradient(90deg, #8b5cf6, #a78bfa);
    }
    
    .analysis-card.technical::before {
        background: linear-gradient(90deg, #3b82f6, #60a5fa);
    }
    
    .analysis-card.fundamental::before {
        background: linear-gradient(90deg, #10b981, #34d399);
    }
    
    .analysis-card.news::before {
        background: linear-gradient(90deg, #f59e0b, #fbbf24);
    }
    
    .analysis-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
    }
    
    .analysis-icon {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
    }
    
    .analysis-icon.strategy {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(167, 139, 250, 0.1) 100%);
    }
    
    .analysis-icon.technical {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(96, 165, 250, 0.1) 100%);
    }
    
    .analysis-icon.fundamental {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(52, 211, 153, 0.1) 100%);
    }
    
    .analysis-icon.news {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(251, 191, 36, 0.1) 100%);
    }
    
    .analysis-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1f2937 !important;
        -webkit-text-fill-color: #1f2937 !important;
        background: none !important;
        margin: 0;
        text-shadow: none;
    }
    
    .analysis-content {
        color: var(--charcoal);
        font-size: 0.9rem;
        line-height: 1.7;
    }
    
    .analysis-content ul {
        margin: 0.75rem 0 0 0;
        padding-left: 1.25rem;
    }
    
    .analysis-content li {
        margin-bottom: 0.5rem;
        position: relative;
    }
    
    .analysis-content li::marker {
        color: #14b8a6;
    }
    
    /* AI Badge */
    .ai-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: linear-gradient(135deg, #14b8a6 0%, #10b981 100%);
        color: white;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 6px 12px;
        border-radius: 20px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 12px rgba(20, 184, 166, 0.3);
    }
    
    .ai-badge::before {
        content: '◈';
        animation: aiPulse 2s ease-in-out infinite;
    }
    
    @keyframes aiPulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(0.9); }
    }
    
    /* Tab text visibility fix */
    .stTabs [data-baseweb="tab"] {
        color: var(--charcoal) !important;
        font-weight: 600 !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: var(--slate) !important;
    }
</style>

<div class="floating-shape shape-1"></div>
<div class="floating-shape shape-2"></div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# DATA FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600)
def fetch_market_data(ticker: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    try:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if data.empty:
            return pd.DataFrame()
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data.reset_index()
    except:
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def fetch_vix_data(start_date: datetime, end_date: datetime) -> pd.DataFrame:
    try:
        vix = yf.download("^VIX", start=start_date, end=end_date, progress=False)
        if vix.empty:
            return pd.DataFrame()
        if isinstance(vix.columns, pd.MultiIndex):
            vix.columns = vix.columns.get_level_values(0)
        return vix.reset_index()[['Date', 'Close']].rename(columns={'Close': 'VIX'})
    except:
        return pd.DataFrame()


def apply_vix_filter(data: pd.DataFrame, vix_data: pd.DataFrame, threshold: float) -> pd.DataFrame:
    if vix_data.empty:
        return data
    df = data.copy()
    df['Date'] = pd.to_datetime(df['Date'])
    vix_data['Date'] = pd.to_datetime(vix_data['Date'])
    df = df.merge(vix_data, on='Date', how='left')
    df['VIX'] = df['VIX'].ffill()
    df.loc[(df['VIX'] > threshold) & (df['Signal'] == 1), 'Signal'] = 0
    df['VIX_Filtered'] = df['VIX'] > threshold
    return df


def calculate_metrics(data: pd.DataFrame, capital: float = 10000) -> dict:
    df = data.copy()
    df['Returns'] = df['Close'].pct_change()
    df['Strategy_Returns'] = df['Signal'].shift(1) * df['Returns']
    df['Strategy_Returns'] = df['Strategy_Returns'].fillna(0)
    df['Cumulative'] = (1 + df['Strategy_Returns']).cumprod()
    df['Portfolio'] = capital * df['Cumulative']
    
    final = df['Portfolio'].iloc[-1]
    profit = final - capital
    profit_pct = (profit / capital) * 100
    
    df['Peak'] = df['Portfolio'].cummax()
    df['DD'] = (df['Portfolio'] - df['Peak']) / df['Peak'] * 100
    max_dd = df['DD'].min()
    
    trades = df[df['Signal'] != 0]
    n_trades = len(trades) - 1 if len(trades) > 1 else 0
    
    win_rate = 0
    if n_trades > 0:
        trades = trades.copy()
        trades['TR'] = trades['Close'].pct_change()
        wins = (trades['TR'] > 0).sum()
        win_rate = (wins / n_trades) * 100
    
    vix_days = df['VIX_Filtered'].sum() if 'VIX_Filtered' in df.columns else 0
    current_vix = df['VIX'].iloc[-1] if 'VIX' in df.columns else 0
    
    return {
        'profit': profit, 'profit_pct': profit_pct, 'final': final,
        'max_dd': max_dd, 'trades': n_trades, 'win_rate': win_rate,
        'vix_days': vix_days, 'current_vix': current_vix
    }


def generate_insights(metrics: dict, strategy: str, ticker: str, lang: str) -> dict:
    insights = {'summary': '', 'factors': [], 'recommendations': []}
    
    pct = metrics['profit_pct']
    if lang == 'zh':
        if pct > 0:
            insights['summary'] = f"策略在 {ticker} 產生了 {pct:.2f}% 的正報酬。"
        else:
            insights['summary'] = f"策略在 {ticker} 產生了 {pct:.2f}% 的虧損。"
        
        if metrics['max_dd'] < -20:
            insights['factors'].append("回撤超過 20% 表示在市場修正期間承受過高風險。")
        if metrics['win_rate'] < 45:
            insights['factors'].append("勝率低於 45% 表示進場時機或訊號可能需要優化。")
        if metrics['vix_days'] > 50:
            insights['factors'].append(f"共有 {metrics['vix_days']} 個交易日處於高波動狀態。")
        
        insights['recommendations'] = [
            "考慮搭配趨勢過濾器以減少假訊號",
            "根據波動率調整部位大小 (ATR)",
            "增加確認指標後再進場",
            "檢視不同市場環境下的績效表現"
        ]
    else:
        if pct > 0:
            insights['summary'] = f"Strategy generated {pct:.2f}% return on {ticker}."
        else:
            insights['summary'] = f"Strategy resulted in {pct:.2f}% loss on {ticker}."
        
        if metrics['max_dd'] < -20:
            insights['factors'].append("Drawdown exceeding 20% indicates high exposure during corrections.")
        if metrics['win_rate'] < 45:
            insights['factors'].append("Win rate below 45% suggests entry timing needs optimization.")
        if metrics['vix_days'] > 50:
            insights['factors'].append(f"{metrics['vix_days']} trading days had elevated volatility.")
        
        insights['recommendations'] = [
            "Consider combining with trend filters to reduce false signals",
            "Implement position sizing based on volatility (ATR)",
            "Add confirmation indicators before entry",
            "Review performance across different market regimes"
        ]
    
    return insights


# ═══════════════════════════════════════════════════════════════════════════════
# CHART - Premium Trading Visualization
# ═══════════════════════════════════════════════════════════════════════════════
def create_chart(data: pd.DataFrame, show_vix: bool = False) -> go.Figure:
    rows = 3 if (show_vix and 'VIX' in data.columns) else 2
    heights = [0.55, 0.22, 0.23] if rows == 3 else [0.7, 0.3]
    
    fig = make_subplots(
        rows=rows, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.06, 
        row_heights=heights,
        subplot_titles=None
    )
    
    # ═══════════════════════════════════════════════════════════════════
    # CANDLESTICK - Enhanced Premium Colors
    # ═══════════════════════════════════════════════════════════════════
    fig.add_trace(go.Candlestick(
        x=data['Date'], 
        open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
        name='Price',
        increasing=dict(line=dict(color='#22c55e', width=1.5), fillcolor='#22c55e'),
        decreasing=dict(line=dict(color='#ef4444', width=1.5), fillcolor='#ef4444'),
        whiskerwidth=0.8,
        hoverinfo='text',
        hovertext=[f"<b>{d.strftime('%Y-%m-%d')}</b><br>Open: ${o:.2f}<br>High: ${h:.2f}<br>Low: ${l:.2f}<br>Close: ${c:.2f}" 
                   for d, o, h, l, c in zip(data['Date'], data['Open'], data['High'], data['Low'], data['Close'])]
    ), row=1, col=1)
    
    # ═══════════════════════════════════════════════════════════════════
    # BOLLINGER BANDS - Refined Gradient Fill
    # ═══════════════════════════════════════════════════════════════════
    if 'BB_Upper' in data.columns:
        # Upper band
        fig.add_trace(go.Scatter(
            x=data['Date'], y=data['BB_Upper'], 
            name='BB Upper', 
            line=dict(color='rgba(99, 102, 241, 0.6)', width=1.5, dash='dot'),
            hoverinfo='skip'
        ), row=1, col=1)
        
        # Middle MA
        fig.add_trace(go.Scatter(
            x=data['Date'], y=data['BB_Middle'], 
            name='MA 20', 
            line=dict(color='#6366f1', width=2),
            hovertemplate='MA: $%{y:.2f}<extra></extra>'
        ), row=1, col=1)
        
        # Lower band with fill
        fig.add_trace(go.Scatter(
            x=data['Date'], y=data['BB_Lower'], 
            name='BB Lower', 
            line=dict(color='rgba(99, 102, 241, 0.6)', width=1.5, dash='dot'),
            fill='tonexty', 
            fillcolor='rgba(99, 102, 241, 0.08)',
            hoverinfo='skip'
        ), row=1, col=1)
    
    # ═══════════════════════════════════════════════════════════════════
    # BUY/SELL SIGNALS - Larger & Clearer Markers
    # ═══════════════════════════════════════════════════════════════════
    buys = data[data['Signal'] == 1]
    sells = data[data['Signal'] == -1]
    
    if not buys.empty:
        fig.add_trace(go.Scatter(
            x=buys['Date'], y=buys['Low']*0.985, 
            mode='markers+text', 
            name='Buy Signal',
            marker=dict(symbol='triangle-up', size=14, color='#22c55e', 
                       line=dict(color='#ffffff', width=2)),
            text=['▲'] * len(buys),
            textposition='bottom center',
            textfont=dict(size=8, color='#22c55e'),
            hovertemplate='<b>BUY</b><br>%{x|%Y-%m-%d}<br>Price: $%{y:.2f}<extra></extra>'
        ), row=1, col=1)
    
    if not sells.empty:
        fig.add_trace(go.Scatter(
            x=sells['Date'], y=sells['High']*1.015, 
            mode='markers+text', 
            name='Sell Signal',
            marker=dict(symbol='triangle-down', size=14, color='#ef4444',
                       line=dict(color='#ffffff', width=2)),
            text=['▼'] * len(sells),
            textposition='top center',
            textfont=dict(size=8, color='#ef4444'),
            hovertemplate='<b>SELL</b><br>%{x|%Y-%m-%d}<br>Price: $%{y:.2f}<extra></extra>'
        ), row=1, col=1)
    
    # ═══════════════════════════════════════════════════════════════════
    # RSI / SIGNAL INDICATOR - Row 2
    # ═══════════════════════════════════════════════════════════════════
    if 'RSI' in data.columns:
        fig.add_trace(go.Scatter(
            x=data['Date'], y=data['RSI'], 
            name='RSI', 
            line=dict(color='#8b5cf6', width=2.5),
            fill='tozeroy', fillcolor='rgba(139, 92, 246, 0.1)',
            hovertemplate='RSI: %{y:.1f}<extra></extra>'
        ), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="#ef4444", line_width=1.5, 
                      annotation_text="Overbought", annotation_position="right", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#22c55e", line_width=1.5,
                      annotation_text="Oversold", annotation_position="right", row=2, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="#9ca3af", line_width=1, row=2, col=1)
    else:
        # Signal bars with gradient effect
        colors = ['#22c55e' if s == 1 else '#ef4444' if s == -1 else '#d1d5db' for s in data['Signal']]
        fig.add_trace(go.Bar(
            x=data['Date'], y=data['Signal'], 
            name='Signal',
            marker=dict(color=colors, line=dict(width=0)),
            hovertemplate='Signal: %{y}<extra></extra>'
        ), row=2, col=1)
        fig.add_hline(y=0, line_color="#9ca3af", line_width=1, row=2, col=1)
    
    # ═══════════════════════════════════════════════════════════════════
    # VIX INDICATOR - Row 3
    # ═══════════════════════════════════════════════════════════════════
    if show_vix and 'VIX' in data.columns and rows == 3:
        fig.add_trace(go.Scatter(
            x=data['Date'], y=data['VIX'], 
            name='VIX', 
            line=dict(color='#f59e0b', width=2.5),
            fill='tozeroy', fillcolor='rgba(245, 158, 11, 0.15)',
            hovertemplate='VIX: %{y:.1f}<extra></extra>'
        ), row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#ef4444", line_width=2,
                      annotation_text="High Fear", annotation_position="right", row=3, col=1)
        fig.add_hline(y=20, line_dash="dot", line_color="#9ca3af", line_width=1, row=3, col=1)
    
    # ═══════════════════════════════════════════════════════════════════
    # PREMIUM LAYOUT STYLING
    # ═══════════════════════════════════════════════════════════════════
    fig.update_layout(
        template='plotly_white',
        paper_bgcolor='rgba(255,255,255,1)',
        plot_bgcolor='rgba(250,251,252,1)',
        font=dict(family='Inter, -apple-system, BlinkMacSystemFont, sans-serif', color='#1f2937', size=12),
        height=550,
        margin=dict(l=60, r=30, t=30, b=40),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#e5e7eb',
            borderwidth=1,
            font=dict(size=11, color='#374151')
        ),
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='#ffffff', 
            bordercolor='#d1d5db', 
            font=dict(color='#1f2937', size=12, family='Inter, sans-serif'),
            namelength=-1
        )
    )
    
    # ═══════════════════════════════════════════════════════════════════
    # AXES STYLING - Refined Grid & Labels
    # ═══════════════════════════════════════════════════════════════════
    for i in range(1, rows + 1):
        fig.update_xaxes(
            gridcolor='#f3f4f6' if i < rows else '#e5e7eb',
            gridwidth=1,
            zeroline=False,
            linecolor='#d1d5db',
            linewidth=1,
            tickfont=dict(size=11, color='#6b7280'),
            tickformat='%b %Y' if i == rows else None,
            showticklabels=(i == rows),
            row=i, col=1
        )
        
        fig.update_yaxes(
            gridcolor='#f3f4f6',
            gridwidth=1,
            zeroline=False,
            linecolor='#d1d5db',
            linewidth=1,
            tickfont=dict(size=11, color='#6b7280'),
            tickprefix='$' if i == 1 else '',
            row=i, col=1
        )
    
    # Y-axis titles
    fig.update_yaxes(title_text="Price", title_font=dict(size=12, color='#374151'), row=1, col=1)
    if 'RSI' in data.columns:
        fig.update_yaxes(title_text="RSI", title_font=dict(size=11, color='#374151'), row=2, col=1)
    else:
        fig.update_yaxes(title_text="Signal", title_font=dict(size=11, color='#374151'), row=2, col=1)
    if show_vix and rows == 3:
        fig.update_yaxes(title_text="VIX", title_font=dict(size=11, color='#374151'), row=3, col=1)
    
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    # Initialize language
    if 'lang' not in st.session_state:
        st.session_state.lang = 'en'
    
    t = TRANSLATIONS[st.session_state.lang]
    now = datetime.now()
    
    # Header with language toggle
    col_logo, col_lang = st.columns([4, 1])
    
    with col_logo:
        st.markdown(f"""
            <div class="premium-header">
                <div class="logo-section">
                    <div class="logo-icon">◈</div>
                    <div>
                        <div class="logo-text">{t['title']}</div>
                        <div class="logo-sub">{t['subtitle']}</div>
                    </div>
                </div>
                <div class="timestamp">
                    {now.strftime('%Y年%m月%d日' if st.session_state.lang == 'zh' else '%B %d, %Y')}<br>
                    {now.strftime('%H:%M')}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col_lang:
        lang_col1, lang_col2 = st.columns(2)
        with lang_col1:
            if st.button("EN", use_container_width=True, type="primary" if st.session_state.lang == 'en' else "secondary"):
                st.session_state.lang = 'en'
                st.rerun()
        with lang_col2:
            if st.button("中文", use_container_width=True, type="primary" if st.session_state.lang == 'zh' else "secondary"):
                st.session_state.lang = 'zh'
                st.rerun()
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"##### {t['asset_selection']}")
        
        cat_display = {k: t['categories'].get(k, k) for k in TICKER_CATEGORIES.keys()}
        category = st.selectbox(t['asset_class'], list(TICKER_CATEGORIES.keys()), format_func=lambda x: cat_display[x])
        ticker = st.selectbox(t['symbol'], TICKER_CATEGORIES[category])
        custom = st.text_input(t['custom_symbol'], placeholder="NFLX, UBER...")
        if custom:
            ticker = custom.upper()
        
        st.markdown("---")
        st.markdown(f"##### {t['date_range']}")
        end = datetime.now()
        start = end - timedelta(days=365)
        start_date = st.date_input(t['from'], value=start)
        end_date = st.date_input(t['to'], value=end)
        
        st.markdown("---")
        st.markdown(f"##### {t['strategy']}")
        strategies = StrategyFactory.get_available_strategies()
        strat_map = {s['key']: s['name'] for s in strategies}
        strat_key = st.selectbox(t['model'], list(strat_map.keys()), format_func=lambda x: strat_map[x])
        
        strat_info = StrategyFactory.get_strategy_info(strat_key)
        params = {}
        for p in strat_info['parameters']:
            label = p['name'].replace('_', ' ').title()
            if p['type'] == 'int':
                params[p['name']] = st.slider(label, p.get('min', 1), p.get('max', 100), p['value'])
            elif p['type'] == 'float':
                params[p['name']] = st.slider(label, float(p.get('min', 0.1)), float(p.get('max', 5.0)), float(p['value']), 0.1)
        
        st.markdown("---")
        st.markdown(f"##### {t['risk_controls']}")
        vix_enabled = st.checkbox(t['vix_filter'], value=True)
        vix_threshold = st.slider(t['vix_threshold'], 20, 50, 30) if vix_enabled else 30
        
        st.markdown("---")
        st.markdown(f"##### {t['capital']}")
        capital = st.number_input(t['initial'], 1000, 1000000, 10000, 1000)
    
    # Fetch Data
    data = fetch_market_data(ticker, start_date, end_date)
    if data.empty:
        st.error(f"{t['no_data']} {ticker}")
        return
    
    # Generate Signals
    strategy = StrategyFactory.create_strategy(strat_key, **params)
    signal_data = strategy.generate_signals(data)
    
    # Apply VIX Filter
    if vix_enabled:
        vix_data = fetch_vix_data(start_date, end_date)
        if not vix_data.empty:
            signal_data = apply_vix_filter(signal_data, vix_data, vix_threshold)
    
    # Calculate Metrics
    metrics = calculate_metrics(signal_data, capital)
    
    # Ticker & Strategy Info
    st.markdown(f"""
        <span class="ticker-badge">{ticker}</span>
        <span class="strategy-badge">{strategy.name}</span>
    """, unsafe_allow_html=True)
    
    # VIX Alert
    if vix_enabled and metrics['vix_days'] > 0:
        st.markdown(f"""
            <div class="alert-card">
                <div class="alert-icon">🛡</div>
                <div class="alert-content">
                    <div class="alert-title">{t['risk_active']}</div>
                    <div class="alert-text">{t['vix_protected_msg'].format(metrics['vix_days'])} {t['current_vix']}: {metrics['current_vix']:.1f}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Metrics Grid
    st.markdown(f"""
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">{t['net_pnl']}</div>
                <div class="metric-value {'positive' if metrics['profit'] >= 0 else 'negative'}">${metrics['profit']:,.2f}</div>
                <div class="metric-delta">{'▲' if metrics['profit_pct'] >= 0 else '▼'} {abs(metrics['profit_pct']):.2f}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">{t['max_drawdown']}</div>
                <div class="metric-value negative">{metrics['max_dd']:.2f}%</div>
                <div class="metric-delta">{t['peak_to_trough']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">{t['total_trades']}</div>
                <div class="metric-value neutral">{metrics['trades']}</div>
                <div class="metric-delta">{t['executed']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">{t['win_rate']}</div>
                <div class="metric-value {'positive' if metrics['win_rate'] >= 50 else 'neutral'}">{metrics['win_rate']:.1f}%</div>
                <div class="metric-delta">{t['success']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">{t['vix_protected']}</div>
                <div class="metric-value neutral">{metrics['vix_days']}</div>
                <div class="metric-delta">{t['sessions']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">{t['final_value']}</div>
                <div class="metric-value neutral">${metrics['final']:,.2f}</div>
                <div class="metric-delta">{t['portfolio']}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Tabs - Added AI Report tab
    ai_report_label = 'AI 深度報告' if st.session_state.lang == 'zh' else 'AI Deep Report'
    tab1, tab2, tab3 = st.tabs([t['chart_analysis'], t['strategy_insights'], ai_report_label])
    
    with tab1:
        st.markdown(f'<div class="section-header">{t["price_signals"]}</div>', unsafe_allow_html=True)
        fig = create_chart(signal_data, show_vix=vix_enabled)
        st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
    
    with tab2:
        insights = generate_insights(metrics, strategy.name, ticker, st.session_state.lang)
        
        st.markdown(f'<div class="section-header">{t["performance_analysis"]}</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class="info-card">
                <div class="info-title">{t['summary']}</div>
                <div class="info-text">{insights['summary']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        if insights['factors']:
            st.markdown(f'<div class="section-header">{t["contributing_factors"]}</div>', unsafe_allow_html=True)
            factors_html = ""
            for f in insights['factors']:
                factors_html += f'<li style="color: #000000; font-weight: 500; padding: 0.5rem 0;">{f}</li>'
            st.markdown(f'''
                <div style="background: #fef3c7; border: 2px solid #f59e0b; border-radius: 12px; padding: 1rem 1.5rem; margin: 1rem 0;">
                    <ul style="margin: 0; padding-left: 1.5rem; color: #000000;">
                        {factors_html}
                    </ul>
                </div>
            ''', unsafe_allow_html=True)
        
        st.markdown(f'<div class="section-header">{t["recommendations"]}</div>', unsafe_allow_html=True)
        recs_html = ""
        for r in insights['recommendations']:
            recs_html += f'<li style="color: #000000; font-weight: 500; padding: 0.5rem 0; border-bottom: 1px solid #e5e7eb;">{r}</li>'
        st.markdown(f'''
            <div style="background: #ffffff; border: 2px solid #10b981; border-radius: 12px; padding: 1rem 1.5rem; margin: 1rem 0; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <ul style="margin: 0; padding-left: 1.5rem; color: #000000;">
                    {recs_html}
                </ul>
            </div>
        ''', unsafe_allow_html=True)
        
        # ═══════════════════════════════════════════════════════════════════
        # AI ANALYSIS SECTION - Strategy, Technical, Fundamental, News
        # ═══════════════════════════════════════════════════════════════════
        st.markdown(f'<div class="ai-badge">{t["ai_analysis"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="section-header">{t["backtest_analysis"]}</div>', unsafe_allow_html=True)
        
        # Generate dynamic analysis content based on metrics
        if st.session_state.lang == 'zh':
            strategy_analysis = f"""
                <ul>
                    <li><strong>策略表現:</strong> {strategy.name} 策略在回測期間產生了 {metrics['profit_pct']:.2f}% 的報酬率</li>
                    <li><strong>風險調整:</strong> 最大回撤 {abs(metrics['max_dd']):.2f}% {'在可接受範圍內' if metrics['max_dd'] > -15 else '較高，需注意風險控制'}</li>
                    <li><strong>訊號效率:</strong> 共觸發 {metrics['trades']} 次交易訊號，勝率 {metrics['win_rate']:.1f}%</li>
                    <li><strong>波動保護:</strong> VIX 過濾器在 {metrics['vix_days']} 個交易日阻擋了高風險進場</li>
                </ul>
            """
            technical_analysis = f"""
                <ul>
                    <li><strong>趨勢分析:</strong> 根據布林通道指標判斷當前市場趨勢與波動性</li>
                    <li><strong>支撐壓力:</strong> 布林上下軌可作為動態支撐與壓力參考位</li>
                    <li><strong>動能指標:</strong> RSI/訊號柱可判斷超買超賣區域</li>
                    <li><strong>進場時機:</strong> {'買入訊號較頻繁' if metrics['trades'] > 20 else '訊號較保守'}</li>
                </ul>
            """
            fundamental_analysis = f"""
                <ul>
                    <li><strong>市值評估:</strong> {ticker} 為{'科技股' if 'AAPL' in ticker or 'MSFT' in ticker or 'GOOGL' in ticker else '標的'}，具有相應的基本面特性</li>
                    <li><strong>產業地位:</strong> 需結合財報數據評估公司競爭力與成長性</li>
                    <li><strong>估值水平:</strong> 建議參考 P/E、P/B 等估值指標進行綜合判斷</li>
                    <li><strong>股息政策:</strong> 長期投資者可考慮股息再投資策略</li>
                </ul>
            """
            news_analysis = f"""
                <ul>
                    <li><strong>市場情緒:</strong> VIX 指數 {metrics['current_vix']:.1f} {'表示市場恐慌情緒較高' if metrics['current_vix'] > 25 else '處於正常水平'}</li>
                    <li><strong>新聞影響:</strong> 建議關注聯準會政策、財報發布等重大事件</li>
                    <li><strong>機構動向:</strong> 可參考機構持股變化與分析師評級</li>
                    <li><strong>社群輿情:</strong> 社群媒體情緒可作為短期交易參考</li>
                </ul>
            """
        else:
            # Calculate additional metrics for display
            avg_daily_return = signal_data['Strategy_Return'].mean() * 100 if 'Strategy_Return' in signal_data.columns else 0
            volatility = signal_data['Strategy_Return'].std() * np.sqrt(252) * 100 if 'Strategy_Return' in signal_data.columns else 0
            sharpe = (avg_daily_return * 252) / volatility if volatility > 0 else 0
            
            # Price range
            price_high = signal_data['High'].max() if 'High' in signal_data.columns else signal_data['Close'].max()
            price_low = signal_data['Low'].min() if 'Low' in signal_data.columns else signal_data['Close'].min()
            current_price = signal_data['Close'].iloc[-1]
            price_change = ((current_price / signal_data['Close'].iloc[0]) - 1) * 100
            
            strategy_analysis = f"""
                <ul>
                    <li><strong>Strategy Performance:</strong> {strategy.name} generated <span style="color: {'#10b981' if metrics['profit_pct'] >= 0 else '#ef4444'}; font-weight: 700;">{metrics['profit_pct']:.2f}%</span> return during backtest period</li>
                    <li><strong>Risk-Adjusted:</strong> Max drawdown of <span style="color: #ef4444; font-weight: 700;">{abs(metrics['max_dd']):.2f}%</span> {'is within acceptable range' if metrics['max_dd'] > -15 else 'is elevated, consider tighter risk controls'}</li>
                    <li><strong>Signal Efficiency:</strong> <span style="font-weight: 700;">{metrics['trades']}</span> trade signals triggered with <span style="font-weight: 700;">{metrics['win_rate']:.1f}%</span> win rate</li>
                    <li><strong>Volatility Protection:</strong> VIX filter blocked entry on <span style="font-weight: 700;">{metrics['vix_days']}</span> high-risk sessions</li>
                </ul>
            """
            technical_analysis = f"""
                <ul>
                    <li><strong>Price Range:</strong> 52-week High: <span style="font-weight: 700;">${price_high:.2f}</span> | Low: <span style="font-weight: 700;">${price_low:.2f}</span></li>
                    <li><strong>Price Change:</strong> <span style="color: {'#10b981' if price_change >= 0 else '#ef4444'}; font-weight: 700;">{price_change:+.2f}%</span> during backtest period</li>
                    <li><strong>Volatility:</strong> Annualized volatility is <span style="font-weight: 700;">{volatility:.1f}%</span></li>
                    <li><strong>Sharpe Ratio:</strong> <span style="font-weight: 700;">{sharpe:.2f}</span> risk-adjusted return</li>
                </ul>
            """
            fundamental_analysis = f"""
                <ul>
                    <li><strong>Ticker:</strong> <span style="font-weight: 700;">{ticker}</span> {'(Tech Stock)' if ticker in ['AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA', 'AMZN'] else ''}</li>
                    <li><strong>Current Price:</strong> <span style="font-weight: 700;">${current_price:.2f}</span></li>
                    <li><strong>Strategy capital:</strong> Initial <span style="font-weight: 700;">${capital:,.0f}</span> → Final <span style="font-weight: 700;">${metrics['final']:,.2f}</span></li>
                    <li><strong>Net Profit:</strong> <span style="color: {'#10b981' if metrics['profit'] >= 0 else '#ef4444'}; font-weight: 700;">${metrics['profit']:,.2f}</span></li>
                </ul>
            """
            news_analysis = f"""
                <ul>
                    <li><strong>Market Sentiment:</strong> VIX at <span style="font-weight: 700;">{metrics['current_vix']:.1f}</span> {'⚠️ (Elevated Fear)' if metrics['current_vix'] > 25 else '✅ (Normal Levels)'}</li>
                    <li><strong>High VIX Days:</strong> <span style="font-weight: 700;">{metrics['vix_days']}</span> days with VIX > 30 were filtered</li>
                    <li><strong>Avg Daily Return:</strong> <span style="font-weight: 700;">{avg_daily_return:.3f}%</span> per trading day</li>
                    <li><strong>Trading Days:</strong> <span style="font-weight: 700;">{len(signal_data)}</span> days analyzed</li>
                </ul>
            """
        
        st.markdown(f"""
            <div class="ai-analysis-grid">
                <div class="analysis-card strategy">
                    <div class="analysis-header">
                        <div class="analysis-icon strategy">📊</div>
                        <h4 class="analysis-title">{t['strategy_perspective']}</h4>
                    </div>
                    <div class="analysis-content">{strategy_analysis}</div>
                </div>
                <div class="analysis-card technical">
                    <div class="analysis-header">
                        <div class="analysis-icon technical">📈</div>
                        <h4 class="analysis-title">{t['technical_perspective']}</h4>
                    </div>
                    <div class="analysis-content">{technical_analysis}</div>
                </div>
                <div class="analysis-card fundamental">
                    <div class="analysis-header">
                        <div class="analysis-icon fundamental">🏢</div>
                        <h4 class="analysis-title">{t['fundamental_perspective']}</h4>
                    </div>
                    <div class="analysis-content">{fundamental_analysis}</div>
                </div>
                <div class="analysis-card news">
                    <div class="analysis-header">
                        <div class="analysis-icon news">📰</div>
                        <h4 class="analysis-title">{t['news_sentiment']}</h4>
                    </div>
                    <div class="analysis-content">{news_analysis}</div>
            </div>
        """, unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════════════
    # TAB 3: AI DEEP REPORT - Full Analysis with Evidence
    # ═══════════════════════════════════════════════════════════════════
    with tab3:
        report_title = 'AI 深度分析報告' if st.session_state.lang == 'zh' else 'AI Deep Analysis Report'
        report_desc = '基於回測數據的詳細時間序列分析、風險指標與智能建議' if st.session_state.lang == 'zh' else 'Detailed timeline analysis, risk metrics, and AI-powered recommendations based on backtest data'
        
        st.markdown(f'<div class="section-header">{report_title}</div>', unsafe_allow_html=True)
        st.markdown(f'<p style="color: #6b7280; margin-bottom: 1.5rem;">{report_desc}</p>', unsafe_allow_html=True)
        
        # Generate button
        generate_btn_text = '📊 生成完整報告' if st.session_state.lang == 'zh' else '📊 Generate Full Report'
        
        if st.button(generate_btn_text, type="primary", use_container_width=True):
            with st.spinner('分析中...' if st.session_state.lang == 'zh' else 'Analyzing...'):
                try:
                    # Generate AI Report
                    report_generator = AIReportGenerator(
                        data=signal_data,
                        metrics=metrics,
                        strategy_name=strategy.name,
                        ticker=ticker,
                        capital=capital,
                        lang=st.session_state.lang
                    )
                    
                    # Generate and display HTML report using components.html for proper rendering
                    html_report = report_generator.generate_html_report()
                    # Wrap in full HTML document for proper rendering
                    full_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="utf-8">
                        <style>
                            * {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }}
                            body {{ margin: 0; padding: 0; background: transparent; }}
                        </style>
                    </head>
                    <body>
                        {html_report}
                    </body>
                    </html>
                    """
                    components.html(full_html, height=800, scrolling=True)
                    
                    # Also store full report data for potential export
                    full_report = report_generator.generate_full_report()
                    st.session_state['last_report'] = full_report
                    
                    # Success message
                    success_msg = '✅ 報告生成完成！' if st.session_state.lang == 'zh' else '✅ Report generated successfully!'
                    st.success(success_msg)
                    
                except Exception as e:
                    error_msg = f'生成報告時發生錯誤: {str(e)}' if st.session_state.lang == 'zh' else f'Error generating report: {str(e)}'
                    st.error(error_msg)
        
        # Show last generated report if exists
        elif 'last_report' in st.session_state:
            try:
                report_generator = AIReportGenerator(
                    data=signal_data,
                    metrics=metrics,
                    strategy_name=strategy.name,
                    ticker=ticker,
                    capital=capital,
                    lang=st.session_state.lang
                )
                html_report = report_generator.generate_html_report()
                full_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <style>
                        * {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }}
                        body {{ margin: 0; padding: 0; background: transparent; }}
                    </style>
                </head>
                <body>
                    {html_report}
                </body>
                </html>
                """
                components.html(full_html, height=800, scrolling=True)
            except:
                pass
        else:
            # Placeholder when no report generated yet
            placeholder_text = '點擊上方按鈕生成詳細 AI 分析報告，包含時間序列績效分析、風險指標和智能交易建議。' if st.session_state.lang == 'zh' else 'Click the button above to generate a detailed AI analysis report including timeline performance analysis, risk metrics, and intelligent trading recommendations.'
            st.info(placeholder_text)
    
    # ═══════════════════════════════════════════════════════════════════
    # INCEPTION SPINNING TOP - Dynamic Quality Indicator
    # ═══════════════════════════════════════════════════════════════════
    st.markdown("""
        <div class="inception-container" title="Quantamental Analysis Running...">
            <div class="spinning-top">
                <div class="top-stem"></div>
                <div class="top-point"></div>
            </div>
            <div class="top-shadow"></div>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

