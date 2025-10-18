import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Activity,
  BarChart3,
  Target,
  RefreshCw,
  Layers,
  Info,
  AlertCircle,
  DollarSign,
  Percent
} from 'lucide-react';
import {
  BarChart,
  Bar,
  PieChart as RechartsPie,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  Area,
  AreaChart
} from 'recharts';

const API_BASE_URL = 'http://localhost:8000';

const MarketTrends = () => {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeframe, setTimeframe] = useState('1M');
  
  // Get user email from localStorage (stored as currentUser object)
  const getUserEmail = () => {
    try {
      const currentUser = localStorage.getItem('currentUser');
      if (currentUser) {
        const user = JSON.parse(currentUser);
        return user.email;
      }
    } catch (e) {
      console.error('Error reading user from localStorage:', e);
    }
    return null;
  };
  
  const userEmail = getUserEmail();

  useEffect(() => {
    if (userEmail) {
      fetchMarketData();
    } else {
      setLoading(false);
      setError('User not logged in');
    }
  }, [userEmail]);

  const fetchMarketData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${API_BASE_URL}/api/portfolio/${userEmail}/market-report`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch market data');
      }
      
      const data = await response.json();
      
      if (data.success) {
        setMarketData(data);
      } else {
        throw new Error(data.error || 'Failed to load market data');
      }
    } catch (err) {
      setError(err.message);
      console.error('Error fetching market data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await fetchMarketData();
    setIsRefreshing(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 text-indigo-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading market analysis...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Data</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={handleRefresh}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!marketData || !marketData.holdings || marketData.holdings.length === 0) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No Market Data</h3>
          <p className="text-gray-600">Add holdings to see market trends</p>
        </div>
      </div>
    );
  }

  const { holdings, portfolioMetrics } = marketData;

  // Calculate sector data from holdings
  const sectorData = holdings.reduce((acc, h) => {
    const sector = h.sector === 'N/A' || !h.sector ? 'Other' : h.sector;
    if (!acc[sector]) {
      acc[sector] = { sector, value: 0, count: 0 };
    }
    acc[sector].value += h.currentValue;
    acc[sector].count += 1;
    return acc;
  }, {});

  const totalValue = portfolioMetrics.totalValue;
  const sectorConcentration = Object.values(sectorData).map(s => ({
    ...s,
    percentage: ((s.value / totalValue) * 100).toFixed(1)
  }));

  // Day change metrics
  const dayChange = portfolioMetrics.dayTotalChange || 0;
  const dayChangePct = portfolioMetrics.dayTotalChangePct || 0;

  // Market cap distribution
  const marketCapData = holdings.reduce((acc, h) => {
    let capCategory = 'Unknown';
    if (h.marketCap) {
      if (h.marketCap > 100000000000) capCategory = 'Large Cap';
      else if (h.marketCap > 10000000000) capCategory = 'Mid Cap';
      else capCategory = 'Small Cap';
    }
    
    if (!acc[capCategory]) {
      acc[capCategory] = { category: capCategory, value: 0, count: 0 };
    }
    acc[capCategory].value += h.currentValue;
    acc[capCategory].count += 1;
    return acc;
  }, {});

  const marketCapDistribution = Object.values(marketCapData);

  // Holdings by type
  const typeData = holdings.reduce((acc, h) => {
    const type = h.type || 'other';
    if (!acc[type]) {
      acc[type] = { type, value: 0, count: 0 };
    }
    acc[type].value += h.currentValue;
    acc[type].count += 1;
    return acc;
  }, {});

  const typeDistribution = Object.values(typeData).map(t => ({
    ...t,
    percentage: ((t.value / totalValue) * 100).toFixed(1)
  }));

  // Average PE ratio for stocks
  const stocksWithPE = holdings.filter(h => h.peRatio && h.type === 'stock');
  const avgPE = stocksWithPE.length > 0
    ? stocksWithPE.reduce((sum, h) => sum + h.peRatio, 0) / stocksWithPE.length
    : 0;

  // Volatility - top movers
  const topMovers = [...holdings]
    .filter(h => h.dayChangePct)
    .sort((a, b) => Math.abs(b.dayChangePct) - Math.abs(a.dayChangePct))
    .slice(0, 5);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white px-4 py-3 rounded-lg shadow-lg border border-gray-200">
          <p className="text-sm font-semibold text-gray-900">
            {payload[0].payload.symbol || payload[0].payload.sector || payload[0].payload.category || payload[0].payload.type}
          </p>
          <p className="text-lg font-bold text-indigo-600">
            {payload[0].value?.toFixed(2)}
          </p>
        </div>
      );
    }
    return null;
  };

  const COLORS = ['#4F46E5', '#8B5CF6', '#10B981', '#F59E0B', '#EF4444'];

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Market Trends</h1>
          <p className="text-gray-600 mt-1">Portfolio performance and market analysis</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-all disabled:opacity-50"
          >
            <RefreshCw className={`w-5 h-5 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm text-gray-600">Total Value</span>
            <DollarSign className="w-5 h-5 text-indigo-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">{formatCurrency(totalValue)}</p>
          <p className="text-xs text-gray-500 mt-1">Portfolio value</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm text-gray-600">Today's Change</span>
            {dayChangePct >= 0 ? (
              <TrendingUp className="w-5 h-5 text-green-600" />
            ) : (
              <TrendingDown className="w-5 h-5 text-red-600" />
            )}
          </div>
          <p className={`text-2xl font-bold ${dayChangePct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {dayChangePct >= 0 ? '+' : ''}{dayChangePct.toFixed(2)}%
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {dayChangePct >= 0 ? '+' : ''}{formatCurrency(dayChange)}
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm text-gray-600">Avg P/E Ratio</span>
            <BarChart3 className="w-5 h-5 text-purple-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {avgPE > 0 ? avgPE.toFixed(2) : 'N/A'}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {avgPE > 22 ? 'Above market avg' : avgPE > 0 ? 'Below market avg' : 'No data'}
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm text-gray-600">Sectors</span>
            <Layers className="w-5 h-5 text-blue-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">{Object.keys(sectorData).length}</p>
          <p className="text-xs text-gray-500 mt-1">Diversification</p>
        </div>
      </div>

      {/* Main Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sector Distribution */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Sector Distribution</h2>
              <p className="text-sm text-gray-500 mt-1">Portfolio allocation by sector</p>
            </div>
            <BarChart3 className="w-6 h-6 text-indigo-600" />
          </div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <RechartsPie>
                <Pie
                  data={sectorConcentration}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={3}
                  dataKey="value"
                  label={(entry) => `${entry.percentage}%`}
                  labelLine={false}
                >
                  {sectorConcentration.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </RechartsPie>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-3">
            {sectorConcentration.map((sector, idx) => (
              <div key={idx} className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[idx % COLORS.length] }}></div>
                <span className="text-sm text-gray-700 truncate">{sector.sector}</span>
                <span className="text-xs text-gray-500">({sector.percentage}%)</span>
              </div>
            ))}
          </div>
        </div>

        {/* Market Cap Distribution */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Market Cap Distribution</h2>
              <p className="text-sm text-gray-500 mt-1">By company size</p>
            </div>
            <BarChart3 className="w-6 h-6 text-indigo-600" />
          </div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={marketCapDistribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" vertical={false} />
                <XAxis
                  dataKey="category"
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
                  tickFormatter={(value) => `₹${(value / 1000).toFixed(0)}k`}
                />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                  {marketCapDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Asset Type & Top Movers */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Asset Type Distribution */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Asset Type Distribution</h2>
              <p className="text-sm text-gray-500 mt-1">Stocks, ETFs, Bonds</p>
            </div>
            <Target className="w-6 h-6 text-indigo-600" />
          </div>
          <div className="space-y-4">
            {typeDistribution.map((type, idx) => (
              <div key={idx} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700 capitalize">{type.type}s</span>
                  <div className="flex items-center space-x-3">
                    <span className="text-sm text-gray-600">{type.count} holdings</span>
                    <span className="text-sm font-bold text-gray-900">{type.percentage}%</span>
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full`}
                    style={{ 
                      width: `${type.percentage}%`,
                      backgroundColor: COLORS[idx % COLORS.length]
                    }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Movers Today */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Top Movers Today</h2>
              <p className="text-sm text-gray-500 mt-1">Biggest daily changes</p>
            </div>
            <Activity className="w-6 h-6 text-indigo-600" />
          </div>
          <div className="space-y-3">
            {topMovers.length > 0 ? (
              topMovers.map((holding, idx) => (
                <div key={idx} className={`flex items-center justify-between p-3 rounded-lg ${
                  holding.dayChangePct >= 0 ? 'bg-green-50' : 'bg-red-50'
                }`}>
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
                      <span className="text-xs font-bold text-gray-700">{idx + 1}</span>
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">{holding.symbol}</p>
                      <p className="text-xs text-gray-500">{holding.sector}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className={`text-sm font-bold ${
                      holding.dayChangePct >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {holding.dayChangePct >= 0 ? '+' : ''}{holding.dayChangePct.toFixed(2)}%
                    </p>
                    <p className="text-xs text-gray-600">{formatCurrency(holding.currentPrice)}</p>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-center text-gray-400 py-8">No price changes today</p>
            )}
          </div>
        </div>
      </div>

      {/* Market Summary */}
      <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl p-6 text-white">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Info className="w-5 h-5 mr-2" />
          Market Summary
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white bg-opacity-20 rounded-lg p-4 backdrop-blur-sm">
            <p className="text-sm text-indigo-100 mb-2">Portfolio Health</p>
            <p className="text-xl font-bold">
              {dayChangePct >= 0 ? '📈 Positive' : '📉 Negative'}
            </p>
            <p className="text-xs text-indigo-100 mt-2">
              {dayChangePct >= 0 ? 'Up' : 'Down'} {Math.abs(dayChangePct).toFixed(2)}% today
            </p>
          </div>
          <div className="bg-white bg-opacity-20 rounded-lg p-4 backdrop-blur-sm">
            <p className="text-sm text-indigo-100 mb-2">Diversification</p>
            <p className="text-xl font-bold">
              {Object.keys(sectorData).length >= 5 ? '✅ Excellent' : 
               Object.keys(sectorData).length >= 3 ? '⚠️ Good' : '❌ Limited'}
            </p>
            <p className="text-xs text-indigo-100 mt-2">
              {Object.keys(sectorData).length} sectors, {holdings.length} holdings
            </p>
          </div>
          <div className="bg-white bg-opacity-20 rounded-lg p-4 backdrop-blur-sm">
            <p className="text-sm text-indigo-100 mb-2">Market Position</p>
            <p className="text-xl font-bold">
              {avgPE > 22 ? '🔴 Growth Focus' : avgPE > 0 ? '🟢 Value Focus' : '⚪ Mixed'}
            </p>
            <p className="text-xs text-indigo-100 mt-2">
              {avgPE > 0 ? `Avg P/E: ${avgPE.toFixed(1)}` : 'Diversified portfolio'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarketTrends;