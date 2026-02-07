import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function Sidebar() {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  const navItems = [
    {
      group: 'Analytics',
      items: [
        { path: '/dashboard', label: 'Dashboard', icon: '📊' },
        { path: '/employees', label: 'Employees', icon: '👥' },
        { path: '/analytics', label: 'Analytics', icon: '📈' },
      ],
    },
    {
      group: 'Predictions',
      items: [
        { path: '/predict/manual', label: 'Manual Prediction', icon: '👤' },
        { path: '/predict/excel', label: 'Bulk Upload', icon: '📁' },
        { path: '/results', label: 'Results', icon: '✓' },
      ],
    },
    {
      group: 'Management',
      items: [
        { path: '/reports', label: 'Reports', icon: '📄' },
        { path: '/settings', label: 'Settings', icon: '⚙️' },
      ],
    },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 h-screen overflow-y-auto fixed left-0 top-16 hidden lg:block">
      <nav className="p-6 space-y-8">
        {navItems.map((group, idx) => (
          <div key={idx}>
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3 px-3">
              {group.group}
            </h3>
            <div className="space-y-2">
              {group.items.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive(item.path)
                      ? 'bg-indigo-50 text-indigo-700 border-l-2 border-indigo-600'
                      : 'text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  <span className="text-lg">{item.icon}</span>
                  <span>{item.label}</span>
                  {isActive(item.path) && (
                    <div className="ml-auto w-2 h-2 bg-indigo-600 rounded-full"></div>
                  )}
                </Link>
              ))}
            </div>
          </div>
        ))}

        {/* Bottom Section */}
        <div className="absolute bottom-0 left-0 right-0 p-6 border-t border-slate-200 bg-gradient-to-t from-slate-50 to-transparent">
          <div className="bg-teal-50 rounded-xl p-4 border border-teal-200">
            <div className="flex items-start gap-2 mb-2">
              <span className="text-lg">💡</span>
              <div>
                <h4 className="text-sm font-semibold text-teal-900">AI Insights</h4>
                <p className="text-xs text-teal-700 mt-1">
                  Analyze 5 new predictions from bulk upload
                </p>
              </div>
            </div>
            <button className="w-full btn-success py-2 text-xs rounded-lg mt-3">
              View Results
            </button>
          </div>
        </div>
      </nav>
    </aside>
  );
}

export default Sidebar;
