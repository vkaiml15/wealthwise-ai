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
  Sparkles
} from 'lucide-react';

const OnboardingWizard = () => {
  const navigate = useNavigate();
  const { currentUser, completeOnboarding } = useAuth();
  const [currentStep, setCurrentStep] = useState(1);
  const totalSteps = 4;

  const [profileData, setProfileData] = useState({
    name: '',
    email: '',
    age: '',
    riskTolerance: 'moderate',
    investmentGoal: 'growth',
    investmentHorizon: '5-10',
    initialInvestment: '',
    monthlyContribution: ''
  });

  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
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
    // Save profile data
    completeOnboarding(profileData);
    navigate('/dashboard');
  };

  const renderStepIndicator = () => (
    <div className="flex items-center justify-center mb-8">
      {[1, 2, 3, 4].map((step) => (
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
              className={`w-16 h-1 mx-2 transition-all ${
                step < currentStep ? 'bg-green-500' : 'bg-gray-200'
              }`}
            ></div>
          )}
        </React.Fragment>
      ))}
    </div>
  );

  const renderStep1 = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-indigo-100 rounded-full mb-4">
          <User className="w-8 h-8 text-indigo-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Personal Information</h2>
        <p className="text-gray-600">Let's start with the basics</p>
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
          Email Address *
        </label>
        <input
          type="email"
          name="email"
          value={profileData.email}
          onChange={handleChange}
          className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none ${
            errors.email ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="john@example.com"
        />
        {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email}</p>}
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
    </div>
  );

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

      {/* Projection Preview */}
      {profileData.initialInvestment > 0 && (
        <div className="mt-6 p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg border border-indigo-100">
          <h3 className="font-semibold text-gray-900 mb-3">Estimated Portfolio Value</h3>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Initial Investment:</span>
              <span className="font-medium">${Number(profileData.initialInvestment).toLocaleString()}</span>
            </div>
            {profileData.monthlyContribution > 0 && (
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Monthly Contribution:</span>
                <span className="font-medium">${Number(profileData.monthlyContribution).toLocaleString()}</span>
              </div>
            )}
            <div className="pt-2 border-t border-indigo-200">
              <div className="flex justify-between">
                <span className="text-gray-600">Projected Value (5 years)*:</span>
                <span className="font-bold text-indigo-600">
                  ${(Number(profileData.initialInvestment) * 1.5 + 
                     Number(profileData.monthlyContribution || 0) * 60 * 1.2).toLocaleString(undefined, {maximumFractionDigits: 0})}
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-1">*Based on historical average returns</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl shadow-lg mb-4">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome to WealthWise AI</h1>
          <p className="text-gray-600">Let's personalize your investment experience</p>
        </div>

        {/* Progress Indicator */}
        {renderStepIndicator()}

        {/* Main Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
          {/* Step Content */}
          <div className="min-h-[400px]">
            {currentStep === 1 && renderStep1()}
            {currentStep === 2 && renderStep2()}
            {currentStep === 3 && renderStep3()}
            {currentStep === 4 && renderStep4()}
          </div>

          {/* Navigation Buttons */}
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

        {/* Footer */}
        <div className="text-center">
          <p className="text-sm text-gray-500">
            Step {currentStep} of {totalSteps} • Your data is secure and encrypted
          </p>
        </div>
      </div>
    </div>
  );
};

export default OnboardingWizard;