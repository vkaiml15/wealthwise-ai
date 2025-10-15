import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';

const Layout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-h-screen">
        {/* Header */}
        <Header sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />

        {/* Main Content */}
        <main className="flex-1 p-4 lg:p-8 overflow-auto">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>

        {/* Footer */}
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
      </div>
    </div>
  );
};

export default Layout;