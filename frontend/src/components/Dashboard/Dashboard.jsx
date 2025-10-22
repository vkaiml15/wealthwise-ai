import React, { useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { 
  TrendingUp, 
  TrendingDown, 
  IndianRupeeIcon, 
  Wallet, 
  Shield, 
  Activity,
  ArrowUpRight,
  ArrowDownRight,
  MessageSquare,
  PieChart,
  BarChart3,
  RefreshCw
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import StatCard from './StatCard';
import PortfolioChart from './PortfolioChart';
import PerformanceChart from './PerformanceChart';

// Helper function to format Indian currency
const formatIndianCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(amount);
};

const Dashboard = () => {
  const { currentUser, portfolio, refreshPortfolio, refreshUserData } = useAuth();
  const navigate = useNavigate();
  const [isRefreshing, setIsRefreshing] = React.useState(false);

  // Auto-refresh portfolio and user data on mount
  useEffect(() => {
    if (currentUser?.hasPortfolio && currentUser?.email) {
      handleRefresh();
    }
  }, [currentUser?.email]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    // Refresh both user data (for risk score) and portfolio data
    await Promise.all([
      refreshUserData(),
      refreshPortfolio()
    ]);
    setIsRefreshing(false);
  };

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

  // Safely extract portfolio data with defaults
  const totalValue = portfolio.totalValue ?? 0;
  const cashReserve = portfolio.cashReserve ?? 0;
  const invested = portfolio.invested ?? 0;
  const returns = portfolio.returns ?? { value: 0, percentage: 0 };
  const riskScore = currentUser?.riskAnalysis?.riskScore ?? 5;
  const allocation = portfolio.allocation ?? [];
  const performance = portfolio.performance ?? [];
  const holdings = portfolio.holdings ?? [];


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
          <div className="flex items-center space-x-3">
            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="hidden md:flex items-center space-x-2 px-4 py-2 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-xl transition-all backdrop-blur-sm disabled:opacity-50"
            >
              <RefreshCw className={`w-5 h-5 ${isRefreshing ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
            <button
              onClick={() => navigate('/chat')}
              className="hidden md:flex items-center space-x-2 px-6 py-3 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-xl transition-all backdrop-blur-sm"
            >
              <MessageSquare className="w-5 h-5" />
              <span>Ask AI Advisor</span>
            </button>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Value"
          value={formatIndianCurrency(totalValue)}
          icon={IndianRupeeIcon}
          iconColor="indigo"
        />
        <StatCard
          title="Total Returns"
          value={formatIndianCurrency(returns.value)}
          change={returns.percentage}
          isPositive={isPositive}
          icon={isPositive ? TrendingUp : TrendingDown}
          iconColor={isPositive ? "green" : "red"}
          // subtitle={`${returns.percentage}%`}
        />
        <StatCard
          title="Cash Reserve"
          value={formatIndianCurrency(cashReserve)}
          
          isPercentage={true}
          icon={Wallet}
          iconColor="purple"
          subtitle={totalValue > 0 ? `${((cashReserve / totalValue) * 100).toFixed(1)}% of portfolio` : '0% of portfolio'}
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Portfolio Allocation */}
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

        {/* Performance Chart */}
        <div className="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Performance</h2>
              <p className="text-sm text-gray-500 mt-1">Portfolio value over time</p>
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

        {holdings.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Symbol</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Type</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">Shares</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">Avg Price</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">Current</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">Value</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">Return</th>
                </tr>
              </thead>
              <tbody>
                {holdings.slice(0, 10).map((holding, index) => {
                  const returnPercent = holding.avgPrice > 0 
                    ? ((holding.currentPrice - holding.avgPrice) / holding.avgPrice * 100)
                    : 0;
                  const isPositiveReturn = returnPercent > 0;
                  
                  return (
                    <tr key={index} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                      <td className="py-4 px-4">
                        <span className="font-semibold text-gray-900">{holding.symbol}</span>
                      </td>
                      <td className="py-4 px-4">
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          holding.type === 'bond' ? 'bg-green-100 text-green-700' :
                          holding.type === 'stock' ? 'bg-blue-100 text-blue-700' :
                          holding.type === 'etf' ? 'bg-purple-100 text-purple-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {holding.type || 'stock'}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-right text-sm text-gray-900">
                        {holding.shares?.toFixed(2) || 0}
                      </td>
                      <td className="py-4 px-4 text-right text-sm text-gray-600">
                        ₹{holding.avgPrice?.toFixed(2) || 0}
                      </td>
                      <td className="py-4 px-4 text-right text-sm text-gray-900">
                        ₹{holding.currentPrice?.toFixed(2) || 0}
                      </td>
                      <td className="py-4 px-4 text-right font-medium text-gray-900">
                        ₹{holding.value?.toLocaleString('en-IN') || 0}
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
        ) : (
          <div className="text-center py-8 text-gray-500">
            <p>No holdings found</p>
          </div>
        )}

        {holdings.length > 10 && (
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

         <button
          onClick={() => navigate('/risk')}
          className="p-6 bg-white rounded-xl shadow-sm border border-gray-200 hover:border-indigo-300 hover:shadow-md transition-all group"
        >
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center group-hover:bg-indigo-200 transition-colors">
              <MessageSquare className="w-6 h-6 text-indigo-600" />
            </div>
            <div className="flex-1 text-left">
              <h3 className="font-semibold text-gray-900">Analyze Portfolio Risk</h3>
              <p className="text-sm text-gray-500">Assess your exposure</p>
            </div>
          </div>
        </button>

        <button  onClick={() => navigate('/recommendations')} 
            className="p-6 bg-white rounded-xl shadow-sm border border-gray-200 hover:border-green-300 hover:shadow-md transition-all group">
          
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