import React from 'react';
import { useAuth } from '../../context/AuthContext';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Wallet,
  Shield,
  Activity,
  ArrowUpRight,
  ArrowDownRight,
  MessageSquare,
  PieChart,
  BarChart3
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import StatCard from './StatCard';
import PortfolioChart from './PortfolioChart';
import PerformanceChart from './PerformanceChart';
 
const Dashboard = () => {
  const { currentUser, portfolio } = useAuth();
  const navigate = useNavigate();
 
  if (!portfolio) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <PieChart className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No Portfolio Found</h3>
          <p className="text-gray-600 mb-4">Please complete your profile setup first.</p>
          <button
            onClick={() => navigate('/onboarding')}
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Complete Setup
          </button>
        </div>
      </div>
    );
  }
 
  // Safely extract portfolio data with default values
  const totalValue = portfolio.totalValue ?? 0;
  const cashReserve = portfolio.cashReserve ?? 0;
  const invested = portfolio.invested ?? 0;
  const returns = portfolio.returns ?? { value: 0, percentage: 0 };
  const riskScore = portfolio.riskScore ?? 5;
  const allocation = portfolio.allocation ?? [];
  const performance = portfolio.performance ?? [];
  const holdings = portfolio.holdings ?? [];
 
  // Calculate percentage changes (mock data - in real app would compare to previous period)
  const valueChange = 2.3; // percentage
  const isPositive = returns.value > 0;
 
  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-6 text-white shadow-lg">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold mb-2">
              Welcome back, {currentUser?.name || 'Investor'}! 👋
            </h1>
            <p className="text-indigo-100">
              Here's your portfolio overview for today
            </p>
          </div>
          <button
            onClick={() => navigate('/chat')}
            className="hidden md:flex items-center space-x-2 px-6 py-3 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-xl transition-all backdrop-blur-sm"
          >
            <MessageSquare className="w-5 h-5" />
            <span>Ask AI Advisor</span>
          </button>
        </div>
      </div>
 
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Value"
          value={`$${totalValue.toLocaleString()}`}
          change={valueChange}
          isPositive={valueChange > 0}
          icon={DollarSign}
          iconColor="indigo"
        />
        <StatCard
          title="Total Returns"
          value={`$${returns.value.toLocaleString()}`}
          change={returns.percentage}
          isPositive={isPositive}
          icon={isPositive ? TrendingUp : TrendingDown}
          iconColor={isPositive ? "green" : "red"}
          subtitle={`${returns.percentage}%`}
        />
        <StatCard
          title="Cash Reserve"
          value={`$${cashReserve.toLocaleString()}`}
          change={totalValue > 0 ? ((cashReserve / totalValue) * 100).toFixed(1) : 0}
          isPercentage={true}
          icon={Wallet}
          iconColor="purple"
          subtitle={totalValue > 0 ? `${((cashReserve / totalValue) * 100).toFixed(1)}% of portfolio` : '0% of portfolio'}
        />
        <StatCard
          title="Risk Score"
          value={`${riskScore}/10`}
          icon={Shield}
          iconColor="yellow"
          subtitle={
            riskScore < 4 ? "Conservative" :
            riskScore < 7 ? "Moderate" :
            "Aggressive"
          }
        />
      </div>
 
      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Portfolio Allocation - Takes 1/3 width */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Portfolio Allocation</h2>
              <p className="text-sm text-gray-500 mt-1">Asset distribution</p>
            </div>
            <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
              <PieChart className="w-5 h-5 text-indigo-600" />
            </div>
          </div>
          <PortfolioChart data={allocation} />
        </div>
 
        {/* Performance Chart - Takes 2/3 width */}
        <div className="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Performance</h2>
              <p className="text-sm text-gray-500 mt-1">Last 6 months</p>
            </div>
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Activity className="w-5 h-5 text-purple-600" />
            </div>
          </div>
          <PerformanceChart data={performance} />
        </div>
      </div>
 
      {/* Holdings Table */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Top Holdings</h2>
            <p className="text-sm text-gray-500 mt-1">Your largest positions</p>
          </div>
          <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
            <BarChart3 className="w-5 h-5 text-green-600" />
          </div>
        </div>
 
        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Symbol</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Name</th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">Shares</th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">Avg Price</th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">Current</th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">Value</th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">Return</th>
              </tr>
            </thead>
            <tbody>
              {holdings.slice(0, 5).map((holding, index) => {
                const returnPercent = ((holding.currentPrice - holding.avgPrice) / holding.avgPrice * 100);
                const isPositiveReturn = returnPercent > 0;
               
                return (
                  <tr key={index} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                    <td className="py-4 px-4">
                      <span className="font-semibold text-gray-900">{holding.symbol}</span>
                    </td>
                    <td className="py-4 px-4">
                      <span className="text-sm text-gray-600">{holding.name}</span>
                    </td>
                    <td className="py-4 px-4 text-right text-sm text-gray-900">
                      {holding.shares}
                    </td>
                    <td className="py-4 px-4 text-right text-sm text-gray-600">
                      ${holding.avgPrice.toFixed(2)}
                    </td>
                    <td className="py-4 px-4 text-right text-sm text-gray-900">
                      ${holding.currentPrice.toFixed(2)}
                    </td>
                    <td className="py-4 px-4 text-right font-medium text-gray-900">
                      ${holding.value.toLocaleString()}
                    </td>
                    <td className="py-4 px-4 text-right">
                      <div className={`flex items-center justify-end space-x-1 ${
                        isPositiveReturn ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {isPositiveReturn ? (
                          <ArrowUpRight className="w-4 h-4" />
                        ) : (
                          <ArrowDownRight className="w-4 h-4" />
                        )}
                        <span className="text-sm font-medium">
                          {returnPercent.toFixed(2)}%
                        </span>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
 
        {/* View All Button */}
        {holdings.length > 5 && (
          <div className="mt-4 text-center">
            <button className="text-sm text-indigo-600 hover:text-indigo-700 font-medium">
              View all {holdings.length} holdings →
            </button>
          </div>
        )}
      </div>
 
      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button
          onClick={() => navigate('/chat')}
          className="p-6 bg-white rounded-xl shadow-sm border border-gray-200 hover:border-indigo-300 hover:shadow-md transition-all group"
        >
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center group-hover:bg-indigo-200 transition-colors">
              <MessageSquare className="w-6 h-6 text-indigo-600" />
            </div>
            <div className="flex-1 text-left">
              <h3 className="font-semibold text-gray-900">Ask AI Advisor</h3>
              <p className="text-sm text-gray-500">Get personalized insights</p>
            </div>
          </div>
        </button>
 
        <button className="p-6 bg-white rounded-xl shadow-sm border border-gray-200 hover:border-purple-300 hover:shadow-md transition-all group">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center group-hover:bg-purple-200 transition-colors">
              <BarChart3 className="w-6 h-6 text-purple-600" />
            </div>
            <div className="flex-1 text-left">
              <h3 className="font-semibold text-gray-900">Analyze Portfolio</h3>
              <p className="text-sm text-gray-500">Deep dive into metrics</p>
            </div>
          </div>
        </button>
 
        <button className="p-6 bg-white rounded-xl shadow-sm border border-gray-200 hover:border-green-300 hover:shadow-md transition-all group">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center group-hover:bg-green-200 transition-colors">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
            <div className="flex-1 text-left">
              <h3 className="font-semibold text-gray-900">Get Recommendations</h3>
              <p className="text-sm text-gray-500">Discover opportunities</p>
            </div>
          </div>
        </button>
      </div>
    </div>
  );
};
 
export default Dashboard;
