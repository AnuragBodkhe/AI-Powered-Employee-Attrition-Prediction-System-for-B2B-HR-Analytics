import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../../services/api';

function Employees() {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({
    department: '',
    risk_level: '',
    search: '',
  });
  const [filterOptions, setFilterOptions] = useState(null);

  useEffect(() => {
    fetchData();
  }, [page, filters]);

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      const [employeesRes, optionsRes] = await Promise.all([
        dashboardAPI.getEmployees({
          skip: (page - 1) * 10,
          limit: 10,
          ...filters,
        }),
        dashboardAPI.getFilterOptions(),
      ]);

      setEmployees(employeesRes.data.employees || []);
      setFilterOptions(optionsRes.data);
    } catch (err) {
      setError('Failed to load employees');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setPage(1);
  };

  const handleExport = async () => {
    try {
      await dashboardAPI.exportToExcel(filters);
      alert('Export started. Check your downloads folder.');
    } catch (err) {
      alert('Export failed');
      console.error(err);
    }
  };

  const getRiskColor = (riskLevel) => {
    if (riskLevel === 'High')
      return 'bg-red-100 text-red-800 border-red-300';
    if (riskLevel === 'Medium')
      return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    return 'bg-green-100 text-green-800 border-green-300';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Employees</h1>
          <p className="text-slate-600 mt-1">Manage and analyze employee data</p>
        </div>
        <button
          onClick={handleExport}
          className="btn-primary py-2 px-4 rounded-lg text-sm font-medium"
        >
          📥 Export
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6">
        <h2 className="text-lg font-bold text-slate-900 mb-4">Filters</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Department Filter */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Department
            </label>
            <select
              value={filters.department}
              onChange={(e) =>
                handleFilterChange('department', e.target.value)
              }
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="">All Departments</option>
              {filterOptions?.departments?.map((dept) => (
                <option key={dept.value} value={dept.value}>
                  {dept.label}
                </option>
              ))}
            </select>
          </div>

          {/* Risk Level Filter */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Risk Level
            </label>
            <select
              value={filters.risk_level}
              onChange={(e) =>
                handleFilterChange('risk_level', e.target.value)
              }
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="">All Risk Levels</option>
              {filterOptions?.risk_levels?.map((risk) => (
                <option key={risk.value} value={risk.value}>
                  {risk.label}
                </option>
              ))}
            </select>
          </div>

          {/* Search */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Search by Name
            </label>
            <input
              type="text"
              placeholder="Search employees..."
              value={filters.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* Table/Loading/Error */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="text-slate-600">Loading employees...</div>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-red-700">
          {error}
        </div>
      ) : employees.length === 0 ? (
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-8 text-center text-slate-600">
          <p className="text-lg font-medium">No employees found</p>
          <p className="text-sm mt-1">Try adjusting your filters</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-4 py-3 text-left font-semibold text-slate-900">
                    Name
                  </th>
                  <th className="px-4 py-3 text-left font-semibold text-slate-900">
                    Department
                  </th>
                  <th className="px-4 py-3 text-left font-semibold text-slate-900">
                    Job Role
                  </th>
                  <th className="px-4 py-3 text-right font-semibold text-slate-900">
                    Salary
                  </th>
                  <th className="px-4 py-3 text-center font-semibold text-slate-900">
                    Risk
                  </th>
                  <th className="px-4 py-3 text-center font-semibold text-slate-900">
                    Years
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {employees.map((emp) => (
                  <tr
                    key={emp.employee_id}
                    className="hover:bg-slate-50 transition-colors"
                  >
                    <td className="px-4 py-3 font-medium text-slate-900">
                      {emp.name}
                    </td>
                    <td className="px-4 py-3 text-slate-600">
                      {emp.department}
                    </td>
                    <td className="px-4 py-3 text-slate-600">
                      {emp.job_role}
                    </td>
                    <td className="px-4 py-3 text-right text-slate-900 font-medium">
                      ${emp.monthly_income.toFixed(0)}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span
                        className={`inline-block px-3 py-1 rounded-full text-xs font-semibold border ${getRiskColor(
                          emp.risk_level
                        )}`}
                      >
                        {emp.risk_level}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center text-slate-600">
                      {emp.years_at_company}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex justify-between items-center px-6 py-4 border-t border-slate-200">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium disabled:opacity-50"
            >
              Previous
            </button>
            <span className="text-slate-600 text-sm">Page {page}</span>
            <button
              onClick={() => setPage((p) => p + 1)}
              className="px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default Employees;
