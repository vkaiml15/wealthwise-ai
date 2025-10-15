import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ChatProvider } from './context/ChatContext';
import { Loader2, Home, ArrowLeft, Zap } from 'lucide-react';

// Components
import LoginPage from './components/Auth/LoginPage';
import OnboardingWizard from './components/Auth/OnboardingWizard';
import Layout from './components/Layout/Layout';
import Dashboard from './components/Dashboard/Dashboard';
import ChatInterface from './components/Chatbot/ChatInterface';
import Settings from './components/Settings/Settings';

// Loading Screen Component
const LoadingScreen = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      <div className="text-center">
        <div className="inline-block">
          <Loader2 className="w-16 h-16 text-indigo-600 animate-spin" />
        </div>
        <p className="mt-4 text-gray-600 font-medium">Loading WealthWise AI...</p>
      </div>
    </div>
  );
};

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingScreen />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

// Public Route Component
const PublicRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingScreen />;
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

// Placeholder Page Component
const PlaceholderPage = ({ title }) => {
  return (
    <div className="flex items-center justify-center h-full min-h-screen">
      <div className="text-center px-4">
        <div className="w-20 h-20 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <Zap className="w-10 h-10 text-indigo-600" />
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-3">{title}</h2>
        <p className="text-gray-600 mb-6">This feature is coming soon...</p>
        <Link
          to="/dashboard"
          className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-medium hover:from-indigo-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back to Dashboard
        </Link>
      </div>
    </div>
  );
};

// 404 Not Found Page Component
const NotFoundPage = () => {
  return (
    <div className="flex items-center justify-center h-full min-h-screen">
      <div className="text-center px-4">
        <h1 className="text-9xl font-bold text-transparent bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text mb-4">
          404
        </h1>
        <h2 className="text-3xl font-bold text-gray-900 mb-3">Page Not Found</h2>
        <p className="text-gray-600 mb-8 max-w-md mx-auto">
          The page you are looking for does not exist or has been moved.
        </p>
        <Link
          to="/dashboard"
          className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-medium hover:from-indigo-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl"
        >
          <Home className="w-5 h-5 mr-2" />
          Go to Dashboard
        </Link>
      </div>
    </div>
  );
};

// App Routes Component
const AppRoutes = () => {
  return (
    <Routes>
      {/* Public Route - Login */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        }
      />

      {/* Onboarding Route */}
      <Route
        path="/onboarding"
        element={
          <ProtectedRoute>
            <OnboardingWizard />
          </ProtectedRoute>
        }
      />

      {/* Protected Routes with Layout */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        {/* Root redirect */}
        <Route index element={<Navigate to="/dashboard" replace />} />

        {/* Main Pages */}
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="chat" element={<ChatInterface />} />
        <Route path="settings" element={<Settings />} />

        {/* Placeholder Pages */}
        <Route path="portfolio" element={<PlaceholderPage title="Portfolio Details" />} />
        <Route path="market" element={<PlaceholderPage title="Market Trends" />} />
        <Route path="recommendations" element={<PlaceholderPage title="Stock Recommendations" />} />
        <Route path="risk" element={<PlaceholderPage title="Risk Analysis" />} />

        {/* 404 within authenticated area */}
        <Route path="*" element={<NotFoundPage />} />
      </Route>

      {/* Catch all - redirect to login */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
};

// Main App Component
function App() {
  return (
    <Router>
      <AuthProvider>
        <ChatProvider>
          <AppRoutes />
        </ChatProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;