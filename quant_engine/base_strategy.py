"""
Base Strategy Module
Abstract base class defining the interface for all trading strategies.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import pandas as pd


class BaseStrategy(ABC):
    """
    Abstract base class for trading strategies.
    All strategies must implement these methods for dashboard integration.
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self._parameters: Dict[str, Any] = {}
    
    @abstractmethod
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all technical indicators required by the strategy.
        
        Args:
            data: DataFrame with 'Close' price column (and optionally OHLC)
            
        Returns:
            DataFrame with indicator columns added
        """
        pass
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on the strategy logic.
        
        Args:
            data: DataFrame with price data
            
        Returns:
            DataFrame with 'Signal' column: 1 (Buy), -1 (Sell), 0 (Hold)
        """
        pass
    
    def get_parameters(self) -> Dict[str, Any]:
        """Return current strategy parameters for dashboard display."""
        return self._parameters.copy()
    
    def set_parameters(self, **kwargs) -> None:
        """Update strategy parameters dynamically."""
        for key, value in kwargs.items():
            if key in self._parameters:
                self._parameters[key] = value
    
    def get_parameter_schema(self) -> List[Dict[str, Any]]:
        """
        Return parameter schema for UI generation.
        Override in subclass for custom parameter metadata.
        """
        return [
            {"name": k, "value": v, "type": type(v).__name__}
            for k, v in self._parameters.items()
        ]
    
    def backtest(self, data: pd.DataFrame, initial_capital: float = 10000.0) -> Dict[str, Any]:
        """
        Run a simple backtest and return performance metrics.
        
        Args:
            data: DataFrame with price data
            initial_capital: Starting capital for backtest
            
        Returns:
            Dictionary with performance metrics
        """
        df = self.generate_signals(data.copy())
        
        # Calculate returns
        df['Returns'] = df['Close'].pct_change()
        df['Strategy_Returns'] = df['Signal'].shift(1) * df['Returns']
        df['Cumulative_Returns'] = (1 + df['Strategy_Returns']).cumprod()
        df['Portfolio_Value'] = initial_capital * df['Cumulative_Returns']
        
        # Calculate metrics
        df['Portfolio_Value'] = df['Portfolio_Value'].fillna(initial_capital)
        df['Peak'] = df['Portfolio_Value'].cummax()
        df['Drawdown'] = (df['Portfolio_Value'] - df['Peak']) / df['Peak']
        
        final_value = df['Portfolio_Value'].iloc[-1]
        net_profit = final_value - initial_capital
        max_drawdown = df['Drawdown'].min() * 100  # As percentage
        
        return {
            'initial_capital': initial_capital,
            'final_value': final_value,
            'net_profit': net_profit,
            'net_profit_pct': (net_profit / initial_capital) * 100,
            'max_drawdown_pct': max_drawdown,
            'data': df
        }
