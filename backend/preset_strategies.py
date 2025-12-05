import pandas as pd
import numpy as np
from typing import List, Dict, Any
from datetime import datetime
from models import StockScanResult, PresetStrategyType

class PresetStrategies:
    """Implementation of preset strategies from the notebook"""
    
    @staticmethod
    def calculate_slope(series: pd.Series, periods: int = 5) -> float:
        """Calculate linear regression slope of last N periods"""
        if len(series) < periods:
            return 0.0
        last_n = series.tail(periods)
        x = np.arange(len(last_n))
        if len(last_n) == 0 or last_n.isna().all():
            return 0.0
        slope, _ = np.polyfit(x, last_n.values, 1)
        return float(slope)
    
    @staticmethod
    def ma44_strategy(stock_data_dict: Dict[str, pd.DataFrame], symbols_info: Dict[str, Dict]) -> List[StockScanResult]:
        """
        MA44 Strategy: Price near 44-day MA with positive slope
        Conditions:
        - MA44 slope > 0
        - -3% < (MA44 - Close) / Close < 3%
        - Close > MA44
        """
        results = []
        
        for symbol, data in stock_data_dict.items():
            if data is None or len(data) < 44:
                continue
            
            try:
                close = data['close']
                ma44 = close.rolling(window=44).mean()
                
                if len(ma44) < 5 or ma44.isna().iloc[-1]:
                    continue
                
                slope = PresetStrategies.calculate_slope(ma44, 5)
                last_close = float(close.iloc[-1])
                last_ma44 = float(ma44.iloc[-1])
                diff_pct = ((last_ma44 - last_close) / last_close) * 100
                
                # Check conditions
                slope_ok = slope > 0
                diff_ok = -3 < diff_pct < 3
                price_above_ma = last_close > last_ma44
                
                matched = slope_ok and diff_ok and price_above_ma
                
                symbol_info = symbols_info.get(symbol, {})
                result = StockScanResult(
                    symbol=symbol,
                    display_name=symbol_info.get('displayName', symbol),
                    matched=matched,
                    conditions_met=[slope_ok, diff_ok, price_above_ma],
                    current_price=last_close,
                    indicator_values={
                        'ma44': last_ma44,
                        'slope': slope,
                        'diff_pct': diff_pct
                    },
                    timestamp=datetime.now()
                )
                results.append(result)
            except Exception as e:
                print(f"Error processing {symbol} in MA44: {e}")
                continue
        
        return results
    
    @staticmethod
    def ma44_cross_ma200_strategy(stock_data_dict: Dict[str, pd.DataFrame], symbols_info: Dict[str, Dict]) -> List[StockScanResult]:
        """
        MA44 Cross MA200 Strategy: 44-day MA near or crossing 200-day MA
        Conditions:
        - -1% < (MA44 - MA200) / MA44 < 1%
        """
        results = []
        
        for symbol, data in stock_data_dict.items():
            if data is None or len(data) < 200:
                continue
            
            try:
                close = data['close']
                ma44 = close.rolling(window=44).mean()
                ma200 = close.rolling(window=200).mean()
                
                if ma44.isna().iloc[-1] or ma200.isna().iloc[-1]:
                    continue
                
                last_close = float(close.iloc[-1])
                last_ma44 = float(ma44.iloc[-1])
                last_ma200 = float(ma200.iloc[-1])
                diff_pct = abs((last_ma44 - last_ma200) / last_ma44) * 100
                
                # Check if near crossover
                near_cross = diff_pct < 1.0
                
                matched = near_cross
                
                symbol_info = symbols_info.get(symbol, {})
                result = StockScanResult(
                    symbol=symbol,
                    display_name=symbol_info.get('displayName', symbol),
                    matched=matched,
                    conditions_met=[near_cross],
                    current_price=last_close,
                    indicator_values={
                        'ma44': last_ma44,
                        'ma200': last_ma200,
                        'diff_pct': diff_pct
                    },
                    timestamp=datetime.now()
                )
                results.append(result)
            except Exception as e:
                print(f"Error processing {symbol} in MA44_CROSS_MA200: {e}")
                continue
        
        return results
    
    @staticmethod
    def ema_crossover_strategy(stock_data_dict: Dict[str, pd.DataFrame], symbols_info: Dict[str, Dict]) -> List[StockScanResult]:
        """
        EMA Crossover Strategy: EMA(10) approaching EMA(30)
        Conditions:
        - |EMA10 - EMA30| / EMA30 < 0.05%
        """
        results = []
        
        for symbol, data in stock_data_dict.items():
            if data is None or len(data) < 30:
                continue
            
            try:
                close = data['close']
                ema10 = close.ewm(span=10, adjust=False).mean()
                ema30 = close.ewm(span=30, adjust=False).mean()
                
                if ema10.isna().iloc[-1] or ema30.isna().iloc[-1]:
                    continue
                
                last_close = float(close.iloc[-1])
                last_ema10 = float(ema10.iloc[-1])
                last_ema30 = float(ema30.iloc[-1])
                diff_pct = abs((last_ema10 - last_ema30) / last_ema30) * 100
                
                # Check if EMAs are approaching
                approaching = diff_pct <= 0.05
                
                matched = approaching
                
                symbol_info = symbols_info.get(symbol, {})
                result = StockScanResult(
                    symbol=symbol,
                    display_name=symbol_info.get('displayName', symbol),
                    matched=matched,
                    conditions_met=[approaching],
                    current_price=last_close,
                    indicator_values={
                        'ema10': last_ema10,
                        'ema30': last_ema30,
                        'diff_pct': diff_pct
                    },
                    timestamp=datetime.now()
                )
                results.append(result)
            except Exception as e:
                print(f"Error processing {symbol} in EMA_CROSSOVER: {e}")
                continue
        
        return results
    
    @staticmethod
    def down_to_ma200_strategy(stock_data_dict: Dict[str, pd.DataFrame], symbols_info: Dict[str, Dict]) -> List[StockScanResult]:
        """
        Down to MA200 Strategy: Price approaching 200-day MA from above
        Conditions:
        - -3% < (MA200 - Close) / Close < 3%
        - MA200 slope < 1 (downtrend or flat)
        - Close > MA200
        """
        results = []
        
        for symbol, data in stock_data_dict.items():
            if data is None or len(data) < 200:
                continue
            
            try:
                close = data['close']
                ma200 = close.rolling(window=200).mean()
                
                if ma200.isna().iloc[-1]:
                    continue
                
                slope = PresetStrategies.calculate_slope(ma200, 5)
                last_close = float(close.iloc[-1])
                last_ma200 = float(ma200.iloc[-1])
                diff_pct = ((last_ma200 - last_close) / last_close) * 100
                
                # Check conditions
                diff_ok = -3 < diff_pct < 3
                slope_ok = slope < 1
                price_above_ma = last_close > last_ma200
                
                matched = diff_ok and slope_ok and price_above_ma
                
                symbol_info = symbols_info.get(symbol, {})
                result = StockScanResult(
                    symbol=symbol,
                    display_name=symbol_info.get('displayName', symbol),
                    matched=matched,
                    conditions_met=[diff_ok, slope_ok, price_above_ma],
                    current_price=last_close,
                    indicator_values={
                        'ma200': last_ma200,
                        'slope': slope,
                        'diff_pct': diff_pct
                    },
                    timestamp=datetime.now()
                )
                results.append(result)
            except Exception as e:
                print(f"Error processing {symbol} in DOWN_TO_MA200: {e}")
                continue
        
        return results
    
    @staticmethod
    def create_zigzag_points(series: pd.Series, min_retrace: float = 0.1) -> pd.DataFrame:
        """Create ZigZag indicator points"""
        if len(series) == 0:
            return pd.DataFrame(columns=['Dir', 'Value'])
        
        cur_val = series.iloc[0]
        cur_pos = 0
        cur_dir = 1
        
        result_data = []
        
        for i in range(len(series)):
            if (series.iloc[i] - cur_val) * cur_dir >= 0:
                cur_val = series.iloc[i]
                cur_pos = i
            else:
                retrace_prc = abs((series.iloc[i] - cur_val) / cur_val * 100)
                if retrace_prc >= min_retrace:
                    result_data.append({'index': cur_pos, 'Value': cur_val, 'Dir': cur_dir})
                    cur_val = series.iloc[i]
                    cur_pos = i
                    cur_dir = -1 * cur_dir
        
        return pd.DataFrame(result_data)
    
    @staticmethod
    def magnet_effect_strategy(stock_data_dict: Dict[str, pd.DataFrame], symbols_info: Dict[str, Dict]) -> List[StockScanResult]:
        """
        Magnet Effect Strategy: Price near resistance with positive MA200 slope
        Conditions:
        - MA200 slope > 0
        - Close > MA44
        - -1% < (Resistance - Close) / Close < 1%
        """
        results = []
        
        for symbol, data in stock_data_dict.items():
            if data is None or len(data) < 200:
                continue
            
            try:
                close = data['close']
                ma44 = close.rolling(window=44).mean()
                ma200 = close.rolling(window=200).mean()
                
                if ma44.isna().iloc[-1] or ma200.isna().iloc[-1]:
                    continue
                
                # Calculate resistance using ZigZag
                last_30_close = close.iloc[-30:] if len(close) >= 30 else close
                zigzag = PresetStrategies.create_zigzag_points(last_30_close)
                
                resistance = None
                if len(zigzag) > 0:
                    peaks = zigzag[zigzag['Dir'] == 1]
                    if len(peaks) > 0:
                        resistance = float(peaks['Value'].max())
                
                if resistance is None:
                    continue
                
                slope = PresetStrategies.calculate_slope(ma200, 5)
                last_close = float(close.iloc[-1])
                last_ma44 = float(ma44.iloc[-1])
                res_diff_pct = ((resistance - last_close) / last_close) * 100
                
                # Check conditions
                slope_ok = slope > 0
                price_above_ma44 = last_close > last_ma44
                near_resistance = -1 < res_diff_pct < 1
                
                matched = slope_ok and price_above_ma44 and near_resistance
                
                symbol_info = symbols_info.get(symbol, {})
                result = StockScanResult(
                    symbol=symbol,
                    display_name=symbol_info.get('displayName', symbol),
                    matched=matched,
                    conditions_met=[slope_ok, price_above_ma44, near_resistance],
                    current_price=last_close,
                    indicator_values={
                        'ma44': last_ma44,
                        'ma200_slope': slope,
                        'resistance': resistance,
                        'res_diff_pct': res_diff_pct
                    },
                    timestamp=datetime.now()
                )
                results.append(result)
            except Exception as e:
                print(f"Error processing {symbol} in MAGNET_EFFECT: {e}")
                continue
        
        return results
    
    @staticmethod
    def top_gainers_strategy(stock_data_dict: Dict[str, pd.DataFrame], symbols_info: Dict[str, Dict], days: int = 7) -> List[StockScanResult]:
        """
        Top Gainers Strategy: Stocks with highest N-day returns
        Returns top 20 gainers
        """
        results = []
        
        for symbol, data in stock_data_dict.items():
            if data is None or len(data) < days:
                continue
            
            try:
                close = data['close']
                recent_close = close.iloc[-days:]
                
                if len(recent_close) < days:
                    continue
                
                start_price = float(recent_close.iloc[0])
                end_price = float(recent_close.iloc[-1])
                change_pct = ((end_price - start_price) / start_price) * 100
                
                symbol_info = symbols_info.get(symbol, {})
                result = StockScanResult(
                    symbol=symbol,
                    display_name=symbol_info.get('displayName', symbol),
                    matched=False,  # Will be set after sorting
                    conditions_met=[],
                    current_price=end_price,
                    indicator_values={
                        'change_pct': change_pct,
                        'days': days
                    },
                    timestamp=datetime.now()
                )
                results.append(result)
            except Exception as e:
                print(f"Error processing {symbol} in TOP_GAINERS: {e}")
                continue
        
        # Sort by change and mark top 20 as matched
        results.sort(key=lambda x: x.indicator_values['change_pct'], reverse=True)
        for i, result in enumerate(results[:20]):
            result.matched = True
        
        return results
    
    @staticmethod
    def top_losers_strategy(stock_data_dict: Dict[str, pd.DataFrame], symbols_info: Dict[str, Dict], days: int = 7) -> List[StockScanResult]:
        """
        Top Losers Strategy: Stocks with lowest N-day returns
        Returns top 20 losers
        """
        results = []
        
        for symbol, data in stock_data_dict.items():
            if data is None or len(data) < days:
                continue
            
            try:
                close = data['close']
                recent_close = close.iloc[-days:]
                
                if len(recent_close) < days:
                    continue
                
                start_price = float(recent_close.iloc[0])
                end_price = float(recent_close.iloc[-1])
                change_pct = ((end_price - start_price) / start_price) * 100
                
                symbol_info = symbols_info.get(symbol, {})
                result = StockScanResult(
                    symbol=symbol,
                    display_name=symbol_info.get('displayName', symbol),
                    matched=False,  # Will be set after sorting
                    conditions_met=[],
                    current_price=end_price,
                    indicator_values={
                        'change_pct': change_pct,
                        'days': days
                    },
                    timestamp=datetime.now()
                )
                results.append(result)
            except Exception as e:
                print(f"Error processing {symbol} in TOP_LOSERS: {e}")
                continue
        
        # Sort by change (ascending) and mark top 20 as matched
        results.sort(key=lambda x: x.indicator_values['change_pct'])
        for i, result in enumerate(results[:20]):
            result.matched = True
        
        return results
