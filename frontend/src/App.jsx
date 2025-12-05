import React, { useState, useEffect } from 'react';
import TradingChart from './components/TradingChart';
import Toolbar from './components/Toolbar';
import SymbolSelector from './components/SymbolSelector';
import StrategyBuilder from './components/StrategyBuilder';
import PresetStrategies from './components/PresetStrategies';
import './App.css';
import axios from 'axios';

function App() {
  const [activeTab, setActiveTab] = useState('charts'); // 'charts', 'strategy', or 'preset'
  const [selectedSymbol, setSelectedSymbol] = useState({
    symbol: 'NIFTY',
    exchange: 'NSE',
    token: '26000'
  });
  const [timeframe, setTimeframe] = useState('5');
  const [chartType, setChartType] = useState('candlestick');
  const [historicalData, setHistoricalData] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchHistoricalData();
  }, [selectedSymbol, timeframe]);

  const fetchHistoricalData = async () => {
    setLoading(true);
    try {
      console.log('Fetching data for:', {
        symbol: selectedSymbol.token,
        exchange: selectedSymbol.exchange,
        interval: timeframe
      });
      
      const response = await axios.post('/api/historical-data', {
        symbol: selectedSymbol.token,
        exchange: selectedSymbol.exchange,
        interval: timeframe
      });
      
      console.log('API Response:', response.data);
      
      if (response.data && response.data.data) {
        const rawData = response.data.data;
        console.log('Setting historical data, length:', rawData.length);
        
        if (rawData.length > 0) {
          console.log('First candle:', rawData[0]);
          console.log('Last candle:', rawData[rawData.length - 1]);
          
          // Sort data by time (ascending) - lightweight-charts requires sorted data
          const sortedData = [...rawData].sort((a, b) => a.time - b.time);
          console.log('Data sorted, first:', sortedData[0], 'last:', sortedData[sortedData.length - 1]);
          
          setHistoricalData(sortedData);
        } else {
          console.warn('Empty data array, using sample data');
          setHistoricalData(generateSampleData());
        }
      } else {
        console.warn('No data in response, using sample data');
        setHistoricalData(generateSampleData());
      }
    } catch (error) {
      console.error('Error fetching historical data:', error);
      // For demo, generate sample data
      setHistoricalData(generateSampleData());
    } finally {
      setLoading(false);
    }
  };

  const generateSampleData = () => {
    const data = [];
    const basePrice = 19500;
    const now = Math.floor(Date.now() / 1000);
    
    for (let i = 100; i >= 0; i--) {
      const time = now - (i * 300); // 5 min intervals
      const open = basePrice + Math.random() * 100 - 50;
      const close = open + Math.random() * 40 - 20;
      const high = Math.max(open, close) + Math.random() * 20;
      const low = Math.min(open, close) - Math.random() * 20;
      
      data.push({
        time: time,
        open: parseFloat(open.toFixed(2)),
        high: parseFloat(high.toFixed(2)),
        low: parseFloat(low.toFixed(2)),
        close: parseFloat(close.toFixed(2)),
        volume: Math.floor(Math.random() * 1000000)
      });
    }
    
    return data;
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">Trading System</h1>
        <div className="header-tabs">
          <button 
            className={`tab-btn ${activeTab === 'charts' ? 'active' : ''}`}
            onClick={() => setActiveTab('charts')}
          >
            📊 Charts
          </button>
          <button 
            className={`tab-btn ${activeTab === 'preset' ? 'active' : ''}`}
            onClick={() => setActiveTab('preset')}
          >
            📈 Preset Strategies
          </button>
          <button 
            className={`tab-btn ${activeTab === 'strategy' ? 'active' : ''}`}
            onClick={() => setActiveTab('strategy')}
          >
            ⚡ Custom Builder
          </button>
        </div>
        {activeTab === 'charts' && (
          <SymbolSelector 
            selectedSymbol={selectedSymbol}
            onSymbolChange={setSelectedSymbol}
          />
        )}
      </header>
      
      {activeTab === 'charts' ? (
        <>
          <Toolbar 
            timeframe={timeframe}
            onTimeframeChange={setTimeframe}
            chartType={chartType}
            onChartTypeChange={setChartType}
          />
          
          <main className="app-main">
            {loading ? (
              <div className="loading">Loading chart data...</div>
            ) : (
              <TradingChart 
                data={historicalData}
                symbol={selectedSymbol.symbol}
                chartType={chartType}
              />
            )}
          </main>
        </>
      ) : activeTab === 'preset' ? (
        <main className="app-main">
          <PresetStrategies />
        </main>
      ) : (
        <main className="app-main">
          <StrategyBuilder />
        </main>
      )}
    </div>
  );
}

export default App;
