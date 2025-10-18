import React, { useState } from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';

const PerformanceChart = ({ data }) => {
  const [activeTab, setActiveTab] = useState('gainers'); // 'gainers' or 'losers'

  if (!data || !data.topGainers) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-400">
        <p>No performance data available</p>
      </div>
    );
  }

  const { topGainers, topLosers, summary } = data;
  
  // Determine which data to show
  const displayData = activeTab === 'gainers' ? topGainers : topLosers;
  
  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="bg-white px-4 py-3 rounded-lg shadow-lg border border-gray-200">
          <p className="text-sm font-semibold text-gray-900 mb-1">
            {item.symbol}
          </p>
          <p className={`text-lg font-bold ${
            item.returnPercent > 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            {item.returnPercent > 0 ? '+' : ''}{item.returnPercent.toFixed(2)}%
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {item.returnPercent > 0 ? '+' : ''}₹{item.returnValue.toFixed(0)}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-4">
      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-500 mb-1">Total Invested</p>
          <p className="text-sm font-bold text-gray-900">
            ₹{summary.totalInvested.toLocaleString()}
          </p>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-500 mb-1">Current Value</p>
          <p className="text-sm font-bold text-gray-900">
            ₹{summary.currentValue.toLocaleString()}
          </p>
        </div>
        <div className={`text-center p-3 rounded-lg ${
          summary.totalReturn >= 0 ? 'bg-green-50' : 'bg-red-50'
        }`}>
          <p className="text-xs text-gray-500 mb-1">Total Return</p>
          <p className={`text-sm font-bold ${
            summary.totalReturn >= 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            {summary.totalReturn >= 0 ? '+' : ''}₹{summary.totalReturn.toLocaleString()}
          </p>
        </div>
      </div>

      {/* Toggle Buttons */}
      <div className="flex space-x-2 bg-gray-100 p-1 rounded-lg">
        <button
          onClick={() => setActiveTab('gainers')}
          className={`flex-1 flex items-center justify-center space-x-2 py-2 px-4 rounded-md transition-all ${
            activeTab === 'gainers'
              ? 'bg-white text-green-600 shadow-sm font-semibold'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <TrendingUp className="w-4 h-4" />
          <span className="text-sm">Top Gainers</span>
        </button>
        <button
          onClick={() => setActiveTab('losers')}
          className={`flex-1 flex items-center justify-center space-x-2 py-2 px-4 rounded-md transition-all ${
            activeTab === 'losers'
              ? 'bg-white text-red-600 shadow-sm font-semibold'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <TrendingDown className="w-4 h-4" />
          <span className="text-sm">Top Losers</span>
        </button>
      </div>

      {/* Bar Chart */}
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={displayData}
            margin={{ top: 10, right: 10, left: 0, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" vertical={false} />
            <XAxis
              dataKey="symbol"
              stroke="#9CA3AF"
              style={{ fontSize: '12px' }}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              stroke="#9CA3AF"
              style={{ fontSize: '12px' }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(value) => `${value.toFixed(0)}%`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar
              dataKey="returnPercent"
              radius={[8, 8, 0, 0]}
              animationDuration={800}
            >
              {displayData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.returnPercent > 0 ? '#10B981' : '#EF4444'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Footer Info */}
      <div className="text-center text-xs text-gray-500">
        Showing top {displayData.length} {activeTab === 'gainers' ? 'performing' : 'underperforming'} holdings
      </div>
    </div>
  );
};

export default PerformanceChart;