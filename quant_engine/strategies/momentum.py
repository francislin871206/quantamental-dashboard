"""
Momentum Strategy with Multiple Timeframe Confirmation
Uses price momentum with volume confirmation for trend-following trades.
"""

import pandas as pd
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_strategy import BaseStrategy


class MomentumStrategy(BaseStrategy):
    """Multi-timeframe Momentum Strategy"""
    
    def __init__(self, momentum_period: int = 20, roc_threshold: float = 5.0):
        super().__init__(
            name="Momentum (Multi-TF)",
            description="Momentum-based trading with ROC confirmation"
        )
        self._parameters = {
            'momentum_period': momentum_period,
            'roc_threshold': roc_threshold
        }
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate momentum indicators."""
        df = data.copy()
        
        # Calculate Rate of Change (momentum)
        df['ROC'] = ((df['Close'] - df['Close'].shift(self._parameters['momentum_period'])) / 
                      df['Close'].shift(self._parameters['momentum_period'])) * 100
        
        # Short-term and long-term momentum
        df['ROC_Short'] = ((df['Close'] - df['Close'].shift(5)) / df['Close'].shift(5)) * 100
        df['ROC_Long'] = ((df['Close'] - df['Close'].shift(50)) / df['Close'].shift(50)) * 100
        
        # Trend SMA
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate buy/sell signals based on momentum."""
        df = self.calculate_indicators(data)
        
        # Initialize signal column
        df['Signal'] = 0
        
        # Buy signal: Strong positive momentum aligned across timeframes
        buy_condition = (
            (df['ROC'] > self._parameters['roc_threshold']) &  # Main momentum positive
            (df['ROC_Short'] > 0) &  # Short-term positive
            (df['Close'] > df['SMA_50'])  # Above trend
        )
        
        # Sell signal: Momentum reversal
        sell_condition = (
            (df['ROC'] < -self._parameters['roc_threshold']) |  # Main momentum negative
            ((df['ROC_Short'] < 0) & (df['ROC'].shift(1) > 0))  # Momentum reversal
        )
        
        df.loc[buy_condition, 'Signal'] = 1
        df.loc[sell_condition, 'Signal'] = -1
        
        # Forward fill positions
        position = 0
        for i in range(len(df)):
            if df['Signal'].iloc[i] == 1:
                position = 1
            elif df['Signal'].iloc[i] == -1:
                position = 0
            df.loc[df.index[i], 'Signal'] = position
        
        return df
    
    def get_parameter_schema(self):
        """Return parameter schema for UI generation."""
        return [
            {"name": "momentum_period", "value": self._parameters['momentum_period'],
             "type": "int", "min": 10, "max": 50, "description": "Momentum lookback period"},
            {"name": "roc_threshold", "value": self._parameters['roc_threshold'],
             "type": "float", "min": 2.0, "max": 15.0, "description": "ROC threshold for signals"},
        ]
