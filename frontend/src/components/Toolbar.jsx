import React from 'react';
import './Toolbar.css';

const Toolbar = ({ timeframe, onTimeframeChange, chartType, onChartTypeChange }) => {
  const timeframes = [
    { label: '1m', value: '1' },
    { label: '3m', value: '3' },
    { label: '5m', value: '5' },
    { label: '10m', value: '10' },
    { label: '15m', value: '15' },
    { label: '30m', value: '30' },
    { label: '1h', value: '60' },
    { label: '2h', value: '120' },
    { label: '4h', value: '240' },
    { label: '1D', value: 'D' },
    { label: '1W', value: 'W' },
    { label: '1M', value: 'M' },
  ];

  const chartTypes = [
    { label: '📊 Candlestick', value: 'candlestick' },
    { label: '📈 Line', value: 'line' },
    { label: '📉 Area', value: 'area' },
  ];

  return (
    <div className="toolbar">
      <div className="toolbar-section">
        <label className="toolbar-label">Timeframe:</label>
        <div className="button-group">
          {timeframes.map((tf) => (
            <button
              key={tf.value}
              className={`toolbar-button ${timeframe === tf.value ? 'active' : ''}`}
              onClick={() => onTimeframeChange(tf.value)}
            >
              {tf.label}
            </button>
          ))}
        </div>
      </div>

      <div className="toolbar-section">
        <label className="toolbar-label">Chart Type:</label>
        <div className="button-group">
          {chartTypes.map((ct) => (
            <button
              key={ct.value}
              className={`toolbar-button ${chartType === ct.value ? 'active' : ''}`}
              onClick={() => onChartTypeChange(ct.value)}
            >
              {ct.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Toolbar;
