"""
Volatility Breakout Strategy (ATR-based)
Generates buy signals when price breaks above the previous day's high plus ATR,
indicating strong momentum with volatility confirmation.
"""

import pandas as pd
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_strategy import BaseStrategy


class VolatilityBreakoutStrategy(BaseStrategy):
    """ATR-based Volatility Breakout Strategy"""
    
    def __init__(self, atr_period: int = 14, atr_multiplier: float = 1.5):
        super().__init__(
            name="Volatility Breakout (ATR)",
            description="Buy when price breaks above range with ATR confirmation"
        )
        self._parameters = {
            'atr_period': atr_period,
            'atr_multiplier': atr_multiplier
        }
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate ATR and breakout levels."""
        df = data.copy()
        
        # Calculate True Range
        df['H-L'] = df['High'] - df['Low']
        df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
        df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
        df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
        
        # Calculate ATR
        df['ATR'] = df['TR'].rolling(window=self._parameters['atr_period']).mean()
        
        # Calculate breakout levels
        df['Upper_Breakout'] = df['High'].shift(1) + (df['ATR'] * self._parameters['atr_multiplier'])
        df['Lower_Exit'] = df['Low'].shift(1) - (df['ATR'] * 2.0)
        
        # Clean up temp columns
        df = df.drop(columns=['H-L', 'H-PC', 'L-PC'])
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate buy/sell signals based on volatility breakouts."""
        df = self.calculate_indicators(data)
        
        # Initialize signal column
        df['Signal'] = 0
        
        # Buy signal: Price closes above upper breakout level
        df.loc[df['Close'] > df['Upper_Breakout'], 'Signal'] = 1
        
        # Exit signal: Price closes below exit level
        df.loc[df['Close'] < df['Lower_Exit'], 'Signal'] = -1
        
        # Forward fill positions
        position = 0
        for i in range(len(df)):
            if df['Signal'].iloc[i] == 1 and position == 0:
                position = 1
            elif df['Signal'].iloc[i] == -1:
                position = 0
            df.loc[df.index[i], 'Signal'] = position
        
        return df
    
    def get_parameter_schema(self):
        """Return parameter schema for UI generation."""
        return [
            {"name": "atr_period", "value": self._parameters['atr_period'],
             "type": "int", "min": 7, "max": 30, "description": "ATR calculation period"},
            {"name": "atr_multiplier", "value": self._parameters['atr_multiplier'],
             "type": "float", "min": 0.5, "max": 3.0, "description": "ATR multiplier for breakout"},
        ]
