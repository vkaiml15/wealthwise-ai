import React, { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';

const Layout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  
  // Check if current route is chat
  const isChatPage = location.pathname === '/chat';

  return (
    <div className="h-screen bg-gray-50 flex overflow-hidden">
      {/* Fixed Sidebar */}
      <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />

      {/* Main Content Area with left padding for sidebar on desktop */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden lg:pl-64">
        {/* Sticky Header */}
        <Header sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />

        {/* Main Content - Different handling for chat vs other pages */}
        {isChatPage ? (
          // Chat page - Takes remaining height after header
          <main className="flex-1 overflow-hidden">
            <Outlet />
          </main>
        ) : (
          // Other pages - Normal scrolling behavior
          <main className="flex-1 overflow-auto">
            <div className="p-4 lg:p-8">
              <div className="max-w-7xl mx-auto">
                <Outlet />
              </div>
            </div>

            {/* Footer - Only for non-chat pages */}
            <footer className="bg-white border-t border-gray-200 py-4 px-6">
              <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between text-sm text-gray-600">
                <p>© 2025 WealthWise AI. All rights reserved.</p>
                <div className="flex space-x-6 mt-2 md:mt-0">
                  <button className="hover:text-indigo-600 transition-colors">Privacy Policy</button>
                  <button className="hover:text-indigo-600 transition-colors">Terms of Service</button>
                  <button className="hover:text-indigo-600 transition-colors">Contact Support</button>
                </div>
              </div>
            </footer>
          </main>
        )}
      </div>
    </div>
  );
};

export default Layout;