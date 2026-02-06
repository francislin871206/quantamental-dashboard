"""
MACD Crossover Strategy
Generates buy signals when MACD line crosses above signal line,
and sell signals when MACD crosses below signal line.
"""

import pandas as pd
from quant_engine.base_strategy import BaseStrategy


class MACDCrossoverStrategy(BaseStrategy):
    """MACD Crossover Trading Strategy"""
    
    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        super().__init__(
            name="MACD Crossover",
            description="Buy when MACD crosses above signal line, sell when crosses below"
        )
        self._parameters = {
            'fast_period': fast_period,
            'slow_period': slow_period,
            'signal_period': signal_period
        }
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD indicators."""
        df = data.copy()
        
        # Calculate EMAs
        df['EMA_Fast'] = df['Close'].ewm(span=self._parameters['fast_period'], adjust=False).mean()
        df['EMA_Slow'] = df['Close'].ewm(span=self._parameters['slow_period'], adjust=False).mean()
        
        # Calculate MACD line
        df['MACD'] = df['EMA_Fast'] - df['EMA_Slow']
        
        # Calculate Signal line
        df['MACD_Signal'] = df['MACD'].ewm(span=self._parameters['signal_period'], adjust=False).mean()
        
        # Calculate MACD Histogram
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate buy/sell signals based on MACD crossovers."""
        df = self.calculate_indicators(data)
        
        # Initialize signal column
        df['Signal'] = 0
        
        # Buy when MACD crosses above signal line
        df.loc[(df['MACD'] > df['MACD_Signal']) & 
               (df['MACD'].shift(1) <= df['MACD_Signal'].shift(1)), 'Signal'] = 1
        
        # Sell when MACD crosses below signal line
        df.loc[(df['MACD'] < df['MACD_Signal']) & 
               (df['MACD'].shift(1) >= df['MACD_Signal'].shift(1)), 'Signal'] = -1
        
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
            {"name": "fast_period", "value": self._parameters['fast_period'],
             "type": "int", "min": 5, "max": 20, "description": "Fast EMA period"},
            {"name": "slow_period", "value": self._parameters['slow_period'],
             "type": "int", "min": 15, "max": 50, "description": "Slow EMA period"},
            {"name": "signal_period", "value": self._parameters['signal_period'],
             "type": "int", "min": 5, "max": 15, "description": "Signal line period"},
        ]
