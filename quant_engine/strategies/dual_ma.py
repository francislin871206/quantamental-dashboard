"""
Dual Moving Average (Golden Cross / Death Cross) Strategy
Generates buy signals when short-term MA crosses above long-term MA (Golden Cross),
and sell signals when short-term MA crosses below long-term MA (Death Cross).
"""

import pandas as pd
from quant_engine.base_strategy import BaseStrategy


class DualMAStrategy(BaseStrategy):
    """Dual Moving Average (Golden/Death Cross) Strategy"""
    
    def __init__(self, short_period: int = 50, long_period: int = 200):
        super().__init__(
            name="Dual MA (Golden Cross)",
            description="Buy on Golden Cross (SMA50 > SMA200), sell on Death Cross"
        )
        self._parameters = {
            'short_period': short_period,
            'long_period': long_period
        }
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate moving averages."""
        df = data.copy()
        
        df['MA_Short'] = df['Close'].rolling(window=self._parameters['short_period']).mean()
        df['MA_Long'] = df['Close'].rolling(window=self._parameters['long_period']).mean()
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate buy/sell signals based on MA crossovers."""
        df = self.calculate_indicators(data)
        
        # Initialize signal column
        df['Signal'] = 0
        
        # Golden Cross - Short MA crosses above Long MA
        df.loc[(df['MA_Short'] > df['MA_Long']) & 
               (df['MA_Short'].shift(1) <= df['MA_Long'].shift(1)), 'Signal'] = 1
        
        # Death Cross - Short MA crosses below Long MA
        df.loc[(df['MA_Short'] < df['MA_Long']) & 
               (df['MA_Short'].shift(1) >= df['MA_Long'].shift(1)), 'Signal'] = -1
        
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
            {"name": "short_period", "value": self._parameters['short_period'],
             "type": "int", "min": 10, "max": 100, "description": "Short-term MA period"},
            {"name": "long_period", "value": self._parameters['long_period'],
             "type": "int", "min": 100, "max": 300, "description": "Long-term MA period"},
        ]
