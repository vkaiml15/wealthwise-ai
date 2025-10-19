import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import {
  Target,
  TrendingUp,
  AlertCircle,
  Clock,
  CheckCircle,
  Sparkles,
  ArrowRight,
  RefreshCw,
  Zap,
  Calendar,
  Activity,
  Bot,
  Calculator,
  Info,
  TrendingDown,
  BarChart3,
  Shield,
  Layers,
  Gauge,
  Brain
} from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_API_URL;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

// Priority badge component
const PriorityBadge = ({ priority }) => {
  const styles = {
    high: 'bg-red-100 text-red-700 border-red-200',
    medium: 'bg-yellow-100 text-yellow-700 border-yellow-200',
    low: 'bg-blue-100 text-blue-700 border-blue-200'
  };

  const icons = {
    high: AlertCircle,
    medium: Clock,
    low: Target
  };

  const Icon = icons[priority] || Clock;

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${styles[priority] || styles.medium}`}>
      <Icon className="w-3 h-3 mr-1" />
      {priority.charAt(0).toUpperCase() + priority.slice(1)}
    </span>
  );
};

// Enhanced Calculation Breakdown Component
const CalculationBreakdown = ({ calculation }) => {
  if (!calculation) return null;

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
      <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
        <Calculator className="w-4 h-4 mr-2 text-blue-600" />
        Detailed Calculation Breakdown
      </h4>
      
      <div className="space-y-3">
        {calculation.currentState && (
          <div className="bg-white rounded-lg p-3 border border-blue-100">
            <p className="text-xs font-medium text-gray-500 uppercase mb-2">📊 Current State</p>
            <div className="space-y-1">
              {Object.entries(calculation.currentState).map(([key, value]) => (
                <div key={key} className="flex justify-between text-sm">
                  <span className="text-gray-600">{key}:</span>
                  <span className="font-semibold text-gray-900">{value}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {calculation.targetState && (
          <div className="bg-white rounded-lg p-3 border border-green-100">
            <p className="text-xs font-medium text-gray-500 uppercase mb-2">🎯 Target State</p>
            <div className="space-y-1">
              {Object.entries(calculation.targetState).map(([key, value]) => (
                <div key={key} className="flex justify-between text-sm">
                  <span className="text-gray-600">{key}:</span>
                  <span className="font-semibold text-green-700">{value}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {calculation.formula && (
          <div className="bg-white rounded-lg p-3 border border-purple-100">
            <p className="text-xs font-medium text-gray-500 uppercase mb-2">📐 Formula Used</p>
            <p className="text-sm font-mono text-purple-900 bg-purple-50 p-2 rounded break-words">
              {calculation.formula}
            </p>
          </div>
        )}

        {calculation.gap && (
          <div className="bg-white rounded-lg p-3 border border-orange-100">
            <p className="text-xs font-medium text-gray-500 uppercase mb-2">Gap Analysis</p>
            <p className="text-sm text-gray-700">{calculation.gap}</p>
          </div>
        )}

        {calculation.user_specific_impact && (
          <div className="bg-white rounded-lg p-3 border border-red-100">
            <p className="text-xs font-medium text-gray-500 uppercase mb-2">⚠️ Impact on You</p>
            <p className="text-sm text-red-700 font-medium">{calculation.user_specific_impact}</p>
          </div>
        )}
      </div>
    </div>
  );
};

// XAI Explanation Component
const XAIExplanation = ({ xaiExplanation }) => {
  if (!xaiExplanation) return null;

  return (
    <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg p-5 border-2 border-purple-300">
      <h4 className="font-bold text-gray-900 mb-3 flex items-center text-base">
        <Brain className="w-5 h-5 mr-2 text-purple-600" />
        Why This Matters (Explainable AI)
      </h4>
      
      <div 
        className="prose prose-sm max-w-none text-gray-800 leading-relaxed"
        dangerouslySetInnerHTML={{ 
          __html: xaiExplanation
            .replace(/\*\*(.*?)\*\*/g, '<strong class="text-purple-900">$1</strong>')
            .replace(/\n\n/g, '<br/><br/>')
            .replace(/\n/g, '<br/>') 
        }}
      />
    </div>
  );
};

// User Context Component
const UserContextDisplay = ({ userContext }) => {
  if (!userContext || Object.keys(userContext).length === 0) return null;

  return (
    <div className="bg-indigo-50 rounded-lg p-4 border border-indigo-200">
      <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
        <Target className="w-4 h-4 mr-2 text-indigo-700" />
        Your Profile Context
      </h4>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {Object.entries(userContext).map(([key, value]) => (
          <div key={key} className="bg-white rounded p-2">
            <p className="text-xs text-gray-500 uppercase">
              {key.replace(/_/g, ' ')}
            </p>
            <p className="text-sm font-semibold text-gray-900">
              {typeof value === 'object' ? JSON.stringify(value) : value}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

// Market Context Component
const MarketContextDisplay = ({ marketContext }) => {
  if (!marketContext || !marketContext.market_available) return null;

  const getSentimentColor = (sentiment) => {
    switch(sentiment?.toLowerCase()) {
      case 'bullish': return 'text-green-700 bg-green-100';
      case 'bearish': return 'text-red-700 bg-red-100';
      default: return 'text-blue-700 bg-blue-100';
    }
  };

  return (
    <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
      <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
        <Activity className="w-4 h-4 mr-2 text-blue-700" />
        Current Market Context
      </h4>
      <div className="flex flex-wrap gap-2">
        {marketContext.sentiment && (
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getSentimentColor(marketContext.sentiment)}`}>
            Sentiment: {marketContext.sentiment.toUpperCase()}
          </span>
        )}
        {marketContext.volatility && (
          <span className="px-3 py-1 rounded-full text-sm font-medium text-orange-700 bg-orange-100">
            Volatility: {marketContext.volatility.level?.toUpperCase()}
          </span>
        )}
        {marketContext.volatility?.vix && (
          <span className="px-3 py-1 rounded-full text-sm font-medium text-purple-700 bg-purple-100">
            VIX: {marketContext.volatility.vix}
          </span>
        )}
      </div>
      {marketContext.volatility?.interpretation && (
        <p className="text-sm text-gray-600 mt-2">
          {marketContext.volatility.interpretation}
        </p>
      )}
    </div>
  );
};

// Recommendation Card Component
const RecommendationCard = ({ recommendation, category }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const categoryColors = {
    immediate: 'border-l-red-500 bg-red-50',
    short_term: 'border-l-yellow-500 bg-yellow-50',
    long_term: 'border-l-blue-500 bg-blue-50',
    opportunities: 'border-l-green-500 bg-green-50'
  };

  const categoryIcons = {
    immediate: Zap,
    short_term: Calendar,
    long_term: TrendingUp,
    opportunities: Sparkles
  };

  const Icon = categoryIcons[category] || Target;

  return (
    <div className={`bg-white rounded-xl border-l-4 shadow-sm hover:shadow-md transition-all ${categoryColors[category]}`}>
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-start space-x-3 flex-1">
            <div className="p-2 bg-white rounded-lg shadow-sm">
              <Icon className="w-5 h-5 text-gray-700" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900 text-lg mb-1">
                {recommendation.title}
              </h3>
              <p className="text-gray-600 text-sm">
                {recommendation.description}
              </p>
            </div>
          </div>
          <PriorityBadge priority={recommendation.priority} />
        </div>

        {recommendation.metrics && recommendation.metrics.length > 0 && (
          <div className="mb-4 p-3 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg border border-indigo-100">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {recommendation.metrics.map((metric, idx) => (
                <div key={idx} className="text-center">
                  <div className="text-xs text-gray-500 uppercase mb-1">{metric.label}</div>
                  <div className="text-lg font-bold text-gray-900">{metric.value}</div>
                  {metric.change && (
                    <div className={`text-xs flex items-center justify-center ${
                      metric.change.startsWith('+') ? 'text-green-600' : 
                      metric.change.startsWith('-') ? 'text-red-600' : 'text-gray-600'
                    }`}>
                      {metric.change.startsWith('+') ? (
                        <TrendingUp className="w-3 h-3 mr-1" />
                      ) : metric.change.startsWith('-') ? (
                        <TrendingDown className="w-3 h-3 mr-1" />
                      ) : null}
                      {metric.change}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div className="bg-white rounded-lg p-3 border border-gray-200">
            <div className="flex items-center space-x-2 mb-1">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span className="text-xs font-medium text-gray-500 uppercase">Action</span>
            </div>
            <p className="text-sm text-gray-900 font-medium">
              {recommendation.action}
            </p>
          </div>

          <div className="bg-white rounded-lg p-3 border border-gray-200">
            <div className="flex items-center space-x-2 mb-1">
              <Activity className="w-4 h-4 text-indigo-600" />
              <span className="text-xs font-medium text-gray-500 uppercase">Expected Impact</span>
            </div>
            <p className="text-sm text-gray-900 font-medium">
              {recommendation.impact}
            </p>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Clock className="w-4 h-4" />
            <span>{recommendation.timeframe}</span>
          </div>
          
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-indigo-600 hover:text-indigo-700 text-sm font-medium flex items-center space-x-1"
          >
            <Info className="w-4 h-4" />
            <span>{isExpanded ? 'Hide' : 'Show'} Full Details</span>
            <ArrowRight className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-90' : ''}`} />
          </button>
        </div>

        {isExpanded && (
          <div className="mt-4 pt-4 border-t border-gray-200 space-y-4">
            {/* XAI Transparency Badge */}
            <div className="bg-gradient-to-r from-purple-100 to-indigo-100 rounded-lg p-3 border-2 border-purple-300">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Brain className="w-5 h-5 text-purple-700" />
                  <span className="text-sm font-bold text-purple-900">Explainable AI Recommendation</span>
                </div>
                <span className="text-xs bg-purple-200 text-purple-800 px-3 py-1 rounded-full font-semibold">
                  Full Transparency
                </span>
              </div>
              <p className="text-xs text-purple-800 mt-2">
                This recommendation uses real-time market data, your personal risk profile, and proven financial models. 
                Every calculation is explained below.
              </p>
            </div>

            {/* XAI Explanation */}
            {recommendation.xai_explanation && (
              <XAIExplanation xaiExplanation={recommendation.xai_explanation} />
            )}

            {/* Calculation Breakdown */}
            {recommendation.calculation && (
              <CalculationBreakdown calculation={recommendation.calculation} />
            )}

            {/* Reasoning */}
            {recommendation.reasoning && (
              <div className="bg-green-50 rounded-lg p-4 border-l-4 border-green-500">
                <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                  <Target className="w-4 h-4 mr-2 text-green-600" />
                  Why This Recommendation
                </h4>
                <p className="text-sm text-gray-700 leading-relaxed">
                  {recommendation.reasoning}
                </p>
              </div>
            )}

            {/* User Context */}
            {recommendation.user_context && (
              <UserContextDisplay userContext={recommendation.user_context} />
            )}

            {/* Market Context */}
            {recommendation.market_context && (
              <MarketContextDisplay marketContext={recommendation.market_context} />
            )}

            {/* Action Steps */}
            {recommendation.steps && (
              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                  <BarChart3 className="w-4 h-4 mr-2 text-indigo-600" />
                  Step-by-Step Action Plan
                </h4>
                <ol className="space-y-2">
                  {recommendation.steps.map((step, idx) => (
                    <li key={idx} className="flex items-start text-sm">
                      <span className="flex-shrink-0 w-6 h-6 bg-indigo-100 text-indigo-700 rounded-full flex items-center justify-center text-xs font-semibold mr-3">
                        {idx + 1}
                      </span>
                      <span className="text-gray-700 pt-0.5">{step}</span>
                    </li>
                  ))}
                </ol>
              </div>
            )}

            {/* Expected Outcome */}
            {recommendation.expectedOutcome && (
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg p-4 border-2 border-green-300">
                <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                  <TrendingUp className="w-4 h-4 mr-2 text-green-600" />
                  Expected Outcome
                </h4>
                <p className="text-sm text-gray-700 leading-relaxed font-medium">
                  {recommendation.expectedOutcome}
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// Main Recommendations Component
const Recommendations = () => {
  const { currentUser } = useAuth();
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('all');
  const [lastFetched, setLastFetched] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchRecommendations = useCallback(async (forceRefresh = false) => {
  if (!currentUser?.email) {
    setError('User information not available');
    setLoading(false);
    return;
  }

  // Try to use cached data if not forcing refresh
  if (!forceRefresh) {
    const cacheKey = `recommendations_${currentUser.email}`;
    const cached = localStorage.getItem(cacheKey);
    
    if (cached) {
      try {
        const { data, timestamp } = JSON.parse(cached);
        const now = Date.now();
        
        // Check if cache is still valid (within CACHE_DURATION)
        if (now - timestamp < CACHE_DURATION) {
          console.log('✅ Using cached recommendations');
          setRecommendations(data);
          setLastFetched(new Date(timestamp));
          setLoading(false);
          setIsRefreshing(false);
          return;
        }
      } catch (e) {
        console.error('Error reading cache:', e);
      }
    }
  }

  // If no valid cache or force refresh, fetch from API
  setLoading(true);
  setError(null);

  try {
    console.log('🔄 Fetching recommendations from API...');
    const response = await fetch(
      `${API_BASE_URL}/api/portfolio/${currentUser.email}/recommendations`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch recommendations: ${response.status}`);
    }

    const data = await response.json();

    if (data.success) {
      setRecommendations(data);
      const now = Date.now();
      setLastFetched(new Date(now));
      setError(null);

      // Save to cache
      const cacheKey = `recommendations_${currentUser.email}`;
      localStorage.setItem(cacheKey, JSON.stringify({
        data,
        timestamp: now
      }));
      console.log('✅ Recommendations cached successfully');
    } else {
      throw new Error(data.error || 'Failed to load recommendations');
    }
  } catch (err) {
    console.error('❌ Error fetching recommendations:', err);
    setError(err.message || 'Unable to load recommendations. Please try again.');
  } finally {
    setLoading(false);
    setIsRefreshing(false);
  }
}, [currentUser]);

  useEffect(() => {
  if (currentUser?.email) {
    fetchRecommendations();
  }
}, [currentUser?.email]); 

  const handleRefresh = () => {
  setIsRefreshing(true);
  fetchRecommendations(true); 
};

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

  if (loading && !isRefreshing) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="relative">
            <RefreshCw className="w-12 h-12 text-indigo-600 animate-spin mx-auto mb-4" />
            <Brain className="w-6 h-6 text-purple-600 absolute top-0 right-0" />
          </div>
          <p className="text-gray-600 font-medium">
            Analyzing your portfolio with AI...
          </p>
          <p className="text-sm text-gray-500 mt-2">Generating personalized recommendations</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-8 text-center">
        <AlertCircle className="w-12 h-12 text-red-600 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-red-900 mb-2">Error Loading Recommendations</h3>
        <p className="text-red-700 mb-4">{error}</p>
        <button
          onClick={handleRefresh}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  const allRecommendations = recommendations?.recommendations || {};
  const summary = recommendations?.summary || {};
  const metadata = recommendations?.metadata || {};
  const explainability = recommendations?.explainability || {};
  const confidence = recommendations?.confidence || {};
  const aiInsights = recommendations?.ai_insights || '';

  const filteredRecommendations = activeTab === 'all'
    ? allRecommendations
    : { [activeTab]: allRecommendations[activeTab] || [] };

  const tabs = [
    { id: 'all', label: 'All', count: (summary.immediate_actions || 0) + (summary.short_term_actions || 0) + (summary.long_term_goals || 0) + (summary.opportunities || 0) },
    { id: 'immediate', label: 'Immediate', count: summary.immediate_actions || 0 },
    { id: 'short_term', label: 'Short-term', count: summary.short_term_actions || 0 },
    { id: 'long_term', label: 'Long-term', count: summary.long_term_goals || 0 },
    { id: 'opportunities', label: 'Opportunities', count: summary.opportunities || 0 }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-6 text-white shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold mb-2 flex items-center">
              <Brain className="w-7 h-7 mr-3" />
              AI-Powered Recommendations with XAI
            </h1>
            <p className="text-indigo-100 flex items-center text-sm">
              <Calculator className="w-4 h-4 mr-2" />
              Personalized analysis with complete transparency
              {lastFetched && (
                <span className="ml-3 text-indigo-200">
                  • Updated {getLastFetchedText()}
                </span>
              )}
            </p>
          </div>
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors flex items-center space-x-2 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>{isRefreshing ? 'Refreshing...' : 'Refresh'}</span>
          </button>
        </div>

        {/* Portfolio Metrics */}
        {metadata.portfolio && (
          <div className="flex items-center space-x-4 bg-white/10 rounded-lg p-4 flex-wrap">
            <div className="flex items-center space-x-3">
              <Gauge className="w-8 h-8" />
              <div>
                <div className="text-xs text-indigo-200 uppercase">Portfolio Value</div>
                <div className="text-2xl font-bold">₹{(metadata.portfolio.total_value / 1000).toFixed(0)}K</div>
              </div>
            </div>
            <div className="h-12 w-px bg-white/20"></div>
            <div>
              <div className="text-xs text-indigo-200 uppercase">Holdings</div>
              <div className="text-xl font-bold">{metadata.portfolio.total_holdings}</div>
            </div>
            {metadata.risk && metadata.risk.score && (
              <>
                <div className="h-12 w-px bg-white/20"></div>
                <div>
                  <div className="text-xs text-indigo-200 uppercase">Risk Profile</div>
                  <div className="text-sm font-semibold">{metadata.risk.label} ({metadata.risk.score}/10)</div>
                </div>
              </>
            )}
          </div>
        )}
      </div>

      {/* AI Insights Card */}
      {aiInsights && (
        <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl p-6 border-2 border-purple-200 shadow-md">
          <div className="flex items-start space-x-4">
            <div className="p-3 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-xl shadow-lg">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="font-bold text-gray-900 mb-2 flex items-center">
                <Bot className="w-5 h-5 mr-2 text-purple-600" />
                Personalized AI Insights
              </h3>
              <p className="text-gray-700 leading-relaxed text-base">
                {aiInsights}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Confidence Indicator */}
      {confidence.recommendation_confidence && (
        <div className="bg-white rounded-xl p-5 border border-gray-200 shadow-sm">
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
            <Shield className="w-5 h-5 mr-2 text-indigo-600" />
            Recommendation Confidence
          </h3>
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">Overall Confidence:</span>
                <span className={`text-sm font-semibold ${
                  confidence.recommendation_confidence === 'high' ? 'text-green-600' : 'text-yellow-600'
                }`}>
                  {confidence.recommendation_confidence.toUpperCase()}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className={`h-3 rounded-full transition-all ${
                    confidence.recommendation_confidence === 'high' ? 'bg-green-500' : 'bg-yellow-500'
                  }`}
                  style={{ width: confidence.recommendation_confidence === 'high' ? '90%' : '70%' }}
                />
              </div>
            </div>
          </div>
          {confidence.explanation && (
            <p className="text-xs text-gray-600 mt-3">{confidence.explanation}</p>
          )}
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <Zap className="w-5 h-5 text-red-600" />
            <span className="text-2xl font-bold text-gray-900">{summary.immediate_actions || 0}</span>
          </div>
          <p className="text-sm text-gray-600">Immediate Actions</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <Calendar className="w-5 h-5 text-yellow-600" />
            <span className="text-2xl font-bold text-gray-900">{summary.short_term_actions || 0}</span>
          </div>
          <p className="text-sm text-gray-600">Short-term Goals</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <TrendingUp className="w-5 h-5 text-blue-600" />
            <span className="text-2xl font-bold text-gray-900">{summary.long_term_goals || 0}
            </span>
          </div>
          <p className="text-sm text-gray-600">Long-term Goals</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <Sparkles className="w-5 h-5 text-green-600" />
            <span className="text-2xl font-bold text-gray-900">{summary.opportunities || 0}</span>
          </div>
          <p className="text-sm text-gray-600">Opportunities</p>
        </div>
      </div>

      {/* Explainability Section */}
      {explainability && Object.keys(explainability).length > 0 && (
        <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-xl p-6 border-2 border-indigo-200">
          <h3 className="font-bold text-gray-900 mb-4 flex items-center text-lg">
            <Layers className="w-5 h-5 mr-2 text-indigo-600" />
            How We Generate Your Recommendations
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {explainability.data_sources && (
              <div className="bg-white rounded-lg p-4 border border-indigo-100">
                <h4 className="font-semibold text-gray-900 mb-2 text-sm flex items-center">
                  <Activity className="w-4 h-4 mr-2 text-indigo-600" />
                  Data Sources Used
                </h4>
                <ul className="space-y-1">
                  {explainability.data_sources.map((source, idx) => (
                    <li key={idx} className="text-sm text-gray-700 flex items-start">
                      <span className="text-indigo-600 mr-2">•</span>
                      {source}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {explainability.factors_considered && (
              <div className="bg-white rounded-lg p-4 border border-indigo-100">
                <h4 className="font-semibold text-gray-900 mb-2 text-sm flex items-center">
                  <Target className="w-4 h-4 mr-2 text-indigo-600" />
                  Factors Considered
                </h4>
                <ul className="space-y-1">
                  {explainability.factors_considered.map((factor, idx) => (
                    <li key={idx} className="text-sm text-gray-700 flex items-start">
                      <span className="text-indigo-600 mr-2">•</span>
                      {factor}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {explainability.methodology && (
              <div className="bg-white rounded-lg p-4 border border-indigo-100 md:col-span-2">
                <h4 className="font-semibold text-gray-900 mb-2 text-sm flex items-center">
                  <Brain className="w-4 h-4 mr-2 text-indigo-600" />
                  Our Methodology
                </h4>
                <p className="text-sm text-gray-700 leading-relaxed">
                  {explainability.methodology}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="flex border-b border-gray-200 overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-6 py-3 text-sm font-medium transition-colors whitespace-nowrap ${
                activeTab === tab.id
                  ? 'bg-indigo-50 text-indigo-700 border-b-2 border-indigo-600'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              {tab.label}
              {tab.count > 0 && (
                <span className={`ml-2 px-2 py-0.5 rounded-full text-xs ${
                  activeTab === tab.id
                    ? 'bg-indigo-200 text-indigo-800'
                    : 'bg-gray-200 text-gray-700'
                }`}>
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Recommendations List */}
        <div className="p-6">
          {Object.keys(filteredRecommendations).length === 0 ? (
            <div className="text-center py-12">
              <CheckCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                All Caught Up!
              </h3>
              <p className="text-gray-600">
                No recommendations in this category at the moment.
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {Object.entries(filteredRecommendations).map(([category, items]) => (
                items && items.length > 0 && (
                  <div key={category}>
                    {activeTab === 'all' && (
                      <h2 className="text-xl font-bold text-gray-900 mb-4 capitalize flex items-center">
                        {category === 'immediate' && <Zap className="w-5 h-5 mr-2 text-red-600" />}
                        {category === 'short_term' && <Calendar className="w-5 h-5 mr-2 text-yellow-600" />}
                        {category === 'long_term' && <TrendingUp className="w-5 h-5 mr-2 text-blue-600" />}
                        {category === 'opportunities' && <Sparkles className="w-5 h-5 mr-2 text-green-600" />}
                        {category.replace('_', ' ')} ({items.length})
                      </h2>
                    )}
                    <div className="space-y-4">
                      {items.map((recommendation, idx) => (
                        <RecommendationCard
                          key={`${category}-${idx}`}
                          recommendation={recommendation}
                          category={category}
                        />
                      ))}
                    </div>
                  </div>
                )
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Footer Note */}
      <div className="bg-gray-50 rounded-xl p-5 border border-gray-200">
        <div className="flex items-start space-x-3">
          <Info className="w-5 h-5 text-gray-500 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-gray-600 space-y-2">
            <p>
              <strong className="text-gray-900">About These Recommendations:</strong> Our AI analyzes your 
              portfolio, risk profile, market conditions, and financial goals to provide personalized insights.
            </p>
            <p>
              <strong className="text-gray-900">Explainable AI (XAI):</strong> Every recommendation includes 
              detailed explanations, calculations, and reasoning. Click "Show Full Details" on any recommendation 
              to see the complete analysis and understand exactly how we arrived at each suggestion.
            </p>
            <p className="text-xs text-gray-500">
              Note: These recommendations are for informational purposes only and should not be considered as 
              financial advice. Please consult with a qualified financial advisor before making investment decisions.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Recommendations;