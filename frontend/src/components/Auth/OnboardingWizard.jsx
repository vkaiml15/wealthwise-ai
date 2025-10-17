import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { 
  User, 
  Mail, 
  Shield, 
  Target, 
  TrendingUp, 
  Check, 
  ArrowRight, 
  ArrowLeft,
  DollarSign,
  Clock,
  Sparkles,
  Wallet,
  FileText,
  BarChart3,
  PieChart,
  Plus,
  Trash2,
  Lock,
  Eye,
  EyeOff
} from 'lucide-react';

const ExtendedOnboardingWizard = () => {
  const navigate = useNavigate();
  const { completeOnboarding } = useAuth();
  const [currentStep, setCurrentStep] = useState(1);
  const totalSteps = 8;

  const [profileData, setProfileData] = useState({
    // Step 1: Personal Information & Credentials
    name: '',
    email: '',
    age: '',
    password: '',
    confirmPassword: '',
    
    // Step 2: Risk Tolerance
    riskTolerance: 'moderate',
    
    // Step 3: Investment Goals
    investmentGoal: 'growth',
    investmentHorizon: '5-10',
    
    // Step 4: Investment Amount
    initialInvestment: '',
    monthlyContribution: '',
    
    // Step 5: Cash Savings
    cashSavings: '',
    
    // Step 6: Bonds Holdings
    bonds: [],
    
    // Step 7: Stocks Holdings
    stocks: [],
    
    // Step 8: ETFs Holdings
    etfs: []
  });

  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // Mock data for dropdowns
  const bondOptions = [
    { value: 'US_TREASURY_10Y', label: 'US Treasury 10Y' },
    { value: 'US_TREASURY_30Y', label: 'US Treasury 30Y' },
    { value: 'CORPORATE_AAA', label: 'Corporate AAA Bond' },
    { value: 'MUNICIPAL', label: 'Municipal Bond' },
    { value: 'HIGH_YIELD', label: 'High Yield Corporate' }
  ];

  const stockOptions = [
    { value: 'AAPL', label: 'Apple Inc. (AAPL)' },
    { value: 'MSFT', label: 'Microsoft (MSFT)' },
    { value: 'GOOGL', label: 'Alphabet (GOOGL)' },
    { value: 'AMZN', label: 'Amazon (AMZN)' },
    { value: 'TSLA', label: 'Tesla (TSLA)' },
    { value: 'NVDA', label: 'NVIDIA (NVDA)' },
    { value: 'JPM', label: 'JPMorgan Chase (JPM)' },
    { value: 'V', label: 'Visa (V)' },
    { value: 'JNJ', label: 'Johnson & Johnson (JNJ)' },
    { value: 'WMT', label: 'Walmart (WMT)' }
  ];

  const etfOptions = [
    { value: 'SPY', label: 'SPDR S&P 500 ETF (SPY)' },
    { value: 'QQQ', label: 'Invesco QQQ Trust (QQQ)' },
    { value: 'VTI', label: 'Vanguard Total Stock Market (VTI)' },
    { value: 'IWM', label: 'iShares Russell 2000 (IWM)' },
    { value: 'EEM', label: 'iShares MSCI Emerging Markets (EEM)' },
    { value: 'VEA', label: 'Vanguard FTSE Developed Markets (VEA)' },
    { value: 'AGG', label: 'iShares Core US Aggregate Bond (AGG)' }
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prev => ({
      ...prev,
      [name]: value
    }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  // Holdings management functions
  const addHolding = (type) => {
    const newHolding = { symbol: '', quantity: '', avgPrice: '' };
    setProfileData(prev => ({
      ...prev,
      [type]: [...prev[type], newHolding]
    }));
  };

  const updateHolding = (type, index, field, value) => {
    setProfileData(prev => ({
      ...prev,
      [type]: prev[type].map((item, i) => 
        i === index ? { ...item, [field]: value } : item
      )
    }));
  };

  const removeHolding = (type, index) => {
    setProfileData(prev => ({
      ...prev,
      [type]: prev[type].filter((_, i) => i !== index)
    }));
  };

  const validatePassword = (password) => {
    const minLength = 8;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

    if (password.length < minLength) {
      return 'Password must be at least 8 characters long';
    }
    if (!hasUpperCase) {
      return 'Password must contain at least one uppercase letter';
    }
    if (!hasLowerCase) {
      return 'Password must contain at least one lowercase letter';
    }
    if (!hasNumber) {
      return 'Password must contain at least one number';
    }
    if (!hasSpecialChar) {
      return 'Password must contain at least one special character';
    }
    return null;
  };

  const getPasswordStrength = (password) => {
    if (!password) return { strength: 0, label: '', color: '' };
    
    let strength = 0;
    if (password.length >= 8) strength++;
    if (password.length >= 12) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength++;

    if (strength <= 2) return { strength: 1, label: 'Weak', color: 'bg-red-500' };
    if (strength <= 4) return { strength: 2, label: 'Medium', color: 'bg-yellow-500' };
    return { strength: 3, label: 'Strong', color: 'bg-green-500' };
  };

  const validateStep = (step) => {
    const newErrors = {};

    if (step === 1) {
      if (!profileData.name.trim()) newErrors.name = 'Name is required';
      
      if (!profileData.email.trim()) {
        newErrors.email = 'Email is required';
      } else if (!/\S+@\S+\.\S+/.test(profileData.email)) {
        newErrors.email = 'Email is invalid';
      }
      
      if (!profileData.age) {
        newErrors.age = 'Age is required';
      } else if (profileData.age < 18 || profileData.age > 100) {
        newErrors.age = 'Age must be between 18 and 100';
      }

      if (!profileData.password) {
        newErrors.password = 'Password is required';
      } else {
        const passwordError = validatePassword(profileData.password);
        if (passwordError) {
          newErrors.password = passwordError;
        }
      }

      if (!profileData.confirmPassword) {
        newErrors.confirmPassword = 'Please confirm your password';
      } else if (profileData.password !== profileData.confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match';
      }
    }

    if (step === 4) {
      if (!profileData.initialInvestment) {
        newErrors.initialInvestment = 'Initial investment is required';
      } else if (profileData.initialInvestment < 1000) {
        newErrors.initialInvestment = 'Minimum investment is $1,000';
      }
      if (!profileData.monthlyContribution) {
        newErrors.monthlyContribution = 'Monthly contribution is required';
      } else if (profileData.monthlyContribution < 0) {
        newErrors.monthlyContribution = 'Amount cannot be negative';
      }
    }

    if (step === 5) {
      if (!profileData.cashSavings) {
        newErrors.cashSavings = 'Cash savings amount is required';
      } else if (profileData.cashSavings < 0) {
        newErrors.cashSavings = 'Amount cannot be negative';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      if (currentStep < totalSteps) {
        setCurrentStep(currentStep + 1);
      } else {
        handleComplete();
      }
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    const result = completeOnboarding(profileData);
    console.log('Onboarding completed!', result);
    navigate('/dashboard');
  };

  const renderStepIndicator = () => (
    <div className="flex items-center justify-center mb-8 overflow-x-auto pb-4">
      {[1, 2, 3, 4, 5, 6, 7, 8].map((step) => (
        <React.Fragment key={step}>
          <div className="flex items-center">
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-all ${
                step < currentStep
                  ? 'bg-green-500 text-white'
                  : step === currentStep
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-200 text-gray-400'
              }`}
            >
              {step < currentStep ? <Check className="w-5 h-5" /> : step}
            </div>
          </div>
          {step < totalSteps && (
            <div
              className={`w-12 h-1 mx-2 transition-all ${
                step < currentStep ? 'bg-green-500' : 'bg-gray-200'
              }`}
            ></div>
          )}
        </React.Fragment>
      ))}
    </div>
  );

  const renderStep1 = () => {
    const passwordStrength = getPasswordStrength(profileData.password);
    
    return (
      <div className="space-y-6">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-indigo-100 rounded-full mb-4">
            <User className="w-8 h-8 text-indigo-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Create Your Account</h2>
          <p className="text-gray-600">Let's get started with the basics</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Full Name *
          </label>
          <input
            type="text"
            name="name"
            value={profileData.name}
            onChange={handleChange}
            className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none ${
              errors.name ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="John Smith"
          />
          {errors.name && <p className="mt-1 text-sm text-red-600">{errors.name}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Email Address (Your User ID) *
          </label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="email"
              name="email"
              value={profileData.email}
              onChange={handleChange}
              className={`w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none ${
                errors.email ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="john@example.com"
            />
          </div>
          {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email}</p>}
          <p className="mt-1 text-xs text-gray-500">You'll use this email to log in</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Age *
          </label>
          <input
            type="number"
            name="age"
            value={profileData.age}
            onChange={handleChange}
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
            Password *
          </label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type={showPassword ? "text" : "password"}
              name="password"
              value={profileData.password}
              onChange={handleChange}
              className={`w-full pl-10 pr-12 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none ${
                errors.password ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Create a strong password"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </button>
          </div>
          {errors.password && <p className="mt-1 text-sm text-red-600">{errors.password}</p>}
          
          {profileData.password && (
            <div className="mt-2">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-gray-600">Password strength:</span>
                <span className={`text-xs font-medium ${
                  passwordStrength.strength === 1 ? 'text-red-600' :
                  passwordStrength.strength === 2 ? 'text-yellow-600' :
                  'text-green-600'
                }`}>
                  {passwordStrength.label}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all ${passwordStrength.color}`}
                  style={{ width: `${(passwordStrength.strength / 3) * 100}%` }}
                ></div>
              </div>
            </div>
          )}
          
          <p className="mt-1 text-xs text-gray-500">
            Must be 8+ characters with uppercase, lowercase, number, and special character
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Confirm Password *
          </label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type={showConfirmPassword ? "text" : "password"}
              name="confirmPassword"
              value={profileData.confirmPassword}
              onChange={handleChange}
              className={`w-full pl-10 pr-12 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none ${
                errors.confirmPassword ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Re-enter your password"
            />
            <button
              type="button"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </button>
          </div>
          {errors.confirmPassword && <p className="mt-1 text-sm text-red-600">{errors.confirmPassword}</p>}
          {profileData.confirmPassword && profileData.password === profileData.confirmPassword && (
            <p className="mt-1 text-sm text-green-600 flex items-center">
              <Check className="w-4 h-4 mr-1" />
              Passwords match
            </p>
          )}
        </div>
      </div>
    );
  };

  const renderStep2 = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-indigo-100 rounded-full mb-4">
          <Shield className="w-8 h-8 text-indigo-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Risk Tolerance</h2>
        <p className="text-gray-600">How comfortable are you with market volatility?</p>
      </div>

      <div className="space-y-4">
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
            onClick={() => setProfileData(prev => ({ ...prev, riskTolerance: option.value }))}
            className={`w-full p-4 border-2 rounded-xl text-left transition-all ${
              profileData.riskTolerance === option.value
                ? 'border-indigo-600 bg-indigo-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900 mb-1">{option.title}</h3>
                <p className="text-sm text-gray-600">{option.description}</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                option.color === 'green' ? 'bg-green-100 text-green-700' :
                option.color === 'yellow' ? 'bg-yellow-100 text-yellow-700' :
                'bg-red-100 text-red-700'
              }`}>
                {option.risk}
              </span>
            </div>
            {profileData.riskTolerance === option.value && (
              <div className="mt-2 flex items-center text-indigo-600 text-sm font-medium">
                <Check className="w-4 h-4 mr-1" />
                Selected
              </div>
            )}
          </button>
        ))}
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-indigo-100 rounded-full mb-4">
          <Target className="w-8 h-8 text-indigo-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Investment Goals</h2>
        <p className="text-gray-600">What are you investing for?</p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Primary Goal
        </label>
        <div className="space-y-3">
          {[
            { value: 'growth', label: 'Long-term Growth', icon: TrendingUp },
            { value: 'income', label: 'Regular Income', icon: DollarSign },
            { value: 'preservation', label: 'Wealth Preservation', icon: Shield },
            { value: 'retirement', label: 'Retirement Planning', icon: Clock }
          ].map((goal) => (
            <button
              key={goal.value}
              type="button"
              onClick={() => setProfileData(prev => ({ ...prev, investmentGoal: goal.value }))}
              className={`w-full p-4 border-2 rounded-lg text-left transition-all flex items-center ${
                profileData.investmentGoal === goal.value
                  ? 'border-indigo-600 bg-indigo-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <goal.icon className={`w-5 h-5 mr-3 ${
                profileData.investmentGoal === goal.value ? 'text-indigo-600' : 'text-gray-400'
              }`} />
              <span className="font-medium text-gray-900">{goal.label}</span>
              {profileData.investmentGoal === goal.value && (
                <Check className="w-5 h-5 ml-auto text-indigo-600" />
              )}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Investment Horizon
        </label>
        <div className="grid grid-cols-2 gap-3">
          {[
            { value: '1-3', label: '1-3 years' },
            { value: '3-5', label: '3-5 years' },
            { value: '5-10', label: '5-10 years' },
            { value: '10+', label: '10+ years' }
          ].map((horizon) => (
            <button
              key={horizon.value}
              type="button"
              onClick={() => setProfileData(prev => ({ ...prev, investmentHorizon: horizon.value }))}
              className={`p-3 border-2 rounded-lg text-sm font-medium transition-all ${
                profileData.investmentHorizon === horizon.value
                  ? 'border-indigo-600 bg-indigo-50 text-indigo-600'
                  : 'border-gray-200 text-gray-700 hover:border-gray-300'
              }`}
            >
              {horizon.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );

  const renderStep4 = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-indigo-100 rounded-full mb-4">
          <DollarSign className="w-8 h-8 text-indigo-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Investment Amount</h2>
        <p className="text-gray-600">How much would you like to invest?</p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Initial Investment *
        </label>
        <div className="relative">
          <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-500">$</span>
          <input
            type="number"
            name="initialInvestment"
            value={profileData.initialInvestment}
            onChange={handleChange}
            className={`w-full pl-8 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none ${
              errors.initialInvestment ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="10,000"
            min="1000"
          />
        </div>
        {errors.initialInvestment && (
          <p className="mt-1 text-sm text-red-600">{errors.initialInvestment}</p>
        )}
        <p className="mt-1 text-sm text-gray-500">Minimum: $1,000</p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Monthly Contribution *
        </label>
        <div className="relative">
          <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-500">$</span>
          <input
            type="number"
            name="monthlyContribution"
            value={profileData.monthlyContribution}
            onChange={handleChange}
            className={`w-full pl-8 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none ${
              errors.monthlyContribution ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="500"
            min="0"
          />
        </div>
        {errors.monthlyContribution && (
          <p className="mt-1 text-sm text-red-600">{errors.monthlyContribution}</p>
        )}
        <p className="mt-1 text-sm text-gray-500">Optional: Set to $0 if not applicable</p>
      </div>
    </div>
  );

  const renderStep5 = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
          <Wallet className="w-8 h-8 text-green-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Cash Savings</h2>
        <p className="text-gray-600">How much cash do you have in savings?</p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Cash Savings Amount *
        </label>
        <div className="relative">
          <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-500">$</span>
          <input
            type="number"
            name="cashSavings"
            value={profileData.cashSavings}
            onChange={handleChange}
            className={`w-full pl-8 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none ${
              errors.cashSavings ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="5,000"
            min="0"
          />
        </div>
        {errors.cashSavings && (
          <p className="mt-1 text-sm text-red-600">{errors.cashSavings}</p>
        )}
        <p className="mt-1 text-sm text-gray-500">Enter your total cash savings across all accounts</p>
      </div>

      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-900">
          <strong>Tip:</strong> Maintaining 3-6 months of expenses in cash savings is recommended for emergency situations.
        </p>
      </div>
    </div>
  );

  const renderHoldingsStep = (type, title, icon, options, color = 'indigo') => {
    const holdings = profileData[type];
    
    return (
      <div className="space-y-6">
        <div className="text-center mb-8">
          <div className={`inline-flex items-center justify-center w-16 h-16 bg-${color}-100 rounded-full mb-4`}>
            {icon}
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">{title}</h2>
          <p className="text-gray-600">Add your existing {title.toLowerCase()}</p>
        </div>

        <div className="space-y-4">
          {holdings.map((holding, index) => (
            <div key={index} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
              <div className="flex items-start justify-between mb-3">
                <span className="text-sm font-medium text-gray-700">
                  {title.slice(0, -1)} #{index + 1}
                </span>
                <button
                  type="button"
                  onClick={() => removeHolding(type, index)}
                  className="text-red-600 hover:text-red-700"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
              
              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Select {title.slice(0, -1)}
                  </label>
                  <select
                    value={holding.symbol}
                    onChange={(e) => updateHolding(type, index, 'symbol', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none text-sm"
                  >
                    <option value="">Select...</option>
                    {options.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">
                      Quantity
                    </label>
                    <input
                      type="number"
                      value={holding.quantity}
                      onChange={(e) => updateHolding(type, index, 'quantity', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none text-sm"
                      placeholder="100"
                      min="0"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">
                      Avg Price ($)
                    </label>
                    <input
                      type="number"
                      value={holding.avgPrice}
                      onChange={(e) => updateHolding(type, index, 'avgPrice', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none text-sm"
                      placeholder="150.00"
                      min="0"
                      step="0.01"
                    />
                  </div>
                </div>
              </div>
            </div>
          ))}

          <button
            type="button"
            onClick={() => addHolding(type)}
            className="w-full py-3 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-indigo-400 hover:text-indigo-600 transition-all flex items-center justify-center space-x-2"
          >
            <Plus className="w-5 h-5" />
            <span>Add {title.slice(0, -1)}</span>
          </button>

          {holdings.length === 0 && (
            <p className="text-center text-sm text-gray-500 py-4">
              No {title.toLowerCase()} added yet. Click the button above to add your first {title.toLowerCase().slice(0, -1)}.
            </p>
          )}
        </div>

        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-600">
            <strong>Note:</strong> You can skip this step if you don't currently hold any {title.toLowerCase()}.
          </p>
        </div>
      </div>
    );
  };

  const renderStep6 = () => renderHoldingsStep(
    'bonds',
    'Bonds',
    <FileText className="w-8 h-8 text-blue-600" />,
    bondOptions,
    'blue'
  );

  const renderStep7 = () => renderHoldingsStep(
    'stocks',
    'Stocks',
    <BarChart3 className="w-8 h-8 text-green-600" />,
    stockOptions,
    'green'
  );

  const renderStep8 = () => renderHoldingsStep(
    'etfs',
    'ETFs',
    <PieChart className="w-8 h-8 text-purple-600" />,
    etfOptions,
    'purple'
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl shadow-lg mb-4">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome to WealthWise AI</h1>
          <p className="text-gray-600">Let's personalize your investment experience</p>
        </div>

        {renderStepIndicator()}

        <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
          <div className="min-h-[400px]">
            {currentStep === 1 && renderStep1()}
            {currentStep === 2 && renderStep2()}
            {currentStep === 3 && renderStep3()}
            {currentStep === 4 && renderStep4()}
            {currentStep === 5 && renderStep5()}
            {currentStep === 6 && renderStep6()}
            {currentStep === 7 && renderStep7()}
            {currentStep === 8 && renderStep8()}
          </div>

          <div className="flex justify-between mt-8 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={handleBack}
              disabled={currentStep === 1}
              className={`px-6 py-3 rounded-lg font-medium transition-all flex items-center space-x-2 ${
                currentStep === 1
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <ArrowLeft className="w-5 h-5" />
              <span>Back</span>
            </button>

            <button
              type="button"
              onClick={handleNext}
              className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-medium hover:from-indigo-700 hover:to-purple-700 transition-all flex items-center space-x-2 shadow-lg hover:shadow-xl"
            >
              <span>{currentStep === totalSteps ? 'Complete Setup' : 'Next'}</span>
              {currentStep === totalSteps ? (
                <Check className="w-5 h-5" />
              ) : (
                <ArrowRight className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>

        <div className="text-center">
          <p className="text-sm text-gray-500">
            Step {currentStep} of {totalSteps} • Your data is secure and encrypted
          </p>
        </div>
      </div>
    </div>
  );
};

export default ExtendedOnboardingWizard;