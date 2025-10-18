import { useState, useEffect } from 'react';

const API_BASE_URL = process.env.REACT_APP_API_URL ;

/**
 * Custom hook to fetch portfolio analysis from backend
 * 
 * Usage:
 *   const { analysis, loading, error, refresh } = usePortfolioAnalysis(userEmail);
 */
export const usePortfolioAnalysis = (userEmail) => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAnalysis = async () => {
    if (!userEmail) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      console.log('Fetching portfolio analysis for:', userEmail);

      const response = await fetch(`${API_BASE_URL}/api/portfolio/${userEmail}/analysis`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch analysis: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success) {
        setAnalysis(data);
        console.log('✅ Analysis loaded:', data);
      } else {
        throw new Error(data.error || 'Analysis failed');
      }
    } catch (err) {
      console.error('Error fetching analysis:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalysis();
  }, [userEmail]);

  return {
    analysis,
    loading,
    error,
    refresh: fetchAnalysis
  };
};

/**
 * Custom hook to fetch market data from backend
 */
export const useMarketData = (userEmail) => {
  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMarketData = async () => {
    if (!userEmail) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/api/portfolio/${userEmail}/market-report`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch market data: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success) {
        setMarketData(data);
      } else {
        throw new Error(data.error || 'Market data fetch failed');
      }
    } catch (err) {
      console.error('Error fetching market data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMarketData();
  }, [userEmail]);

  return {
    marketData,
    loading,
    error,
    refresh: fetchMarketData
  };
};

/**
 * Custom hook for complete dashboard data (market + analysis)
 */
export const useDashboardData = (userEmail) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboard = async () => {
    if (!userEmail) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/api/portfolio/${userEmail}/dashboard`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch dashboard: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success) {
        setDashboardData(data);
        console.log('✅ Dashboard loaded');
      } else {
        throw new Error(data.error || 'Dashboard fetch failed');
      }
    } catch (err) {
      console.error('Error fetching dashboard:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, [userEmail]);

  return {
    dashboardData,
    loading,
    error,
    refresh: fetchDashboard
  };
};

export default usePortfolioAnalysis;