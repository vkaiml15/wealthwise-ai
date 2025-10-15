import React, { createContext, useContext, useState, useEffect } from 'react';
import { mockUsers } from '../data/mockUsers';
import { mockPortfolios } from '../data/mockPortfolios';

const AuthContext = createContext();

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
    if (storedUser) {
      try {
        const user = JSON.parse(storedUser);
        setCurrentUser(user);
        setIsAuthenticated(true);
        
        // Load portfolio if user has one
        if (user.hasPortfolio && user.userId) {
          const userPortfolio = mockPortfolios[user.userId];
          setPortfolio(userPortfolio || null);
        }
      } catch (error) {
        console.error('Error loading stored user:', error);
        localStorage.removeItem('currentUser');
      }
    }
    setIsLoading(false);
  }, []);

  // Login function
  const login = (userId, password) => {
    // Check in existing users
    const existingUser = mockUsers.existing.find(
      (u) => u.userId === userId && u.password === password
    );

    if (existingUser) {
      setCurrentUser(existingUser);
      setIsAuthenticated(true);
      localStorage.setItem('currentUser', JSON.stringify(existingUser));
      
      // Load portfolio
      const userPortfolio = mockPortfolios[userId];
      setPortfolio(userPortfolio || null);
      
      return { success: true, needsOnboarding: false };
    }

    // Check in new users
    const newUser = mockUsers.new.find(
      (u) => u.userId === userId && u.password === password
    );

    if (newUser) {
      setCurrentUser(newUser);
      setIsAuthenticated(true);
      localStorage.setItem('currentUser', JSON.stringify(newUser));
      
      return { success: true, needsOnboarding: true };
    }

    return { success: false, needsOnboarding: false };
  };

  // Logout function
  const logout = () => {
    setCurrentUser(null);
    setPortfolio(null);
    setIsAuthenticated(false);
    localStorage.removeItem('currentUser');
  };

  // Complete onboarding
  const completeOnboarding = (profileData) => {
    const updatedUser = {
      ...currentUser,
      ...profileData,
      hasPortfolio: true
    };

    // Create a basic portfolio for the new user
    const newPortfolio = {
      totalValue: Number(profileData.initialInvestment) || 0,
      cashReserve: Number(profileData.initialInvestment) * 0.1 || 0,
      invested: Number(profileData.initialInvestment) * 0.9 || 0,
      returns: {
        value: 0,
        percentage: 0
      },
      riskScore: 
        profileData.riskTolerance === 'conservative' ? 3.5 :
        profileData.riskTolerance === 'aggressive' ? 8.5 : 6.0,
      allocation: [
        { name: "Cash", value: Number(profileData.initialInvestment) * 0.1, percentage: 10, color: "#F59E0B" },
        { name: "Bonds", value: Number(profileData.initialInvestment) * 0.3, percentage: 30, color: "#10B981" },
        { name: "Stocks", value: Number(profileData.initialInvestment) * 0.5, percentage: 50, color: "#4F46E5" },
        { name: "ETFs", value: Number(profileData.initialInvestment) * 0.1, percentage: 10, color: "#8B5CF6" }
      ],
      performance: [
        { month: "Week 1", value: Number(profileData.initialInvestment) }
      ],
      holdings: []
    };

    setCurrentUser(updatedUser);
    setPortfolio(newPortfolio);
    localStorage.setItem('currentUser', JSON.stringify(updatedUser));
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

  // Update portfolio (for future use)
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
    completeOnboarding,
    updateUserProfile,
    updatePortfolio
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;