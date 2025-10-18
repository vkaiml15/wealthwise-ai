import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ChatProvider } from './context/ChatContext';
import { Loader2 } from 'lucide-react';

// Components
import LoginPage from './components/Auth/LoginPage';
import OnboardingWizard from './components/Auth/OnboardingWizard';
import Layout from './components/Layout/Layout';
import Dashboard from './components/Dashboard/Dashboard';
import ChatInterface from './components/Chatbot/ChatInterface';
import Settings from './components/Settings/Settings';
import MarketTrends from './components/MarketTrends.jsx';

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

// App Routes Component
const AppRoutes = () => {
  return (
    <Routes>
      {/* Login - Public Route */}
      <Route path="/login" element={<LoginPage />} />

      {/* Onboarding - Public Route (No Protection) */}
      <Route path="/onboarding" element={<OnboardingWizard />} />

      {/* Protected Routes with Layout */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="chat" element={<ChatInterface />} />
        <Route path="market" element={<MarketTrends />} />
        <Route path="settings" element={<Settings />} />
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