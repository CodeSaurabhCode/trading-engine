import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './SymbolSelector.css';

const SymbolSelector = ({ selectedSymbol, onSymbolChange }) => {
  const [symbols, setSymbols] = useState([]);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    fetchSymbols();
  }, []);

  const fetchSymbols = async () => {
    try {
      const response = await axios.get('/api/symbols');
      if (response.data && response.data.symbols) {
        setSymbols(response.data.symbols);
      }
    } catch (error) {
      console.error('Error fetching symbols:', error);
      // Fallback to default symbols
      setSymbols([
        { symbol: 'NIFTY', exchange: 'NSE', token: '26000' },
        { symbol: 'BANKNIFTY', exchange: 'NSE', token: '26009' },
        { symbol: 'RELIANCE-EQ', exchange: 'NSE', token: '2885' },
        { symbol: 'TCS-EQ', exchange: 'NSE', token: '11536' },
        { symbol: 'INFY-EQ', exchange: 'NSE', token: '1594' },
      ]);
    }
  };

  const handleSymbolSelect = (symbol) => {
    onSymbolChange(symbol);
    setIsOpen(false);
  };

  return (
    <div className="symbol-selector">
      <button 
        className="symbol-selector-button"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="symbol-name">{selectedSymbol.symbol}</span>
        <span className="symbol-exchange">{selectedSymbol.exchange}</span>
        <span className="dropdown-arrow">▼</span>
      </button>

      {isOpen && (
        <div className="symbol-dropdown">
          <div className="symbol-dropdown-header">
            <input 
              type="text" 
              placeholder="Search symbols..." 
              className="symbol-search"
              autoFocus
            />
          </div>
          <div className="symbol-list">
            {symbols.map((symbol) => (
              <div
                key={`${symbol.exchange}-${symbol.token}`}
                className={`symbol-item ${
                  selectedSymbol.token === symbol.token ? 'selected' : ''
                }`}
                onClick={() => handleSymbolSelect(symbol)}
              >
                <span className="symbol-item-name">{symbol.symbol}</span>
                <span className="symbol-item-exchange">{symbol.exchange}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {isOpen && (
        <div 
          className="symbol-selector-overlay" 
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

export default SymbolSelector;
