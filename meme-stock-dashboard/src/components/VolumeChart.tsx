import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { VolumeChartProps } from '@/types';

const VolumeChart: React.FC<VolumeChartProps> = ({ data, ticker }) => {
  return (
    <div className="w-full h-64 bg-white rounded-lg p-4 shadow-sm">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">
        Volume Analysis - {ticker}
      </h3>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="time" 
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => new Date(value).toLocaleTimeString()}
          />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip 
            labelFormatter={(value) => new Date(value).toLocaleString()}
            formatter={(value, name) => [
              `${Number(value).toLocaleString()}`, 
              name === 'volume' ? 'Current Volume' : 'Average Volume'
            ]}
          />
          <Line 
            type="monotone" 
            dataKey="volume" 
            stroke="#ef4444" 
            strokeWidth={2}
            dot={{ fill: '#ef4444', strokeWidth: 2, r: 4 }}
          />
          <Line 
            type="monotone" 
            dataKey="average" 
            stroke="#6b7280" 
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={{ fill: '#6b7280', strokeWidth: 2, r: 3 }}
          />
        </LineChart>
      </ResponsiveContainer>
      <div className="flex justify-center mt-2 space-x-4 text-sm">
        <div className="flex items-center">
          <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
          <span>Current Volume</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-gray-500 rounded-full mr-2"></div>
          <span>Average Volume</span>
        </div>
      </div>
    </div>
  );
};

export default VolumeChart;
