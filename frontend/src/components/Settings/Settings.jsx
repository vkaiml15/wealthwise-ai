import React, { useState } from 'react';
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
  DollarSign,
  Clock
} from 'lucide-react';

const Settings = () => {
  const { currentUser, updateUserProfile } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [saveStatus, setSaveStatus] = useState(null); // 'success', 'error', null
  
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
    { id: 'preferences', label: 'Investment Preferences', icon: Target },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Lock }
  ];

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

  const handleNotificationChange = (e) => {
    const { name, checked } = e.target;
    setNotificationForm(prev => ({ ...prev, [name]: checked }));
  };

  const handleSecurityChange = (e) => {
    const { name, value } = e.target;
    setSecurityForm(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateProfile = () => {
    const newErrors = {};
    if (!profileForm.name.trim()) newErrors.name = 'Name is required';
    if (!profileForm.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(profileForm.email)) {
      newErrors.email = 'Email is invalid';
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
    if (!securityForm.newPassword) {
      newErrors.newPassword = 'New password is required';
    } else if (securityForm.newPassword.length < 8) {
      newErrors.newPassword = 'Password must be at least 8 characters';
    }
    if (securityForm.newPassword !== securityForm.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = () => {
    if (activeTab === 'profile') {
      if (!validateProfile()) return;
      updateUserProfile(profileForm);
    } else if (activeTab === 'preferences') {
      updateUserProfile(preferencesForm);
    } else if (activeTab === 'notifications') {
      // Save notification preferences
      console.log('Saving notifications:', notificationForm);
    } else if (activeTab === 'security') {
      if (!validateSecurity()) return;
      // Update password
      console.log('Updating password');
      setSecurityForm({ currentPassword: '', newPassword: '', confirmPassword: '' });
    }

    // Show success message
    setSaveStatus('success');
    setTimeout(() => setSaveStatus(null), 3000);
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

  const renderPreferencesTab = () => (
    <div className="space-y-6">
      {/* Risk Tolerance */}
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
                  <h4 className="font-semibold text-gray-900 mb-1">{option.title}</h4>
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
              {preferencesForm.riskTolerance === option.value && (
                <div className="mt-2 flex items-center text-indigo-600 text-sm font-medium">
                  <Check className="w-4 h-4 mr-1" />
                  Selected
                </div>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Investment Goal */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Investment Goal</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {[
            { value: 'growth', label: 'Long-term Growth', icon: Target },
            { value: 'income', label: 'Regular Income', icon: DollarSign },
            { value: 'preservation', label: 'Wealth Preservation', icon: Shield },
            { value: 'retirement', label: 'Retirement Planning', icon: Clock }
          ].map((goal) => (
            <button
              key={goal.value}
              type="button"
              onClick={() => setPreferencesForm(prev => ({ ...prev, investmentGoal: goal.value }))}
              className={`p-4 border-2 rounded-lg text-left transition-all flex items-center ${
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

      {/* Investment Horizon */}
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

      {/* Monthly Contribution */}
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
              description: 'Receive notifications via email'
            },
            {
              name: 'pushNotifications',
              label: 'Push Notifications',
              description: 'Receive push notifications in your browser'
            },
            {
              name: 'portfolioAlerts',
              label: 'Portfolio Alerts',
              description: 'Get notified about significant portfolio changes'
            },
            {
              name: 'marketNews',
              label: 'Market News',
              description: 'Stay updated with relevant market news'
            },
            {
              name: 'weeklyReports',
              label: 'Weekly Reports',
              description: 'Receive weekly portfolio performance reports'
            },
            {
              name: 'recommendations',
              label: 'Investment Recommendations',
              description: 'Get personalized investment recommendations'
            }
          ].map((notification) => (
            <div
              key={notification.name}
              className="flex items-start justify-between p-4 bg-gray-50 rounded-lg"
            >
              <div className="flex-1">
                <h4 className="font-medium text-gray-900 mb-1">{notification.label}</h4>
                <p className="text-sm text-gray-600">{notification.description}</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer ml-4">
                <input
                  type="checkbox"
                  name={notification.name}
                  checked={notificationForm[notification.name]}
                  onChange={handleNotificationChange}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
              </label>
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
              placeholder="Enter current password"
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
              placeholder="Enter new password"
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
              placeholder="Confirm new password"
            />
            {errors.confirmPassword && (
              <p className="mt-1 text-sm text-red-600">{errors.confirmPassword}</p>
            )}
          </div>

          <div className="pt-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div className="text-sm text-blue-900">
                  <p className="font-medium mb-1">Password Requirements:</p>
                  <ul className="list-disc list-inside space-y-1 text-blue-800">
                    <li>At least 8 characters long</li>
                    <li>Include uppercase and lowercase letters</li>
                    <li>Include at least one number</li>
                    <li>Include at least one special character</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Two-Factor Authentication */}
      <div className="pt-6 border-t border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Two-Factor Authentication</h3>
        <div className="flex items-start justify-between p-4 bg-gray-50 rounded-lg">
          <div className="flex-1">
            <h4 className="font-medium text-gray-900 mb-1">Enable 2FA</h4>
            <p className="text-sm text-gray-600">
              Add an extra layer of security to your account
            </p>
          </div>
          <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm font-medium">
            Enable
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Settings</h1>
        <p className="text-gray-600">Manage your account settings and preferences</p>
      </div>

      {/* Success/Error Message */}
      {saveStatus && (
        <div className={`mb-6 p-4 rounded-lg flex items-center space-x-3 ${
          saveStatus === 'success' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
        }`}>
          {saveStatus === 'success' ? (
            <>
              <Check className="w-5 h-5 text-green-600" />
              <p className="text-green-800 font-medium">Settings saved successfully!</p>
            </>
          ) : (
            <>
              <AlertCircle className="w-5 h-5 text-red-600" />
              <p className="text-red-800 font-medium">Error saving settings. Please try again.</p>
            </>
          )}
        </div>
      )}

      {/* Tabs */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
        {/* Tab Headers */}
        <div className="border-b border-gray-200 bg-gray-50">
          <div className="flex overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-6 py-4 text-sm font-medium whitespace-nowrap transition-all ${
                  activeTab === tab.id
                    ? 'text-indigo-600 border-b-2 border-indigo-600 bg-white'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <tab.icon className="w-5 h-5" />
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="p-6 md:p-8">
          {activeTab === 'profile' && renderProfileTab()}
          {activeTab === 'preferences' && renderPreferencesTab()}
          {activeTab === 'notifications' && renderNotificationsTab()}
          {activeTab === 'security' && renderSecurityTab()}
        </div>

        {/* Save Button */}
        <div className="border-t border-gray-200 bg-gray-50 px-6 md:px-8 py-4 flex justify-end">
          <button
            onClick={handleSave}
            className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-medium hover:from-indigo-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl"
          >
            <Save className="w-5 h-5" />
            <span>Save Changes</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Settings;