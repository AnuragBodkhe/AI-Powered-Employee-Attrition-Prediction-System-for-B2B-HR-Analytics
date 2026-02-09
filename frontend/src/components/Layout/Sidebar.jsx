import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function Sidebar({ sidebarOpen, onClose }) {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  const navItems = [
    {
      group: 'ANALYTICS',
      items: [
        { path: '/dashboard', label: 'Dashboard', icon: '📊' },
        { path: '/employees', label: 'Employees', icon: '👥' },
        { path: '/analytics', label: 'Analytics', icon: '📈' },
      ],
    },
    {
      group: 'PREDICTIONS',
      items: [
        { path: '/predict/manual', label: 'Manual Prediction', icon: '👤' },
        { path: '/predict/excel', label: 'Bulk Upload', icon: '📁' },
        { path: '/results', label: 'Results', icon: '✓' },
      ],
    },
    {
      group: 'MANAGEMENT',
      items: [
        { path: '/reports', label: 'Reports', icon: '📄' },
        { path: '/settings', label: 'Settings', icon: '⚙️' },
      ],
    },
  ];

  const SidebarContent = () => (
    <nav className="p-4 sm:p-6 space-y-8 pb-32 lg:pb-8">
      {navItems.map((group, idx) => (
        <div key={idx}>
          <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3 px-3">
            {group.group}
          </h3>
          <div className="space-y-1">
            {group.items.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive(item.path)
                    ? 'bg-indigo-50 text-indigo-700 border-l-4 border-indigo-600 pl-3'
                    : 'text-slate-700 hover:bg-slate-100 border-l-4 border-transparent'
                }`}
              >
                <span className="text-lg w-5 text-center">{item.icon}</span>
                <span className="flex-1">{item.label}</span>
                {isActive(item.path) && (
                  <div className="w-2 h-2 bg-indigo-600 rounded-full animate-pulse"></div>
                )}
              </Link>
            ))}
          </div>
        </div>
      ))}

      {/* Bottom Section - AI Insights */}
      <div className="fixed bottom-0 left-0 right-0 lg:static p-4 sm:p-6 border-t border-slate-200 bg-gradient-to-t from-white to-slate-50 lg:bg-gradient-to-t lg:from-slate-50 lg:to-transparent">
        <div className="bg-gradient-to-br from-teal-50 to-cyan-50 rounded-xl p-4 border border-teal-200 shadow-sm">
          <div className="flex items-start gap-3 mb-3">
            <span className="text-lg flex-shrink-0">💡</span>
            <div className="flex-1 min-w-0">
              <h4 className="text-sm font-bold text-teal-900">AI Insights</h4>
              <p className="text-xs text-teal-700 mt-1 line-clamp-2">
                5 new predictions from bulk upload
              </p>
            </div>
          </div>
          <button className="w-full bg-teal-600 hover:bg-teal-700 text-white py-2 text-xs rounded-lg font-medium transition-colors">
            View Results
          </button>
        </div>
      </div>
    </nav>
  );

  return (
    <>
      {/* Desktop Sidebar - Fixed */}
      <aside className="hidden lg:block w-64 bg-white border-r border-slate-200 h-screen overflow-y-auto fixed left-0 top-16 shadow-sm">
        <SidebarContent />
      </aside>

      {/* Mobile Sidebar - Fixed overlay when open */}
      <aside
        className={`fixed left-0 top-16 w-64 h-screen bg-white border-r border-slate-200 overflow-y-auto z-40 lg:hidden transition-transform duration-300 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <SidebarContent />
      </aside>
    </>
  );
}

export default Sidebar;
