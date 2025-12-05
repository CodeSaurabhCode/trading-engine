from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class IndicatorType(str, Enum):
    SMA = "SMA"  # Simple Moving Average
    EMA = "EMA"  # Exponential Moving Average
    RSI = "RSI"  # Relative Strength Index
    MACD = "MACD"
    BOLLINGER_BANDS = "BOLLINGER_BANDS"
    VOLUME = "VOLUME"
    PRICE = "PRICE"
    ATR = "ATR"  # Average True Range
    STOCHASTIC = "STOCHASTIC"
    ADX = "ADX"  # Average Directional Index

class PresetStrategyType(str, Enum):
    MA44 = "MA44"  # Price near 44-day MA with positive slope
    MA44_CROSS_MA200 = "MA44_CROSS_MA200"  # 44-day MA crossing 200-day MA
    EMA_CROSSOVER = "EMA_CROSSOVER"  # EMA(10) approaching EMA(30)
    DOWN_TO_MA200 = "DOWN_TO_MA200"  # Price approaching 200-day MA from above
    MAGNET_EFFECT = "MAGNET_EFFECT"  # Price near resistance with MA slope
    TOP_GAINERS = "TOP_GAINERS"  # N-day gainers
    TOP_LOSERS = "TOP_LOSERS"  # N-day losers

class OperatorType(str, Enum):
    GREATER_THAN = ">"
    LESS_THAN = "<"
    EQUALS = "=="
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    CROSSES_ABOVE = "CROSSES_ABOVE"
    CROSSES_BELOW = "CROSSES_BELOW"

class ConditionModel(BaseModel):
    indicator1: IndicatorType
    indicator1_params: Dict[str, Any]  # e.g., {"period": 50} for SMA(50)
    operator: OperatorType
    indicator2: Optional[IndicatorType] = None
    indicator2_params: Optional[Dict[str, Any]] = None
    value: Optional[float] = None  # Used when comparing to a static value

class StrategyModel(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    conditions: List[ConditionModel]
    timeframe: str  # "5m", "15m", "1h", "1D", etc.
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class StrategyCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    conditions: List[ConditionModel]
    timeframe: str

class StrategyUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    conditions: Optional[List[ConditionModel]] = None
    timeframe: Optional[str] = None

class StockScanRequest(BaseModel):
    strategy_id: str
    symbols: Optional[List[str]] = None  # If None, scan all symbols

class StockScanResult(BaseModel):
    symbol: str
    display_name: str
    matched: bool
    conditions_met: List[bool]
    current_price: float
    indicator_values: Dict[str, Any]
    timestamp: datetime

class PresetScanRequest(BaseModel):
    preset_type: PresetStrategyType
    parameters: Optional[Dict[str, Any]] = {}  # e.g., {"days": 7} for gainers/losers
    symbols: Optional[List[str]] = None  # If None, scan all symbols

