import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
from models import (
    StrategyModel, 
    ConditionModel, 
    StockScanResult,
    IndicatorType,
    OperatorType
)
from indicators import IndicatorCalculator

class StrategyEngine:
    """Engine for creating, managing, and executing trading strategies"""
    
    def __init__(self, strategies_file: str = "strategies.json"):
        self.strategies_file = strategies_file
        self.strategies: Dict[str, StrategyModel] = {}
        self.load_strategies()
    
    def load_strategies(self):
        """Load strategies from JSON file"""
        if os.path.exists(self.strategies_file):
            try:
                with open(self.strategies_file, 'r') as f:
                    data = json.load(f)
                    for strategy_data in data:
                        strategy = StrategyModel(**strategy_data)
                        self.strategies[strategy.id] = strategy
            except Exception as e:
                print(f"Error loading strategies: {e}")
    
    def save_strategies(self):
        """Save strategies to JSON file"""
        try:
            data = [strategy.dict() for strategy in self.strategies.values()]
            with open(self.strategies_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving strategies: {e}")
    
    def create_strategy(self, name: str, description: str, conditions: List[ConditionModel], timeframe: str) -> StrategyModel:
        """Create a new strategy"""
        strategy_id = f"strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        strategy = StrategyModel(
            id=strategy_id,
            name=name,
            description=description,
            conditions=conditions,
            timeframe=timeframe,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.strategies[strategy_id] = strategy
        self.save_strategies()
        return strategy
    
    def update_strategy(self, strategy_id: str, **kwargs) -> Optional[StrategyModel]:
        """Update an existing strategy"""
        if strategy_id not in self.strategies:
            return None
        
        strategy = self.strategies[strategy_id]
        for key, value in kwargs.items():
            if value is not None and hasattr(strategy, key):
                setattr(strategy, key, value)
        
        strategy.updated_at = datetime.now()
        self.save_strategies()
        return strategy
    
    def delete_strategy(self, strategy_id: str) -> bool:
        """Delete a strategy"""
        if strategy_id in self.strategies:
            del self.strategies[strategy_id]
            self.save_strategies()
            return True
        return False
    
    def get_strategy(self, strategy_id: str) -> Optional[StrategyModel]:
        """Get a strategy by ID"""
        return self.strategies.get(strategy_id)
    
    def get_all_strategies(self) -> List[StrategyModel]:
        """Get all strategies"""
        return list(self.strategies.values())
    
    def calculate_indicator(self, data: pd.DataFrame, indicator_type: IndicatorType, params: Dict[str, Any]) -> Any:
        """Calculate indicator value based on type and parameters"""
        calculator = IndicatorCalculator()
        
        if indicator_type == IndicatorType.SMA:
            period = params.get('period', 20)
            return calculator.calculate_sma(data, period)
        
        elif indicator_type == IndicatorType.EMA:
            period = params.get('period', 20)
            return calculator.calculate_ema(data, period)
        
        elif indicator_type == IndicatorType.RSI:
            period = params.get('period', 14)
            return calculator.calculate_rsi(data, period)
        
        elif indicator_type == IndicatorType.MACD:
            fast = params.get('fast', 12)
            slow = params.get('slow', 26)
            signal = params.get('signal', 9)
            macd_data = calculator.calculate_macd(data, fast, slow, signal)
            return macd_data.get(params.get('line', 'macd'))  # Return specific line
        
        elif indicator_type == IndicatorType.BOLLINGER_BANDS:
            period = params.get('period', 20)
            std_dev = params.get('std_dev', 2)
            bb_data = calculator.calculate_bollinger_bands(data, period, std_dev)
            return bb_data.get(params.get('band', 'middle'))  # upper, middle, or lower
        
        elif indicator_type == IndicatorType.ATR:
            period = params.get('period', 14)
            return calculator.calculate_atr(data, period)
        
        elif indicator_type == IndicatorType.STOCHASTIC:
            k_period = params.get('k_period', 14)
            d_period = params.get('d_period', 3)
            stoch_data = calculator.calculate_stochastic(data, k_period, d_period)
            return stoch_data.get(params.get('line', 'k'))  # k or d
        
        elif indicator_type == IndicatorType.ADX:
            period = params.get('period', 14)
            return calculator.calculate_adx(data, period)
        
        elif indicator_type == IndicatorType.VOLUME:
            return data['volume']
        
        elif indicator_type == IndicatorType.PRICE:
            price_type = params.get('type', 'close')  # open, high, low, close
            return data[price_type]
        
        return None
    
    def evaluate_condition(self, data: pd.DataFrame, condition: ConditionModel) -> bool:
        """Evaluate a single condition"""
        # Calculate indicator 1
        indicator1_value = self.calculate_indicator(data, condition.indicator1, condition.indicator1_params)
        
        if indicator1_value is None or len(indicator1_value) == 0:
            return False
        
        # Get the latest value
        if isinstance(indicator1_value, pd.Series):
            if indicator1_value.isna().iloc[-1]:
                return False
            indicator1_latest = indicator1_value.iloc[-1]
        else:
            indicator1_latest = indicator1_value
        
        # Handle comparison
        if condition.operator in [OperatorType.CROSSES_ABOVE, OperatorType.CROSSES_BELOW]:
            # Need indicator2 for crossover
            if not condition.indicator2:
                return False
            
            indicator2_value = self.calculate_indicator(data, condition.indicator2, condition.indicator2_params)
            if indicator2_value is None:
                return False
            
            calculator = IndicatorCalculator()
            if condition.operator == OperatorType.CROSSES_ABOVE:
                return calculator.check_crossover(indicator1_value, indicator2_value)
            else:
                return calculator.check_crossunder(indicator1_value, indicator2_value)
        
        else:
            # Standard comparison operators
            if condition.indicator2:
                indicator2_value = self.calculate_indicator(data, condition.indicator2, condition.indicator2_params)
                if isinstance(indicator2_value, pd.Series):
                    if indicator2_value.isna().iloc[-1]:
                        return False
                    compare_value = indicator2_value.iloc[-1]
                else:
                    compare_value = indicator2_value
            else:
                compare_value = condition.value
            
            if compare_value is None:
                return False
            
            # Perform comparison
            if condition.operator == OperatorType.GREATER_THAN:
                return indicator1_latest > compare_value
            elif condition.operator == OperatorType.LESS_THAN:
                return indicator1_latest < compare_value
            elif condition.operator == OperatorType.EQUALS:
                return abs(indicator1_latest - compare_value) < 0.01
            elif condition.operator == OperatorType.GREATER_EQUAL:
                return indicator1_latest >= compare_value
            elif condition.operator == OperatorType.LESS_EQUAL:
                return indicator1_latest <= compare_value
        
        return False
    
    def evaluate_strategy(self, data: pd.DataFrame, strategy: StrategyModel) -> tuple[bool, List[bool], Dict[str, Any]]:
        """
        Evaluate if data matches the strategy
        Returns: (all_conditions_met, individual_condition_results, indicator_values)
        """
        condition_results = []
        indicator_values = {}
        
        for i, condition in enumerate(strategy.conditions):
            result = self.evaluate_condition(data, condition)
            condition_results.append(result)
            
            # Store indicator values for display
            indicator1_value = self.calculate_indicator(data, condition.indicator1, condition.indicator1_params)
            if isinstance(indicator1_value, pd.Series) and len(indicator1_value) > 0:
                indicator_values[f"condition_{i}_indicator1"] = float(indicator1_value.iloc[-1])
            
            if condition.indicator2:
                indicator2_value = self.calculate_indicator(data, condition.indicator2, condition.indicator2_params)
                if isinstance(indicator2_value, pd.Series) and len(indicator2_value) > 0:
                    indicator_values[f"condition_{i}_indicator2"] = float(indicator2_value.iloc[-1])
        
        all_met = all(condition_results)
        return all_met, condition_results, indicator_values
    
    def scan_stocks(self, strategy_id: str, stock_data_dict: Dict[str, pd.DataFrame], symbols_info: Dict[str, Dict]) -> List[StockScanResult]:
        """
        Scan multiple stocks against a strategy
        stock_data_dict: {symbol: DataFrame with OHLCV data}
        symbols_info: {symbol: {display_name, ...}}
        """
        strategy = self.get_strategy(strategy_id)
        if not strategy:
            return []
        
        results = []
        
        for symbol, data in stock_data_dict.items():
            if data is None or len(data) == 0:
                continue
            
            try:
                matched, conditions_met, indicator_values = self.evaluate_strategy(data, strategy)
                
                symbol_info = symbols_info.get(symbol, {})
                current_price = float(data['close'].iloc[-1]) if len(data) > 0 else 0.0
                
                result = StockScanResult(
                    symbol=symbol,
                    display_name=symbol_info.get('displayName', symbol),
                    matched=matched,
                    conditions_met=conditions_met,
                    current_price=current_price,
                    indicator_values=indicator_values,
                    timestamp=datetime.now()
                )
                results.append(result)
            except Exception as e:
                print(f"Error scanning {symbol}: {e}")
                continue
        
        return results
