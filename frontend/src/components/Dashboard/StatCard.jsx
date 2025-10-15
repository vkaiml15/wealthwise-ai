import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

const StatCard = ({ 
  title, 
  value, 
  change, 
  isPositive, 
  icon: Icon, 
  iconColor = 'indigo',
  subtitle,
  isPercentage = false
}) => {
  // Color mapping for icons
  const colorClasses = {
    indigo: {
      bg: 'bg-indigo-100',
      text: 'text-indigo-600',
      lightBg: 'bg-indigo-50'
    },
    green: {
      bg: 'bg-green-100',
      text: 'text-green-600',
      lightBg: 'bg-green-50'
    },
    red: {
      bg: 'bg-red-100',
      text: 'text-red-600',
      lightBg: 'bg-red-50'
    },
    purple: {
      bg: 'bg-purple-100',
      text: 'text-purple-600',
      lightBg: 'bg-purple-50'
    },
    yellow: {
      bg: 'bg-yellow-100',
      text: 'text-yellow-600',
      lightBg: 'bg-yellow-50'
    },
    blue: {
      bg: 'bg-blue-100',
      text: 'text-blue-600',
      lightBg: 'bg-blue-50'
    }
  };

  const colors = colorClasses[iconColor] || colorClasses.indigo;

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <h3 className="text-2xl font-bold text-gray-900">{value}</h3>
        </div>
        <div className={`w-12 h-12 ${colors.bg} rounded-xl flex items-center justify-center flex-shrink-0`}>
          <Icon className={`w-6 h-6 ${colors.text}`} />
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between">
        {/* Change indicator */}
        {change !== undefined && !isPercentage && (
          <div className={`flex items-center space-x-1 ${
            isPositive ? 'text-green-600' : 'text-red-600'
          }`}>
            {isPositive ? (
              <TrendingUp className="w-4 h-4" />
            ) : (
              <TrendingDown className="w-4 h-4" />
            )}
            <span className="text-sm font-medium">
              {isPositive ? '+' : ''}{change}%
            </span>
          </div>
        )}

        {/* Subtitle or percentage info */}
        {subtitle && (
          <span className="text-sm text-gray-500 ml-auto">{subtitle}</span>
        )}

        {/* If it's a percentage display without trend */}
        {isPercentage && change !== undefined && (
          <span className="text-sm text-gray-500">{subtitle || `${change}%`}</span>
        )}
      </div>

      {/* Optional progress bar for percentage values */}
      {isPercentage && change !== undefined && (
        <div className="mt-3">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${colors.bg}`}
              style={{ width: `${Math.min(change, 100)}%` }}
            ></div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StatCard;