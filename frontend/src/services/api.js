/**
 * API Service Module
 * Centralized API calls for WealthWise frontend
 */

const API_BASE_URL = process.env.REACT_APP_API_URL;

class APIService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Helper method for making requests
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.error || `HTTP ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // ==================== AUTH ENDPOINTS ====================

  /**
   * Login user
   */
  async login(email, password) {
    return this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  /**
   * Complete onboarding
   */
  async completeOnboarding(onboardingData) {
    return this.request('/api/onboarding/complete', {
      method: 'POST',
      body: JSON.stringify(onboardingData),
    });
  }

  // ==================== USER ENDPOINTS ====================

  /**
   * Get user profile
   */
  async getUserProfile(email) {
    return this.request(`/api/user/${email}`);
  }

  // ==================== PORTFOLIO ENDPOINTS ====================

  /**
   * Get raw portfolio data
   */
  async getPortfolio(email) {
    return this.request(`/api/portfolio/${email}`);
  }

  /**
   * Get market report (live prices + portfolio metrics)
   */
  async getMarketReport(email) {
    return this.request(`/api/portfolio/${email}/market-report`);
  }

  /**
   * Get portfolio analysis (health score, recommendations)
   */
  async getPortfolioAnalysis(email) {
    return this.request(`/api/portfolio/${email}/analysis`);
  }

  /**
   * Get complete dashboard data
   */
  async getDashboardData(email) {
    return this.request(`/api/portfolio/${email}/dashboard`);
  }

  /**
   * Update portfolio
   */
  async updatePortfolio(email, portfolioUpdates) {
    return this.request(`/api/portfolio/${email}`, {
      method: 'PUT',
      body: JSON.stringify(portfolioUpdates),
    });
  }

  // ==================== STRAND AI ENDPOINTS ====================

  /**
   * Chat with AI advisor
   */
  async chat(userEmail, message, forceRefresh = false) {
    return this.request(`/api/chat?user_email=${userEmail}`, {
      method: 'POST',
      body: JSON.stringify({
        message,
        force_refresh: forceRefresh,
      }),
    });
  }

  /**
   * Ask a question about portfolio
   */
  async askAboutPortfolio(email, question) {
    return this.request(`/api/portfolio/${email}/ask`, {
      method: 'POST',
      body: JSON.stringify({ question }),
    });
  }

  /**
   * Get portfolio analysis v2 (Strand-powered)
   */
  async getPortfolioAnalysisV2(email) {
    return this.request(`/api/portfolio/${email}/analysis-v2`);
  }

  /**
   * Clear chat history
   */
  async clearChatHistory(email) {
    return this.request(`/api/chat/${email}/history`, {
      method: 'DELETE',
    });
  }

  /**
   * Get conversation summary
   */
  async getConversationSummary(email) {
    return this.request(`/api/chat/${email}/summary`);
  }

  // ==================== STATS ENDPOINTS ====================

  /**
   * Get market data API stats
   */
  async getMarketDataStats() {
    return this.request('/api/market-data/stats');
  }

  /**
   * Get Strand system stats
   */
  async getStrandStats() {
    return this.request('/api/strand/stats');
  }

  // ==================== HEALTH CHECK ====================

  /**
   * Health check
   */
  async healthCheck() {
    return this.request('/health');
  }

  /**
   * Get API info
   */
  async getAPIInfo() {
    return this.request('/');
  }
}

// Create singleton instance
const apiService = new APIService();

// Export both the class and the instance
export { APIService };
export default apiService;

// ==================== CONVENIENCE EXPORTS ====================

/**
 * Export individual methods for direct import
 * Usage: import { login, getMarketReport } from './services/api';
 */

export const login = (email, password) => apiService.login(email, password);
export const completeOnboarding = (data) => apiService.completeOnboarding(data);
export const getUserProfile = (email) => apiService.getUserProfile(email);
export const getPortfolio = (email) => apiService.getPortfolio(email);
export const getMarketReport = (email) => apiService.getMarketReport(email);
export const getPortfolioAnalysis = (email) => apiService.getPortfolioAnalysis(email);
export const getDashboardData = (email) => apiService.getDashboardData(email);
export const updatePortfolio = (email, updates) => apiService.updatePortfolio(email, updates);
export const chat = (email, message, refresh) => apiService.chat(email, message, refresh);
export const askAboutPortfolio = (email, question) => apiService.askAboutPortfolio(email, question);
export const getPortfolioAnalysisV2 = (email) => apiService.getPortfolioAnalysisV2(email);
export const clearChatHistory = (email) => apiService.clearChatHistory(email);
export const getConversationSummary = (email) => apiService.getConversationSummary(email);
export const getMarketDataStats = () => apiService.getMarketDataStats();
export const getStrandStats = () => apiService.getStrandStats();
export const healthCheck = () => apiService.healthCheck();
export const getAPIInfo = () => apiService.getAPIInfo();