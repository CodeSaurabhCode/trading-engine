import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional

class IndicatorCalculator:
    """Calculate technical indicators for strategy evaluation"""
    
    @staticmethod
    def calculate_sma(data: pd.DataFrame, period: int, price_col: str = 'close') -> pd.Series:
        """Calculate Simple Moving Average"""
        return data[price_col].rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(data: pd.DataFrame, period: int, price_col: str = 'close') -> pd.Series:
        """Calculate Exponential Moving Average"""
        return data[price_col].ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_rsi(data: pd.DataFrame, period: int = 14, price_col: str = 'close') -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = data[price_col].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_macd(data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9, price_col: str = 'close') -> Dict[str, pd.Series]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        ema_fast = data[price_col].ewm(span=fast, adjust=False).mean()
        ema_slow = data[price_col].ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.DataFrame, period: int = 20, std_dev: int = 2, price_col: str = 'close') -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands"""
        sma = data[price_col].rolling(window=period).mean()
        std = data[price_col].rolling(window=period).std()
        
        return {
            'upper': sma + (std * std_dev),
            'middle': sma,
            'lower': sma - (std * std_dev)
        }
    
    @staticmethod
    def calculate_atr(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high = data['high']
        low = data['low']
        close = data['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    @staticmethod
    def calculate_stochastic(data: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Dict[str, pd.Series]:
        """Calculate Stochastic Oscillator"""
        low_min = data['low'].rolling(window=k_period).min()
        high_max = data['high'].rolling(window=k_period).max()
        
        k = 100 * ((data['close'] - low_min) / (high_max - low_min))
        d = k.rolling(window=d_period).mean()
        
        return {
            'k': k,
            'd': d
        }
    
    @staticmethod
    def calculate_adx(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average Directional Index"""
        high = data['high']
        low = data['low']
        close = data['close']
        
        # Calculate +DM and -DM
        plus_dm = high.diff()
        minus_dm = low.diff() * -1
        
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        # Calculate True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate smoothed averages
        atr = tr.rolling(window=period).mean()
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        # Calculate ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return adx
    
    @staticmethod
    def check_crossover(series1: pd.Series, series2: pd.Series, lookback: int = 2) -> bool:
        """Check if series1 crosses above series2"""
        if len(series1) < lookback or len(series2) < lookback:
            return False
        return series1.iloc[-2] <= series2.iloc[-2] and series1.iloc[-1] > series2.iloc[-1]
    
    @staticmethod
    def check_crossunder(series1: pd.Series, series2: pd.Series, lookback: int = 2) -> bool:
        """Check if series1 crosses below series2"""
        if len(series1) < lookback or len(series2) < lookback:
            return False
        return series1.iloc[-2] >= series2.iloc[-2] and series1.iloc[-1] < series2.iloc[-1]
