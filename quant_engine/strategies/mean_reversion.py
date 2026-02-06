"""
Mean Reversion Strategy
Buy when price < lower band, Sell at the midline (SMA).
"""

import pandas as pd
from quant_engine.base_strategy import BaseStrategy
from quant_engine.indicators import calculate_bollinger_bands


class MeanReversionStrategy(BaseStrategy):
    """
    Mean Reversion Strategy using Bollinger Bands.
    
    Logic:
    - Buy Signal: Price drops below the lower Bollinger Band (oversold)
    - Sell Signal: Price crosses above the middle band (SMA) - return to mean
    """
    
    def __init__(self, period: int = 20, std_dev: float = 2.0):
        super().__init__(
            name="Mean Reversion",
            description="Buy when price < lower band, Sell at the midline"
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
        """Generate buy/sell signals based on mean reversion logic."""
        df = self.calculate_indicators(data)
        
        # Initialize signal column
        df['Signal'] = 0
        
        # Track position state for proper mean reversion logic
        position = 0  # 0 = no position, 1 = long
        
        for i in range(1, len(df)):
            if position == 0:
                # Buy when price < lower band (oversold)
                if df['Close'].iloc[i] < df['BB_Lower'].iloc[i]:
                    df.iloc[i, df.columns.get_loc('Signal')] = 1
                    position = 1
            else:
                # Sell when price crosses above midline (mean reversion complete)
                if df['Close'].iloc[i] > df['BB_Middle'].iloc[i]:
                    df.iloc[i, df.columns.get_loc('Signal')] = -1
                    position = 0
                else:
                    # Hold position
                    df.iloc[i, df.columns.get_loc('Signal')] = 1
        
        return df
    
    def get_parameter_schema(self):
        """Return parameter schema for UI generation."""
        return [
            {"name": "period", "value": self._parameters['period'], 
             "type": "int", "min": 5, "max": 50, "description": "Lookback period for Bollinger Bands"},
            {"name": "std_dev", "value": self._parameters['std_dev'], 
             "type": "float", "min": 1.0, "max": 3.0, "description": "Standard deviation multiplier"}
        ]
