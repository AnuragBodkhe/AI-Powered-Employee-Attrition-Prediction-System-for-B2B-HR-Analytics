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
    <nav className="bg-neutral-0 border-b border-neutral-200 sticky top-0 z-40 shadow-xs">
      <div className="px-4 sm:px-6 lg:px-8 py-3.5 flex items-center justify-between">
        {/* Left Section - Menu & Logo */}
        <div className="flex items-center gap-4 flex-1 min-w-0">
          {/* Mobile Menu Button */}
          <button
            onClick={onToggleSidebar}
            className="p-2 -ml-2 lg:hidden rounded-md hover:bg-neutral-100 transition-all duration-200 text-neutral-600"
            aria-label="Toggle sidebar"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          {/* Logo */}
          <Link to="/dashboard" className="flex items-center gap-2.5 no-underline group shrink-0 focus-ring">
            <div className="w-9 h-9 bg-primary-600 rounded-md flex items-center justify-center shadow-sm group-hover:shadow-md transition-all duration-200">
              <span className="text-base font-bold text-neutral-0">✦</span>
            </div>
            <div className="hidden sm:block">
              <h1 className="text-sm font-semibold text-neutral-900 tracking-tight">HR Analytics</h1>
            </div>
          </Link>
        </div>

        {/* Center Section - Search (hidden on mobile) */}
        <div className="hidden md:flex items-center flex-1 max-w-xs mx-4">
          <div className="relative w-full group">
            <input
              type="text"
              placeholder="Search employees..."
              className="w-full px-4 py-2 rounded-lg border border-neutral-200 bg-neutral-50 text-sm font-400 text-neutral-900 placeholder-neutral-500 transition-all duration-200 focus:bg-neutral-0 focus:border-primary-500 focus:ring-1 focus:ring-primary-500/20"
            />
            <svg
              className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-neutral-400 group-focus-within:text-primary-600 transition-colors duration-200"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>

        {/* Right Section - Actions */}
        <div className="flex items-center gap-1 sm:gap-2 shrink-0">
          {/* Notifications Button */}
          <button
            className="p-2 -mr-2 rounded-md hover:bg-neutral-100 transition-all duration-200 text-neutral-600 hover:text-neutral-900 relative"
            aria-label="Notifications"
            title="Notifications"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
              />
            </svg>
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-primary-600 rounded-full"></span>
          </button>

          {/* User Profile Menu */}
          <div className="relative ml-1">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="flex items-center gap-2 px-2.5 py-1.5 rounded-md hover:bg-neutral-100 transition-all duration-200 focus-ring"
              aria-label="Profile menu"
              aria-expanded={showMenu}
            >
              <div className="w-8 h-8 bg-primary-600 rounded-md flex items-center justify-center text-neutral-0 text-xs font-bold shadow-sm flex-shrink-0">
                {user?.username?.[0]?.toUpperCase() || 'U'}
              </div>
              <svg
                className={`w-4 h-4 text-neutral-500 transition-transform duration-200 hidden sm:block ${
                  showMenu ? 'rotate-180' : ''
                }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
              </svg>
            </button>

            {/* Dropdown Menu */}
            {showMenu && (
              <div className="absolute right-0 mt-2.5 w-56 bg-neutral-0 rounded-lg border border-neutral-200 shadow-lg overflow-hidden z-50 animate-slide-down">
                {/* Header */}
                <div className="px-4 py-3 border-b border-neutral-100">
                  <p className="text-sm font-semibold text-neutral-900">{user?.full_name || user?.username}</p>
                  <p className="text-xs text-neutral-500 mt-0.5">{user?.email}</p>
                </div>

                {/* Menu Items */}
                <div className="py-1.5">
                  <Link
                    to="/settings"
                    onClick={() => setShowMenu(false)}
                    className="flex items-center gap-3 px-4 py-2 text-sm text-neutral-700 hover:bg-neutral-50 transition-colors duration-150"
                  >
                    <svg className="w-4 h-4 text-neutral-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={1.5}
                        d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                      />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    <span>Settings</span>
                  </Link>
                </div>

                {/* Logout Button */}
                <button
                  onClick={() => {
                    setShowMenu(false);
                    handleLogout();
                  }}
                  className="w-full text-left flex items-center gap-3 px-4 py-2 text-sm text-danger hover:bg-red-50 transition-colors duration-150 border-t border-neutral-100"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                    />
                  </svg>
                  <span>Sign Out</span>
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
