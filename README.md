# Trading System

A comprehensive trading and strategy screening application that integrates with Shoonya API to provide advanced charting and stock filtering capabilities.

## Features

### 📊 Advanced Charting
- Interactive candlestick, line, and area charts with TradingView-style interface
- Multiple timeframe support (1m, 5m, 15m, 1h, 1D, 1W, 1M)
- Volume histogram overlay with auto-scaling
- Real-time price crosshair with OHLCV display
- Professional dark theme UI

### 📈 Preset Strategy Screener
- **7 battle-tested quantitative strategies** from production notebook:
  - **MA44 Strategy** - Price consolidation around 44-day moving average with positive slope
  - **MA44 Cross MA200** - Golden/Death cross detection between 44-day and 200-day MA
  - **EMA Crossover** - Short-term momentum shifts (EMA10 approaching EMA30)
  - **Down to MA200** - Support bounce opportunities (price near 200-day MA from above)
  - **Magnet Effect** - Resistance breakout candidates using ZigZag indicator
  - **Top Gainers** - Best performers over customizable period (default 7 days)
  - **Top Losers** - Worst performers over customizable period (default 7 days)
- Real-time scanning across all configured symbols
- Results table with strategy-specific metrics and color-coded indicators

### ⚡ Custom Strategy Builder
- Create and manage custom screening strategies
- **10 Technical Indicators**: SMA, EMA, RSI, MACD, Bollinger Bands, ATR, Stochastic, OBV, ADX, CCI
- **7 Comparison Operators**: Greater than, Less than, Equal to, Crosses above, Crosses below, Between, Not between
- Multi-condition support with AND/OR logic
- Save, edit, and delete custom strategies
- Instant scanning with real-time results

### 🔌 Shoonya API Integration
- Automatic TOTP authentication
- Historical data fetching (intraday and daily)
- Multi-symbol support with NSE integration

## Project Structure

```
trading-system/
├── backend/                      # FastAPI backend
│   ├── main.py                  # Main API server with endpoints
│   ├── shoonya_client.py        # Shoonya API client wrapper
│   ├── strategy_engine.py       # Custom strategy evaluation engine
│   ├── preset_strategies.py     # 7 preset strategies from notebook
│   ├── models.py                # Pydantic models for API
│   ├── symbols.json             # Symbol configuration (NSE tokens)
│   ├── requirements.txt         # Python dependencies
│   └── .env                     # Environment variables (credentials)
└── frontend/                     # React + Vite frontend
    ├── src/
    │   ├── components/
    │   │   ├── TradingChart.jsx       # Main charting component
    │   │   ├── PresetStrategies.jsx   # Preset strategy screener UI
    │   │   ├── StrategyBuilder.jsx    # Custom strategy builder
    │   │   ├── StrategyBuilder.css    # Strategy builder styles
    │   │   └── PresetStrategies.css   # Preset strategies styles
    │   ├── App.jsx              # Main app with 3-tab navigation
    │   ├── App.css              # App-wide styles
    │   └── main.jsx             # Entry point
    ├── package.json
    └── vite.config.js
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file from `.env.example`:
```bash
copy .env.example .env
```

5. Fill in your Shoonya API credentials in `.env`:
```
SHOONYA_USER_ID=your_user_id
SHOONYA_PASSWORD=your_password
SHOONYA_TOTP_KEY=your_totp_key
SHOONYA_VENDOR_CODE=your_vendor_code
SHOONYA_API_KEY=your_api_key
SHOONYA_IMEI=your_imei
```

6. Run the backend server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Usage

### Quick Start
1. **Start Backend**: `cd backend && python main.py` (runs on port 8000)
2. **Start Frontend**: `cd frontend && npm run dev` (runs on port 3000/3001)
3. **Open Browser**: Navigate to `http://localhost:3000` (or 3001)

### Three Main Features

#### 1. 📊 Charts Tab
- Select a symbol from the dropdown (e.g., NIFTY 50, SBIN, RELIANCE)
- Choose timeframe (1m to 1M)
- Switch between candlestick/line/area chart types
- View volume histogram and price crosshair

#### 2. 📈 Preset Strategies Tab
- Click any of the 7 strategy cards to select
- For Top Gainers/Losers: adjust the days parameter (default 7)
- Click **"Run Strategy Scan"** to scan all symbols
- View results table with:
  - **Green rows**: Matched conditions
  - **Gray rows**: Didn't match
  - Strategy-specific columns (MA values, slopes, percentages)

**Strategy Examples:**
- **MA44**: Find stocks consolidating around 44-day MA (±3%) with uptrend
- **Magnet Effect**: Find stocks near resistance with potential breakout
- **Top Gainers (7 days)**: See best performers in last week

#### 3. ⚡ Custom Builder Tab
- Click **"New Strategy"** to create
- Add conditions using:
  - **Indicators**: SMA(20), RSI(14), MACD, Bollinger Bands, etc.
  - **Operators**: >, <, =, crosses above, crosses below, between
  - **Values**: Price, numbers, or other indicators
- Save strategy and click **"Scan"**
- Edit or delete strategies anytime

## API Endpoints

### Chart Data
- `GET /api/symbols` - Get available symbols with tokens
- `POST /api/historical-data` - Get OHLCV data for charting
  - Body: `{ symbol, interval, from_date, to_date }`
  - Returns: Array of candlestick data

### Strategy Scanning
- `POST /api/preset-strategies/scan` - Scan with preset strategies
  - Body: `{ preset_type: "MA44" | "MA44_CROSS_MA200" | etc., parameters?: { days: 7 }, symbols?: [...] }`
  - Returns: Array of `StockScanResult` with matched stocks first

- `POST /api/strategies/scan` - Scan with custom strategy
  - Body: `{ strategy: { name, conditions: [...] }, symbols?: [...] }`
  - Returns: Array of `StockScanResult` with indicator values

### Real-time (Future)
- `WS /ws/market-data` - WebSocket for live data (planned)

## Timeframes Supported

- 1m, 3m, 5m, 10m, 15m, 30m (Minutes)
- 1h, 2h, 4h (Hours)
- 1D (Daily)
- 1W (Weekly)
- 1M (Monthly)

## Technologies Used

### Backend
- **FastAPI** - Modern async Python web framework
- **NorenRestApiPy** - Shoonya API client for Indian markets
- **pandas** - Data manipulation and indicator calculations
- **numpy** - Mathematical operations (slope, ZigZag indicator)
- **uvicorn** - ASGI server
- **pydantic** - Data validation and models
- **pyotp** - TOTP authentication

### Frontend
- **React 18** - UI library with hooks
- **Vite** - Fast build tool and dev server
- **lightweight-charts** - TradingView charting library
- **axios** - HTTP client for API calls
- **CSS3** - Custom dark theme styling

### Strategy Engine Features
- **Custom Indicators**: SMA, EMA, RSI, MACD, Bollinger Bands, ATR, Stochastic, OBV, ADX, CCI
- **Preset Strategies**: MA44, MA crossovers, EMA momentum, ZigZag resistance detection
- **Mathematical Tools**: Linear regression slopes, percentage calculations, peak/trough detection

## Preset Strategies Explained

### 1. MA44 Strategy
Finds stocks consolidating around the 44-day moving average with positive momentum.
- **Conditions**: MA44 slope > 0, price within ±3% of MA44, close above MA44
- **Use Case**: Identify stocks in healthy uptrend with low volatility
- **Columns**: MA44 value, slope, % difference from MA44

### 2. MA44 Cross MA200 (Golden/Death Cross)
Detects major trend changes when 44-day MA crosses 200-day MA.
- **Conditions**: |MA44 - MA200| < 1% (approaching crossover)
- **Use Case**: Catch major trend reversals early
- **Columns**: MA44, MA200, % difference

### 3. EMA Crossover
Finds short-term momentum shifts as fast EMA approaches slow EMA.
- **Conditions**: EMA(10) approaching EMA(30), difference < 0.05%
- **Use Case**: Early entry signals for swing trades
- **Columns**: EMA10, EMA30, % difference

### 4. Down to MA200
Identifies stocks pulling back to long-term support.
- **Conditions**: Price near 200-day MA from above, MA200 slope > 0
- **Use Case**: Buy-the-dip opportunities in uptrends
- **Columns**: MA200, slope, % difference

### 5. Magnet Effect
Finds stocks approaching resistance levels using ZigZag indicator.
- **Conditions**: Price near resistance (within 2%), MA200 slope > 0
- **Use Case**: Potential breakout candidates
- **Columns**: MA44, resistance level, distance to resistance

### 6. Top Gainers
Ranks top 20 performers by % change over N days.
- **Parameters**: Days (default 7)
- **Use Case**: Momentum trading, sector rotation analysis
- **Columns**: % change, period

### 7. Top Losers
Ranks bottom 20 performers by % change over N days.
- **Parameters**: Days (default 7)
- **Use Case**: Oversold bounce plays, contrarian opportunities
- **Columns**: % change, period

## Custom Strategy Builder

### Available Indicators
1. **SMA (Simple Moving Average)** - Trend following, default period: 20
2. **EMA (Exponential Moving Average)** - Faster trend following, default: 20
3. **RSI (Relative Strength Index)** - Momentum oscillator (0-100), default: 14
4. **MACD (Moving Average Convergence Divergence)** - Trend and momentum
5. **Bollinger Bands** - Volatility and overbought/oversold, default: 20, 2 std dev
6. **ATR (Average True Range)** - Volatility measure, default: 14
7. **Stochastic Oscillator** - Momentum (0-100), default: 14, 3, 3
8. **OBV (On-Balance Volume)** - Volume-based momentum
9. **ADX (Average Directional Index)** - Trend strength, default: 14
10. **CCI (Commodity Channel Index)** - Cyclical trends, default: 20

### Operators
- **Greater than (>)** - Value1 > Value2
- **Less than (<)** - Value1 < Value2
- **Equal to (=)** - Value1 ≈ Value2 (±0.1% tolerance)
- **Crosses above** - Value1 crosses above Value2
- **Crosses below** - Value1 crosses below Value2
- **Between** - Value1 is between Value2 and Value3
- **Not between** - Value1 is outside Value2 to Value3 range

### Example Strategies
```
Name: "RSI Oversold Bounce"
Conditions: 
  - RSI(14) < 30 (oversold)
  - Close > SMA(50) (above long-term trend)

Name: "Bollinger Squeeze Breakout"
Conditions:
  - Close > Bollinger Upper Band
  - Volume > SMA(Volume, 20)

Name: "MACD Bullish Cross"
Conditions:
  - MACD crosses above Signal Line
  - ADX(14) > 25 (strong trend)
```

## Roadmap

### Current Features ✅
- [x] TradingView-style charting with volume
- [x] 7 preset quantitative strategies from production notebook
- [x] Custom strategy builder with 10 technical indicators
- [x] Multi-timeframe support (1m to 1M)
- [x] Real-time scanning across symbols
- [x] Three-tab navigation (Charts | Preset | Custom)

### Planned Features 🚀
- [ ] Real-time WebSocket data streaming for live charts
- [ ] Backtesting engine for custom strategies
- [ ] Strategy performance metrics (win rate, profit factor, Sharpe ratio)
- [ ] Export scan results to CSV/Excel
- [ ] Save strategy scan history
- [ ] Portfolio tracking and P&L analysis
- [ ] Watchlist functionality with alerts
- [ ] Multiple chart layouts (2x2, 3x3 grids)
- [ ] Mobile-responsive design
- [ ] Dark/Light theme toggle
- [ ] Order placement integration (paper trading first)
- [ ] News and events calendar integration

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - Feel free to use this project for personal or commercial purposes.

## Disclaimer

This software is for educational and research purposes only. It is not intended as financial advice. Trading in financial markets involves substantial risk of loss. Always do your own research and consult with a qualified financial advisor before making investment decisions.

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**Built with ❤️ for traders and developers**
