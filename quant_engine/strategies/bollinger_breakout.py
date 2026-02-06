"""
Bollinger Band Breakout Strategy
Buy when price > upper band, Sell when price < lower band.
"""

import pandas as pd
from quant_engine.base_strategy import BaseStrategy
from quant_engine.indicators import calculate_bollinger_bands


class BollingerBreakoutStrategy(BaseStrategy):
    """
    Bollinger Band Breakout Strategy.
    
    Logic:
    - Buy Signal: Price breaks above the upper Bollinger Band
    - Sell Signal: Price breaks below the lower Bollinger Band
    """
    
    def __init__(self, period: int = 20, std_dev: float = 2.0):
        super().__init__(
            name="Bollinger Band Breakout",
            description="Buy when price > upper band, Sell when price < lower band"
        )
        self._parameters = {
            'period': period,
            'std_dev': std_dev
        }
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate Bollinger Bands and add to DataFrame."""
        df = data.copy()
        
        upper, middle, lower = calculate_bollinger_bands(
            df['Close'],
            period=self._parameters['period'],
            std_dev=self._parameters['std_dev']
        )
        
        df['BB_Upper'] = upper
        df['BB_Middle'] = middle
        df['BB_Lower'] = lower
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate buy/sell signals based on Bollinger Band breakouts."""
        df = self.calculate_indicators(data)
        
        # Initialize signal column
        df['Signal'] = 0
        
        # Buy when price > upper band
        df.loc[df['Close'] > df['BB_Upper'], 'Signal'] = 1
        
        # Sell when price < lower band
        df.loc[df['Close'] < df['BB_Lower'], 'Signal'] = -1
        
        return df
    
    def get_parameter_schema(self):
        """Return parameter schema for UI generation."""
        return [
            {"name": "period", "value": self._parameters['period'], 
             "type": "int", "min": 5, "max": 50, "description": "Lookback period for Bollinger Bands"},
            {"name": "std_dev", "value": self._parameters['std_dev'], 
             "type": "float", "min": 1.0, "max": 3.0, "description": "Standard deviation multiplier"}
        ]
