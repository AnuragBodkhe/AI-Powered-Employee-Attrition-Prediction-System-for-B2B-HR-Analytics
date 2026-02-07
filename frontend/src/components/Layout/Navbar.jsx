import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authAPI } from '../../services/api';

function Navbar({ onToggleSidebar }) {
  const [user, setUser] = useState(null);
  const [showMenu, setShowMenu] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchUser();
  }, []);

  const fetchUser = async () => {
    try {
      const response = await authAPI.getCurrentUser();
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user');
    }
  };

  const handleLogout = async () => {
    try {
      await authAPI.logout();
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      navigate('/login');
    } catch (error) {
      console.error('Logout failed');
    }
  };

  return (
    <nav className="bg-white border-b border-slate-200 sticky top-0 z-40 shadow-sm">
      <div className="px-6 py-4 flex items-center justify-between max-w-7xl mx-auto">
        {/* Left Section */}
        <div className="flex items-center gap-4">
          <button
            onClick={onToggleSidebar}
            className="btn-icon lg:hidden"
            aria-label="Toggle sidebar"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <Link to="/dashboard" className="flex items-center gap-3 no-underline group">
            <div className="w-10 h-10 bg-gradient-to-br from-indigo-600 to-indigo-700 rounded-lg flex items-center justify-center">
              <span className="text-lg font-bold text-white">✦</span>
            </div>
            <div className="hidden sm:block">
              <h1 className="text-lg font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">
                HR Analytics
              </h1>
              <p className="text-xs text-slate-500">AI-Powered Insights</p>
            </div>
          </Link>
        </div>

        {/* Center Section - Search (optional) */}
        <div className="hidden md:flex items-center flex-1 max-w-96 mx-8">
          <div className="relative w-full">
            <input
              type="text"
              placeholder="Search employees, departments..."
              className="w-full px-4 py-2 rounded-lg border border-slate-200 bg-slate-50 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            />
            <svg
              className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>

        {/* Right Section */}
        <div className="flex items-center gap-3">
          {/* Notifications */}
          <button className="btn-icon relative" aria-label="Notifications">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>

          {/* User Profile Menu */}
          <div className="relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="btn-icon flex items-center gap-2 pl-3 pr-2"
              aria-label="Profile menu"
            >
              <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-lg flex items-center justify-center text-white text-sm font-bold">
                {user?.username?.[0]?.toUpperCase() || 'U'}
              </div>
              <svg className={`w-4 h-4 transition-transform ${showMenu ? 'rotate-180' : ''}`} 
                fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
              </svg>
            </button>

            {/* Dropdown Menu */}
            {showMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-xl border border-slate-200 shadow-lg overflow-hidden z-50">
                <div className="px-4 py-3 border-b border-slate-100">
                  <p className="text-sm font-semibold text-slate-900">{user?.username}</p>
                  <p className="text-xs text-slate-500">{user?.email}</p>
                </div>
                <a href="/settings" className="flex items-center gap-3 px-4 py-3 text-sm text-slate-700 hover:bg-slate-50 transition-colors">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  Settings
                </a>
                <button
                  onClick={handleLogout}
                  className="w-full text-left flex items-center gap-3 px-4 py-3 text-sm text-red-700 hover:bg-red-50 transition-colors border-t border-slate-100"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  Sign Out
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
