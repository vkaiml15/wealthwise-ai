import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [portfolio, setPortfolio] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Helper function to normalize portfolio data from backend
  const normalizePortfolioFromBackend = (backendPortfolio, marketData = null) => {
    if (!backendPortfolio) return null;

    // If we have market data from the market-report endpoint, use it
    if (marketData && marketData.success) {
      const { portfolioMetrics, holdings, cashSavings } = marketData;
      
      // Calculate allocation from holdings
      const totalValue = portfolioMetrics.totalValue + (cashSavings || 0);
      const calculatePercentage = (value) => totalValue > 0 ? (value / totalValue * 100) : 0;

      // Group holdings by type for allocation
      const stocksValue = holdings
        .filter(h => h.type === 'stock')
        .reduce((sum, h) => sum + h.currentValue, 0);
      
      const bondsValue = holdings
        .filter(h => h.type === 'bond')
        .reduce((sum, h) => sum + h.currentValue, 0);
      
      const etfsValue = holdings
        .filter(h => h.type === 'etf')
        .reduce((sum, h) => sum + h.currentValue, 0);

      // Debug: Log what types we're seeing
      console.log('Holdings breakdown:', {
        total: holdings.length,
        stocks: holdings.filter(h => h.type === 'stock').length,
        bonds: holdings.filter(h => h.type === 'bond').length,
        etfs: holdings.filter(h => h.type === 'etf').length,
        stocksValue,
        bondsValue,
        etfsValue
      });

      // Calculate total invested amount from holdings
      const totalInvested = holdings.reduce((sum, h) => {
        return sum + (h.avgPrice * h.quantity);
      }, 0);

// Calculate returns
      const currentValue = portfolioMetrics.totalValue;
      const returnsValue = currentValue - totalInvested;
      const returnsPercentage = totalInvested > 0 
        ? ((currentValue - totalInvested) / totalInvested) * 100 
        : 0;

      const holdingsWithReturns = holdings.map(h => ({
          symbol: h.symbol,
          currentValue: h.currentValue,
          returnPercent: h.avgPrice > 0 ? ((h.currentPrice - h.avgPrice) / h.avgPrice * 100) : 0,
          returnValue: h.currentValue - (h.avgPrice * h.quantity),
          type: h.type
        }));

        // Sort by return percentage
        const sortedByReturn = [...holdingsWithReturns].sort((a, b) => b.returnPercent - a.returnPercent);

        // Get top 5 gainers and top 5 losers
        const topGainers = sortedByReturn.slice(0, 3);
        const topLosers = sortedByReturn.slice(-3).reverse();

      return {
        totalValue: totalValue,
        cashReserve: cashSavings || 0,
        invested: totalInvested,        // ✅ FIXED
        returns: {
          value: returnsValue,           // ✅ FIXED
          percentage: returnsPercentage  // ✅ FIXED
        },
        riskScore: 5,
        allocation: [
          { name: "Stocks", value: stocksValue, percentage: calculatePercentage(stocksValue), color: "#4F46E5" },
          { name: "ETFs", value: etfsValue, percentage: calculatePercentage(etfsValue), color: "#8B5CF6" },
          { name: "Bonds", value: bondsValue, percentage: calculatePercentage(bondsValue), color: "#10B981" },
          { name: "Cash", value: cashSavings, percentage: calculatePercentage(cashSavings), color: "#F59E0B" }
        ].filter(item => item.value > 0),
        performance: {
            topGainers,
            topLosers,
            summary: {
              totalInvested: totalInvested,
              currentValue: currentValue,
              totalReturn: returnsValue,
              returnPercent: returnsPercentage
            }
          },
        holdings: holdings.map(h => ({
          symbol: h.symbol,
          name: h.symbol,
          shares: h.quantity,
          avgPrice: h.avgPrice,
          currentPrice: h.currentPrice,
          value: h.currentValue,
          type: h.type,
          sector: h.sector
        })),
        userId: backendPortfolio.userId,
        createdAt: backendPortfolio.createdAt,
        updatedAt: backendPortfolio.updatedAt
      };
    }

    // Fallback: Basic normalization from raw portfolio data
    return {
      totalValue: 0,
      cashReserve: parseFloat(backendPortfolio.cashSavings || 0),
      invested: 0,
      returns: { value: 0, percentage: 0 },
      riskScore: 5,
      allocation: [],
      performance: [],
      holdings: [],
      userId: backendPortfolio.userId,
      createdAt: backendPortfolio.createdAt,
      updatedAt: backendPortfolio.updatedAt
    };
  };

  

  // Load portfolio data from backend
  const fetchPortfolioData = async (email) => {
    try {
      console.log('Fetching portfolio data for:', email);
      
      const marketResponse = await fetch(`${API_BASE_URL}/api/portfolio/${email}/market-report`);
      
      if (marketResponse.ok) {
        const marketData = await marketResponse.json();
        console.log('Market data received:', marketData);
        
        const portfolioResponse = await fetch(`${API_BASE_URL}/api/portfolio/${email}`);
        const portfolioData = portfolioResponse.ok ? await portfolioResponse.json() : null;
        
        const normalizedPortfolio = normalizePortfolioFromBackend(
          portfolioData?.portfolio,
          marketData
        );
        
        setPortfolio(normalizedPortfolio);
        localStorage.setItem('currentPortfolio', JSON.stringify(normalizedPortfolio));
        
        return normalizedPortfolio;
      } else {
        console.error('Failed to fetch market report');
        return null;
      }
    } catch (error) {
      console.error('Error fetching portfolio data:', error);
      return null;
    }
  };

  // Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = async () => {
      const savedUser = localStorage.getItem('currentUser');
      
      if (savedUser) {
        try {
          const user = JSON.parse(savedUser);
          setCurrentUser(user);
          setIsAuthenticated(true);
          
          if (user.hasPortfolio && user.email) {
            await fetchPortfolioData(user.email);
          }
        } catch (error) {
          console.error('Error initializing auth:', error);
          localStorage.removeItem('currentUser');
          localStorage.removeItem('currentPortfolio');
        }
      }
      
      setIsLoading(false);
    };

    initializeAuth();
  }, []);

  // Login function
  const login = async (email, password) => {
    try {
      console.log('Attempting login for:', email);
      
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('Login failed:', errorData);
        return { success: false, needsOnboarding: false };
      }

      const data = await response.json();
      console.log('Login successful:', data);
      
      setCurrentUser(data.user);
      setIsAuthenticated(true);
      localStorage.setItem('currentUser', JSON.stringify(data.user));
      
      if (data.user.hasPortfolio) {
        await fetchPortfolioData(data.user.email);
      }
      
      return { 
        success: true, 
        needsOnboarding: !data.user.hasPortfolio 
      };
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, needsOnboarding: false };
    }
  };

  // Logout function
  const logout = () => {
    setCurrentUser(null);
    setPortfolio(null);
    setIsAuthenticated(false);
    localStorage.removeItem('currentUser');
    localStorage.removeItem('currentPortfolio');
  };

  // Signup function
  const signup = () => {
    const newUser = {
      userId: null,
      isNewUser: true,
      hasPortfolio: false,
      createdAt: new Date().toISOString()
    };
    
    setCurrentUser(newUser);
    localStorage.setItem('currentUser', JSON.stringify(newUser));
    
    return { success: true };
  };

  // Complete onboarding function
  const completeOnboarding = async (profileData) => {
    try {
      console.log('Starting onboarding completion...');

      const payload = {
        userId: profileData.email,
        name: profileData.name,
        email: profileData.email,
        password: profileData.password,
        age: parseInt(profileData.age),
        riskTolerance: profileData.riskTolerance,
        investmentGoal: profileData.investmentGoal,
        investmentHorizon: profileData.investmentHorizon,
        initialInvestment: parseFloat(profileData.initialInvestment || 0),
        monthlyContribution: parseFloat(profileData.monthlyContribution || 0),
        cashSavings: parseFloat(profileData.cashSavings || 0),
        bonds: (profileData.bonds || []).map(b => ({
          symbol: b.symbol,
          quantity: parseFloat(b.quantity),
          avgPrice: parseFloat(b.avgPrice)
        })),
        stocks: (profileData.stocks || []).map(s => ({
          symbol: s.symbol,
          quantity: parseFloat(s.quantity),
          avgPrice: parseFloat(s.avgPrice)
        })),
        etfs: (profileData.etfs || []).map(e => ({
          symbol: e.symbol,
          quantity: parseFloat(e.quantity),
          avgPrice: parseFloat(e.avgPrice)
        })),
        timestamp: new Date().toISOString()
      };

      console.log('Sending onboarding request:', payload);

      const response = await fetch(`${API_BASE_URL}/api/onboarding/complete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Onboarding failed:', errorText);
        throw new Error(`Failed to complete onboarding: ${response.status}`);
      }

      const result = await response.json();
      console.log('✅ Onboarding successful:', result);

      setCurrentUser(result.user);
      setIsAuthenticated(true);
      localStorage.setItem('currentUser', JSON.stringify(result.user));

      await fetchPortfolioData(result.user.email);

      return { success: true };
    } catch (error) {
      console.error('❌ Onboarding error:', error);
      return { 
        success: false, 
        error: error.message || 'Failed to complete onboarding'
      };
    }
  };

  // Update user profile
  const updateUserProfile = (updates) => {
    const updatedUser = {
      ...currentUser,
      ...updates
    };
    setCurrentUser(updatedUser);
    localStorage.setItem('currentUser', JSON.stringify(updatedUser));
  };

  // Refresh portfolio data
  const refreshPortfolio = async () => {
    if (currentUser?.email && currentUser?.hasPortfolio) {
      return await fetchPortfolioData(currentUser.email);
    }
    return null;
  };

  const value = {
    currentUser,
    portfolio,
    isAuthenticated,
    isLoading,
    login,
    logout,
    signup,
    completeOnboarding,
    updateUserProfile,
    refreshPortfolio,
    fetchPortfolioData
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;