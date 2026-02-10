import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import Footer from './Footer';

function Layout() {
  const [sidebarOpen, setSidebarOpen] = React.useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex flex-col">
      {/* Navbar */}
      <Navbar onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />

      {/* Main Content Wrapper */}
      <div className="flex flex-1 overflow-hidden relative">
        {/* Sidebar - Mobile Overlay */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 bg-black/40 backdrop-blur-sm z-30 lg:hidden"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close menu"
          ></div>
        )}

        {/* Sidebar */}
        <Sidebar sidebarOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        {/* Main Content Area - Offset for Desktop Sidebar */}
        <main className="flex-1 overflow-auto flex flex-col lg:ml-64">
          {/* Content */}
          <div className="flex-1 p-4 sm:p-6 lg:p-8">
            <div className="max-w-7xl mx-auto">
              <Outlet />
            </div>
          </div>
          
          {/* Footer */}
          <Footer />
        </main>
      </div>
    </div>
  );
}

export default Layout;
