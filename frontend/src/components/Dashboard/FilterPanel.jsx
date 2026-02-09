import React, { useState } from 'react';

function FilterPanel({ options, onFilterChange }) {
  const [expanded, setExpanded] = useState(true);

  const handleFilterChange = (filterName, value) => {
    onFilterChange((prev) => ({ ...prev, [filterName]: value }));
  };

  const filterGroups = [
    {
      name: 'department',
      label: 'Department',
      icon: '🏢',
      options: options?.departments || [],
    },
    {
      name: 'risk_level',
      label: 'Risk Level',
      icon: '⚠️',
      options: options?.risk_levels || [],
    },
    {
      name: 'job_role',
      label: 'Job Role',
      icon: '💼',
      options: options?.job_roles || [],
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
          <span>🔍</span> Refine Results
        </h3>
        <button
          onClick={() => setExpanded(!expanded)}
          className="btn-icon"
        >
          <svg
            className={`w-5 h-5 transition-transform ${expanded ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </button>
      </div>

      {expanded && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filterGroups.map((group) => (
            <div key={group.name} className="space-y-2">
              <label className="flex items-center gap-2 text-sm font-semibold text-slate-700">
                <span>{group.icon}</span>
                {group.label}
              </label>
              <select
                onChange={(e) => handleFilterChange(group.name, e.target.value)}
                className="w-full px-4 py-2.5 rounded-lg border-2 border-slate-200 bg-white hover:bg-slate-50 focus:border-indigo-500 focus:outline-none text-sm transition-all"
              >
                <option value="">All {group.label}s</option>
                {group.options.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          ))}
        </div>
      )}

      {/* Clear Filters */}
      <button
        onClick={() => {
          onFilterChange({});
        }}
        className="btn-secondary py-2 px-4 text-sm rounded-lg w-full"
      >
        ✕ Clear All Filters
      </button>
    </div>
  );
}

export default FilterPanel;
