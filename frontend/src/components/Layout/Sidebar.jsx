import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  MessageSquare,
  PieChart,
  TrendingUp,
  Settings,
  BarChart3,
  Shield,
  Target,
  Sparkles,
  X,
  RefreshCw
} from 'lucide-react';

const Sidebar = ({ isOpen, setIsOpen }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [quickStats, setQuickStats] = useState({
    riskScore: '...',
    riskLabel: '...',
    totalHoldings: '...',
    diversity: '...',
    loading: true
  });
  const [userEmail, setUserEmail] = useState(null);

  const menuItems = [
    {
      icon: LayoutDashboard,
      label: 'Dashboard',
      path: '/dashboard',
      color: 'indigo'
    },
    {
      icon: MessageSquare,
      label: 'AI Advisor',
      path: '/chat',
      color: 'purple',
      badge: 'AI'
    },
    {
      icon: TrendingUp,
      label: 'Market Trends',
      path: '/market',
      color: 'green'
    },
    {
      icon: Target,
      label: 'Recommendations',
      path: '/recommendations',
      color: 'orange'
    },
    {
      icon: Shield,
      label: 'Risk Analysis',
      path: '/risk',
      color: 'red'
    }
  ];

  const bottomMenuItems = [
    {
      icon: Settings,
      label: 'Settings',
      path: '/settings',
      color: 'gray'
    }
  ];

  // Get user email from localStorage - check multiple possible keys
  useEffect(() => {
    const getUserEmail = () => {
      // Try multiple possible localStorage keys
      let email = localStorage.getItem("userEmail");
      
      if (!email) {
        // Try getting from currentUser object
        const currentUser = localStorage.getItem('currentUser');
        if (currentUser) {
          try {
            const user = JSON.parse(currentUser);
            email = user.email;
          } catch (e) {
            console.error('Error parsing currentUser:', e);
          }
        }
      }
      
      if (!email) {
        // Try other common keys
        email = localStorage.getItem("email") || localStorage.getItem("user_email");
      }
      
      return email;
    };

    const email = getUserEmail();
    console.log('Found email in localStorage:', email);
    
    if (email) {
      setUserEmail(email);
    } else {
      console.warn('No email found in localStorage. Checking all keys:', Object.keys(localStorage));
    }

    // Listen for storage changes (in case email is set after mount)
    const handleStorageChange = () => {
      const newEmail = getUserEmail();
      if (newEmail && newEmail !== userEmail) {
        console.log('Email updated via storage event:', newEmail);
        setUserEmail(newEmail);
      }
    };

    window.addEventListener('storage', handleStorageChange);
    
    // Also check periodically in case storage event doesn't fire
    const interval = setInterval(() => {
      const newEmail = getUserEmail();
      if (newEmail && newEmail !== userEmail) {
        console.log('Email found via interval check:', newEmail);
        setUserEmail(newEmail);
        clearInterval(interval);
      }
    }, 500);

    // Clean up after 5 seconds
    const timeout = setTimeout(() => {
      clearInterval(interval);
    }, 5000);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      clearInterval(interval);
      clearTimeout(timeout);
    };
  }, [userEmail]);

  // Fetch quick stats when userEmail is available
  useEffect(() => {
    if (userEmail) {
      fetchQuickStats();
    }
  }, [userEmail]);

  const fetchQuickStats = async () => {
    if (!userEmail) {
      console.log('No user email available');
      return;
    }

    setQuickStats(prev => ({ ...prev, loading: true }));

    try {
      console.log('Fetching stats for:', userEmail);

      // Fetch user data (including risk analysis)
      const userResponse = await fetch(`${process.env.REACT_APP_API_URL}/api/user/${userEmail}`);
      
      if (!userResponse.ok) {
        throw new Error(`User API returned ${userResponse.status}`);
      }
      
      const userData = await userResponse.json();
      console.log('User data:', userData);

      // Fetch portfolio data
      const portfolioResponse = await fetch(`${process.env.REACT_APP_API_URL}/api/portfolio/${userEmail}`);
      
      if (!portfolioResponse.ok) {
        throw new Error(`Portfolio API returned ${portfolioResponse.status}`);
      }
      
      const portfolioData = await portfolioResponse.json();
      console.log('Portfolio data:', portfolioData);

      // Calculate total holdings
      const stocksCount = portfolioData.portfolio?.stocks?.length || 0;
      const bondsCount = portfolioData.portfolio?.bonds?.length || 0;
      const etfsCount = portfolioData.portfolio?.etfs?.length || 0;
      const totalHoldings = stocksCount + bondsCount + etfsCount;

      // Calculate diversity (based on asset type distribution)
      let diversity = 'Low';
      const assetTypes = [stocksCount > 0, bondsCount > 0, etfsCount > 0].filter(Boolean).length;

      if (assetTypes >= 3) {
        diversity = 'High';
      } else if (assetTypes === 2) {
        diversity = 'Medium';
      }

      // Get risk score from analysis
      const riskScore = userData.user?.riskAnalysis?.riskScore || 'N/A';
      const riskLabel = userData.user?.riskAnalysis?.riskLabel || 'Not analyzed';

      setQuickStats({
        riskScore: typeof riskScore === 'number' ? `${riskScore}/10` : riskScore,
        riskLabel: riskLabel,
        totalHoldings: totalHoldings,
        stocksCount,
        bondsCount,
        etfsCount,
        diversity: diversity,
        loading: false
      });

    } catch (error) {
      console.error('Error fetching quick stats:', error);
      setQuickStats({
        riskScore: 'N/A',
        riskLabel: 'Error',
        totalHoldings: 'N/A',
        diversity: 'N/A',
        loading: false
      });
    }
  };

  const handleNavigation = (path) => {
    navigate(path);
    // Close sidebar on mobile after navigation
    if (window.innerWidth < 1024) {
      setIsOpen(false);
    }
  };

  const isActive = (path) => location.pathname === path;

  // Get risk score color based on label
  const getRiskColor = (label) => {
    switch (label?.toLowerCase()) {
      case 'conservative':
        return 'text-green-300';
      case 'moderate':
        return 'text-yellow-300';
      case 'aggressive':
        return 'text-red-300';
      default:
        return 'text-white';
    }
  };

  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setIsOpen(false)}
        ></div>
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:static inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 transform transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Logo Section */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-gray-900">WealthWise AI</h1>
                <p className="text-xs text-gray-500">Investment Intelligence</p>
              </div>
            </div>
            {/* Close button for mobile */}
            <button
              onClick={() => setIsOpen(false)}
              className="lg:hidden p-1 rounded-lg hover:bg-gray-100"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>

          {/* Main Menu */}
          <nav className="flex-1 px-4 py-6 overflow-y-auto">
            <div className="space-y-1">
              {menuItems.map((item) => {
                const active = isActive(item.path);
                return (
                  <button
                    key={item.path}
                    onClick={() => handleNavigation(item.path)}
                    className={`w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all ${
                      active
                        ? 'bg-gradient-to-r from-indigo-50 to-purple-50 text-indigo-600 shadow-sm'
                        : 'text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <item.icon className={`w-5 h-5 ${active ? 'text-indigo-600' : 'text-gray-400'}`} />
                      <span className={`font-medium ${active ? 'text-indigo-600' : 'text-gray-700'}`}>
                        {item.label}
                      </span>
                    </div>
                    {item.badge && (
                      <span className="px-2 py-0.5 bg-gradient-to-r from-indigo-500 to-purple-500 text-white text-xs font-bold rounded-full">
                        {item.badge}
                      </span>
                    )}
                    {active && (
                      <div className="w-1 h-8 bg-indigo-600 rounded-full absolute right-0"></div>
                    )}
                  </button>
                );
              })}
            </div>

            {/* Divider */}
            <div className="my-6 border-t border-gray-200"></div>

            {/* Quick Stats Card */}
            <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl p-4 text-white mb-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <BarChart3 className="w-5 h-5" />
                  <span className="font-semibold text-sm">Quick Stats</span>
                </div>
                <button
                  onClick={fetchQuickStats}
                  className="p-1 hover:bg-white/20 rounded-lg transition-colors"
                  title="Refresh stats"
                  disabled={!userEmail || quickStats.loading}
                >
                  <RefreshCw className={`w-4 h-4 ${quickStats.loading ? 'animate-spin' : ''}`} />
                </button>
              </div>

              {!userEmail ? (
                <div className="text-center py-4">
                  <p className="text-sm text-indigo-100 mb-3">Unable to load user data</p>
                  <button
                    onClick={() => {
                      // Try to get email again
                      const email = localStorage.getItem("userEmail") || 
                                   localStorage.getItem("email") ||
                                   (localStorage.getItem('currentUser') && JSON.parse(localStorage.getItem('currentUser')).email);
                      if (email) {
                        setUserEmail(email);
                      } else {
                        console.error('Still no email found. localStorage keys:', Object.keys(localStorage));
                        alert('Please refresh the page or log in again.');
                      }
                    }}
                    className="px-3 py-1.5 bg-white/20 hover:bg-white/30 rounded-lg text-xs font-medium transition-colors"
                  >
                    Retry
                  </button>
                </div>
              ) : quickStats.loading ? (
                <div className="space-y-2">
                  <div className="h-4 bg-white/20 rounded animate-pulse"></div>
                  <div className="h-4 bg-white/20 rounded animate-pulse"></div>
                  <div className="h-4 bg-white/20 rounded animate-pulse"></div>
                </div>
              ) : (
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-indigo-100">Risk Score</span>
                    <span className={`text-sm font-bold ${getRiskColor(quickStats.riskLabel)}`}>
                      {quickStats.riskScore}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-indigo-100">Risk Profile</span>
                    <span className="text-sm font-bold">{quickStats.riskLabel}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-indigo-100">Holdings</span>
                    <span className="text-sm font-bold">
                      {quickStats.totalHoldings} {quickStats.totalHoldings === 1 ? 'asset' : 'assets'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-indigo-100">Diversity</span>
                    <span className="text-sm font-bold">{quickStats.diversity}</span>
                  </div>

                  {/* Asset breakdown tooltip */}
                  {quickStats.totalHoldings > 0 && (
                    <div className="pt-2 mt-2 border-t border-white/20">
                      <div className="text-xs text-indigo-100 space-y-1">
                        {quickStats.stocksCount > 0 && (
                          <div className="flex justify-between">
                            <span>Stocks:</span>
                            <span className="font-semibold">{quickStats.stocksCount}</span>
                          </div>
                        )}
                        {quickStats.bondsCount > 0 && (
                          <div className="flex justify-between">
                            <span>Bonds:</span>
                            <span className="font-semibold">{quickStats.bondsCount}</span>
                          </div>
                        )}
                        {quickStats.etfsCount > 0 && (
                          <div className="flex justify-between">
                            <span>ETFs:</span>
                            <span className="font-semibold">{quickStats.etfsCount}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </nav>

          {/* Bottom Menu */}
          <div className="border-t border-gray-200 p-4">
            {bottomMenuItems.map((item) => {
              const active = isActive(item.path);
              return (
                <button
                  key={item.path}
                  onClick={() => handleNavigation(item.path)}
                  className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all ${
                    active
                      ? 'bg-gray-100 text-gray-900'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <item.icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
