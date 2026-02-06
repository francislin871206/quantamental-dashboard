"""
AI Analysis Report Engine
Generates comprehensive, data-driven trading analysis reports with:
- Timeline-based performance breakdown
- Numerical evidence and proof
- Strategy signal quality scoring
- Actionable recommendations with confidence scores
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class TradeAnalysis:
    """Individual trade analysis with evidence"""
    entry_date: datetime
    exit_date: Optional[datetime]
    entry_price: float
    exit_price: Optional[float]
    signal_type: str  # 'buy' or 'sell'
    return_pct: float
    holding_days: int
    market_regime: str  # 'bullish', 'bearish', 'sideways'
    vix_at_entry: float
    reason: str


@dataclass
class PeriodAnalysis:
    """Analysis for a specific time period"""
    period_name: str
    start_date: datetime
    end_date: datetime
    total_return: float
    num_trades: int
    win_rate: float
    max_drawdown: float
    avg_vix: float
    market_regime: str
    key_events: List[str] = field(default_factory=list)
    performance_drivers: List[str] = field(default_factory=list)


class AIReportGenerator:
    """
    Generates comprehensive AI-driven trading analysis reports
    with timeline evidence and numerical proof.
    """
    
    def __init__(self, data: pd.DataFrame, metrics: Dict, strategy_name: str, 
                 ticker: str, capital: float = 10000, lang: str = 'en'):
        self.data = data.copy()
        self.metrics = metrics
        self.strategy_name = strategy_name
        self.ticker = ticker
        self.capital = capital
        self.lang = lang
        
        # Ensure Date is datetime
        if 'Date' in self.data.columns:
            self.data['Date'] = pd.to_datetime(self.data['Date'])
        
        # Calculate additional metrics for analysis
        self._prepare_data()
    
    def _prepare_data(self):
        """Prepare data with additional calculated fields"""
        df = self.data
        
        # Daily returns
        df['Daily_Return'] = df['Close'].pct_change()
        
        # Strategy returns
        df['Strategy_Return'] = df['Signal'].shift(1) * df['Daily_Return']
        df['Strategy_Return'] = df['Strategy_Return'].fillna(0)
        
        # Cumulative returns
        df['Cumulative_Return'] = (1 + df['Strategy_Return']).cumprod() - 1
        df['Buy_Hold_Return'] = (1 + df['Daily_Return']).cumprod() - 1
        
        # Portfolio value
        df['Portfolio_Value'] = self.capital * (1 + df['Cumulative_Return'])
        
        # Drawdown
        df['Peak'] = df['Portfolio_Value'].cummax()
        df['Drawdown'] = (df['Portfolio_Value'] - df['Peak']) / df['Peak'] * 100
        
        # Rolling metrics
        df['Rolling_Volatility'] = df['Daily_Return'].rolling(20).std() * np.sqrt(252)
        df['Rolling_Sharpe'] = (df['Strategy_Return'].rolling(60).mean() * 252) / \
                               (df['Strategy_Return'].rolling(60).std() * np.sqrt(252) + 1e-10)
        
        # Market regime detection
        df['SMA_50'] = df['Close'].rolling(50).mean()
        df['SMA_200'] = df['Close'].rolling(200).mean()
        df['Market_Regime'] = 'sideways'
        df.loc[df['Close'] > df['SMA_50'], 'Market_Regime'] = 'bullish'
        df.loc[df['Close'] < df['SMA_50'], 'Market_Regime'] = 'bearish'
        
        # Month/Week for grouping
        df['YearMonth'] = df['Date'].dt.to_period('M')
        df['YearWeek'] = df['Date'].dt.to_period('W')
        
        self.data = df
    
    def _identify_trades(self) -> List[TradeAnalysis]:
        """Identify and analyze individual trades"""
        trades = []
        df = self.data
        
        in_position = False
        entry_idx = None
        
        for i in range(len(df)):
            signal = df['Signal'].iloc[i]
            
            if signal == 1 and not in_position:
                # Entry
                in_position = True
                entry_idx = i
            elif (signal == -1 or signal == 0) and in_position and entry_idx is not None:
                # Exit
                entry_row = df.iloc[entry_idx]
                exit_row = df.iloc[i]
                
                entry_price = entry_row['Close']
                exit_price = exit_row['Close']
                return_pct = ((exit_price - entry_price) / entry_price) * 100
                holding_days = (exit_row['Date'] - entry_row['Date']).days
                
                vix_at_entry = entry_row.get('VIX', 0) if 'VIX' in df.columns else 0
                
                # Determine reason for performance
                if return_pct > 5:
                    reason = "Strong trend continuation after entry signal"
                elif return_pct > 0:
                    reason = "Moderate price appreciation during holding period"
                elif return_pct > -5:
                    reason = "Minor pullback, strategy exit triggered near breakeven"
                else:
                    reason = "Adverse price movement, possible false signal or market reversal"
                
                trade = TradeAnalysis(
                    entry_date=entry_row['Date'],
                    exit_date=exit_row['Date'],
                    entry_price=entry_price,
                    exit_price=exit_price,
                    signal_type='buy',
                    return_pct=return_pct,
                    holding_days=holding_days,
                    market_regime=entry_row.get('Market_Regime', 'unknown'),
                    vix_at_entry=vix_at_entry,
                    reason=reason
                )
                trades.append(trade)
                in_position = False
                entry_idx = None
        
        return trades
    
    def _analyze_periods(self) -> List[PeriodAnalysis]:
        """Analyze performance by time periods (monthly)"""
        periods = []
        df = self.data
        
        for period, group in df.groupby('YearMonth'):
            if len(group) < 5:  # Skip periods with too few data points
                continue
            
            # Calculate period metrics
            period_return = group['Strategy_Return'].sum() * 100
            trades_in_period = (group['Signal'].diff().abs() > 0).sum()
            
            winning_days = (group['Strategy_Return'] > 0).sum()
            total_days = (group['Strategy_Return'] != 0).sum()
            win_rate = (winning_days / total_days * 100) if total_days > 0 else 0
            
            max_dd = group['Drawdown'].min()
            avg_vix = group['VIX'].mean() if 'VIX' in group.columns else 0
            
            # Determine market regime for period
            regime_counts = group['Market_Regime'].value_counts()
            dominant_regime = regime_counts.index[0] if len(regime_counts) > 0 else 'unknown'
            
            # Identify performance drivers
            drivers = []
            if period_return > 5:
                drivers.append("Strong trend alignment with signals")
            if avg_vix < 20:
                drivers.append("Low volatility environment favorable for strategy")
            elif avg_vix > 30:
                drivers.append("High volatility created both opportunities and risks")
            if win_rate > 60:
                drivers.append("High signal accuracy during this period")
            
            period_analysis = PeriodAnalysis(
                period_name=str(period),
                start_date=group['Date'].min(),
                end_date=group['Date'].max(),
                total_return=period_return,
                num_trades=trades_in_period,
                win_rate=win_rate,
                max_drawdown=max_dd,
                avg_vix=avg_vix,
                market_regime=dominant_regime,
                performance_drivers=drivers
            )
            periods.append(period_analysis)
        
        return periods
    
    def _calculate_risk_metrics(self) -> Dict:
        """Calculate comprehensive risk-adjusted metrics"""
        df = self.data
        returns = df['Strategy_Return'].dropna()
        
        # Annualized return
        total_days = len(returns)
        total_return = (1 + returns).prod() - 1
        annual_return = (1 + total_return) ** (252 / total_days) - 1 if total_days > 0 else 0
        
        # Volatility
        daily_vol = returns.std()
        annual_vol = daily_vol * np.sqrt(252)
        
        # Sharpe Ratio (assuming risk-free rate of 4%)
        risk_free = 0.04
        sharpe = (annual_return - risk_free) / annual_vol if annual_vol > 0 else 0
        
        # Sortino Ratio (downside deviation)
        downside_returns = returns[returns < 0]
        downside_vol = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0.01
        sortino = (annual_return - risk_free) / downside_vol if downside_vol > 0 else 0
        
        # Calmar Ratio
        max_dd = abs(df['Drawdown'].min()) / 100
        calmar = annual_return / max_dd if max_dd > 0 else 0
        
        # Win/Loss analysis
        winning_trades = returns[returns > 0]
        losing_trades = returns[returns < 0]
        avg_win = winning_trades.mean() * 100 if len(winning_trades) > 0 else 0
        avg_loss = losing_trades.mean() * 100 if len(losing_trades) > 0 else 0
        profit_factor = abs(winning_trades.sum() / losing_trades.sum()) if len(losing_trades) > 0 and losing_trades.sum() != 0 else float('inf')
        
        return {
            'annual_return': annual_return * 100,
            'annual_volatility': annual_vol * 100,
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'calmar_ratio': calmar,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': df['Drawdown'].min(),
            'recovery_time': self._calculate_recovery_time(),
        }
    
    def _calculate_recovery_time(self) -> int:
        """Calculate average recovery time from drawdowns"""
        df = self.data
        in_drawdown = False
        dd_start = None
        recovery_times = []
        
        for i in range(len(df)):
            if df['Drawdown'].iloc[i] < -5 and not in_drawdown:
                in_drawdown = True
                dd_start = i
            elif df['Drawdown'].iloc[i] >= -1 and in_drawdown:
                recovery_times.append(i - dd_start)
                in_drawdown = False
        
        return int(np.mean(recovery_times)) if recovery_times else 0
    
    def _generate_strategy_insights(self) -> Dict:
        """Generate strategy-specific insights"""
        trades = self._identify_trades()
        periods = self._analyze_periods()
        
        # Best and worst periods
        if periods:
            best_period = max(periods, key=lambda p: p.total_return)
            worst_period = min(periods, key=lambda p: p.total_return)
        else:
            best_period = worst_period = None
        
        # Best and worst trades
        if trades:
            best_trade = max(trades, key=lambda t: t.return_pct)
            worst_trade = min(trades, key=lambda t: t.return_pct)
        else:
            best_trade = worst_trade = None
        
        # Market regime analysis
        regime_performance = {}
        for regime in ['bullish', 'bearish', 'sideways']:
            regime_data = self.data[self.data['Market_Regime'] == regime]
            if len(regime_data) > 0:
                regime_return = regime_data['Strategy_Return'].sum() * 100
                regime_performance[regime] = regime_return
        
        return {
            'best_period': best_period,
            'worst_period': worst_period,
            'best_trade': best_trade,
            'worst_trade': worst_trade,
            'regime_performance': regime_performance,
            'total_trades': len(trades),
            'winning_trades': len([t for t in trades if t.return_pct > 0]),
            'losing_trades': len([t for t in trades if t.return_pct < 0]),
        }
    
    def _generate_recommendations(self, risk_metrics: Dict, insights: Dict) -> List[Dict]:
        """Generate actionable recommendations with confidence scores"""
        recommendations = []
        
        # Sharpe ratio based recommendations
        if risk_metrics['sharpe_ratio'] < 0.5:
            recommendations.append({
                'category': 'risk_adjustment',
                'priority': 'high',
                'confidence': 85,
                'recommendation': 'Consider adding trend filter to reduce false signals',
                'evidence': f"Sharpe Ratio of {risk_metrics['sharpe_ratio']:.2f} is below optimal threshold of 1.0",
                'recommendation_zh': '建議添加趨勢過濾器以減少假訊號',
            })
        
        # Drawdown based recommendations
        if risk_metrics['max_drawdown'] < -20:
            recommendations.append({
                'category': 'position_sizing',
                'priority': 'high',
                'confidence': 90,
                'recommendation': 'Reduce position size or add stop-loss rules',
                'evidence': f"Max drawdown of {risk_metrics['max_drawdown']:.2f}% exceeds 20% threshold",
                'recommendation_zh': '建議減少部位大小或添加停損規則',
            })
        
        # Win rate based recommendations
        if self.metrics.get('win_rate', 0) < 45:
            recommendations.append({
                'category': 'signal_quality',
                'priority': 'medium',
                'confidence': 75,
                'recommendation': 'Add confirmation indicator before entry (RSI, MACD)',
                'evidence': f"Win rate of {self.metrics.get('win_rate', 0):.1f}% suggests signal timing needs improvement",
                'recommendation_zh': '建議在進場前添加確認指標 (RSI, MACD)',
            })
        
        # Regime-specific recommendations
        regime_perf = insights.get('regime_performance', {})
        if regime_perf.get('bearish', 0) < -10:
            recommendations.append({
                'category': 'market_regime',
                'priority': 'medium',
                'confidence': 80,
                'recommendation': 'Consider disabling strategy during bearish regimes (SMA50 < SMA200)',
                'evidence': f"Strategy lost {abs(regime_perf.get('bearish', 0)):.2f}% during bearish periods",
                'recommendation_zh': '建議在熊市期間停用策略 (當SMA50低於SMA200時)',
            })
        
        # VIX-based recommendations
        if self.metrics.get('vix_days', 0) > 30:
            recommendations.append({
                'category': 'volatility',
                'priority': 'low',
                'confidence': 70,
                'recommendation': 'VIX filter is effective; consider tightening threshold to 25',
                'evidence': f"VIX filter protected against {self.metrics.get('vix_days', 0)} high-volatility days",
                'recommendation_zh': 'VIX過濾器有效；建議將閾值收緊至25',
            })
        
        return sorted(recommendations, key=lambda x: x['confidence'], reverse=True)
    
    def generate_full_report(self) -> Dict:
        """Generate the complete AI analysis report"""
        trades = self._identify_trades()
        periods = self._analyze_periods()
        risk_metrics = self._calculate_risk_metrics()
        insights = self._generate_strategy_insights()
        recommendations = self._generate_recommendations(risk_metrics, insights)
        
        # Create timeline chart data
        timeline_data = self.data[['Date', 'Close', 'Portfolio_Value', 'Drawdown', 'Signal']].copy()
        timeline_data = timeline_data.dropna()
        
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'ticker': self.ticker,
                'strategy': self.strategy_name,
                'period': {
                    'start': self.data['Date'].min().strftime('%Y-%m-%d'),
                    'end': self.data['Date'].max().strftime('%Y-%m-%d'),
                    'trading_days': len(self.data),
                },
                'initial_capital': self.capital,
            },
            'summary': {
                'total_return': self.metrics.get('profit_pct', 0),
                'final_value': self.metrics.get('final', self.capital),
                'vs_buy_hold': self.metrics.get('profit_pct', 0) - (self.data['Buy_Hold_Return'].iloc[-1] * 100 if len(self.data) > 0 else 0),
                'total_trades': insights['total_trades'],
                'win_rate': self.metrics.get('win_rate', 0),
            },
            'risk_metrics': risk_metrics,
            'timeline': {
                'monthly_performance': [
                    {
                        'period': p.period_name,
                        'return': p.total_return,
                        'trades': p.num_trades,
                        'win_rate': p.win_rate,
                        'regime': p.market_regime,
                        'drivers': p.performance_drivers,
                    } for p in periods
                ],
                'best_period': {
                    'name': insights['best_period'].period_name if insights['best_period'] else 'N/A',
                    'return': insights['best_period'].total_return if insights['best_period'] else 0,
                } if insights['best_period'] else None,
                'worst_period': {
                    'name': insights['worst_period'].period_name if insights['worst_period'] else 'N/A',
                    'return': insights['worst_period'].total_return if insights['worst_period'] else 0,
                } if insights['worst_period'] else None,
            },
            'trades': {
                'total': insights['total_trades'],
                'winning': insights['winning_trades'],
                'losing': insights['losing_trades'],
                'best_trade': {
                    'date': insights['best_trade'].entry_date.strftime('%Y-%m-%d') if insights['best_trade'] else 'N/A',
                    'return': insights['best_trade'].return_pct if insights['best_trade'] else 0,
                    'reason': insights['best_trade'].reason if insights['best_trade'] else '',
                } if insights['best_trade'] else None,
                'worst_trade': {
                    'date': insights['worst_trade'].entry_date.strftime('%Y-%m-%d') if insights['worst_trade'] else 'N/A',
                    'return': insights['worst_trade'].return_pct if insights['worst_trade'] else 0,
                    'reason': insights['worst_trade'].reason if insights['worst_trade'] else '',
                } if insights['worst_trade'] else None,
            },
            'regime_analysis': insights['regime_performance'],
            'recommendations': recommendations,
        }
        
        return report
    
    def generate_html_report(self) -> str:
        """Generate HTML formatted report for display"""
        report = self.generate_full_report()
        
        # Build HTML sections
        if self.lang == 'zh':
            html = self._build_chinese_html(report)
        else:
            html = self._build_english_html(report)
        
        return html
    
    def _build_english_html(self, report: Dict) -> str:
        """Build English HTML report"""
        recs_html = ""
        for rec in report['recommendations']:
            priority_color = {'high': '#ef4444', 'medium': '#f59e0b', 'low': '#10b981'}[rec['priority']]
            recs_html += f"""
                <div class="recommendation-item" style="border-left: 4px solid {priority_color}; padding-left: 1rem; margin-bottom: 1rem; background: #f9fafb; padding: 1rem; border-radius: 8px;">
                    <div style="font-weight: 600; color: {priority_color};">{rec['category'].replace('_', ' ').title()} (Confidence: {rec['confidence']}%)</div>
                    <div style="margin-top: 0.25rem; color: #1f2937; font-weight: 500;">{rec['recommendation']}</div>
                    <div style="font-size: 0.85rem; color: #4b5563; margin-top: 0.25rem;"><em>Evidence: {rec['evidence']}</em></div>
                </div>
            """
        
        timeline_html = ""
        for period in report['timeline']['monthly_performance'][-6:]:  # Last 6 months
            color = '#16a34a' if period['return'] > 0 else '#dc2626'
            timeline_html += f"""
                <tr style="border-bottom: 1px solid #d1d5db;">
                    <td style="padding: 0.75rem; color: #000000; font-weight: 500;">{period['period']}</td>
                    <td style="padding: 0.75rem; color: {color}; font-weight: 700;">{period['return']:.2f}%</td>
                    <td style="padding: 0.75rem; color: #000000; font-weight: 500;">{period['trades']}</td>
                    <td style="padding: 0.75rem; color: #000000; font-weight: 500;">{period['win_rate']:.1f}%</td>
                    <td style="padding: 0.75rem; color: #000000; font-weight: 500;">{period['regime'].title()}</td>
                </tr>
            """
        
        html = f"""
        <div class="ai-report-container" style="font-family: 'Inter', sans-serif; color: #000000 !important;">
            <!-- Performance Summary Box -->
            <div style="background: #ffffff; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; border: 3px solid #059669; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <h3 style="color: #059669; margin-top: 0; font-size: 1.25rem; border-bottom: 2px solid #059669; padding-bottom: 0.5rem;">📊 Performance Summary</h3>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-top: 1rem;">
                    <div style="background: #f0fdf4; padding: 1rem; border-radius: 8px; border: 1px solid #86efac;">
                        <div style="color: #166534; font-weight: 600; font-size: 0.9rem;">Total Return</div>
                        <div style="font-size: 1.75rem; font-weight: 700; color: {'#16a34a' if report['summary']['total_return'] >= 0 else '#dc2626'};">{report['summary']['total_return']:.2f}%</div>
                    </div>
                    <div style="background: #f0fdf4; padding: 1rem; border-radius: 8px; border: 1px solid #86efac;">
                        <div style="color: #166534; font-weight: 600; font-size: 0.9rem;">vs Buy & Hold</div>
                        <div style="font-size: 1.75rem; font-weight: 700; color: {'#16a34a' if report['summary']['vs_buy_hold'] >= 0 else '#dc2626'};">{report['summary']['vs_buy_hold']:+.2f}%</div>
                    </div>
                    <div style="background: #f0fdf4; padding: 1rem; border-radius: 8px; border: 1px solid #86efac;">
                        <div style="color: #166534; font-weight: 600; font-size: 0.9rem;">Win Rate</div>
                        <div style="font-size: 1.75rem; font-weight: 700; color: #000000;">{report['summary']['win_rate']:.1f}%</div>
                    </div>
                    <div style="background: #f0fdf4; padding: 1rem; border-radius: 8px; border: 1px solid #86efac;">
                        <div style="color: #166534; font-weight: 600; font-size: 0.9rem;">Total Trades</div>
                        <div style="font-size: 1.75rem; font-weight: 700; color: #000000;">{report['summary']['total_trades']}</div>
                    </div>
                </div>
            </div>
            
            <!-- Risk Metrics Box -->
            <div style="background: #ffffff; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; border: 3px solid #3b82f6; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <h3 style="color: #3b82f6; margin-top: 0; font-size: 1.25rem; border-bottom: 2px solid #3b82f6; padding-bottom: 0.5rem;">📈 Risk-Adjusted Metrics</h3>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-top: 1rem;">
                    <div style="background: #eff6ff; padding: 1rem; border-radius: 8px; border: 1px solid #93c5fd;">
                        <div style="color: #1e40af; font-weight: 600; font-size: 0.9rem;">Sharpe Ratio</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #000000;">{report['risk_metrics']['sharpe_ratio']:.2f}</div>
                    </div>
                    <div style="background: #eff6ff; padding: 1rem; border-radius: 8px; border: 1px solid #93c5fd;">
                        <div style="color: #1e40af; font-weight: 600; font-size: 0.9rem;">Sortino Ratio</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #000000;">{report['risk_metrics']['sortino_ratio']:.2f}</div>
                    </div>
                    <div style="background: #eff6ff; padding: 1rem; border-radius: 8px; border: 1px solid #93c5fd;">
                        <div style="color: #1e40af; font-weight: 600; font-size: 0.9rem;">Calmar Ratio</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #000000;">{report['risk_metrics']['calmar_ratio']:.2f}</div>
                    </div>
                    <div style="background: #eff6ff; padding: 1rem; border-radius: 8px; border: 1px solid #93c5fd;">
                        <div style="color: #1e40af; font-weight: 600; font-size: 0.9rem;">Profit Factor</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #000000;">{min(report['risk_metrics']['profit_factor'], 99.99):.2f}</div>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1rem;">
                    <div style="background: #f0fdf4; padding: 0.75rem; border-radius: 8px; border: 1px solid #bbf7d0;">
                        <span style="color: #166534; font-weight: 600;">Avg Win:</span> 
                        <span style="color: #16a34a; font-weight: 700;">+{report['risk_metrics']['avg_win']:.2f}%</span>
                    </div>
                    <div style="background: #fef2f2; padding: 0.75rem; border-radius: 8px; border: 1px solid #fecaca;">
                        <span style="color: #991b1b; font-weight: 600;">Avg Loss:</span> 
                        <span style="color: #dc2626; font-weight: 700;">{report['risk_metrics']['avg_loss']:.2f}%</span>
                    </div>
                    <div style="background: #fef2f2; padding: 0.75rem; border-radius: 8px; border: 1px solid #fecaca;">
                        <span style="color: #991b1b; font-weight: 600;">Max DD:</span> 
                        <span style="color: #dc2626; font-weight: 700;">{report['risk_metrics']['max_drawdown']:.2f}%</span>
                    </div>
                </div>
            </div>
            
            <!-- Timeline Box -->
            <div style="background: #ffffff; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; border: 3px solid #8b5cf6; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <h3 style="color: #8b5cf6; margin-top: 0; font-size: 1.25rem; border-bottom: 2px solid #8b5cf6; padding-bottom: 0.5rem;">📅 Timeline Analysis (Recent 6 Months)</h3>
                <table style="width: 100%; border-collapse: collapse; margin-top: 1rem; color: #000000;">
                    <thead>
                        <tr style="background: #f3f4f6; border-bottom: 2px solid #6b7280;">
                            <th style="text-align: left; padding: 0.75rem; color: #000000; font-weight: 700;">Period</th>
                            <th style="text-align: left; padding: 0.75rem; color: #000000; font-weight: 700;">Return</th>
                            <th style="text-align: left; padding: 0.75rem; color: #000000; font-weight: 700;">Trades</th>
                            <th style="text-align: left; padding: 0.75rem; color: #000000; font-weight: 700;">Win Rate</th>
                            <th style="text-align: left; padding: 0.75rem; color: #000000; font-weight: 700;">Regime</th>
                        </tr>
                    </thead>
                    <tbody style="color: #000000;">{timeline_html}</tbody>
                </table>
            </div>
            
            <!-- Recommendations Box -->
            <div style="background: #fffbeb; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; border: 3px solid #f59e0b; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <h3 style="color: #b45309; margin-top: 0; font-size: 1.25rem; border-bottom: 2px solid #f59e0b; padding-bottom: 0.5rem;">💡 AI Recommendations</h3>
                <div style="margin-top: 1rem;">{recs_html}</div>
            </div>
        </div>
        """
        return html
    
    def _build_chinese_html(self, report: Dict) -> str:
        """Build Chinese HTML report"""
        recs_html = ""
        for rec in report['recommendations']:
            priority_color = {'high': '#ef4444', 'medium': '#f59e0b', 'low': '#10b981'}[rec['priority']]
            priority_text = {'high': '高', 'medium': '中', 'low': '低'}[rec['priority']]
            recs_html += f"""
                <div class="recommendation-item" style="border-left: 4px solid {priority_color}; padding-left: 1rem; margin-bottom: 1rem; background: #f9fafb; padding: 1rem; border-radius: 8px;">
                    <div style="font-weight: 600; color: {priority_color};">優先級: {priority_text} (信心度: {rec['confidence']}%)</div>
                    <div style="margin-top: 0.25rem; color: #1f2937; font-weight: 500;">{rec['recommendation_zh']}</div>
                    <div style="font-size: 0.85rem; color: #4b5563; margin-top: 0.25rem;"><em>證據: {rec['evidence']}</em></div>
                </div>
            """
        
        timeline_html = ""
        for period in report['timeline']['monthly_performance'][-6:]:  # Last 6 months
            color = '#16a34a' if period['return'] > 0 else '#dc2626'
            regime_zh = {'bullish': '多頭', 'bearish': '空頭', 'sideways': '盤整'}.get(period['regime'], period['regime'])
            timeline_html += f"""
                <tr style="border-bottom: 1px solid #d1d5db;">
                    <td style="padding: 0.75rem; color: #000000; font-weight: 500;">{period['period']}</td>
                    <td style="padding: 0.75rem; color: {color}; font-weight: 700;">{period['return']:.2f}%</td>
                    <td style="padding: 0.75rem; color: #000000; font-weight: 500;">{period['trades']}</td>
                    <td style="padding: 0.75rem; color: #000000; font-weight: 500;">{period['win_rate']:.1f}%</td>
                    <td style="padding: 0.75rem; color: #000000; font-weight: 500;">{regime_zh}</td>
                </tr>
            """
        
        html = f"""
        <div class="ai-report-container" style="font-family: 'Noto Sans TC', 'Inter', sans-serif; color: #000000 !important;">
            <!-- 績效摘要 Box -->
            <div style="background: #ffffff; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; border: 3px solid #059669; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <h3 style="color: #059669; margin-top: 0; font-size: 1.25rem; border-bottom: 2px solid #059669; padding-bottom: 0.5rem;">📊 績效摘要</h3>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-top: 1rem;">
                    <div style="background: #f0fdf4; padding: 1rem; border-radius: 8px; border: 1px solid #86efac;">
                        <div style="color: #166534; font-weight: 600; font-size: 0.9rem;">總報酬</div>
                        <div style="font-size: 1.75rem; font-weight: 700; color: {'#16a34a' if report['summary']['total_return'] >= 0 else '#dc2626'};">{report['summary']['total_return']:.2f}%</div>
                    </div>
                    <div style="background: #f0fdf4; padding: 1rem; border-radius: 8px; border: 1px solid #86efac;">
                        <div style="color: #166534; font-weight: 600; font-size: 0.9rem;">相對買入持有</div>
                        <div style="font-size: 1.75rem; font-weight: 700; color: {'#16a34a' if report['summary']['vs_buy_hold'] >= 0 else '#dc2626'};">{report['summary']['vs_buy_hold']:+.2f}%</div>
                    </div>
                    <div style="background: #f0fdf4; padding: 1rem; border-radius: 8px; border: 1px solid #86efac;">
                        <div style="color: #166534; font-weight: 600; font-size: 0.9rem;">勝率</div>
                        <div style="font-size: 1.75rem; font-weight: 700; color: #000000;">{report['summary']['win_rate']:.1f}%</div>
                    </div>
                    <div style="background: #f0fdf4; padding: 1rem; border-radius: 8px; border: 1px solid #86efac;">
                        <div style="color: #166534; font-weight: 600; font-size: 0.9rem;">總交易數</div>
                        <div style="font-size: 1.75rem; font-weight: 700; color: #000000;">{report['summary']['total_trades']}</div>
                    </div>
                </div>
            </div>
            
            <!-- 風險調整指標 Box -->
            <div style="background: #ffffff; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; border: 3px solid #3b82f6; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <h3 style="color: #3b82f6; margin-top: 0; font-size: 1.25rem; border-bottom: 2px solid #3b82f6; padding-bottom: 0.5rem;">📈 風險調整指標</h3>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-top: 1rem;">
                    <div style="background: #eff6ff; padding: 1rem; border-radius: 8px; border: 1px solid #93c5fd;">
                        <div style="color: #1e40af; font-weight: 600; font-size: 0.9rem;">夏普比率</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #000000;">{report['risk_metrics']['sharpe_ratio']:.2f}</div>
                    </div>
                    <div style="background: #eff6ff; padding: 1rem; border-radius: 8px; border: 1px solid #93c5fd;">
                        <div style="color: #1e40af; font-weight: 600; font-size: 0.9rem;">索提諾比率</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #000000;">{report['risk_metrics']['sortino_ratio']:.2f}</div>
                    </div>
                    <div style="background: #eff6ff; padding: 1rem; border-radius: 8px; border: 1px solid #93c5fd;">
                        <div style="color: #1e40af; font-weight: 600; font-size: 0.9rem;">卡瑪比率</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #000000;">{report['risk_metrics']['calmar_ratio']:.2f}</div>
                    </div>
                    <div style="background: #eff6ff; padding: 1rem; border-radius: 8px; border: 1px solid #93c5fd;">
                        <div style="color: #1e40af; font-weight: 600; font-size: 0.9rem;">獲利因子</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #000000;">{min(report['risk_metrics']['profit_factor'], 99.99):.2f}</div>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1rem;">
                    <div style="background: #f0fdf4; padding: 0.75rem; border-radius: 8px; border: 1px solid #bbf7d0;">
                        <span style="color: #166534; font-weight: 600;">平均獲利:</span> 
                        <span style="color: #16a34a; font-weight: 700;">+{report['risk_metrics']['avg_win']:.2f}%</span>
                    </div>
                    <div style="background: #fef2f2; padding: 0.75rem; border-radius: 8px; border: 1px solid #fecaca;">
                        <span style="color: #991b1b; font-weight: 600;">平均虧損:</span> 
                        <span style="color: #dc2626; font-weight: 700;">{report['risk_metrics']['avg_loss']:.2f}%</span>
                    </div>
                    <div style="background: #fef2f2; padding: 0.75rem; border-radius: 8px; border: 1px solid #fecaca;">
                        <span style="color: #991b1b; font-weight: 600;">最大回撤:</span> 
                        <span style="color: #dc2626; font-weight: 700;">{report['risk_metrics']['max_drawdown']:.2f}%</span>
                    </div>
                </div>
            </div>
            
            <!-- 時間序列分析 Box -->
            <div style="background: #ffffff; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; border: 3px solid #8b5cf6; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <h3 style="color: #8b5cf6; margin-top: 0; font-size: 1.25rem; border-bottom: 2px solid #8b5cf6; padding-bottom: 0.5rem;">📅 時間序列分析 (近六個月)</h3>
                <table style="width: 100%; border-collapse: collapse; margin-top: 1rem; color: #000000;">
                    <thead>
                        <tr style="background: #f3f4f6; border-bottom: 2px solid #6b7280;">
                            <th style="text-align: left; padding: 0.75rem; color: #000000; font-weight: 700;">期間</th>
                            <th style="text-align: left; padding: 0.75rem; color: #000000; font-weight: 700;">報酬</th>
                            <th style="text-align: left; padding: 0.75rem; color: #000000; font-weight: 700;">交易數</th>
                            <th style="text-align: left; padding: 0.75rem; color: #000000; font-weight: 700;">勝率</th>
                            <th style="text-align: left; padding: 0.75rem; color: #000000; font-weight: 700;">市場狀態</th>
                        </tr>
                    </thead>
                    <tbody style="color: #000000;">{timeline_html}</tbody>
                </table>
            </div>
            
            <!-- AI 智能建議 Box -->
            <div style="background: #fffbeb; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; border: 3px solid #f59e0b; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <h3 style="color: #b45309; margin-top: 0; font-size: 1.25rem; border-bottom: 2px solid #f59e0b; padding-bottom: 0.5rem;">💡 AI 智能建議</h3>
                <div style="margin-top: 1rem;">{recs_html}</div>
            </div>
        </div>
        """
        return html
