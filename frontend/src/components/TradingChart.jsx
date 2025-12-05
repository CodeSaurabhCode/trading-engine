import React, { useEffect, useRef, useState } from 'react';
import { createChart, CrosshairMode } from 'lightweight-charts';
import './TradingChart.css';

const TradingChart = ({ data, symbol, chartType }) => {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const mainSeriesRef = useRef(null);
  const volumeSeriesRef = useRef(null);
  const [priceInfo, setPriceInfo] = useState(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Create chart with advanced options
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: '#131722' },
        textColor: '#d1d4dc',
      },
      grid: {
        vertLines: { color: '#1e222d' },
        horzLines: { color: '#1e222d' },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: {
          width: 1,
          color: '#758696',
          style: 3, // Dashed
          labelBackgroundColor: '#2962FF',
        },
        horzLine: {
          width: 1,
          color: '#758696',
          style: 3,
          labelBackgroundColor: '#2962FF',
        },
      },
      rightPriceScale: {
        borderColor: '#2a2e39',
        scaleMargins: {
          top: 0.1,
          bottom: 0.25, // Leave space for volume
        },
      },
      timeScale: {
        borderColor: '#2a2e39',
        timeVisible: true,
        secondsVisible: false,
        rightOffset: 12,
        barSpacing: 6,
        minBarSpacing: 0.5,
        fixLeftEdge: false,
        fixRightEdge: false,
      },
      watermark: {
        visible: true,
        fontSize: 64,
        horzAlign: 'center',
        vertAlign: 'center',
        color: 'rgba(255, 255, 255, 0.03)',
        text: symbol,
      },
      handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
        horzTouchDrag: true,
        vertTouchDrag: true,
      },
      handleScale: {
        axisPressedMouseMove: true,
        mouseWheel: true,
        pinch: true,
      },
    });

    chartRef.current = chart;

    // Add main series (candlestick/line/area)
    let mainSeries;
    if (chartType === 'candlestick') {
      mainSeries = chart.addCandlestickSeries({
        upColor: '#26a69a',
        downColor: '#ef5350',
        borderVisible: false,
        wickUpColor: '#26a69a',
        wickDownColor: '#ef5350',
        priceFormat: {
          type: 'price',
          precision: 2,
          minMove: 0.01,
        },
      });
    } else if (chartType === 'line') {
      mainSeries = chart.addLineSeries({
        color: '#2962FF',
        lineWidth: 2,
        priceFormat: {
          type: 'price',
          precision: 2,
          minMove: 0.01,
        },
      });
    } else {
      mainSeries = chart.addAreaSeries({
        topColor: 'rgba(41, 98, 255, 0.4)',
        bottomColor: 'rgba(41, 98, 255, 0.0)',
        lineColor: 'rgba(41, 98, 255, 1)',
        lineWidth: 2,
        priceFormat: {
          type: 'price',
          precision: 2,
          minMove: 0.01,
        },
      });
    }

    mainSeriesRef.current = mainSeries;

    // Add volume histogram with its own price scale
    const volumeSeries = chart.addHistogramSeries({
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: '', // Empty string means it will use a separate overlay scale
    });

    // Configure the volume price scale
    chart.priceScale('').applyOptions({
      scaleMargins: {
        top: 0.8, // Volume takes bottom 20% of chart
        bottom: 0,
      },
    });

    volumeSeriesRef.current = volumeSeries;

    // Subscribe to crosshair move for price info display
    chart.subscribeCrosshairMove((param) => {
      if (!param.time || !param.seriesData.get(mainSeries)) {
        setPriceInfo(null);
        return;
      }

      const data = param.seriesData.get(mainSeries);
      const volumeData = param.seriesData.get(volumeSeries);
      
      if (chartType === 'candlestick' && data) {
        setPriceInfo({
          time: param.time,
          open: data.open,
          high: data.high,
          low: data.low,
          close: data.close,
          volume: volumeData?.value || 0,
        });
      } else if (data && data.value !== undefined) {
        setPriceInfo({
          time: param.time,
          price: data.value,
          volume: volumeData?.value || 0,
        });
      }
    });

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({
          width: chartContainerRef.current.clientWidth,
          height: chartContainerRef.current.clientHeight,
        });
      }
    };

    window.addEventListener('resize', handleResize);
    handleResize();

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [chartType, symbol]);

  useEffect(() => {
    if (!mainSeriesRef.current || !volumeSeriesRef.current || !data || data.length === 0) {
      console.log('Chart update skipped:', {
        hasMainSeries: !!mainSeriesRef.current,
        hasVolumeSeries: !!volumeSeriesRef.current,
        hasData: !!data,
        dataLength: data?.length
      });
      return;
    }

    try {
      console.log('Updating chart with data:', {
        chartType,
        dataLength: data.length,
        firstItem: data[0],
        lastItem: data[data.length - 1]
      });
      
      // Set main series data
      if (chartType === 'candlestick') {
        mainSeriesRef.current.setData(data);
      } else {
        // For line/area charts, use close prices
        const lineData = data.map(d => ({
          time: d.time,
          value: d.close
        }));
        mainSeriesRef.current.setData(lineData);
      }

      // Set volume data
      const volumeData = data.map(d => ({
        time: d.time,
        value: d.volume,
        color: d.close >= d.open ? 'rgba(38, 166, 154, 0.5)' : 'rgba(239, 83, 80, 0.5)'
      }));
      volumeSeriesRef.current.setData(volumeData);

      // Fit content with padding
      chartRef.current.timeScale().fitContent();
      
      console.log('Chart updated successfully');
    } catch (error) {
      console.error('Error setting chart data:', error);
    }
  }, [data, chartType]);

  return (
    <div className="trading-chart-container">
      {priceInfo && (
        <div className="price-info">
          {chartType === 'candlestick' ? (
            <>
              <span className="info-label">O:</span>
              <span className="info-value">{priceInfo.open?.toFixed(2)}</span>
              <span className="info-label">H:</span>
              <span className="info-value high">{priceInfo.high?.toFixed(2)}</span>
              <span className="info-label">L:</span>
              <span className="info-value low">{priceInfo.low?.toFixed(2)}</span>
              <span className="info-label">C:</span>
              <span className={`info-value ${priceInfo.close >= priceInfo.open ? 'up' : 'down'}`}>
                {priceInfo.close?.toFixed(2)}
              </span>
              <span className="info-label">Vol:</span>
              <span className="info-value">{priceInfo.volume?.toLocaleString()}</span>
            </>
          ) : (
            <>
              <span className="info-label">Price:</span>
              <span className="info-value">{priceInfo.price?.toFixed(2)}</span>
              <span className="info-label">Vol:</span>
              <span className="info-value">{priceInfo.volume?.toLocaleString()}</span>
            </>
          )}
        </div>
      )}
      <div ref={chartContainerRef} className="chart" />
      <div className="chart-controls">
        <button className="control-btn" onClick={() => chartRef.current?.timeScale().fitContent()} title="Fit Content">
          📊
        </button>
        <button className="control-btn" onClick={() => chartRef.current?.timeScale().scrollToRealTime()} title="Scroll to Latest">
          ⏩
        </button>
        <button className="control-btn" onClick={() => chartRef.current?.timeScale().resetTimeScale()} title="Reset Zoom">
          🔍
        </button>
      </div>
    </div>
  );
};

export default TradingChart;
