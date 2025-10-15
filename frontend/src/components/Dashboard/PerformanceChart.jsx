import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart
} from 'recharts';

const PerformanceChart = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-400">
        <p>No performance data available</p>
      </div>
    );
  }

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white px-4 py-3 rounded-lg shadow-lg border border-gray-200">
          <p className="text-sm font-semibold text-gray-900 mb-1">
            {payload[0].payload.month}
          </p>
          <p className="text-lg font-bold text-indigo-600">
            ${payload[0].value.toLocaleString()}
          </p>
          {payload[0].payload.change && (
            <p className={`text-xs mt-1 ${
              payload[0].payload.change > 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {payload[0].payload.change > 0 ? '+' : ''}
              {payload[0].payload.change}%
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  // Calculate min and max for better Y-axis scaling
  const values = data.map(item => item.value);
  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);
  const padding = (maxValue - minValue) * 0.1;

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
        >
          <defs>
            <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#6366F1" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#6366F1" stopOpacity={0}/>
            </linearGradient>
          </defs>
          
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke="#E5E7EB" 
            vertical={false}
          />
          
          <XAxis
            dataKey="month"
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
            domain={[minValue - padding, maxValue + padding]}
            tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
          />
          
          <Tooltip content={<CustomTooltip />} />
          
          <Area
            type="monotone"
            dataKey="value"
            stroke="#6366F1"
            strokeWidth={3}
            fill="url(#colorValue)"
            animationDuration={1000}
          />
        </AreaChart>
      </ResponsiveContainer>

      {/* Performance Summary */}
      <div className="mt-4 grid grid-cols-3 gap-4">
        <div className="text-center">
          <p className="text-xs text-gray-500 mb-1">Starting Value</p>
          <p className="text-sm font-semibold text-gray-900">
            ${data[0]?.value.toLocaleString()}
          </p>
        </div>
        <div className="text-center">
          <p className="text-xs text-gray-500 mb-1">Current Value</p>
          <p className="text-sm font-semibold text-gray-900">
            ${data[data.length - 1]?.value.toLocaleString()}
          </p>
        </div>
        <div className="text-center">
          <p className="text-xs text-gray-500 mb-1">Total Gain</p>
          <p className="text-sm font-semibold text-green-600">
            +${(data[data.length - 1]?.value - data[0]?.value).toLocaleString()}
          </p>
        </div>
      </div>
    </div>
  );
};

export default PerformanceChart;