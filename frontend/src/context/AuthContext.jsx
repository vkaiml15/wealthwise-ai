import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

// API Base URL - Change this if your backend runs on different port
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

  // Check for existing session on mount
  useEffect(() => {
    const storedUser = localStorage.getItem('currentUser');
    const storedPortfolio = localStorage.getItem('currentPortfolio');
    
    if (storedUser) {
      try {
        const user = JSON.parse(storedUser);
        setCurrentUser(user);
        
        // Only set authenticated if user has completed onboarding
        if (user.hasPortfolio) {
          setIsAuthenticated(true);
        }
        
        // Load portfolio if exists
        if (storedPortfolio) {
          const userPortfolio = JSON.parse(storedPortfolio);
          setPortfolio(userPortfolio);
        }
      } catch (error) {
        console.error('Error loading stored user:', error);
        localStorage.removeItem('currentUser');
        localStorage.removeItem('currentPortfolio');
      }
    }
    setIsLoading(false);
  }, []);

  // Login function - connects to backend API
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

      console.log('Login response status:', response.status);

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
      
      // Load portfolio if exists
      if (data.portfolio) {
        setPortfolio(data.portfolio);
        localStorage.setItem('currentPortfolio', JSON.stringify(data.portfolio));
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

  // Signup/Register function - creates new user for onboarding
  const signup = () => {
    const newUser = {
      userId: null, // Will be set to email during onboarding
      isNewUser: true,
      hasPortfolio: false,
      createdAt: new Date().toISOString()
    };
    
    setCurrentUser(newUser);
    localStorage.setItem('currentUser', JSON.stringify(newUser));
    
    return { success: true };
  };

  // Logout function
  const logout = () => {
    setCurrentUser(null);
    setPortfolio(null);
    setIsAuthenticated(false);
    localStorage.removeItem('currentUser');
    localStorage.removeItem('currentPortfolio');
  };

  // Complete onboarding - Save only user input to DynamoDB
  const completeOnboarding = async (profileData) => {
    try {
      console.log('Starting onboarding completion...');
      console.log('Profile data:', profileData);

      // Prepare data for backend API - ONLY what user entered
      const apiPayload = {
        userId: profileData.email, // Email as user ID
        name: profileData.name,
        email: profileData.email,
        password: profileData.password,
        age: profileData.age,
        riskTolerance: profileData.riskTolerance,
        investmentGoal: profileData.investmentGoal,
        investmentHorizon: profileData.investmentHorizon,
        initialInvestment: profileData.initialInvestment,
        monthlyContribution: profileData.monthlyContribution,
        cashSavings: profileData.cashSavings,
        bonds: profileData.bonds,
        stocks: profileData.stocks,
        etfs: profileData.etfs,
        timestamp: new Date().toISOString()
      };

      console.log('Sending to backend:', `${API_BASE_URL}/api/onboarding/complete`);
      console.log('Payload:', JSON.stringify(apiPayload, null, 2));

      // Save to backend API
      const response = await fetch(`${API_BASE_URL}/api/onboarding/complete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(apiPayload)
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Backend error response:', errorText);
        throw new Error(`Failed to save onboarding data: ${response.status} ${errorText}`);
      }

      const result = await response.json();
      console.log('✅ Successfully saved to backend:', result);

      // Update local state
      const updatedUser = {
        ...currentUser,
        userId: profileData.email,
        name: profileData.name,
        email: profileData.email,
        password: profileData.password,
        age: profileData.age,
        riskTolerance: profileData.riskTolerance,
        investmentGoal: profileData.investmentGoal,
        investmentHorizon: profileData.investmentHorizon,
        monthlyContribution: profileData.monthlyContribution,
        hasPortfolio: true
      };
      
      setCurrentUser(updatedUser);
      setIsAuthenticated(true);
      localStorage.setItem('currentUser', JSON.stringify(updatedUser));

      return { success: true, data: result };
    } catch (error) {
      console.error('❌ Error completing onboarding:', error);
      return { success: false, error: error.message };
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

  // Update portfolio
  const updatePortfolio = (updates) => {
    const updatedPortfolio = {
      ...portfolio,
      ...updates
    };
    setPortfolio(updatedPortfolio);
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
    updatePortfolio
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Helper functions
const getBondName = (symbol) => {
  const bondNames = {
    'US_TREASURY_10Y': 'US Treasury 10Y',
    'US_TREASURY_30Y': 'US Treasury 30Y',
    'CORPORATE_AAA': 'Corporate AAA Bond',
    'MUNICIPAL': 'Municipal Bond',
    'HIGH_YIELD': 'High Yield Corporate'
  };
  return bondNames[symbol] || symbol;
};

const getStockName = (symbol) => {
  const stockNames = {
    'AAPL': 'Apple Inc.',
    'MSFT': 'Microsoft Corporation',
    'GOOGL': 'Alphabet Inc.',
    'AMZN': 'Amazon.com Inc.',
    'TSLA': 'Tesla Inc.',
    'NVDA': 'NVIDIA Corporation',
    'JPM': 'JPMorgan Chase & Co.',
    'V': 'Visa Inc.',
    'JNJ': 'Johnson & Johnson',
    'WMT': 'Walmart Inc.'
  };
  return stockNames[symbol] || symbol;
};

const getETFName = (symbol) => {
  const etfNames = {
    'SPY': 'SPDR S&P 500 ETF',
    'QQQ': 'Invesco QQQ Trust',
    'VTI': 'Vanguard Total Stock Market ETF',
    'IWM': 'iShares Russell 2000 ETF',
    'EEM': 'iShares MSCI Emerging Markets ETF',
    'VEA': 'Vanguard FTSE Developed Markets ETF',
    'AGG': 'iShares Core US Aggregate Bond ETF'
  };
  return etfNames[symbol] || symbol;
};

export default AuthContext;