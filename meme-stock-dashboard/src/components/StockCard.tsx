import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, MessageSquare, BarChart3, Clock, Lightbulb, Activity, Gauge, Smile } from 'lucide-react';
import { StockCardProps } from '@/types';
import AlertBadge from './AlertBadge';
import VolumeChart from './VolumeChart';

const StockCard: React.FC<StockCardProps> = ({ alert }) => {
  const [showChart, setShowChart] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const formatPrice = (price: number) => {
    return `$${price.toFixed(2)}`;
  };

  const formatChange = (change: number) => {
    const sign = change >= 0 ? '+' : '';
    return `${sign}${change.toFixed(2)}%`;
  };

  const formatTime = (timestamp: string) => {
    if (!mounted) return 'Loading...';
    return new Date(timestamp).toLocaleString();
  };

  const getRSIColor = (rsi: number | undefined) => {
    if (!rsi) return 'text-gray-600';
    if (rsi >= 70) return 'text-red-600';  // Overbought
    if (rsi <= 30) return 'text-green-600';  // Oversold
    return 'text-blue-600';  // Neutral
  };

  const getSentimentColor = (score: number | undefined) => {
    if (!score) return 'text-gray-600';
    if (score >= 0.5) return 'text-green-600';  // Bullish
    if (score <= -0.5) return 'text-red-600';  // Bearish
    return 'text-yellow-600';  // Neutral
  };

  // Generate mock volume data for the chart
  const generateVolumeData = () => {
    const data = [];
    const now = new Date();
    const average = 1000000; // Mock average volume
    
    for (let i = 23; i >= 0; i--) {
      const time = new Date(now.getTime() - i * 60 * 60 * 1000);
      const volume = average * (0.5 + Math.random() * 2);
      data.push({
        time: time.toISOString(),
        volume: Math.round(volume),
        average: average
      });
    }
    return data;
  };

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 p-6">
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center space-x-3">
          <h2 className="text-2xl font-bold text-gray-900">${alert.ticker}</h2>
          <AlertBadge priority={alert.priority} />
        </div>
        <div className="text-right">
          <div className="text-lg font-semibold text-gray-900">
            {formatPrice(alert.currentPrice)}
          </div>
          <div className={`flex items-center text-sm ${
            alert.priceChange >= 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            {alert.priceChange >= 0 ? (
              <TrendingUp className="w-4 h-4 mr-1" />
            ) : (
              <TrendingDown className="w-4 h-4 mr-1" />
            )}
            {formatChange(alert.priceChange)}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="flex items-center text-gray-600 mb-1">
            <MessageSquare className="w-4 h-4 mr-2" />
            <span className="text-sm font-medium">Mentions</span>
          </div>
          <div className="text-xl font-bold text-gray-900">{alert.mentionCount}</div>
        </div>
        
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="flex items-center text-gray-600 mb-1">
            <BarChart3 className="w-4 h-4 mr-2" />
            <span className="text-sm font-medium">Volume Ratio</span>
          </div>
          <div className="text-xl font-bold text-gray-900">{alert.volumeRatio.toFixed(2)}x</div>
        </div>
        
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="flex items-center text-gray-600 mb-1">
            <Gauge className="w-4 h-4 mr-2" />
            <span className="text-sm font-medium">RSI</span>
          </div>
          <div className={`text-xl font-bold ${getRSIColor(alert.rsi)}`}>
            {alert.rsi !== undefined && alert.rsi !== null ? alert.rsi.toFixed(1) : 'N/A'}
          </div>
        </div>
        
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="flex items-center text-gray-600 mb-1">
            <Activity className="w-4 h-4 mr-2" />
            <span className="text-sm font-medium">Vol Z-Score</span>
          </div>
          <div className="text-xl font-bold text-gray-900">
            {alert.volumeZScore !== undefined && alert.volumeZScore !== null ? alert.volumeZScore.toFixed(2) : 'N/A'}
          </div>
        </div>
        
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="flex items-center text-gray-600 mb-1">
            <Smile className="w-4 h-4 mr-2" />
            <span className="text-sm font-medium">Sentiment</span>
          </div>
          <div className={`text-xl font-bold ${getSentimentColor(alert.sentimentScore)}`}>
            {alert.sentimentScore !== undefined && alert.sentimentScore !== null ? alert.sentimentScore.toFixed(2) : 'N/A'}
          </div>
        </div>
        
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="flex items-center text-gray-600 mb-1">
            <Clock className="w-4 h-4 mr-2" />
            <span className="text-sm font-medium">Detected</span>
          </div>
          <div className="text-sm font-medium text-gray-900">
            {formatTime(alert.detectedAt)}
          </div>
        </div>
        
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="text-sm font-medium text-gray-600 mb-1">Status</div>
          <div className={`text-sm font-bold ${
            alert.priority === 'high' ? 'text-red-600' : 
            alert.priority === 'medium' ? 'text-yellow-600' : 'text-green-600'
          }`}>
            {alert.priority === 'high' ? 'High Alert' : 
             alert.priority === 'medium' ? 'Medium Alert' : 'Low Alert'}
          </div>
        </div>
      </div>

      {alert.advice && (
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4 mb-4 border border-purple-200">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <Lightbulb className="w-5 h-5 text-purple-600 mt-0.5" />
            </div>
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-purple-900 mb-1">AI Investment Advice</h3>
              <p className="text-sm text-gray-700 leading-relaxed">{alert.advice}</p>
            </div>
          </div>
        </div>
      )}

      <button
        onClick={() => setShowChart(!showChart)}
        className="w-full bg-blue-50 hover:bg-blue-100 text-blue-700 font-medium py-2 px-4 rounded-lg transition-colors duration-200"
      >
        {showChart ? 'Hide' : 'Show'} Volume Chart
      </button>

      {showChart && (
        <div className="mt-4">
          <VolumeChart data={generateVolumeData()} ticker={alert.ticker} />
        </div>
      )}
    </div>
  );
};

export default StockCard;
