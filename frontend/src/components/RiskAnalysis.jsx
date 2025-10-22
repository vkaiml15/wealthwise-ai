import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import {
  Shield,
  TrendingUp,
  AlertTriangle,
  Info,
  RefreshCw,
  AlertCircle,
  Activity,
  Target,
  Calendar,
  IndianRupeeIcon,
  BarChart3,
  Layers,
  Clock
} from 'lucide-react';
import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Cell
} from 'recharts';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Cache duration: 10 minutes (risk data changes less frequently than recommendations)
const CACHE_DURATION = 10 * 60 * 1000;

const RiskAnalysis = () => {
  const { currentUser } = useAuth();
  const [riskData, setRiskData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastFetched, setLastFetched] = useState(null);
  const [isCached, setIsCached] = useState(false);

  useEffect(() => {
    if (currentUser?.email) {
      loadFromCacheOrFetch();
    }
  }, [currentUser?.email]);

  const loadFromCacheOrFetch = () => {
    const cacheKey = `risk_analysis_${currentUser.email}`;
    const cached = localStorage.getItem(cacheKey);
    
    if (cached) {
      try {
        const { data, timestamp } = JSON.parse(cached);
        const age = Date.now() - timestamp;
        
        // If cache is less than 10 minutes old, use it
        if (age < CACHE_DURATION) {
          console.log('✅ Loading risk analysis from cache (age:', Math.round(age / 1000), 'seconds)');
          setRiskData(data.riskAnalysis);
          setLastFetched(new Date(timestamp));
          setIsCached(true);
          setLoading(false);
          return;
        } else {
          console.log('⏰ Risk analysis cache expired, fetching fresh data');
        }
      } catch (e) {
        console.error('Cache parse error:', e);
      }
    }
    
    // No valid cache, fetch fresh data
    fetchRiskAnalysis();
  };

  const fetchRiskAnalysis = async (forceRefresh = false) => {
    if (!forceRefresh && isCached && riskData) {
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setIsCached(false);
      
      const response = await fetch(`${API_BASE_URL}/api/portfolio/${currentUser.email}/risk-analysis`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch risk analysis');
      }
      
      const data = await response.json();
      
      if (data.success) {
        setRiskData(data.riskAnalysis);
        setLastFetched(new Date());
        
        // Save to cache
        const cacheKey = `risk_analysis_${currentUser.email}`;
        localStorage.setItem(cacheKey, JSON.stringify({
          data,
          timestamp: Date.now()
        }));
        
        console.log('💾 Risk analysis saved to cache');
      } else {
        throw new Error(data.error || 'Failed to load risk analysis');
      }
    } catch (err) {
      setError(err.message);
      console.error('Error fetching risk analysis:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    console.log('🔄 Manual refresh triggered');
    setIsRefreshing(true);
    await fetchRiskAnalysis(true);
    setIsRefreshing(false);
  };

  // Format last fetched time
  const getLastFetchedText = () => {
    if (!lastFetched) return '';
    
    const now = Date.now();
    const diff = now - lastFetched.getTime();
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return 'Just now';
    if (minutes === 1) return '1 minute ago';
    if (minutes < 60) return `${minutes} minutes ago`;
    
    const hours = Math.floor(minutes / 60);
    if (hours === 1) return '1 hour ago';
    return `${hours} hours ago`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 text-indigo-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600 font-medium">
            {isCached ? 'Loading from cache...' : 'Analyzing your risk profile...'}
          </p>
          {!isCached && (
            <p className="text-sm text-gray-500 mt-2">This may take a few seconds</p>
          )}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Risk Analysis</h3>
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

  if (!riskData) return null;

  const { riskScore, riskLabel, recommendation, factors, breakdown, rationale } = riskData;

  // Prepare radar chart data
  const radarData = [
    { factor: 'Age', value: breakdown.ageContribution, fullMark: 1.5 },
    { factor: 'Horizon', value: breakdown.horizonContribution, fullMark: 2.5 },
    { factor: 'Tolerance', value: breakdown.toleranceContribution, fullMark: 3.5 },
    { factor: 'Allocation', value: breakdown.allocationContribution, fullMark: 1.5 },
    { factor: 'Contribution', value: breakdown.contributionContribution, fullMark: 1.0 }
  ];

  // Prepare bar chart data
  const barData = Object.entries(breakdown).map(([key, value]) => ({
    name: key.replace('Contribution', ''),
    value: value
  }));

  const getRiskColor = () => {
    if (riskScore < 4) return { 
      bg: 'bg-green-100', 
      text: 'text-green-600', 
      border: 'border-green-200',
      gradient: 'from-green-500 to-green-600'
    };
    if (riskScore < 7) return { 
      bg: 'bg-blue-100', 
      text: 'text-blue-600', 
      border: 'border-blue-200',
      gradient: 'from-blue-500 to-blue-600'
    };
    return { 
      bg: 'bg-red-100', 
      text: 'text-red-600', 
      border: 'border-red-200',
      gradient: 'from-red-500 to-red-600'
    };
  };

  const colors = getRiskColor();

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white px-4 py-3 rounded-lg shadow-lg border border-gray-200">
          <p className="text-sm font-semibold text-gray-900">
            {payload[0].payload.factor || payload[0].payload.name}
          </p>
          <p className="text-lg font-bold text-indigo-600">
            {payload[0].value.toFixed(2)}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Risk Analysis</h1>
          <p className="text-gray-600 mt-1">
            Understanding your investment risk profile
            {lastFetched && (
              <span className="ml-3 text-gray-500 text-sm">
                • Updated {getLastFetchedText()}
              </span>
            )}
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-5 h-5 ${isRefreshing ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Risk Score Hero Card */}
      <div className={`${colors.bg} ${colors.border} border-2 rounded-2xl p-8`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className={`w-20 h-20 bg-gradient-to-br ${colors.gradient} rounded-full flex items-center justify-center shadow-lg`}>
              <Shield className="w-10 h-10 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Your Risk Score</p>
              <h2 className={`text-5xl font-bold ${colors.text}`}>{riskScore}/10</h2>
              <p className={`text-lg font-semibold ${colors.text} mt-1`}>{riskLabel}</p>
            </div>
          </div>
          <div className="text-right max-w-md">
            <p className="text-sm text-gray-600 mb-2 font-semibold">Recommendation</p>
            <p className="text-gray-900">{recommendation}</p>
          </div>
        </div>
      </div>

      {/* AI Rationale */}
      <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl p-6 text-white shadow-lg">
        <div className="flex items-start space-x-3">
          <Activity className="w-6 h-6 mt-1 flex-shrink-0" />
          <div>
            <h3 className="text-lg font-semibold mb-2">🤖 AI Analysis</h3>
            <p className="text-indigo-100 leading-relaxed">{rationale}</p>
            
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Radar Chart */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Target className="w-5 h-5 mr-2 text-indigo-600" />
            Risk Factor Breakdown
          </h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
                <PolarGrid stroke="#E5E7EB" />
                <PolarAngleAxis dataKey="factor" tick={{ fill: '#6B7280', fontSize: 12 }} />
                <PolarRadiusAxis angle={90} domain={[0, 3.5]} tick={{ fill: '#9CA3AF' }} />
                <Radar
                  name="Contribution"
                  dataKey="value"
                  stroke="#6366F1"
                  fill="#6366F1"
                  fillOpacity={0.6}
                />
                <Tooltip content={<CustomTooltip />} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Bar Chart */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <BarChart3 className="w-5 h-5 mr-2 text-indigo-600" />
            Score Contributions
          </h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" vertical={false} />
                <XAxis 
                  dataKey="name" 
                  stroke="#9CA3AF" 
                  style={{ fontSize: '12px' }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis stroke="#9CA3AF" style={{ fontSize: '12px' }} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="value" fill="#6366F1" radius={[8, 8, 0, 0]}>
                  {barData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={`hsl(${240 - index * 20}, 70%, 60%)`} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Factor Details Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <div className="flex items-center space-x-3 mb-3">
            <Calendar className="w-5 h-5 text-indigo-600" />
            <h4 className="font-semibold text-gray-900">Age Factor</h4>
          </div>
          <p className="text-2xl font-bold text-gray-900">{factors.age} years</p>
          <p className="text-sm text-gray-600 mt-1">
            Risk capacity: {(factors.ageFactor * 100).toFixed(0)}%
          </p>
          <div className="mt-3 w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-indigo-600 h-2 rounded-full"
              style={{ width: `${factors.ageFactor * 100}%` }}
            ></div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <div className="flex items-center space-x-3 mb-3">
            <Target className="w-5 h-5 text-indigo-600" />
            <h4 className="font-semibold text-gray-900">Investment Horizon</h4>
          </div>
          <p className="text-2xl font-bold text-gray-900">{factors.horizonYears} years</p>
          <p className="text-sm text-gray-600 mt-1">
            Time capacity: {(factors.horizonFactor * 100).toFixed(0)}%
          </p>
          <div className="mt-3 w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-purple-600 h-2 rounded-full"
              style={{ width: `${factors.horizonFactor * 100}%` }}
            ></div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <div className="flex items-center space-x-3 mb-3">
            <TrendingUp className="w-5 h-5 text-indigo-600" />
            <h4 className="font-semibold text-gray-900">Risk Tolerance</h4>
          </div>
          <p className="text-2xl font-bold text-gray-900 capitalize">{factors.tolerance}</p>
          <p className="text-sm text-gray-600 mt-1">
            Comfort level: {(factors.toleranceIndex * 100).toFixed(0)}%
          </p>
          <div className="mt-3 w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-green-600 h-2 rounded-full"
              style={{ width: `${factors.toleranceIndex * 100}%` }}
            ></div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <div className="flex items-center space-x-3 mb-3">
            <Layers className="w-5 h-5 text-indigo-600" />
            <h4 className="font-semibold text-gray-900">Portfolio Risk</h4>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {(factors.allocationRisk * 10).toFixed(1)}/10
          </p>
          <p className="text-sm text-gray-600 mt-1">Current allocation risk</p>
          <div className="mt-3 w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-orange-600 h-2 rounded-full"
              style={{ width: `${factors.allocationRisk * 100}%` }}
            ></div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <div className="flex items-center space-x-3 mb-3">
            <IndianRupeeIcon className="w-5 h-5 text-indigo-600" />
            <h4 className="font-semibold text-gray-900">Contribution Capacity</h4>
          </div>
          <p className="text-2xl font-bold text-gray-900">Active</p>
          <p className="text-sm text-gray-600 mt-1">
            Factor: {(factors.contributionFactor * 100).toFixed(0)}%
          </p>
          <div className="mt-3 w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full"
              style={{ width: `${factors.contributionFactor * 100}%` }}
            ></div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <div className="flex items-center space-x-3 mb-3">
            <Info className="w-5 h-5 text-indigo-600" />
            <h4 className="font-semibold text-gray-900">Overall Assessment</h4>
          </div>
          <p className={`text-2xl font-bold ${colors.text}`}>{riskLabel}</p>
          <p className="text-sm text-gray-600 mt-1">Risk profile category</p>
          <div className="mt-3 flex items-center space-x-1">
            {[...Array(10)].map((_, i) => (
              <div
                key={i}
                className={`h-2 flex-1 rounded-full ${
                  i < Math.round(riskScore) ? colors.bg : 'bg-gray-200'
                }`}
              ></div>
            ))}
          </div>
        </div>
      </div>

      {/* Info Box */}
      <div className="bg-gray-50 border border-gray-200 rounded-xl p-6">
        <div className="flex items-start space-x-3">
          <Info className="w-5 h-5 text-gray-600 mt-1 flex-shrink-0" />
          <div>
            <h4 className="font-semibold text-gray-900 mb-2">Understanding Your Risk Score</h4>
            <p className="text-sm text-gray-600 leading-relaxed">
              Your risk score is calculated based on five key factors: <strong>age</strong>, 
              <strong> investment horizon</strong>, <strong> risk tolerance</strong>, 
              <strong> portfolio allocation</strong>, and <strong> monthly contribution capacity</strong>. 
              A higher score indicates greater capacity and willingness to take investment risks for potentially higher returns.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskAnalysis;