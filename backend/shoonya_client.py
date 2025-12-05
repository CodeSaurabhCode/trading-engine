import os
from dotenv import load_dotenv
from NorenRestApiPy.NorenApi import NorenApi
import pyotp
from datetime import datetime
import pandas as pd
from typing import List, Dict, Optional
import json

load_dotenv()

class ShoonyaClient:
    def __init__(self):
        self.api = NorenApi(
            host='https://api.shoonya.com/NorenWClientTP/',
            websocket='wss://api.shoonya.com/NorenWSTP/'
        )
        self.user_id = os.getenv('SHOONYA_USER_ID')
        self.password = os.getenv('SHOONYA_PASSWORD')
        self.totp_key = os.getenv('SHOONYA_TOTP_KEY')
        self.vendor_code = os.getenv('SHOONYA_VENDOR_CODE')
        self.api_key = os.getenv('SHOONYA_API_KEY')
        self.imei = os.getenv('SHOONYA_IMEI')
        self.session_token = None
        
        # Load symbol mappings
        self.symbol_map = self._load_symbol_map()
        
        # Validate credentials
        print(f"Loaded credentials - User ID: {self.user_id}")
        if not all([self.user_id, self.password, self.totp_key, self.vendor_code, self.api_key, self.imei]):
            print("WARNING: Some Shoonya credentials are missing!")
    
    def _load_symbol_map(self) -> Dict:
        """Load symbol mappings from JSON file"""
        try:
            json_path = os.path.join(os.path.dirname(__file__), 'symbols.json')
            with open(json_path, 'r') as f:
                data = json.load(f)
                # Create quick lookup by token
                symbol_map = {}
                for symbol in data['symbols']:
                    symbol_map[symbol['token']] = symbol
                return symbol_map
        except Exception as e:
            print(f"Warning: Could not load symbols.json: {e}")
            return {}
        
    async def login(self):
        """Login to Shoonya API"""
        if not all([self.user_id, self.password, self.totp_key, self.vendor_code, self.api_key, self.imei]):
            print("Cannot login: Missing credentials")
            return False
            
        try:
            # Generate TOTP
            totp = pyotp.TOTP(self.totp_key).now()
            print(f"Generated TOTP: {totp}")
            
            # Login (NorenApi methods are synchronous, not async)
            ret = self.api.login(
                userid=self.user_id,
                password=self.password,
                twoFA=totp,
                vendor_code=self.vendor_code,
                api_secret=self.api_key,
                imei=self.imei
            )
            
            print(f"Login response: {ret}")
            
            if ret and ret.get('stat') == 'Ok':
                self.session_token = ret.get('susertoken')
                print(f"✓ Login successful for user: {self.user_id}")
                return True
            else:
                print(f"✗ Login failed: {ret}")
                return False
                
        except Exception as e:
            print(f"✗ Login error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def get_historical_data(
        self, 
        symbol: str, 
        exchange: str, 
        interval: str,
        from_date: str,
        to_date: str
    ) -> List[Dict]:
        """
        Get historical candlestick data
        interval: 1, 3, 5, 10, 15, 30, 60, 120, 240 (intraday minutes), D (daily), W (weekly), M (monthly)
        date format: dd-mm-yyyy
        
        IMPORTANT: Shoonya has TWO different APIs:
        - get_time_price_series: For intraday data (1-240 minute candles)
        - get_daily_price_series: For daily, weekly, monthly data (D, W, M)
        """
        if not self.session_token:
            print("Not logged in to Shoonya")
            return []
            
        try:
            print(f"Fetching data for {symbol} ({exchange}) - Interval: {interval}")
            print(f"Date range: {from_date} to {to_date}")
            
            # Check if we need daily/weekly/monthly data (different API endpoint)
            if interval in ['D', 'W', 'M']:
                return await self._get_daily_data(symbol, exchange, from_date, to_date)
            else:
                return await self._get_intraday_data(symbol, exchange, interval, from_date, to_date)
            
        except Exception as e:
            print(f"✗ Error fetching historical data: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def _get_intraday_data(
        self,
        symbol: str,
        exchange: str,
        interval: str,
        from_date: str,
        to_date: str
    ) -> List[Dict]:
        """Get intraday data using get_time_price_series"""
        # Convert date strings to Unix timestamps
        start_timestamp = self._date_to_timestamp(from_date, "09:15:00")
        end_timestamp = self._date_to_timestamp(to_date, "15:30:00")
        
        print(f"Using get_time_price_series (intraday)")
        print(f"Start timestamp: {start_timestamp}, End timestamp: {end_timestamp}")
        
        # According to docs: starttime and endtime should be Unix timestamps (seconds since 1970)
        ret = self.api.get_time_price_series(
            exchange=exchange,
            token=symbol,
            starttime=start_timestamp,
            endtime=end_timestamp,
            interval=interval
        )
        
        print(f"API Response type: {type(ret)}")
        
        if ret is None:
            print("⚠️ API returned None - Historical intraday data may not be available")
            return []
        
        if isinstance(ret, dict) and ret.get('stat') == 'Not_Ok':
            print(f"✗ API Error: {ret.get('emsg', 'Unknown error')}")
            return []
        
        if ret and isinstance(ret, list):
            candles = []
            for bar in ret:
                if bar.get('stat') == 'Ok':  # Each bar has a stat field
                    candles.append({
                        'time': self._convert_timestamp(bar.get('time')),
                        'open': float(bar.get('into', 0)),
                        'high': float(bar.get('inth', 0)),
                        'low': float(bar.get('intl', 0)),
                        'close': float(bar.get('intc', 0)),
                        'volume': int(bar.get('v', 0))
                    })
            
            print(f"✓ Fetched {len(candles)} intraday candles")
            return candles
        
        print("No data returned from API")
        return []
    
    async def _get_daily_data(
        self,
        symbol: str,
        exchange: str,
        from_date: str,
        to_date: str
    ) -> List[Dict]:
        """Get daily/weekly/monthly data using get_daily_price_series"""
        # Convert date strings to Unix timestamps for daily API
        start_timestamp = self._date_to_timestamp(from_date, "00:00:00")
        end_timestamp = self._date_to_timestamp(to_date, "23:59:59")
        
        print(f"Using get_daily_price_series (daily/weekly/monthly)")
        print(f"Start timestamp: {start_timestamp}, End timestamp: {end_timestamp}")
        
        trading_symbol = None
        search_text = None
        
        # Check if symbol is in our symbol map
        if symbol in self.symbol_map:
            symbol_info = self.symbol_map[symbol]
            trading_symbol = symbol_info.get('tradingSymbol')
            search_text = symbol_info.get('searchName', symbol_info.get('tradingSymbol'))
            print(f"Found in symbol map: token={symbol} -> tradingSymbol={trading_symbol}")
        elif symbol.isdigit():
            # Token not in map, try to search for it
            print(f"Token {symbol} not in map, searching...")
            search_text = symbol
        else:
            # Assume it's already a trading symbol
            trading_symbol = symbol
            search_text = symbol
        
        # If we don't have trading symbol yet, search for it
        if not trading_symbol and search_text:
            search_ret = self.api.searchscrip(exchange=exchange, searchtext=search_text)
            
            if search_ret and search_ret.get('stat') == 'Ok':
                values = search_ret.get('values', [])
                if values:
                    # If we have a token, find exact match
                    if symbol.isdigit():
                        for val in values:
                            if val.get('token') == symbol:
                                trading_symbol = val.get('tsym')
                                break
                    # If no exact match or not a token, use first result
                    if not trading_symbol:
                        trading_symbol = values[0].get('tsym')
                    
                    print(f"Search found trading symbol: {trading_symbol}")
        
        if not trading_symbol:
            print(f"✗ Could not find trading symbol for {symbol} on {exchange}")
            return []
        
        # Call get_daily_price_series
        # NorenApi signature: (exchange, tradingsymbol, startdate=None, enddate=None)
        # Accepts both int and str timestamps
        print(f"Calling get_daily_price_series with tradingsymbol={trading_symbol}, startdate={start_timestamp}, enddate={end_timestamp}")
        
        ret = self.api.get_daily_price_series(
            exchange=exchange,
            tradingsymbol=trading_symbol,
            startdate=start_timestamp,  # Unix timestamp (int)
            enddate=end_timestamp
        )
        
        print(f"API Response type: {type(ret)}")
        
        if ret is None:
            print("⚠️ API returned None - Daily data may not be available")
            return []
        
        if isinstance(ret, dict) and ret.get('stat') == 'Not_Ok':
            print(f"✗ API Error: {ret.get('emsg', 'Unknown error')}")
            return []
        
        if ret and isinstance(ret, list):
            candles = []
            for bar in ret:
                # Daily API returns dict objects directly (not JSON strings as docs suggest)
                if isinstance(bar, str):
                    import json
                    bar = json.loads(bar)
                
                # Daily data doesn't have 'stat' field in each bar
                if 'time' in bar:
                    # Convert time format: "26-NOV-2025" to Unix timestamp
                    time_str = bar.get('time', '')
                    candles.append({
                        'time': self._convert_daily_timestamp(time_str),
                        'open': float(bar.get('into', 0)),
                        'high': float(bar.get('inth', 0)),
                        'low': float(bar.get('intl', 0)),
                        'close': float(bar.get('intc', 0)),
                        'volume': int(float(bar.get('intv', 0)))  # Note: 'intv' for daily data (can be float string)
                    })
            
            print(f"✓ Fetched {len(candles)} daily candles")
            return candles
        
        print("No data returned from API")
        return []
    
    async def get_quote(self, exchange: str, symbol: str) -> Dict:
        """Get current quote for a symbol"""
        try:
            ret = self.api.get_quotes(exchange=exchange, token=symbol)
            
            if ret:
                return {
                    'symbol': symbol,
                    'ltp': float(ret.get('lp', 0)),
                    'open': float(ret.get('o', 0)),
                    'high': float(ret.get('h', 0)),
                    'low': float(ret.get('l', 0)),
                    'close': float(ret.get('c', 0)),
                    'volume': int(ret.get('v', 0)),
                    'change': float(ret.get('lp', 0)) - float(ret.get('c', 0))
                }
            return {}
            
        except Exception as e:
            print(f"Error fetching quote: {e}")
            raise
    
    def _date_to_timestamp(self, date_str: str, time_str: str) -> int:
        """
        Convert date string to Unix timestamp (seconds since 1970)
        date_str: dd-mm-yyyy
        time_str: HH:MM:SS
        Returns: Unix timestamp as integer
        """
        try:
            datetime_str = f"{date_str} {time_str}"
            dt = datetime.strptime(datetime_str, "%d-%m-%Y %H:%M:%S")
            return int(dt.timestamp())
        except Exception as e:
            print(f"Error converting date to timestamp: {e}")
            return 0
    
    def _convert_timestamp(self, timestamp_str: str) -> int:
        """Convert timestamp string from intraday API to Unix timestamp"""
        try:
            # Parse the timestamp from Shoonya format: "dd-mm-yyyy HH:MM:SS"
            dt = datetime.strptime(timestamp_str, "%d-%m-%Y %H:%M:%S")
            return int(dt.timestamp())
        except:
            return 0
    
    def _convert_daily_timestamp(self, timestamp_str: str) -> int:
        """Convert timestamp string from daily API to Unix timestamp"""
        try:
            # Parse the timestamp from Shoonya daily format: "21-SEP-2022"
            dt = datetime.strptime(timestamp_str, "%d-%b-%Y")
            return int(dt.timestamp())
        except Exception as e:
            print(f"Error converting daily timestamp '{timestamp_str}': {e}")
            return 0
    
    def subscribe_symbols(self, symbols: List[Dict]):
        """Subscribe to symbols for real-time data"""
        try:
            for symbol_info in symbols:
                self.api.subscribe(
                    f"{symbol_info['exchange']}|{symbol_info['token']}"
                )
        except Exception as e:
            print(f"Error subscribing to symbols: {e}")
            raise
