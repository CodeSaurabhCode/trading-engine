from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime, timedelta
from shoonya_client import ShoonyaClient
import json
import os
import pandas as pd

# Import strategy models and engine
from models import (
    StrategyCreateRequest, 
    StrategyUpdateRequest, 
    StockScanRequest,
    StockScanResult,
    StrategyModel,
    PresetScanRequest,
    PresetStrategyType
)
from strategy_engine import StrategyEngine
from preset_strategies import PresetStrategies

# Initialize Shoonya client and Strategy Engine
shoonya_client = ShoonyaClient()
strategy_engine = StrategyEngine()

# Load symbols from JSON
def load_symbols():
    try:
        json_path = os.path.join(os.path.dirname(__file__), 'symbols.json')
        with open(json_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading symbols.json: {e}")
        return {"symbols": []}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    try:
        await shoonya_client.login()
        print("Shoonya client logged in successfully")
    except Exception as e:
        print(f"Failed to login to Shoonya: {e}")
    
    yield
    
    # Shutdown (cleanup if needed)
    print("Shutting down...")

app = FastAPI(title="Trading System API", lifespan=lifespan)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HistoricalDataRequest(BaseModel):
    symbol: str
    exchange: str = "NSE"
    interval: str = "1"  # 1, 3, 5, 10, 15, 30, 60, 120, 240, D, W, M
    from_date: Optional[str] = None  # Format: dd-mm-yyyy
    to_date: Optional[str] = None    # Format: dd-mm-yyyy
    
    # Shoonya API Historical Data Limits:
    # - 1 min candles: Max 7 days of data
    # - 5 min candles: Max 30 days of data
    # - 15 min candles: Max 90 days of data
    # - 1 hour candles: Max 180 days of data
    # - Daily candles: Max 365 days of data
    # - Weekly/Monthly: 2-5 years of data

@app.get("/")
async def root():
    return {"message": "Trading System API", "status": "running"}

@app.get("/api/symbols")
async def get_symbols():
    """Get list of available symbols from symbols.json"""
    symbols_data = load_symbols()
    # Format for frontend
    formatted_symbols = []
    for symbol in symbols_data.get('symbols', []):
        formatted_symbols.append({
            "symbol": symbol['tradingSymbol'],
            "token": symbol['token'],
            "exchange": symbol['exchange'],
            "display": symbol['displayName'],
            "type": symbol['type']
        })
    return {"symbols": formatted_symbols}

@app.post("/api/historical-data")
async def get_historical_data(request: HistoricalDataRequest):
    """Get historical candlestick data"""
    try:
        # Shoonya API limits for historical data based on interval
        # Define optimal lookback periods for each interval
        interval_limits = {
            "1": 7,      # 1 min - 7 days max
            "3": 15,     # 3 min - 15 days
            "5": 30,     # 5 min - 30 days
            "10": 60,    # 10 min - 60 days
            "15": 90,    # 15 min - 90 days
            "30": 90,    # 30 min - 90 days
            "60": 180,   # 1 hour - 180 days
            "120": 365,  # 2 hour - 365 days
            "240": 365,  # 4 hour - 365 days
            "D": 365,    # Daily - 365 days
            "W": 730,    # Weekly - 2 years
            "M": 1825,   # Monthly - 5 years
        }
        
        # Get appropriate lookback days for the interval
        lookback_days = interval_limits.get(str(request.interval), 30)
        
        # Calculate date range if not provided
        to_date = request.to_date or datetime.now().strftime("%d-%m-%Y")
        from_date = request.from_date or (datetime.now() - timedelta(days=lookback_days)).strftime("%d-%m-%Y")
        
        print(f"Fetching {request.interval} interval data from {from_date} to {to_date} ({lookback_days} days)")
        
        # Get data from Shoonya
        data = await shoonya_client.get_historical_data(
            symbol=request.symbol,
            exchange=request.exchange,
            interval=request.interval,
            from_date=from_date,
            to_date=to_date
        )
        
        return {"data": data, "symbol": request.symbol, "interval": request.interval}
    except Exception as e:
        print(f"Error in get_historical_data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/quote/{exchange}/{symbol}")
async def get_quote(exchange: str, symbol: str):
    """Get current quote for a symbol"""
    try:
        quote = await shoonya_client.get_quote(exchange, symbol)
        return quote
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/market-data")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time market data"""
    await websocket.accept()
    try:
        while True:
            # Receive subscription request
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("action") == "subscribe":
                symbol = message.get("symbol")
                exchange = message.get("exchange")
                # Handle subscription
                await websocket.send_text(json.dumps({
                    "type": "subscribed",
                    "symbol": symbol,
                    "exchange": exchange
                }))
            
            # In a real implementation, you would set up Shoonya WebSocket here
            # and forward the tick data to the client
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

# ============= Strategy Management Endpoints =============

@app.post("/api/strategies", response_model=StrategyModel)
async def create_strategy(request: StrategyCreateRequest):
    """Create a new trading strategy"""
    try:
        strategy = strategy_engine.create_strategy(
            name=request.name,
            description=request.description,
            conditions=request.conditions,
            timeframe=request.timeframe
        )
        return strategy
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/strategies", response_model=List[StrategyModel])
async def get_all_strategies():
    """Get all strategies"""
    return strategy_engine.get_all_strategies()

@app.get("/api/strategies/{strategy_id}", response_model=StrategyModel)
async def get_strategy(strategy_id: str):
    """Get a specific strategy by ID"""
    strategy = strategy_engine.get_strategy(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy

@app.put("/api/strategies/{strategy_id}", response_model=StrategyModel)
async def update_strategy(strategy_id: str, request: StrategyUpdateRequest):
    """Update an existing strategy"""
    strategy = strategy_engine.update_strategy(
        strategy_id,
        name=request.name,
        description=request.description,
        conditions=request.conditions,
        timeframe=request.timeframe
    )
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy

@app.delete("/api/strategies/{strategy_id}")
async def delete_strategy(strategy_id: str):
    """Delete a strategy"""
    success = strategy_engine.delete_strategy(strategy_id)
    if not success:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return {"message": "Strategy deleted successfully"}

@app.post("/api/strategies/scan", response_model=List[StockScanResult])
async def scan_stocks(request: StockScanRequest):
    """Scan stocks against a strategy"""
    try:
        # Get strategy
        strategy = strategy_engine.get_strategy(request.strategy_id)
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        # Get symbols to scan
        symbols_data = load_symbols()
        all_symbols = symbols_data.get('symbols', [])
        
        # Filter symbols if specific ones requested
        if request.symbols:
            symbols_to_scan = [s for s in all_symbols if s['tradingSymbol'] in request.symbols]
        else:
            symbols_to_scan = all_symbols
        
        # Fetch historical data for each symbol
        stock_data_dict = {}
        symbols_info = {}
        
        for symbol_info in symbols_to_scan:
            try:
                symbol = symbol_info['tradingSymbol']
                exchange = symbol_info['exchange']
                
                # Determine lookback based on timeframe
                timeframe_days = {
                    "5m": 30, "15m": 90, "30m": 90, "1h": 180, 
                    "2h": 365, "4h": 365, "1D": 365, "1W": 730
                }
                lookback = timeframe_days.get(strategy.timeframe, 90)
                
                from_date = (datetime.now() - timedelta(days=lookback)).strftime("%d-%m-%Y")
                to_date = datetime.now().strftime("%d-%m-%Y")
                
                # Fetch data
                data = await shoonya_client.get_historical_data(
                    symbol=symbol,
                    exchange=exchange,
                    interval=strategy.timeframe.replace("m", "").replace("h", "").replace("D", "D").replace("W", "W"),
                    from_date=from_date,
                    to_date=to_date
                )
                
                # Convert to DataFrame
                if data and len(data) > 0:
                    df = pd.DataFrame(data)
                    # Ensure columns are properly named
                    if 'time' in df.columns:
                        df['date'] = pd.to_datetime(df['time'], unit='s')
                    stock_data_dict[symbol] = df
                    symbols_info[symbol] = symbol_info
                
            except Exception as e:
                print(f"Error fetching data for {symbol_info['tradingSymbol']}: {e}")
                continue
        
        # Scan stocks
        results = strategy_engine.scan_stocks(request.strategy_id, stock_data_dict, symbols_info)
        
        # Sort by matched stocks first
        results.sort(key=lambda x: x.matched, reverse=True)
        
        return results
        
    except Exception as e:
        print(f"Error in scan_stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/preset-strategies/scan", response_model=List[StockScanResult])
async def scan_preset_strategy(request: PresetScanRequest):
    """Scan stocks using preset strategies from notebook"""
    try:
        # Get symbols to scan
        symbols_data = load_symbols()
        all_symbols = symbols_data.get('symbols', [])
        
        # Filter symbols if specific ones requested
        if request.symbols:
            symbols_to_scan = [s for s in all_symbols if s['tradingSymbol'] in request.symbols]
        else:
            symbols_to_scan = all_symbols
        
        # Determine lookback based on strategy type
        strategy_lookback = {
            PresetStrategyType.MA44: 90,
            PresetStrategyType.MA44_CROSS_MA200: 365,
            PresetStrategyType.EMA_CROSSOVER: 90,
            PresetStrategyType.DOWN_TO_MA200: 365,
            PresetStrategyType.MAGNET_EFFECT: 365,
            PresetStrategyType.TOP_GAINERS: 30,
            PresetStrategyType.TOP_LOSERS: 30
        }
        lookback = strategy_lookback.get(request.preset_type, 90)
        
        # Fetch historical data for each symbol
        stock_data_dict = {}
        symbols_info = {}
        
        for symbol_info in symbols_to_scan:
            try:
                symbol = symbol_info['tradingSymbol']
                exchange = symbol_info['exchange']
                
                from_date = (datetime.now() - timedelta(days=lookback)).strftime("%d-%m-%Y")
                to_date = datetime.now().strftime("%d-%m-%Y")
                
                # Use daily data for these strategies
                data = await shoonya_client.get_historical_data(
                    symbol=symbol,
                    exchange=exchange,
                    interval="D",
                    from_date=from_date,
                    to_date=to_date
                )
                
                # Convert to DataFrame
                if data and len(data) > 0:
                    df = pd.DataFrame(data)
                    if 'time' in df.columns:
                        df['date'] = pd.to_datetime(df['time'], unit='s')
                    stock_data_dict[symbol] = df
                    symbols_info[symbol] = symbol_info
                
            except Exception as e:
                print(f"Error fetching data for {symbol_info['tradingSymbol']}: {e}")
                continue
        
        # Execute preset strategy
        preset_strategies = PresetStrategies()
        
        if request.preset_type == PresetStrategyType.MA44:
            results = preset_strategies.ma44_strategy(stock_data_dict, symbols_info)
        elif request.preset_type == PresetStrategyType.MA44_CROSS_MA200:
            results = preset_strategies.ma44_cross_ma200_strategy(stock_data_dict, symbols_info)
        elif request.preset_type == PresetStrategyType.EMA_CROSSOVER:
            results = preset_strategies.ema_crossover_strategy(stock_data_dict, symbols_info)
        elif request.preset_type == PresetStrategyType.DOWN_TO_MA200:
            results = preset_strategies.down_to_ma200_strategy(stock_data_dict, symbols_info)
        elif request.preset_type == PresetStrategyType.MAGNET_EFFECT:
            results = preset_strategies.magnet_effect_strategy(stock_data_dict, symbols_info)
        elif request.preset_type == PresetStrategyType.TOP_GAINERS:
            days = request.parameters.get('days', 7)
            results = preset_strategies.top_gainers_strategy(stock_data_dict, symbols_info, days)
        elif request.preset_type == PresetStrategyType.TOP_LOSERS:
            days = request.parameters.get('days', 7)
            results = preset_strategies.top_losers_strategy(stock_data_dict, symbols_info, days)
        else:
            raise HTTPException(status_code=400, detail="Invalid preset strategy type")
        
        # Sort by matched stocks first
        results.sort(key=lambda x: x.matched, reverse=True)
        
        return results
        
    except Exception as e:
        print(f"Error in scan_preset_strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
