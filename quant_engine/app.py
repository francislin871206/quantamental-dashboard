"""
Quantamental Trading Platform - Main Entry Point
Multi-page Streamlit application with login, backtesting, and virtual trading.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import yfinance as yf
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quant_engine.virtual_trading import VirtualTradingEngine
from quant_engine.strategy_factory import StrategyFactory
from quant_engine.ai_report import AIReportGenerator

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG & SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Quantamental Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize trading engine
if 'trading_engine' not in st.session_state:
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'virtual_trading.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    st.session_state.trading_engine = VirtualTradingEngine(db_path=db_path)

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'lang' not in st.session_state:
    st.session_state.lang = 'en'

# ═══════════════════════════════════════════════════════════════════════════════
# STYLES
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* Premium minimal design */
    .stApp {
        background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 50%, #f0f0f0 100%);
    }
    
    .login-container {
        max-width: 400px;
        margin: 4rem auto;
        padding: 2.5rem;
        background: white;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    
    .login-header {
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    
    .login-subtitle {
        text-align: center;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .welcome-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TRANSLATIONS
# ═══════════════════════════════════════════════════════════════════════════════
TRANSLATIONS = {
    'en': {
        'title': 'Quantamental Platform',
        'subtitle': 'AI-Powered Trading Intelligence',
        'login': 'Login',
        'register': 'Register',
        'username': 'Username',
        'password': 'Password',
        'login_btn': 'Sign In',
        'register_btn': 'Create Account',
        'welcome': 'Welcome',
        'features': 'Features',
        'backtesting': '📊 Backtesting',
        'backtesting_desc': 'Test trading strategies with historical data',
        'virtual_trading': '📈 Virtual Trading',
        'virtual_trading_desc': 'Practice trading with paper money',
        'ai_reports': '🤖 AI Reports',
        'ai_reports_desc': 'Get intelligent analysis and recommendations',
        'login_error': 'Invalid username or password',
        'register_error': 'Username already exists',
        'register_success': 'Account created successfully! Please login.',
        'logout': 'Logout',
        'guest': 'Continue as Guest',
    },
    'zh': {
        'title': 'Quantamental 量化平台',
        'subtitle': 'AI 驅動的智慧交易',
        'login': '登入',
        'register': '註冊',
        'username': '用戶名',
        'password': '密碼',
        'login_btn': '登入',
        'register_btn': '建立帳號',
        'welcome': '歡迎',
        'features': '功能',
        'backtesting': '📊 回測分析',
        'backtesting_desc': '使用歷史數據測試交易策略',
        'virtual_trading': '📈 虛擬交易',
        'virtual_trading_desc': '使用模擬資金練習交易',
        'ai_reports': '🤖 AI 分析報告',
        'ai_reports_desc': '獲取智能分析與建議',
        'login_error': '用戶名或密碼錯誤',
        'register_error': '用戶名已存在',
        'register_success': '帳號創建成功！請登入。',
        'logout': '登出',
        'guest': '以訪客身分繼續',
    }
}

def get_translation():
    return TRANSLATIONS[st.session_state.lang]

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    t = get_translation()
    
    # Language toggle in sidebar
    st.sidebar.markdown("### 🌐 Language")
    lang_options = {"English": "en", "中文": "zh"}
    selected_lang = st.sidebar.radio(
        "Select Language",
        list(lang_options.keys()),
        index=0 if st.session_state.lang == 'en' else 1,
        label_visibility="collapsed"
    )
    if lang_options[selected_lang] != st.session_state.lang:
        st.session_state.lang = lang_options[selected_lang]
        st.rerun()
    
    # Check if logged in
    if st.session_state.user_id:
        show_main_menu()
    else:
        show_login_page()


def show_login_page():
    """Display login/register page"""
    t = get_translation()
    engine = st.session_state.trading_engine
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
            <div class="login-container">
                <div class="login-header">{t['title']}</div>
                <div class="login-subtitle">{t['subtitle']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs([t['login'], t['register']])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input(t['username'])
                password = st.text_input(t['password'], type="password")
                
                if st.form_submit_button(t['login_btn'], use_container_width=True, type="primary"):
                    user_id = engine.authenticate_user(username, password)
                    if user_id:
                        st.session_state.user_id = user_id
                        st.session_state.username = username
                        st.rerun()
                    else:
                        st.error(t['login_error'])
        
        with tab2:
            with st.form("register_form"):
                new_username = st.text_input(t['username'], key="reg_user")
                new_password = st.text_input(t['password'], type="password", key="reg_pass")
                
                if st.form_submit_button(t['register_btn'], use_container_width=True):
                    user_id = engine.create_user(new_username, new_password)
                    if user_id:
                        st.success(t['register_success'])
                    else:
                        st.error(t['register_error'])
        
        # Guest access
        st.markdown("---")
        if st.button(t['guest'], use_container_width=True):
            # Create or get guest account
            guest_id = engine.authenticate_user("guest", "guest123")
            if not guest_id:
                guest_id = engine.create_user("guest", "guest123")
            st.session_state.user_id = guest_id
            st.session_state.username = "guest"
            st.rerun()
    
    # Features showcase
    st.markdown("---")
    st.markdown(f"### {t['features']}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <h4>{t['backtesting']}</h4>
                <p style="color: #6b7280;">{t['backtesting_desc']}</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">📈</div>
                <h4>{t['virtual_trading']}</h4>
                <p style="color: #6b7280;">{t['virtual_trading_desc']}</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <h4>{t['ai_reports']}</h4>
                <p style="color: #6b7280;">{t['ai_reports_desc']}</p>
            </div>
        """, unsafe_allow_html=True)


def show_main_menu():
    """Display main menu after login"""
    t = get_translation()
    
    st.sidebar.markdown(f"### 👤 {t['welcome']}, {st.session_state.username}!")
    
    if st.sidebar.button(t['logout'], use_container_width=True):
        st.session_state.user_id = None
        st.session_state.username = None
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Navigation
    page_options = {
        t['backtesting']: "backtesting",
        t['virtual_trading']: "virtual_trading",
        t['ai_reports']: "ai_reports"
    }
    
    selected_page = st.sidebar.radio(
        "Navigation",
        list(page_options.keys()),
        label_visibility="collapsed"
    )
    
    page = page_options[selected_page]
    
    if page == "backtesting":
        show_backtesting()
    elif page == "virtual_trading":
        show_virtual_trading()
    elif page == "ai_reports":
        show_ai_reports()


def show_virtual_trading():
    """Display virtual trading interface"""
    t = get_translation()
    engine = st.session_state.trading_engine
    user_id = st.session_state.user_id
    
    # Get portfolio summary
    portfolio = engine.get_portfolio_value(user_id)
    
    # Header
    title = "虛擬交易" if st.session_state.lang == 'zh' else "Virtual Trading"
    st.markdown(f"## 💰 {title}")
    
    # Portfolio metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        label = "投資組合價值" if st.session_state.lang == 'zh' else "Portfolio Value"
        st.metric(label, f"${portfolio['total_value']:,.2f}")
    
    with col2:
        label = "現金餘額" if st.session_state.lang == 'zh' else "Cash Balance"
        st.metric(label, f"${portfolio['cash']:,.2f}")
    
    with col3:
        label = "總損益" if st.session_state.lang == 'zh' else "Total P&L"
        delta_color = "normal" if portfolio['total_pnl'] >= 0 else "inverse"
        st.metric(label, f"${portfolio['total_pnl']:,.2f}", 
                  f"{portfolio['total_pnl_pct']:+.2f}%")
    
    with col4:
        label = "持倉市值" if st.session_state.lang == 'zh' else "Positions Value"
        st.metric(label, f"${portfolio['positions_value']:,.2f}")
    
    st.markdown("---")
    
    # Trading form
    col1, col2 = st.columns([1, 2])
    
    with col1:
        trade_label = "下單交易" if st.session_state.lang == 'zh' else "Place Order"
        st.markdown(f"### {trade_label}")
        
        with st.form("trade_form"):
            ticker = st.text_input("Ticker", value="AAPL").upper()
            
            order_type_options = ["買入 (Buy)", "賣出 (Sell)"] if st.session_state.lang == 'zh' else ["Buy", "Sell"]
            order_type = st.selectbox("Order Type", order_type_options)
            order_type_val = 'buy' if 'Buy' in order_type or '買入' in order_type else 'sell'
            
            quantity = st.number_input("Quantity", min_value=1, value=10)
            
            submit_label = "執行交易" if st.session_state.lang == 'zh' else "Execute Trade"
            if st.form_submit_button(submit_label, use_container_width=True, type="primary"):
                result = engine.place_order(user_id, ticker, order_type_val, quantity)
                if result['success']:
                    action = "買入" if order_type_val == 'buy' else "賣出"
                    action_en = "Bought" if order_type_val == 'buy' else "Sold"
                    if st.session_state.lang == 'zh':
                        st.success(f"✅ 成功{action} {quantity} 股 {ticker} @ ${result['price']:.2f}")
                    else:
                        st.success(f"✅ {action_en} {quantity} shares of {ticker} @ ${result['price']:.2f}")
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")
        
        # Reset button
        st.markdown("---")
        reset_label = "重置帳戶" if st.session_state.lang == 'zh' else "Reset Account"
        if st.button(reset_label, use_container_width=True, type="secondary"):
            engine.reset_account(user_id)
            st.success("Account reset to initial state")
            st.rerun()
    
    with col2:
        # Positions
        positions_label = "持倉" if st.session_state.lang == 'zh' else "Positions"
        st.markdown(f"### {positions_label}")
        
        positions = engine.get_positions(user_id)
        
        if positions:
            pos_data = []
            for p in positions:
                pos_data.append({
                    'Ticker': p.ticker,
                    'Quantity': p.quantity,
                    'Avg Cost': f"${p.avg_cost:.2f}",
                    'Current': f"${p.current_price:.2f}",
                    'P&L': f"${p.unrealized_pnl:,.2f}",
                    'P&L %': f"{p.unrealized_pnl_pct:+.2f}%"
                })
            
            df = pd.DataFrame(pos_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            no_positions_msg = "目前沒有持倉" if st.session_state.lang == 'zh' else "No positions yet"
            st.info(no_positions_msg)
        
        # Order history
        st.markdown("---")
        history_label = "交易記錄" if st.session_state.lang == 'zh' else "Trade History"
        st.markdown(f"### {history_label}")
        
        orders = engine.get_orders(user_id, limit=10)
        
        if orders:
            order_data = []
            for o in orders:
                order_data.append({
                    'Time': o['timestamp'][:16],
                    'Action': o['order_type'].upper(),
                    'Ticker': o['ticker'],
                    'Qty': o['quantity'],
                    'Price': f"${o['price']:.2f}"
                })
            
            df = pd.DataFrame(order_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            no_orders_msg = "目前沒有交易記錄" if st.session_state.lang == 'zh' else "No trades yet"
            st.info(no_orders_msg)


def show_backtesting():
    """Display backtesting interface with strategy selection and charts"""
    title = "📊 回測分析" if st.session_state.lang == 'zh' else "📊 Backtesting"
    st.markdown(f"## {title}")
    
    # Sidebar controls for backtesting
    st.sidebar.markdown("---")
    settings_label = "回測設定" if st.session_state.lang == 'zh' else "Backtest Settings"
    st.sidebar.markdown(f"### ⚙️ {settings_label}")
    
    # Ticker input
    ticker_label = "股票代碼" if st.session_state.lang == 'zh' else "Ticker Symbol"
    ticker = st.sidebar.text_input(ticker_label, value="AAPL").upper()
    
    # Date range
    date_label = "日期範圍" if st.session_state.lang == 'zh' else "Date Range"
    st.sidebar.markdown(f"**{date_label}**")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Start", datetime.now() - timedelta(days=365))
    with col2:
        end_date = st.date_input("End", datetime.now())
    
    # Strategy selection
    strategy_label = "選擇策略" if st.session_state.lang == 'zh' else "Select Strategy"
    available_strategies = StrategyFactory.get_available_strategies()
    strategy_names = {s['name']: s['key'] for s in available_strategies}
    
    selected_strategy_name = st.sidebar.selectbox(strategy_label, list(strategy_names.keys()))
    strategy_key = strategy_names[selected_strategy_name]
    
    # Capital
    capital_label = "初始資金" if st.session_state.lang == 'zh' else "Initial Capital"
    capital = st.sidebar.number_input(capital_label, min_value=1000, value=10000, step=1000)
    
    # Run backtest button
    run_label = "🚀 執行回測" if st.session_state.lang == 'zh' else "🚀 Run Backtest"
    
    if st.sidebar.button(run_label, use_container_width=True, type="primary"):
        with st.spinner("正在執行回測..." if st.session_state.lang == 'zh' else "Running backtest..."):
            try:
                # Fetch data
                data = yf.download(ticker, start=start_date, end=end_date)
                
                if data.empty:
                    st.error("無法獲取數據" if st.session_state.lang == 'zh' else "Could not fetch data")
                    return
                
                data = data.reset_index()
                if 'Adj Close' in data.columns:
                    data['Close'] = data['Adj Close']
                
                # Flatten MultiIndex columns if present
                if hasattr(data.columns, 'levels'):
                    data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
                
                # VIX data
                try:
                    vix = yf.download("^VIX", start=start_date, end=end_date)
                    if not vix.empty:
                        vix = vix.reset_index()
                        if hasattr(vix.columns, 'levels'):
                            vix.columns = [col[0] if isinstance(col, tuple) else col for col in vix.columns]
                        data['VIX'] = vix['Close'].values[:len(data)] if len(vix) >= len(data) else 20
                    else:
                        data['VIX'] = 20
                except:
                    data['VIX'] = 20
                
                # Create strategy and generate signals
                strategy = StrategyFactory.create_strategy(strategy_key)
                signal_data = strategy.generate_signals(data)
                
                # Calculate metrics
                signal_data['Return'] = signal_data['Close'].pct_change()
                signal_data['Strategy_Return'] = signal_data['Signal'].shift(1) * signal_data['Return']
                signal_data['Cumulative'] = (1 + signal_data['Strategy_Return'].fillna(0)).cumprod()
                signal_data['Portfolio'] = capital * signal_data['Cumulative']
                signal_data['Peak'] = signal_data['Portfolio'].cummax()
                signal_data['Drawdown'] = (signal_data['Portfolio'] - signal_data['Peak']) / signal_data['Peak'] * 100
                
                final_value = signal_data['Portfolio'].iloc[-1]
                profit = final_value - capital
                profit_pct = (final_value / capital - 1) * 100
                max_dd = signal_data['Drawdown'].min()
                trades = (signal_data['Signal'].diff().abs() > 0).sum()
                winning = (signal_data['Strategy_Return'] > 0).sum()
                total_trading = (signal_data['Strategy_Return'] != 0).sum()
                win_rate = (winning / total_trading * 100) if total_trading > 0 else 0
                
                # Store in session state for AI report
                st.session_state['backtest_data'] = signal_data
                st.session_state['backtest_metrics'] = {
                    'profit': profit, 'profit_pct': profit_pct, 'max_dd': max_dd,
                    'trades': trades, 'win_rate': win_rate, 'final': final_value,
                    'vix_days': (signal_data['VIX'] > 30).sum()
                }
                st.session_state['backtest_strategy'] = strategy
                st.session_state['backtest_ticker'] = ticker
                st.session_state['backtest_capital'] = capital
                
                # Display metrics
                st.markdown("### 📈 " + ("績效指標" if st.session_state.lang == 'zh' else "Performance Metrics"))
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    label = "總損益" if st.session_state.lang == 'zh' else "Total P&L"
                    st.metric(label, f"${profit:,.2f}", f"{profit_pct:+.2f}%")
                with col2:
                    label = "最大回撤" if st.session_state.lang == 'zh' else "Max Drawdown"
                    st.metric(label, f"{max_dd:.2f}%")
                with col3:
                    label = "交易次數" if st.session_state.lang == 'zh' else "Total Trades"
                    st.metric(label, trades)
                with col4:
                    label = "勝率" if st.session_state.lang == 'zh' else "Win Rate"
                    st.metric(label, f"{win_rate:.1f}%")
                
                # Chart
                st.markdown("### 📊 " + ("價格走勢與訊號" if st.session_state.lang == 'zh' else "Price & Signals"))
                
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                    vertical_spacing=0.05, row_heights=[0.7, 0.3])
                
                # Price with signals
                fig.add_trace(go.Scatter(x=signal_data['Date'], y=signal_data['Close'],
                                         mode='lines', name='Price', line=dict(color='#10b981')), row=1, col=1)
                
                # Buy signals
                buys = signal_data[(signal_data['Signal'] == 1) & (signal_data['Signal'].shift(1) != 1)]
                fig.add_trace(go.Scatter(x=buys['Date'], y=buys['Close'],
                                         mode='markers', name='Buy', marker=dict(color='#22c55e', size=10, symbol='triangle-up')), row=1, col=1)
                
                # Sell signals
                sells = signal_data[(signal_data['Signal'] == -1) | ((signal_data['Signal'] == 0) & (signal_data['Signal'].shift(1) == 1))]
                fig.add_trace(go.Scatter(x=sells['Date'], y=sells['Close'],
                                         mode='markers', name='Sell', marker=dict(color='#ef4444', size=10, symbol='triangle-down')), row=1, col=1)
                
                # Drawdown
                fig.add_trace(go.Scatter(x=signal_data['Date'], y=signal_data['Drawdown'],
                                         fill='tozeroy', name='Drawdown', line=dict(color='#ef4444')), row=2, col=1)
                
                fig.update_layout(height=600, template='plotly_white', showlegend=True,
                                  legend=dict(orientation="h", yanchor="bottom", y=1.02))
                fig.update_xaxes(showgrid=False)
                fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0')
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.success("✅ " + ("回測完成！" if st.session_state.lang == 'zh' else "Backtest complete!"))
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    else:
        # Show instruction if no backtest run yet
        if 'backtest_data' not in st.session_state:
            instruction = "使用側邊欄設定參數並執行回測" if st.session_state.lang == 'zh' else "Use the sidebar to configure parameters and run backtest"
            st.info(f"👈 {instruction}")


def show_ai_reports():
    """Display AI analysis reports"""
    title = "🤖 AI 深度報告" if st.session_state.lang == 'zh' else "🤖 AI Deep Report"
    st.markdown(f"## {title}")
    
    if 'backtest_data' not in st.session_state:
        instruction = "請先執行回測以生成 AI 分析報告" if st.session_state.lang == 'zh' else "Please run a backtest first to generate AI analysis report"
        st.warning(f"⚠️ {instruction}")
        return
    
    # Generate report button
    generate_label = "📊 生成 AI 報告" if st.session_state.lang == 'zh' else "📊 Generate AI Report"
    
    if st.button(generate_label, type="primary", use_container_width=True):
        with st.spinner("分析中..." if st.session_state.lang == 'zh' else "Analyzing..."):
            try:
                report_generator = AIReportGenerator(
                    data=st.session_state['backtest_data'],
                    metrics=st.session_state['backtest_metrics'],
                    strategy_name=st.session_state['backtest_strategy'].name,
                    ticker=st.session_state['backtest_ticker'],
                    capital=st.session_state['backtest_capital'],
                    lang=st.session_state.lang
                )
                
                html_report = report_generator.generate_html_report()
                st.markdown(html_report, unsafe_allow_html=True)
                st.success("✅ " + ("報告生成完成！" if st.session_state.lang == 'zh' else "Report generated!"))
                
            except Exception as e:
                st.error(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
