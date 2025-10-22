import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { 
  User, 
  Mail, 
  Shield, 
  Bell, 
  Lock, 
  Save,
  Check,
  AlertCircle,
  Calendar,
  Target,
  IndianRupeeIcon,
  Clock,
  Briefcase,
  Plus,
  Trash2,
  Edit2,
  TrendingUp,
  PieChart,
  Wallet,
  AlertTriangle
} from 'lucide-react';

const Settings = () => {
  const { currentUser, updateUserProfile } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [saveStatus, setSaveStatus] = useState(null);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [showUnsavedWarning, setShowUnsavedWarning] = useState(false);
  const [pendingTab, setPendingTab] = useState(null);
  
  // Dropdown options for portfolio assets
  const bondOptions = [
    { value: 'IDFC_GILT', label: 'IDFC Gilt Fund - Government Securities' },
    { value: 'ICICI_GILT', label: 'ICICI Prudential Gilt Fund' },
    { value: 'SBI_GILT', label: 'SBI Magnum Gilt Fund' },
    { value: 'HDFC_SHORT_DEBT', label: 'HDFC Short Term Debt Fund' },
    { value: 'ICICI_SHORT_DEBT', label: 'ICICI Prudential Short Term Fund' },
    { value: 'SBI_SHORT_DEBT', label: 'SBI Short Term Debt Fund' },
    { value: 'HDFC_CORP_BOND', label: 'HDFC Corporate Bond Fund' },
    { value: 'ICICI_CORP_BOND', label: 'ICICI Corporate Bond Fund' },
    { value: 'AXIS_CORP_BOND', label: 'Axis Corporate Debt Fund' },
    { value: 'HDFC_LIQUID', label: 'HDFC Liquid Fund' },
    { value: 'ICICI_LIQUID', label: 'ICICI Liquid Fund' },
    { value: 'SBI_LIQUID', label: 'SBI Liquid Fund' },
    { value: 'AXIS_BANKING_DEBT', label: 'Axis Banking & PSU Debt Fund' },
    { value: 'ICICI_BANKING_DEBT', label: 'ICICI Banking & PSU Debt Fund' }
  ];

  const stockOptions = [
    { value: 'RELIANCE.NS', label: 'Reliance Industries' },
    { value: 'TCS.NS', label: 'Tata Consultancy Services' },
    { value: 'INFY.NS', label: 'Infosys' },
    { value: 'HDFCBANK.NS', label: 'HDFC Bank' },
    { value: 'ICICIBANK.NS', label: 'ICICI Bank' },
    { value: 'KOTAKBANK.NS', label: 'Kotak Mahindra Bank' },
    { value: 'BHARTIARTL.NS', label: 'Bharti Airtel' },
    { value: 'ITC.NS', label: 'ITC Limited' },
    { value: 'HINDUNILVR.NS', label: 'Hindustan Unilever' },
    { value: 'SBIN.NS', label: 'State Bank of India' },
    { value: 'LT.NS', label: 'Larsen & Toubro' },
    { value: 'ASIANPAINT.NS', label: 'Asian Paints' },
    { value: 'MARUTI.NS', label: 'Maruti Suzuki' },
    { value: 'TITAN.NS', label: 'Titan Company' },
    { value: 'SUNPHARMA.NS', label: 'Sun Pharmaceutical' },
    { value: 'WIPRO.NS', label: 'Wipro' },
    { value: 'AXISBANK.NS', label: 'Axis Bank' },
    { value: 'ULTRACEMCO.NS', label: 'UltraTech Cement' },
    { value: 'NESTLEIND.NS', label: 'Nestle India' },
    { value: 'TATASTEEL.NS', label: 'Tata Steel' },
    { value: 'POWERGRID.NS', label: 'Power Grid Corporation' },
    { value: 'NTPC.NS', label: 'NTPC Limited' },
    { value: 'ONGC.NS', label: 'Oil and Natural Gas Corporation' },
    { value: 'TECHM.NS', label: 'Tech Mahindra' },
    { value: 'HCLTECH.NS', label: 'HCL Technologies' },
    { value: 'BAJFINANCE.NS', label: 'Bajaj Finance' },
    { value: 'DRREDDY.NS', label: 'Dr. Reddy\'s Laboratories' },
    { value: 'CIPLA.NS', label: 'Cipla' },
    { value: 'DIVISLAB.NS', label: 'Divi\'s Laboratories' },
    { value: 'EICHERMOT.NS', label: 'Eicher Motors' },
    { value: 'HEROMOTOCO.NS', label: 'Hero MotoCorp' },
    { value: 'BAJAJFINSV.NS', label: 'Bajaj Finserv' },
    { value: 'M&M.NS', label: 'Mahindra & Mahindra' }
  ];

  const etfOptions = [
    { value: 'NIFTYBEES.NS', label: 'Nifty BeES - Nifty 50 Index' },
    { value: 'JUNIORBEES.NS', label: 'Junior BeES - Nifty Next 50' },
    { value: 'BANKBEES.NS', label: 'Bank BeES - Banking Sector' },
    { value: 'ITBEES.NS', label: 'IT BeES - Technology Sector' },
    { value: 'GOLDBEES.NS', label: 'Gold BeES - Gold ETF' },
    { value: 'LIQUIDBEES.NS', label: 'Liquid BeES - Overnight Fund' },
    { value: 'CPSEETF.NS', label: 'CPSE ETF - Public Sector Companies' }
  ];
  
  // Profile form state
  const [profileForm, setProfileForm] = useState({
    name: currentUser?.name || '',
    email: currentUser?.email || '',
    age: currentUser?.age || '',
    phone: currentUser?.phone || ''
  });

  // Investment preferences state
  const [preferencesForm, setPreferencesForm] = useState({
    riskTolerance: currentUser?.riskTolerance || 'moderate',
    investmentGoal: currentUser?.investmentGoal || 'growth',
    investmentHorizon: currentUser?.investmentHorizon || '5-10',
    monthlyContribution: currentUser?.monthlyContribution || ''
  });

  // Portfolio management state
  const [portfolioForm, setPortfolioForm] = useState({
    cashSavings: 0,
    bonds: [],
    stocks: [],
    etfs: []
  });
  
  const [originalPortfolio, setOriginalPortfolio] = useState(null);
  const [portfolioLoading, setPortfolioLoading] = useState(false);

  // Notification preferences state
  const [notificationForm, setNotificationForm] = useState({
    emailNotifications: true,
    pushNotifications: true,
    portfolioAlerts: true,
    marketNews: true,
    weeklyReports: true,
    recommendations: true
  });

  // Security form state
  const [securityForm, setSecurityForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  const [errors, setErrors] = useState({});

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'portfolio', label: 'Portfolio', icon: Briefcase },
    { id: 'preferences', label: 'Investment Preferences', icon: Target },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Shield }
  ];

  // Load existing portfolio data when component mounts
  useEffect(() => {
    const loadPortfolioData = async () => {
      if (!currentUser?.email) return;
      
      setPortfolioLoading(true);
      try {
        const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
        const response = await fetch(`${API_BASE_URL}/api/portfolio/${currentUser.email}`);
        
        if (response.ok) {
          const data = await response.json();
          if (data.success && data.portfolio) {
            const portfolioData = {
              cashSavings: data.portfolio.cashSavings || 0,
              bonds: data.portfolio.bonds || [],
              stocks: data.portfolio.stocks || [],
              etfs: data.portfolio.etfs || []
            };
            setPortfolioForm(portfolioData);
            setOriginalPortfolio(JSON.parse(JSON.stringify(portfolioData)));
            console.log('Loaded existing portfolio:', data.portfolio);
          }
        }
      } catch (error) {
        console.error('Error loading portfolio:', error);
        // If load fails, user can still add new holdings from scratch
      } finally {
        setPortfolioLoading(false);
      }
    };

    loadPortfolioData();
  }, [currentUser]);

  // Detect unsaved changes for portfolio tab
  useEffect(() => {
    if (activeTab === 'portfolio' && originalPortfolio) {
      const hasChanges = JSON.stringify(portfolioForm) !== JSON.stringify(originalPortfolio);
      setHasUnsavedChanges(hasChanges);
    }
  }, [portfolioForm, originalPortfolio, activeTab]);

  // Warn before leaving page with unsaved changes
  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = '';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [hasUnsavedChanges]);

  const handleTabChange = (tabId) => {
    if (hasUnsavedChanges && activeTab === 'portfolio') {
      setShowUnsavedWarning(true);
      setPendingTab(tabId);
    } else {
      setActiveTab(tabId);
      setHasUnsavedChanges(false);
    }
  };

  const confirmTabChange = () => {
    setActiveTab(pendingTab);
    setShowUnsavedWarning(false);
    setHasUnsavedChanges(false);
    setPendingTab(null);
    // Reset portfolio to original
    if (originalPortfolio) {
      setPortfolioForm(JSON.parse(JSON.stringify(originalPortfolio)));
    }
  };

  const cancelTabChange = () => {
    setShowUnsavedWarning(false);
    setPendingTab(null);
  };

  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfileForm(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handlePreferencesChange = (e) => {
    const { name, value } = e.target;
    setPreferencesForm(prev => ({ ...prev, [name]: value }));
  };

  const handleNotificationChange = (name) => {
    setNotificationForm(prev => ({ ...prev, [name]: !prev[name] }));
  };

  const handleSecurityChange = (e) => {
    const { name, value } = e.target;
    setSecurityForm(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  // Validation: Check for duplicates
  const hasDuplicates = (holdings) => {
    const symbols = holdings.map(h => h.symbol).filter(Boolean);
    return symbols.length !== new Set(symbols).size;
  };

  // Validation: Check for invalid values
  const hasInvalidValues = (holdings) => {
    const MAX_QUANTITY = 1000000;
    const MAX_PRICE = 10000000;
    
    return holdings.some(h => {
      const qty = parseFloat(h.quantity);
      const price = parseFloat(h.avgPrice);
      return qty > MAX_QUANTITY || price > MAX_PRICE || qty < 0 || price < 0;
    });
  };

  // Holdings management functions
  const addHolding = (type) => {
    const newHolding = { symbol: '', quantity: '', avgPrice: '' };
    setPortfolioForm(prev => ({
      ...prev,
      [type]: [...prev[type], newHolding]
    }));
  };

  const updateHolding = (type, index, field, value) => {
    setPortfolioForm(prev => ({
      ...prev,
      [type]: prev[type].map((item, i) => 
        i === index ? { ...item, [field]: value } : item
      )
    }));
  };

  const removeHolding = (type, index) => {
    setPortfolioForm(prev => ({
      ...prev,
      [type]: prev[type].filter((_, i) => i !== index)
    }));
  };

  const validateProfile = () => {
    const newErrors = {};
    if (!profileForm.name.trim()) {
      newErrors.name = 'Name is required';
    }
    if (!profileForm.email.trim() || !/\S+@\S+\.\S+/.test(profileForm.email)) {
      newErrors.email = 'Valid email is required';
    }
    if (profileForm.age && (profileForm.age < 18 || profileForm.age > 100)) {
      newErrors.age = 'Age must be between 18 and 100';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateSecurity = () => {
    const newErrors = {};
    if (!securityForm.currentPassword) {
      newErrors.currentPassword = 'Current password is required';
    }
    if (!securityForm.newPassword || securityForm.newPassword.length < 8) {
      newErrors.newPassword = 'Password must be at least 8 characters';
    }
    if (securityForm.newPassword !== securityForm.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validatePortfolio = () => {
    const newErrors = {};
    
    // Check for duplicates in each category
    if (hasDuplicates(portfolioForm.bonds)) {
      newErrors.bonds = 'Duplicate bond entries detected. Please remove duplicates.';
    }
    if (hasDuplicates(portfolioForm.stocks)) {
      newErrors.stocks = 'Duplicate stock entries detected. Please remove duplicates.';
    }
    if (hasDuplicates(portfolioForm.etfs)) {
      newErrors.etfs = 'Duplicate ETF entries detected. Please remove duplicates.';
    }
    
    // Check for invalid values
    if (hasInvalidValues(portfolioForm.bonds)) {
      newErrors.bondsValues = 'Invalid quantity or price values in bonds (max: 1M quantity, 10M price)';
    }
    if (hasInvalidValues(portfolioForm.stocks)) {
      newErrors.stocksValues = 'Invalid quantity or price values in stocks (max: 1M quantity, 10M price)';
    }
    if (hasInvalidValues(portfolioForm.etfs)) {
      newErrors.etfsValues = 'Invalid quantity or price values in ETFs (max: 1M quantity, 10M price)';
    }
    
    // Check cash savings
    if (portfolioForm.cashSavings < 0 || portfolioForm.cashSavings > 100000000) {
      newErrors.cashSavings = 'Cash savings must be between 0 and 100M';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = async () => {
    try {
      if (activeTab === 'profile') {
        if (!validateProfile()) return;
        updateUserProfile(profileForm);
      } else if (activeTab === 'portfolio') {
        // Validate portfolio before saving
        if (!validatePortfolio()) {
          setSaveStatus('error');
          setTimeout(() => setSaveStatus(null), 5000);
          return;
        }

        // Format portfolio data to match backend structure
        const portfolioUpdate = {
          cashSavings: parseFloat(portfolioForm.cashSavings) || 0,
          bonds: portfolioForm.bonds
            .filter(b => b.symbol && b.quantity && b.avgPrice) // Only include complete entries
            .map(b => ({
              symbol: b.symbol,
              quantity: parseFloat(b.quantity) || 0,
              avgPrice: parseFloat(b.avgPrice) || 0
            })),
          stocks: portfolioForm.stocks
            .filter(s => s.symbol && s.quantity && s.avgPrice)
            .map(s => ({
              symbol: s.symbol,
              quantity: parseFloat(s.quantity) || 0,
              avgPrice: parseFloat(s.avgPrice) || 0
            })),
          etfs: portfolioForm.etfs
            .filter(e => e.symbol && e.quantity && e.avgPrice)
            .map(e => ({
              symbol: e.symbol,
              quantity: parseFloat(e.quantity) || 0,
              avgPrice: parseFloat(e.avgPrice) || 0
            }))
        };
        
        // Call the backend API to update portfolio
        const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
        
        console.log('Updating portfolio for:', currentUser.email);
        console.log('Portfolio data:', portfolioUpdate);
        
        const response = await fetch(`${API_BASE_URL}/api/portfolio/${currentUser.email}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(portfolioUpdate)
        });
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: Failed to update portfolio`);
        }
        
        const result = await response.json();
        
        if (result.success) {
          console.log('Portfolio updated successfully:', result);
          
          // Update original portfolio to new saved state
          setOriginalPortfolio(JSON.parse(JSON.stringify(portfolioForm)));
          setHasUnsavedChanges(false);
          
          // Optionally refresh the entire portfolio data
          try {
            const portfolioResponse = await fetch(`${API_BASE_URL}/api/portfolio/${currentUser.email}/market-report`);
            if (portfolioResponse.ok) {
              const marketData = await portfolioResponse.json();
              console.log('Refreshed market data:', marketData);
            }
          } catch (refreshError) {
            console.log('Market data refresh failed (non-critical):', refreshError);
          }
        } else {
          throw new Error(result.message || 'Failed to update portfolio');
        }
        
      } else if (activeTab === 'preferences') {
        updateUserProfile(preferencesForm);
      } else if (activeTab === 'notifications') {
        console.log('Saving notifications:', notificationForm);
      } else if (activeTab === 'security') {
        if (!validateSecurity()) return;
        console.log('Updating password');
        setSecurityForm({ currentPassword: '', newPassword: '', confirmPassword: '' });
      }

      // Show success message
      setSaveStatus('success');
      setTimeout(() => setSaveStatus(null), 3000);
      
    } catch (error) {
      console.error('Error saving changes:', error);
      setSaveStatus('error');
      setTimeout(() => setSaveStatus(null), 5000);
    }
  };

  const renderProfileTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Personal Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Full Name *
            </label>
            <input
              type="text"
              name="name"
              value={profileForm.name}
              onChange={handleProfileChange}
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none ${
                errors.name ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="John Smith"
            />
            {errors.name && <p className="mt-1 text-sm text-red-600">{errors.name}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email Address *
            </label>
            <input
              type="email"
              name="email"
              value={profileForm.email}
              onChange={handleProfileChange}
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none ${
                errors.email ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="john@example.com"
            />
            {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Age
            </label>
            <input
              type="number"
              name="age"
              value={profileForm.age}
              onChange={handleProfileChange}
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none ${
                errors.age ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="30"
              min="18"
              max="100"
            />
            {errors.age && <p className="mt-1 text-sm text-red-600">{errors.age}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Phone Number
            </label>
            <input
              type="tel"
              name="phone"
              value={profileForm.phone}
              onChange={handleProfileChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none"
              placeholder="+1 (555) 123-4567"
            />
          </div>
        </div>
      </div>
    </div>
  );

  const renderPortfolioTab = () => {
    const renderHoldingSection = (type, title, bgColor, borderColor, icon, options) => {
      const Icon = icon;
      const holdings = portfolioForm[type] || [];

      return (
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <Icon className="w-6 h-6 text-gray-700" />
            <h3 className="text-xl font-semibold text-gray-900">{title}</h3>
            <span className="ml-auto text-sm text-gray-500">
              {holdings.length} holding{holdings.length !== 1 ? 's' : ''}
            </span>
          </div>

          {/* Error messages for this section */}
          {errors[type] && (
            <div className="mb-3 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
              <p className="text-sm text-red-700">{errors[type]}</p>
            </div>
          )}
          {errors[`${type}Values`] && (
            <div className="mb-3 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
              <p className="text-sm text-red-700">{errors[`${type}Values`]}</p>
            </div>
          )}

          {/* Existing Holdings */}
          {holdings.length > 0 && (
            <div className="space-y-3 mb-4">
              {holdings.map((holding, index) => (
                <div
                  key={index}
                  className={`p-4 bg-white border-2 ${borderColor} rounded-lg`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="text-xs font-medium text-gray-500 mb-1 block">Symbol</label>
                        <select
                          value={holding.symbol}
                          onChange={(e) => updateHolding(type, index, 'symbol', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm font-semibold focus:ring-2 focus:ring-indigo-500 outline-none"
                        >
                          <option value="">Select {title.slice(0, -1)}</option>
                          {/* If current symbol is not in the list, show it as the first option */}
                          {holding.symbol && !options.find(opt => opt.value === holding.symbol) && (
                            <option value={holding.symbol}>
                              {holding.symbol} (Current)
                            </option>
                          )}
                          {options.map((opt) => (
                            <option key={opt.value} value={opt.value}>
                              {opt.label}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="text-xs font-medium text-gray-500 mb-1 block">Quantity</label>
                        <input
                          type="number"
                          value={holding.quantity}
                          onChange={(e) => updateHolding(type, index, 'quantity', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
                          placeholder="10"
                          min="0"
                          max="1000000"
                          step="0.01"
                        />
                      </div>
                      <div>
                        <label className="text-xs font-medium text-gray-500 mb-1 block">Avg Price ($)</label>
                        <input
                          type="number"
                          value={holding.avgPrice}
                          onChange={(e) => updateHolding(type, index, 'avgPrice', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
                          placeholder="150.00"
                          min="0"
                          max="10000000"
                          step="0.01"
                        />
                      </div>
                    </div>
                    <button
                      onClick={() => removeHolding(type, index)}
                      className="ml-4 p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      title="Remove holding"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Add New Holding Button */}
          <button
            onClick={() => addHolding(type)}
            className={`w-full p-4 border-2 border-dashed ${borderColor} ${bgColor} rounded-lg hover:bg-opacity-80 transition-all flex items-center justify-center gap-2 text-gray-700 font-medium`}
          >
            <Plus className="w-5 h-5" />
            Add {title.slice(0, -1)}
          </button>
        </div>
      );
    };

    return (
      <div className="space-y-6">
        {portfolioLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading your portfolio...</p>
            </div>
          </div>
        ) : (
          <div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">Manage Your Portfolio</h3>
            <p className="text-sm text-gray-600 mb-8">
              Update your portfolio holdings across different asset classes. Changes will be saved when you click "Save Changes" at the bottom.
            </p>

            {/* Unsaved changes indicator */}
            {hasUnsavedChanges && (
              <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
                <div>
                  <p className="font-semibold text-yellow-900">You have unsaved changes</p>
                  <p className="text-sm text-yellow-700">Don't forget to click "Save Changes" to keep your updates.</p>
                </div>
              </div>
            )}

            {/* Cash Savings */}
            <div className="mb-8 p-6 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border-2 border-green-200">
              <div className="flex items-center gap-3 mb-4">
                <Wallet className="w-6 h-6 text-green-700" />
                <h3 className="text-xl font-semibold text-gray-900">Cash Savings</h3>
              </div>
              {errors.cashSavings && (
                <div className="mb-3 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
                  <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
                  <p className="text-sm text-red-700">{errors.cashSavings}</p>
                </div>
              )}
              <div className="relative max-w-sm">
                <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-600 font-semibold text-lg">
                  $
                </span>
                <input
                  type="number"
                  value={portfolioForm.cashSavings}
                  onChange={(e) => setPortfolioForm(prev => ({ ...prev, cashSavings: parseFloat(e.target.value) || 0 }))}
                  className="w-full pl-10 pr-4 py-3 border-2 border-green-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none text-lg font-semibold"
                  placeholder="10000.00"
                  min="0"
                  max="100000000"
                  step="0.01"
                />
              </div>
              <p className="mt-2 text-sm text-gray-600">
                Enter your total cash savings available for investment
              </p>
            </div>

            {/* Bonds Section */}
            {renderHoldingSection(
              'bonds',
              'Bonds',
              'bg-blue-50',
              'border-blue-200',
              Shield,
              bondOptions
            )}

            {/* Stocks Section */}
            {renderHoldingSection(
              'stocks',
              'Stocks',
              'bg-purple-50',
              'border-purple-200',
              TrendingUp,
              stockOptions
            )}

            {/* ETFs Section */}
            {renderHoldingSection(
              'etfs',
              'ETFs',
              'bg-orange-50',
              'border-orange-200',
              PieChart,
              etfOptions
            )}
          </div>
        )}
      </div>
    );
  };

  const renderPreferencesTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Tolerance</h3>
        <div className="space-y-3">
          {[
            {
              value: 'conservative',
              title: 'Conservative',
              description: 'Prefer stability over growth. Minimal risk.',
              risk: 'Low Risk',
              color: 'green'
            },
            {
              value: 'moderate',
              title: 'Moderate',
              description: 'Balance between growth and stability.',
              risk: 'Medium Risk',
              color: 'yellow'
            },
            {
              value: 'aggressive',
              title: 'Aggressive',
              description: 'Maximize growth potential. Higher volatility.',
              risk: 'High Risk',
              color: 'red'
            }
          ].map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => setPreferencesForm(prev => ({ ...prev, riskTolerance: option.value }))}
              className={`w-full p-4 border-2 rounded-xl text-left transition-all ${
                preferencesForm.riskTolerance === option.value
                  ? 'border-indigo-600 bg-indigo-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="font-semibold text-gray-900">{option.title}</div>
                  <div className="text-sm text-gray-600 mt-1">{option.description}</div>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium bg-${option.color}-100 text-${option.color}-700`}>
                  {option.risk}
                </span>
              </div>
            </button>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Investment Goal</h3>
        <div className="space-y-2">
          {[
            { value: 'growth', label: 'Long-term Growth', icon: Target },
            { value: 'income', label: 'Income Generation', icon: IndianRupeeIcon },
            { value: 'preservation', label: 'Capital Preservation', icon: Shield },
            { value: 'balanced', label: 'Balanced Approach', icon: Briefcase }
          ].map((goal) => (
            <button
              key={goal.value}
              type="button"
              onClick={() => setPreferencesForm(prev => ({ ...prev, investmentGoal: goal.value }))}
              className={`w-full p-3 border-2 rounded-lg flex items-center transition-all ${
                preferencesForm.investmentGoal === goal.value
                  ? 'border-indigo-600 bg-indigo-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <goal.icon className={`w-5 h-5 mr-3 ${
                preferencesForm.investmentGoal === goal.value ? 'text-indigo-600' : 'text-gray-400'
              }`} />
              <span className="font-medium text-gray-900">{goal.label}</span>
              {preferencesForm.investmentGoal === goal.value && (
                <Check className="w-5 h-5 ml-auto text-indigo-600" />
              )}
            </button>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Investment Horizon</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { value: '1-3', label: '1-3 years' },
            { value: '3-5', label: '3-5 years' },
            { value: '5-10', label: '5-10 years' },
            { value: '10+', label: '10+ years' }
          ].map((horizon) => (
            <button
              key={horizon.value}
              type="button"
              onClick={() => setPreferencesForm(prev => ({ ...prev, investmentHorizon: horizon.value }))}
              className={`p-3 border-2 rounded-lg text-sm font-medium transition-all ${
                preferencesForm.investmentHorizon === horizon.value
                  ? 'border-indigo-600 bg-indigo-50 text-indigo-600'
                  : 'border-gray-200 text-gray-700 hover:border-gray-300'
              }`}
            >
              {horizon.label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Monthly Contribution</h3>
        <div className="max-w-md">
          <div className="relative">
            <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-500">$</span>
            <input
              type="number"
              name="monthlyContribution"
              value={preferencesForm.monthlyContribution}
              onChange={handlePreferencesChange}
              className="w-full pl-8 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none"
              placeholder="500"
              min="0"
            />
          </div>
          <p className="mt-2 text-sm text-gray-500">Set to $0 if not applicable</p>
        </div>
      </div>
    </div>
  );

  const renderNotificationsTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Notification Preferences</h3>
        <div className="space-y-4">
          {[
            {
              name: 'emailNotifications',
              label: 'Email Notifications',
              description: 'Receive updates via email'
            },
            {
              name: 'pushNotifications',
              label: 'Push Notifications',
              description: 'Get real-time alerts in your browser'
            },
            {
              name: 'portfolioAlerts',
              label: 'Portfolio Alerts',
              description: 'Significant changes in your portfolio value'
            },
            {
              name: 'marketNews',
              label: 'Market News',
              description: 'Important market updates and trends'
            },
            {
              name: 'weeklyReports',
              label: 'Weekly Reports',
              description: 'Weekly portfolio performance summary'
            },
            {
              name: 'recommendations',
              label: 'AI Recommendations',
              description: 'Personalized investment suggestions'
            }
          ].map((notif) => (
            <div
              key={notif.name}
              className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
            >
              <div>
                <div className="font-medium text-gray-900">{notif.label}</div>
                <div className="text-sm text-gray-500 mt-1">{notif.description}</div>
              </div>
              <button
                onClick={() => handleNotificationChange(notif.name)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  notificationForm[notif.name] ? 'bg-indigo-600' : 'bg-gray-300'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    notificationForm[notif.name] ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderSecurityTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Change Password</h3>
        <div className="max-w-md space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Current Password
            </label>
            <input
              type="password"
              name="currentPassword"
              value={securityForm.currentPassword}
              onChange={handleSecurityChange}
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none ${
                errors.currentPassword ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.currentPassword && (
              <p className="mt-1 text-sm text-red-600">{errors.currentPassword}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              New Password
            </label>
            <input
              type="password"
              name="newPassword"
              value={securityForm.newPassword}
              onChange={handleSecurityChange}
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none ${
                errors.newPassword ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.newPassword && (
              <p className="mt-1 text-sm text-red-600">{errors.newPassword}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Confirm New Password
            </label>
            <input
              type="password"
              name="confirmPassword"
              value={securityForm.confirmPassword}
              onChange={handleSecurityChange}
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none ${
                errors.confirmPassword ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.confirmPassword && (
              <p className="mt-1 text-sm text-red-600">{errors.confirmPassword}</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600 mt-2">Manage your account settings and preferences</p>
        </div>

        {/* Unsaved Changes Warning Modal */}
        {showUnsavedWarning && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl p-6 max-w-md mx-4 shadow-2xl">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <AlertTriangle className="w-6 h-6 text-yellow-600" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Unsaved Changes
                  </h3>
                  <p className="text-gray-600 mb-4">
                    You have unsaved changes in your portfolio. If you leave now, your changes will be lost.
                  </p>
                  <div className="flex gap-3">
                    <button
                      onClick={cancelTabChange}
                      className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors font-medium"
                    >
                      Keep Editing
                    </button>
                    <button
                      onClick={confirmTabChange}
                      className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
                    >
                      Discard Changes
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {/* Tabs */}
          <div className="border-b border-gray-200">
            <div className="flex overflow-x-auto">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => handleTabChange(tab.id)}
                    className={`flex items-center gap-2 px-6 py-4 font-medium transition-all whitespace-nowrap ${
                      activeTab === tab.id
                        ? 'text-indigo-600 border-b-2 border-indigo-600 bg-indigo-50'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    {tab.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Tab Content */}
          <div className="p-8">
            {activeTab === 'profile' && renderProfileTab()}
            {activeTab === 'portfolio' && renderPortfolioTab()}
            {activeTab === 'preferences' && renderPreferencesTab()}
            {activeTab === 'notifications' && renderNotificationsTab()}
            {activeTab === 'security' && renderSecurityTab()}
          </div>

          {/* Save Button */}
          <div className="px-8 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
            <div>
              {saveStatus === 'success' && (
                <div className="flex items-center gap-2 text-green-600">
                  <Check className="w-5 h-5" />
                  <span className="font-medium">Changes saved successfully!</span>
                </div>
              )}
              {saveStatus === 'error' && (
                <div className="flex items-center gap-2 text-red-600">
                  <AlertCircle className="w-5 h-5" />
                  <span className="font-medium">Error saving changes. Please try again.</span>
                </div>
              )}
            </div>
            <button
              onClick={handleSave}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2 font-medium"
            >
              <Save className="w-5 h-5" />
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;