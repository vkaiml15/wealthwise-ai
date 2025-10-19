import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import NotificationBell from './NotificationBell';
import { 
  User, 
  Settings, 
  LogOut, 
  ChevronDown,
  Search,
  Menu,
  X
} from 'lucide-react';

const Header = ({ sidebarOpen, setSidebarOpen }) => {
  const { currentUser, logout, portfolio } = useAuth();
  const navigate = useNavigate();
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
    setShowUserMenu(false);
  };

  return (
    <header className="bg-white border-b border-gray-200 px-4 lg:px-6 h-16 flex items-center justify-between sticky top-0 z-40">
      {/* Left Section */}
      <div className="flex items-center space-x-4">
        {/* Mobile Menu Toggle */}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
        >
          {sidebarOpen ? (
            <X className="w-6 h-6 text-gray-600" />
          ) : (
            <Menu className="w-6 h-6 text-gray-600" />
          )}
        </button>

        {/* Search Bar - Hidden on mobile */}
        <div className="hidden md:flex items-center">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search stocks, portfolio..."
              className="pl-10 pr-4 py-2 w-64 lg:w-80 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none text-sm"
            />
          </div>
        </div>
      </div>

      {/* Right Section */}
      <div className="flex items-center space-x-2 lg:space-x-4">
        {/* Portfolio Value - Hidden on small screens */}
        {portfolio && (
          <div className="hidden md:flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg border border-indigo-100">
            <div className="text-right">
              <p className="text-xs text-gray-600">Portfolio</p>
              <p className="text-sm font-bold text-indigo-600">
                ${portfolio.totalValue?.toLocaleString()}
              </p>
            </div>
          </div>
        )}

        {/* Notification Bell - Replaced with new component */}
        <NotificationBell />

        {/* User Menu */}
        <div className="relative">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-semibold">
                {currentUser?.name?.charAt(0).toUpperCase() || 'U'}
              </span>
            </div>
            <div className="hidden lg:block text-left">
              <p className="text-sm font-medium text-gray-900">
                {currentUser?.name || 'User'}
              </p>
              <p className="text-xs text-gray-500">
                {currentUser?.riskProfile || 'Investor'}
              </p>
            </div>
            <ChevronDown className="hidden lg:block w-4 h-4 text-gray-400" />
          </button>

          {/* User Dropdown */}
          {showUserMenu && (
            <>
              <div
                className="fixed inset-0 z-40"
                onClick={() => setShowUserMenu(false)}
              ></div>
              <div className="absolute right-0 mt-2 w-64 bg-white rounded-xl shadow-lg border border-gray-200 z-50">
                <div className="p-4 border-b border-gray-200">
                  <p className="text-sm font-semibold text-gray-900">
                    {currentUser?.name || 'User'}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {currentUser?.email || 'user@example.com'}
                  </p>
                </div>
                <div className="py-2">
                  <button
                    onClick={() => {
                      navigate('/settings');
                      setShowUserMenu(false);
                    }}
                    className="w-full flex items-center space-x-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    <User className="w-4 h-4" />
                    <span>Profile</span>
                  </button>
                  <button
                    onClick={() => {
                      navigate('/settings');
                      setShowUserMenu(false);
                    }}
                    className="w-full flex items-center space-x-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    <Settings className="w-4 h-4" />
                    <span>Settings</span>
                  </button>
                </div>
                <div className="border-t border-gray-200 py-2">
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center space-x-3 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                  >
                    <LogOut className="w-4 h-4" />
                    <span>Log out</span>
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;