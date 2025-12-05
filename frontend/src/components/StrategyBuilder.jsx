import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './StrategyBuilder.css';

const API_BASE_URL = 'http://localhost:8000';

const StrategyBuilder = () => {
  const [strategies, setStrategies] = useState([]);
  const [showBuilder, setShowBuilder] = useState(false);
  const [currentStrategy, setCurrentStrategy] = useState({
    name: '',
    description: '',
    timeframe: '5m',
    conditions: []
  });
  const [scanResults, setScanResults] = useState([]);
  const [scanning, setScanning] = useState(false);

  const indicators = [
    { value: 'SMA', label: 'Simple Moving Average' },
    { value: 'EMA', label: 'Exponential Moving Average' },
    { value: 'RSI', label: 'Relative Strength Index' },
    { value: 'MACD', label: 'MACD' },
    { value: 'BOLLINGER_BANDS', label: 'Bollinger Bands' },
    { value: 'VOLUME', label: 'Volume' },
    { value: 'PRICE', label: 'Price' },
    { value: 'ATR', label: 'Average True Range' },
    { value: 'STOCHASTIC', label: 'Stochastic' },
    { value: 'ADX', label: 'ADX' }
  ];

  const operators = [
    { value: '>', label: 'Greater Than (>)' },
    { value: '<', label: 'Less Than (<)' },
    { value: '>=', label: 'Greater or Equal (>=)' },
    { value: '<=', label: 'Less or Equal (<=)' },
    { value: '==', label: 'Equals (==)' },
    { value: 'CROSSES_ABOVE', label: 'Crosses Above' },
    { value: 'CROSSES_BELOW', label: 'Crosses Below' }
  ];

  const timeframes = [
    { value: '1', label: '1 Minute' },
    { value: '3', label: '3 Minutes' },
    { value: '5', label: '5 Minutes' },
    { value: '10', label: '10 Minutes' },
    { value: '15', label: '15 Minutes' },
    { value: '30', label: '30 Minutes' },
    { value: '60', label: '1 Hour' },
    { value: '120', label: '2 Hours' },
    { value: 'D', label: 'Daily' },
    { value: 'W', label: 'Weekly' }
  ];

  useEffect(() => {
    fetchStrategies();
  }, []);

  const fetchStrategies = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/strategies`);
      setStrategies(response.data);
    } catch (error) {
      console.error('Error fetching strategies:', error);
    }
  };

  const addCondition = () => {
    setCurrentStrategy({
      ...currentStrategy,
      conditions: [
        ...currentStrategy.conditions,
        {
          indicator1: 'SMA',
          indicator1_params: { period: 20 },
          operator: '>',
          indicator2: null,
          indicator2_params: null,
          value: 0
        }
      ]
    });
  };

  const updateCondition = (index, field, value) => {
    const newConditions = [...currentStrategy.conditions];
    newConditions[index] = { ...newConditions[index], [field]: value };
    setCurrentStrategy({ ...currentStrategy, conditions: newConditions });
  };

  const removeCondition = (index) => {
    const newConditions = currentStrategy.conditions.filter((_, i) => i !== index);
    setCurrentStrategy({ ...currentStrategy, conditions: newConditions });
  };

  const saveStrategy = async () => {
    try {
      await axios.post(`${API_BASE_URL}/api/strategies`, currentStrategy);
      alert('Strategy saved successfully!');
      setShowBuilder(false);
      setCurrentStrategy({ name: '', description: '', timeframe: '5m', conditions: [] });
      fetchStrategies();
    } catch (error) {
      console.error('Error saving strategy:', error);
      alert('Failed to save strategy');
    }
  };

  const deleteStrategy = async (strategyId) => {
    if (!window.confirm('Are you sure you want to delete this strategy?')) return;
    
    try {
      await axios.delete(`${API_BASE_URL}/api/strategies/${strategyId}`);
      alert('Strategy deleted successfully!');
      fetchStrategies();
    } catch (error) {
      console.error('Error deleting strategy:', error);
      alert('Failed to delete strategy');
    }
  };

  const scanStocks = async (strategyId) => {
    setScanning(true);
    setScanResults([]);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/strategies/scan`, {
        strategy_id: strategyId
      });
      setScanResults(response.data);
    } catch (error) {
      console.error('Error scanning stocks:', error);
      alert('Failed to scan stocks');
    } finally {
      setScanning(false);
    }
  };

  const getIndicatorParams = (indicator) => {
    switch (indicator) {
      case 'SMA':
      case 'EMA':
        return { period: 20 };
      case 'RSI':
        return { period: 14 };
      case 'MACD':
        return { fast: 12, slow: 26, signal: 9, line: 'macd' };
      case 'BOLLINGER_BANDS':
        return { period: 20, std_dev: 2, band: 'middle' };
      case 'ATR':
        return { period: 14 };
      case 'STOCHASTIC':
        return { k_period: 14, d_period: 3, line: 'k' };
      case 'ADX':
        return { period: 14 };
      case 'PRICE':
        return { type: 'close' };
      case 'VOLUME':
        return {};
      default:
        return {};
    }
  };

  return (
    <div className="strategy-builder">
      <div className="builder-header">
        <h2>Strategy Builder</h2>
        <button className="btn-primary" onClick={() => setShowBuilder(!showBuilder)}>
          {showBuilder ? 'View Strategies' : 'Create New Strategy'}
        </button>
      </div>

      {showBuilder ? (
        <div className="strategy-form">
          <div className="form-group">
            <label>Strategy Name</label>
            <input
              type="text"
              value={currentStrategy.name}
              onChange={(e) => setCurrentStrategy({ ...currentStrategy, name: e.target.value })}
              placeholder="e.g., SMA Crossover"
            />
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea
              value={currentStrategy.description}
              onChange={(e) => setCurrentStrategy({ ...currentStrategy, description: e.target.value })}
              placeholder="Describe your strategy..."
              rows={3}
            />
          </div>

          <div className="form-group">
            <label>Timeframe</label>
            <select
              value={currentStrategy.timeframe}
              onChange={(e) => setCurrentStrategy({ ...currentStrategy, timeframe: e.target.value })}
            >
              {timeframes.map(tf => (
                <option key={tf.value} value={tf.value}>{tf.label}</option>
              ))}
            </select>
          </div>

          <div className="conditions-section">
            <div className="conditions-header">
              <h3>Conditions (All must be true)</h3>
              <button className="btn-add" onClick={addCondition}>+ Add Condition</button>
            </div>

            {currentStrategy.conditions.map((condition, index) => (
              <div key={index} className="condition-row">
                <div className="condition-number">{index + 1}</div>
                
                <select
                  value={condition.indicator1}
                  onChange={(e) => {
                    updateCondition(index, 'indicator1', e.target.value);
                    updateCondition(index, 'indicator1_params', getIndicatorParams(e.target.value));
                  }}
                >
                  {indicators.map(ind => (
                    <option key={ind.value} value={ind.value}>{ind.label}</option>
                  ))}
                </select>

                {condition.indicator1 === 'SMA' || condition.indicator1 === 'EMA' ? (
                  <input
                    type="number"
                    className="param-input"
                    placeholder="Period"
                    value={condition.indicator1_params?.period || 20}
                    onChange={(e) => updateCondition(index, 'indicator1_params', { period: parseInt(e.target.value) })}
                  />
                ) : condition.indicator1 === 'RSI' ? (
                  <input
                    type="number"
                    className="param-input"
                    placeholder="Period"
                    value={condition.indicator1_params?.period || 14}
                    onChange={(e) => updateCondition(index, 'indicator1_params', { period: parseInt(e.target.value) })}
                  />
                ) : null}

                <select
                  value={condition.operator}
                  onChange={(e) => updateCondition(index, 'operator', e.target.value)}
                >
                  {operators.map(op => (
                    <option key={op.value} value={op.value}>{op.label}</option>
                  ))}
                </select>

                {condition.operator === 'CROSSES_ABOVE' || condition.operator === 'CROSSES_BELOW' ? (
                  <>
                    <select
                      value={condition.indicator2 || 'SMA'}
                      onChange={(e) => {
                        updateCondition(index, 'indicator2', e.target.value);
                        updateCondition(index, 'indicator2_params', getIndicatorParams(e.target.value));
                      }}
                    >
                      {indicators.map(ind => (
                        <option key={ind.value} value={ind.value}>{ind.label}</option>
                      ))}
                    </select>
                    {condition.indicator2 === 'SMA' || condition.indicator2 === 'EMA' ? (
                      <input
                        type="number"
                        className="param-input"
                        placeholder="Period"
                        value={condition.indicator2_params?.period || 50}
                        onChange={(e) => updateCondition(index, 'indicator2_params', { period: parseInt(e.target.value) })}
                      />
                    ) : null}
                  </>
                ) : (
                  <input
                    type="number"
                    className="param-input"
                    placeholder="Value"
                    value={condition.value || 0}
                    onChange={(e) => updateCondition(index, 'value', parseFloat(e.target.value))}
                  />
                )}

                <button className="btn-remove" onClick={() => removeCondition(index)}>×</button>
              </div>
            ))}
          </div>

          <div className="form-actions">
            <button className="btn-cancel" onClick={() => setShowBuilder(false)}>Cancel</button>
            <button 
              className="btn-save" 
              onClick={saveStrategy}
              disabled={!currentStrategy.name || currentStrategy.conditions.length === 0}
            >
              Save Strategy
            </button>
          </div>
        </div>
      ) : (
        <div className="strategies-list">
          {strategies.length === 0 ? (
            <div className="empty-state">
              <p>No strategies yet. Create your first strategy to get started!</p>
            </div>
          ) : (
            strategies.map(strategy => (
              <div key={strategy.id} className="strategy-card">
                <div className="strategy-info">
                  <h3>{strategy.name}</h3>
                  <p>{strategy.description || 'No description'}</p>
                  <div className="strategy-meta">
                    <span className="meta-item">⏱️ {timeframes.find(tf => tf.value === strategy.timeframe)?.label}</span>
                    <span className="meta-item">📋 {strategy.conditions.length} conditions</span>
                  </div>
                </div>
                <div className="strategy-actions">
                  <button 
                    className="btn-scan" 
                    onClick={() => scanStocks(strategy.id)}
                    disabled={scanning}
                  >
                    {scanning ? 'Scanning...' : '🔍 Scan Stocks'}
                  </button>
                  <button className="btn-delete" onClick={() => deleteStrategy(strategy.id)}>🗑️</button>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {scanResults.length > 0 && (
        <div className="scan-results">
          <h3>Scan Results ({scanResults.filter(r => r.matched).length} matches)</h3>
          <div className="results-grid">
            {scanResults.map(result => (
              <div key={result.symbol} className={`result-card ${result.matched ? 'matched' : 'not-matched'}`}>
                <div className="result-header">
                  <span className="symbol">{result.display_name}</span>
                  <span className={`status ${result.matched ? 'match' : 'no-match'}`}>
                    {result.matched ? '✓ Match' : '✗ No Match'}
                  </span>
                </div>
                <div className="result-price">₹{result.current_price.toFixed(2)}</div>
                <div className="result-conditions">
                  {result.conditions_met.map((met, idx) => (
                    <span key={idx} className={`condition-badge ${met ? 'met' : 'not-met'}`}>
                      Condition {idx + 1}: {met ? '✓' : '✗'}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default StrategyBuilder;
