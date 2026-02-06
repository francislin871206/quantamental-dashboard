"""
Strategy Factory
Factory pattern for web dashboard integration.
"""

from typing import Dict, List, Any, Type
from base_strategy import BaseStrategy
from strategies.bollinger_breakout import BollingerBreakoutStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.rsi_momentum import RSIMomentumStrategy
from strategies.macd_crossover import MACDCrossoverStrategy
from strategies.dual_ma import DualMAStrategy
from strategies.volatility_breakout import VolatilityBreakoutStrategy
from strategies.momentum import MomentumStrategy


class StrategyFactory:
    """
    Factory for creating and managing trading strategies.
    Designed for easy integration with web dashboards.
    """
    
    _strategies: Dict[str, Type[BaseStrategy]] = {
        'bollinger_breakout': BollingerBreakoutStrategy,
        'mean_reversion': MeanReversionStrategy,
        'rsi_momentum': RSIMomentumStrategy,
        'macd_crossover': MACDCrossoverStrategy,
        'dual_ma': DualMAStrategy,
        'volatility_breakout': VolatilityBreakoutStrategy,
        'momentum': MomentumStrategy,
    }
    
    @classmethod
    def get_available_strategies(cls) -> List[Dict[str, str]]:
        """
        Get list of all available strategies with metadata.
        
        Returns:
            List of dicts with strategy info for dashboard display
        """
        strategies = []
        for key, strategy_class in cls._strategies.items():
            instance = strategy_class()
            strategies.append({
                'key': key,
                'name': instance.name,
                'description': instance.description
            })
        return strategies
    
    @classmethod
    def create_strategy(cls, name: str, **params) -> BaseStrategy:
        """
        Instantiate a strategy by name with optional parameters.
        
        Args:
            name: Strategy key (e.g., 'bollinger_breakout')
            **params: Strategy-specific parameters
            
        Returns:
            Instantiated strategy object
            
        Raises:
            ValueError: If strategy name is not recognized
        """
        if name not in cls._strategies:
            available = list(cls._strategies.keys())
            raise ValueError(f"Unknown strategy: {name}. Available: {available}")
        
        return cls._strategies[name](**params)
    
    @classmethod
    def get_strategy_info(cls, name: str) -> Dict[str, Any]:
        """
        Get detailed info about a strategy for UI generation.
        
        Args:
            name: Strategy key
            
        Returns:
            Dict with name, description, and parameter schema
        """
        if name not in cls._strategies:
            raise ValueError(f"Unknown strategy: {name}")
        
        instance = cls._strategies[name]()
        return {
            'key': name,
            'name': instance.name,
            'description': instance.description,
            'parameters': instance.get_parameter_schema()
        }
    
    @classmethod
    def register_strategy(cls, key: str, strategy_class: Type[BaseStrategy]) -> None:
        """
        Register a new strategy (for extensibility).
        
        Args:
            key: Unique identifier for the strategy
            strategy_class: Strategy class (must inherit from BaseStrategy)
        """
        if not issubclass(strategy_class, BaseStrategy):
            raise TypeError("Strategy must inherit from BaseStrategy")
        cls._strategies[key] = strategy_class
