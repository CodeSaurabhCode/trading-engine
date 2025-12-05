import React, { useState } from 'react';
import axios from 'axios';
import './PresetStrategies.css';

const API_BASE_URL = 'http://localhost:8000';

const PresetStrategies = () => {
  const [selectedStrategy, setSelectedStrategy] = useState('MA44');
  const [parameters, setParameters] = useState({ days: 7 });
  const [scanResults, setScanResults] = useState([]);
  const [scanning, setScanning] = useState(false);

  const strategies = [
    {
      id: 'MA44',
      name: 'MA44 Strategy',
      description: 'Price near 44-day MA with positive slope. Identifies stocks consolidating around MA44.',
      conditions: ['MA44 slope > 0', '-3% < (MA44 - Close) < 3%', 'Close > MA44']
    },
    {
      id: 'MA44_CROSS_MA200',
      name: 'MA44 Cross MA200',
      description: '44-day MA crossing 200-day MA. Golden/Death cross opportunities.',
      conditions: ['|MA44 - MA200| < 1%']
    },
    {
      id: 'EMA_CROSSOVER',
      name: 'EMA Crossover',
      description: 'EMA(10) approaching EMA(30). Short-term momentum shifts.',
      conditions: ['|EMA10 - EMA30| < 0.05%']
    },
    {
      id: 'DOWN_TO_MA200',
      name: 'Down to MA200',
      description: 'Price approaching 200-day MA from above. Potential support bounce.',
      conditions: ['-3% < (MA200 - Close) < 3%', 'MA200 slope < 1', 'Close > MA200']
    },
    {
      id: 'MAGNET_EFFECT',
      name: 'Magnet Effect',
      description: 'Price near resistance with positive MA200 slope. Breakout candidates.',
      conditions: ['MA200 slope > 0', 'Close > MA44', '|Resistance - Close| < 1%']
    },
    {
      id: 'TOP_GAINERS',
      name: 'Top Gainers',
      description: 'Stocks with highest N-day returns. Top 20 performers.',
      hasParams: true
    },
    {
      id: 'TOP_LOSERS',
      name: 'Top Losers',
      description: 'Stocks with lowest N-day returns. Top 20 underperformers.',
      hasParams: true
    }
  ];

  const scanStrategy = async () => {
    setScanning(true);
    setScanResults([]);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/preset-strategies/scan`, {
        preset_type: selectedStrategy,
        parameters: (selectedStrategy === 'TOP_GAINERS' || selectedStrategy === 'TOP_LOSERS') ? parameters : {}
      });
      setScanResults(response.data);
    } catch (error) {
      console.error('Error scanning preset strategy:', error);
      alert('Failed to scan stocks');
    } finally {
      setScanning(false);
    }
  };

  const selectedStrategyInfo = strategies.find(s => s.id === selectedStrategy);

  return (
    <div className="preset-strategies">
      <div className="preset-header">
        <h2>📈 Preset Strategies</h2>
        <p className="subtitle">Proven strategies from quantitative analysis notebook</p>
      </div>

      <div className="strategy-selection">
        <div className="strategy-cards">
          {strategies.map(strategy => (
            <div
              key={strategy.id}
              className={`strategy-card ${selectedStrategy === strategy.id ? 'selected' : ''}`}
              onClick={() => setSelectedStrategy(strategy.id)}
            >
              <div className="strategy-name">{strategy.name}</div>
              <div className="strategy-desc">{strategy.description}</div>
              {strategy.conditions && (
                <div className="strategy-conditions">
                  {strategy.conditions.map((cond, idx) => (
                    <span key={idx} className="condition-tag">{cond}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {selectedStrategyInfo?.hasParams && (
          <div className="strategy-params">
            <label>Number of Days:</label>
            <input
              type="number"
              min="1"
              max="90"
              value={parameters.days}
              onChange={(e) => setParameters({ days: parseInt(e.target.value) || 7 })}
            />
          </div>
        )}

        <button 
          className="btn-scan-large" 
          onClick={scanStrategy}
          disabled={scanning}
        >
          {scanning ? '🔍 Scanning All Stocks...' : '🚀 Run Strategy Scan'}
        </button>
      </div>

      {scanResults.length > 0 && (
        <div className="scan-results">
          <div className="results-header">
            <h3>
              {selectedStrategyInfo?.name} Results
              <span className="match-count">
                ({scanResults.filter(r => r.matched).length} matches out of {scanResults.length} stocks)
              </span>
            </h3>
          </div>

          <div className="results-table-container">
            <table className="results-table">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Current Price</th>
                  {selectedStrategy === 'MA44' && (
                    <>
                      <th>MA44</th>
                      <th>Slope</th>
                      <th>Diff %</th>
                    </>
                  )}
                  {selectedStrategy === 'MA44_CROSS_MA200' && (
                    <>
                      <th>MA44</th>
                      <th>MA200</th>
                      <th>Diff %</th>
                    </>
                  )}
                  {selectedStrategy === 'EMA_CROSSOVER' && (
                    <>
                      <th>EMA10</th>
                      <th>EMA30</th>
                      <th>Diff %</th>
                    </>
                  )}
                  {selectedStrategy === 'DOWN_TO_MA200' && (
                    <>
                      <th>MA200</th>
                      <th>Slope</th>
                      <th>Diff %</th>
                    </>
                  )}
                  {selectedStrategy === 'MAGNET_EFFECT' && (
                    <>
                      <th>MA44</th>
                      <th>Resistance</th>
                      <th>To Resistance</th>
                    </>
                  )}
                  {(selectedStrategy === 'TOP_GAINERS' || selectedStrategy === 'TOP_LOSERS') && (
                    <>
                      <th>Change %</th>
                      <th>Period</th>
                    </>
                  )}
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {scanResults.filter(r => r.matched).map(result => (
                  <tr key={result.symbol} className="matched-row">
                    <td className="symbol-cell">{result.display_name}</td>
                    <td className="price-cell">₹{result.current_price.toFixed(2)}</td>
                    
                    {selectedStrategy === 'MA44' && (
                      <>
                        <td>₹{result.indicator_values.ma44?.toFixed(2)}</td>
                        <td className={result.indicator_values.slope > 0 ? 'positive' : 'negative'}>
                          {result.indicator_values.slope?.toFixed(4)}
                        </td>
                        <td className={Math.abs(result.indicator_values.diff_pct) < 1 ? 'near' : ''}>
                          {result.indicator_values.diff_pct?.toFixed(2)}%
                        </td>
                      </>
                    )}
                    
                    {selectedStrategy === 'MA44_CROSS_MA200' && (
                      <>
                        <td>₹{result.indicator_values.ma44?.toFixed(2)}</td>
                        <td>₹{result.indicator_values.ma200?.toFixed(2)}</td>
                        <td className="near">{result.indicator_values.diff_pct?.toFixed(2)}%</td>
                      </>
                    )}
                    
                    {selectedStrategy === 'EMA_CROSSOVER' && (
                      <>
                        <td>₹{result.indicator_values.ema10?.toFixed(2)}</td>
                        <td>₹{result.indicator_values.ema30?.toFixed(2)}</td>
                        <td className="near">{result.indicator_values.diff_pct?.toFixed(4)}%</td>
                      </>
                    )}
                    
                    {selectedStrategy === 'DOWN_TO_MA200' && (
                      <>
                        <td>₹{result.indicator_values.ma200?.toFixed(2)}</td>
                        <td className={result.indicator_values.slope < 1 ? 'positive' : 'negative'}>
                          {result.indicator_values.slope?.toFixed(4)}
                        </td>
                        <td className={Math.abs(result.indicator_values.diff_pct) < 1 ? 'near' : ''}>
                          {result.indicator_values.diff_pct?.toFixed(2)}%
                        </td>
                      </>
                    )}
                    
                    {selectedStrategy === 'MAGNET_EFFECT' && (
                      <>
                        <td>₹{result.indicator_values.ma44?.toFixed(2)}</td>
                        <td>₹{result.indicator_values.resistance?.toFixed(2)}</td>
                        <td className="near">{result.indicator_values.res_diff_pct?.toFixed(2)}%</td>
                      </>
                    )}
                    
                    {(selectedStrategy === 'TOP_GAINERS' || selectedStrategy === 'TOP_LOSERS') && (
                      <>
                        <td className={result.indicator_values.change_pct > 0 ? 'positive' : 'negative'}>
                          {result.indicator_values.change_pct?.toFixed(2)}%
                        </td>
                        <td>{result.indicator_values.days} days</td>
                      </>
                    )}
                    
                    <td>
                      <span className="status-badge matched">✓ Match</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default PresetStrategies;
