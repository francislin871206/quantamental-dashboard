"""
RSI Momentum Strategy
Buy at RSI < 30 (oversold), Sell at RSI > 70 (overbought).
"""

import pandas as pd
from quant_engine.base_strategy import BaseStrategy
from quant_engine.indicators import calculate_rsi


class RSIMomentumStrategy(BaseStrategy):
    """
    RSI Momentum Strategy.
    
    Logic:
    - Buy Signal: RSI drops below oversold threshold (default 30)
    - Sell Signal: RSI rises above overbought threshold (default 70)
    """
    
    def __init__(self, period: int = 14, oversold: int = 30, overbought: int = 70):
        super().__init__(
            name="RSI Momentum",
            description="Buy at RSI < 30, Sell at RSI > 70"
        )
        self._parameters = {
            'period': period,
            'oversold': oversold,
            'overbought': overbought
        }
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate RSI and add to DataFrame."""
        df = data.copy()
        
        df['RSI'] = calculate_rsi(
            df['Close'],
            period=self._parameters['period']
        )
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate buy/sell signals based on RSI levels."""
        df = self.calculate_indicators(data)
        
        # Initialize signal column
        df['Signal'] = 0
        
        oversold = self._parameters['oversold']
        overbought = self._parameters['overbought']
        
        # Buy when RSI < oversold threshold
        df.loc[df['RSI'] < oversold, 'Signal'] = 1
        
        # Sell when RSI > overbought threshold
        df.loc[df['RSI'] > overbought, 'Signal'] = -1
        
        return df
    
    def get_parameter_schema(self):
        """Return parameter schema for UI generation."""
        return [
            {"name": "period", "value": self._parameters['period'], 
             "type": "int", "min": 5, "max": 30, "description": "RSI calculation period"},
            {"name": "oversold", "value": self._parameters['oversold'], 
             "type": "int", "min": 10, "max": 40, "description": "Oversold threshold (buy signal)"},
            {"name": "overbought", "value": self._parameters['overbought'], 
             "type": "int", "min": 60, "max": 90, "description": "Overbought threshold (sell signal)"}
        ]
