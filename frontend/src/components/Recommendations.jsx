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
  DollarSign,
  Activity,
  Bot
} from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_API_URL;

// Cache duration: 5 minutes
const CACHE_DURATION = 5 * 60 * 1000;

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

// Recommendation card component
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
            <span>{isExpanded ? 'Less' : 'More'} details</span>
            <ArrowRight className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-90' : ''}`} />
          </button>
        </div>

        {isExpanded && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                <DollarSign className="w-4 h-4 mr-2 text-green-600" />
                Why This Matters
              </h4>
              <p className="text-sm text-gray-700 leading-relaxed">
                This recommendation is tailored to your risk profile and investment goals. 
                Taking this action can help optimize your portfolio performance and align 
                with your long-term financial objectives.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Main Recommendations component
const Recommendations = () => {
  const { currentUser } = useAuth();
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('all');
  const [aiInsights, setAiInsights] = useState('');
  const [lastFetched, setLastFetched] = useState(null);
  const [isCached, setIsCached] = useState(false);

  // Load from cache on mount
  useEffect(() => {
    if (currentUser?.email) {
      loadFromCacheOrFetch();
    }
  }, [currentUser]);

  const loadFromCacheOrFetch = () => {
    const cacheKey = `recommendations_${currentUser.email}`;
    const cached = localStorage.getItem(cacheKey);
    
    if (cached) {
      try {
        const { data, timestamp } = JSON.parse(cached);
        const age = Date.now() - timestamp;
        
        // If cache is less than 5 minutes old, use it
        if (age < CACHE_DURATION) {
          console.log('✅ Loading from cache (age:', Math.round(age / 1000), 'seconds)');
          setRecommendations(data);
          setAiInsights(data.ai_insights || '');
          setLastFetched(new Date(timestamp));
          setIsCached(true);
          setLoading(false);
          return;
        } else {
          console.log('⏰ Cache expired, fetching fresh data');
        }
      } catch (e) {
        console.error('Cache parse error:', e);
      }
    }
    
    // No valid cache, fetch fresh data
    fetchRecommendations();
  };

  const fetchRecommendations = async (forceRefresh = false) => {
    if (!forceRefresh && isCached && recommendations) {
      // Already have cached data, don't fetch again
      return;
    }

    setLoading(true);
    setError(null);
    setIsCached(false);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/portfolio/${currentUser.email}/recommendations`
      );

      if (!response.ok) {
        throw new Error('Failed to fetch recommendations');
      }

      const data = await response.json();
      
      if (data.success) {
        setRecommendations(data);
        setAiInsights(data.ai_insights || '');
        setLastFetched(new Date());
        
        // Save to cache
        const cacheKey = `recommendations_${currentUser.email}`;
        localStorage.setItem(cacheKey, JSON.stringify({
          data,
          timestamp: Date.now()
        }));
        
        console.log('💾 Saved to cache');
      } else {
        throw new Error(data.error || 'Unknown error');
      }
    } catch (err) {
      console.error('Error fetching recommendations:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    console.log('🔄 Manual refresh triggered');
    fetchRecommendations(true);
  };

  const getCategoryTitle = (category) => {
    const titles = {
      immediate: 'Immediate Actions',
      short_term: 'Short-Term Goals (1-3 months)',
      long_term: 'Long-Term Strategy',
      opportunities: 'Growth Opportunities'
    };
    return titles[category] || category;
  };

  const getCategoryDescription = (category) => {
    const descriptions = {
      immediate: 'Critical actions that need your attention now',
      short_term: 'Strategic moves to implement in the coming months',
      long_term: 'Build wealth over time with these strategies',
      opportunities: 'Explore new investment possibilities'
    };
    return descriptions[category] || '';
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
          <div className="relative">
            <RefreshCw className="w-12 h-12 text-indigo-600 animate-spin mx-auto mb-4" />
            <Bot className="w-6 h-6 text-purple-600 absolute top-0 right-0" />
          </div>
          <p className="text-gray-600 font-medium">
            {isCached ? 'Loading from cache...' : 'Analyzing your portfolio with AI...'}
          </p>
          {!isCached && (
            <p className="text-sm text-gray-500 mt-2">This may take 3-5 seconds</p>
          )}
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

  const filteredRecommendations = activeTab === 'all'
    ? allRecommendations
    : { [activeTab]: allRecommendations[activeTab] || [] };

  const tabs = [
    { id: 'all', label: 'All', count: summary.immediate_actions + summary.short_term_actions + summary.long_term_goals + summary.opportunities },
    { id: 'immediate', label: 'Immediate', count: summary.immediate_actions },
    { id: 'short_term', label: 'Short-term', count: summary.short_term_actions },
    { id: 'long_term', label: 'Long-term', count: summary.long_term_goals },
    { id: 'opportunities', label: 'Opportunities', count: summary.opportunities }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-6 text-white shadow-lg">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold mb-2 flex items-center">
              <Target className="w-7 h-7 mr-3" />
              AI-Powered Recommendations
            </h1>
            <p className="text-indigo-100 flex items-center text-sm">
              <Bot className="w-4 h-4 mr-2" />
              Personalized insights powered by Claude AI
              {lastFetched && (
                <span className="ml-3 text-indigo-200">
                  • Updated {getLastFetchedText()}
                </span>
              )}
            </p>
          </div>
          <button
            onClick={handleRefresh}
            className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors flex items-center space-x-2"
            disabled={loading}
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      

      {/* AI Insights Card */}
      {aiInsights && (
        <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl p-6 border-2 border-purple-200 shadow-md">
          <div className="flex items-start space-x-4">
            <div className="p-3 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-xl shadow-lg">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="font-bold text-gray-900 mb-2 flex items-center">
                <Sparkles className="w-5 h-5 mr-2 text-purple-600" />
                AI Insights from Claude
              </h3>
              <p className="text-gray-700 leading-relaxed text-base">
                {aiInsights}
              </p>
            </div>
          </div>
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
            <span className="text-2xl font-bold text-gray-900">{summary.long_term_goals || 0}</span>
          </div>
          <p className="text-sm text-gray-600">Long-term Strategy</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <Sparkles className="w-5 h-5 text-green-600" />
            <span className="text-2xl font-bold text-gray-900">{summary.opportunities || 0}</span>
          </div>
          <p className="text-sm text-gray-600">Opportunities</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-2">
        <div className="flex space-x-2 overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {tab.label}
              {tab.count > 0 && (
                <span className={`ml-2 px-2 py-0.5 rounded-full text-xs ${
                  activeTab === tab.id ? 'bg-white/20' : 'bg-gray-200'
                }`}>
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Recommendations List */}
      <div className="space-y-6">
        {Object.entries(filteredRecommendations).map(([category, recs]) => {
          if (!recs || recs.length === 0) return null;

          return (
            <div key={category} className="space-y-4">
              <div className="flex items-center space-x-3">
                <div className="h-px flex-1 bg-gradient-to-r from-gray-200 to-transparent"></div>
                <div className="text-center">
                  <h2 className="text-lg font-bold text-gray-900">
                    {getCategoryTitle(category)}
                  </h2>
                  <p className="text-sm text-gray-500">
                    {getCategoryDescription(category)}
                  </p>
                </div>
                <div className="h-px flex-1 bg-gradient-to-l from-gray-200 to-transparent"></div>
              </div>

              <div className="space-y-4">
                {recs.map((rec, index) => (
                  <RecommendationCard
                    key={`${category}-${index}`}
                    recommendation={rec}
                    category={category}
                  />
                ))}
              </div>
            </div>
          );
        })}

        {Object.values(filteredRecommendations).every(recs => !recs || recs.length === 0) && (
          <div className="text-center py-12">
            <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              All Caught Up!
            </h3>
            <p className="text-gray-600">
              No recommendations in this category right now. Keep up the great work!
            </p>
          </div>
        )}
      </div>

      {/* Bottom CTA */}
      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-6 border border-indigo-100">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-gray-900 mb-1 flex items-center">
              <Bot className="w-5 h-5 mr-2 text-purple-600" />
              Want to discuss these recommendations?
            </h3>
            <p className="text-sm text-gray-600">
              Chat with our AI Advisor for detailed explanations and custom strategies
            </p>
          </div>
          <button
            onClick={() => window.location.href = '/chat'}
            className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center space-x-2"
          >
            <Sparkles className="w-4 h-4" />
            <span>Ask AI Advisor</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Recommendations;