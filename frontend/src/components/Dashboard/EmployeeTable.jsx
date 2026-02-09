import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../../services/api';
import { getRiskColor, formatCurrency } from '../../utils/helpers';

function EmployeeTable({ filters }) {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sortConfig, setSortConfig] = useState({ key: 'risk_score', direction: 'desc' });
  const [pagination, setPagination] = useState({ page: 0, limit: 10, total: 0 });

  useEffect(() => {
    fetchEmployees();
  }, [filters, pagination.page]);

  const fetchEmployees = async () => {
    setLoading(true);
    try {
      const response = await dashboardAPI.getEmployees({
        skip: pagination.page * pagination.limit,
        limit: pagination.limit,
        ...filters,
      });
      setEmployees(response.data.employees);
      setPagination((prev) => ({ ...prev, total: response.data.total }));
    } catch (error) {
      console.error('Failed to fetch employees', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskBadge = (riskLevel) => {
    const badges = {
      High: { bg: 'bg-red-100', text: 'text-red-700', icon: '🔴' },
      Medium: { bg: 'bg-amber-100', text: 'text-amber-700', icon: '🟡' },
      Low: { bg: 'bg-green-100', text: 'text-green-700', icon: '🟢' },
    };
    const badge = badges[riskLevel] || badges.Low;
    return badge;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-3"></div>
          <p className="text-slate-600 text-sm">Loading employees...</p>
        </div>
      </div>
    );
  }

  if (employees.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-500 text-lg">No employees found</p>
      </div>
    );
  }

  const totalPages = Math.ceil(pagination.total / pagination.limit);

  return (
    <div className="space-y-4">
      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50">
              <th className="px-6 py-3 text-left text-xs font-bold text-slate-700 uppercase tracking-wider">
                Employee
              </th>
              <th className="px-6 py-3 text-left text-xs font-bold text-slate-700 uppercase tracking-wider">
                Department
              </th>
              <th className="px-6 py-3 text-left text-xs font-bold text-slate-700 uppercase tracking-wider">
                Role
              </th>
              <th className="px-6 py-3 text-left text-xs font-bold text-slate-700 uppercase tracking-wider">
                Risk Score
              </th>
              <th className="px-6 py-3 text-left text-xs font-bold text-slate-700 uppercase tracking-wider">
                Risk Level
              </th>
              <th className="px-6 py-3 text-left text-xs font-bold text-slate-700 uppercase tracking-wider">
                Experience
              </th>
              <th className="px-6 py-3 text-left text-xs font-bold text-slate-700 uppercase tracking-wider">
                Action
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {employees.map((emp) => {
              const riskBadge = getRiskBadge(emp.risk_level);
              return (
                <tr
                  key={emp.employee_id}
                  className="hover:bg-slate-50 transition-colors duration-150"
                >
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">
                        {emp.name?.[0]?.toUpperCase() || 'E'}
                      </div>
                      <div>
                        <p className="font-medium text-slate-900 text-sm">{emp.name}</p>
                        <p className="text-xs text-slate-500">ID: {emp.employee_id}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-600">{emp.department}</td>
                  <td className="px-6 py-4 text-sm text-slate-600">{emp.job_role}</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <div className="w-12 h-2 bg-slate-200 rounded-full overflow-hidden">
                        <div
                          className={`h-full transition-all ${
                            emp.risk_score > 0.7
                              ? 'bg-red-500'
                              : emp.risk_score > 0.4
                              ? 'bg-amber-500'
                              : 'bg-green-500'
                          }`}
                          style={{ width: `${emp.risk_score * 100}%` }}
                        ></div>
                      </div>
                      <span className="font-bold text-sm text-slate-900">
                        {(emp.risk_score * 100).toFixed(0)}%
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold ${riskBadge.bg} ${riskBadge.text}`}>
                      <span>{riskBadge.icon}</span>
                      {emp.risk_level}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-600">
                    {emp.years_at_company} year{emp.years_at_company !== 1 ? 's' : ''}
                  </td>
                  <td className="px-6 py-4">
                    <button className="text-indigo-600 hover:text-indigo-700 font-medium text-sm transition-colors">
                      View →
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between pt-4 border-t border-slate-200">
        <p className="text-sm text-slate-600">
          Showing <span className="font-semibold">{pagination.page * pagination.limit + 1}</span> to{' '}
          <span className="font-semibold">
            {Math.min((pagination.page + 1) * pagination.limit, pagination.total)}
          </span>{' '}
          of <span className="font-semibold">{pagination.total}</span> employees
        </p>

        <div className="flex items-center gap-2">
          <button
            onClick={() =>
              setPagination((prev) =>
                prev.page > 0 ? { ...prev, page: prev.page - 1 } : prev
              )
            }
            disabled={pagination.page === 0}
            className="btn-secondary py-2 px-3 text-sm rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ← Previous
          </button>

          <div className="flex items-center gap-1">
            {Array.from({ length: Math.min(5, totalPages) }).map((_, i) => {
              const pageNum = i;
              return (
                <button
                  key={pageNum}
                  onClick={() => setPagination((prev) => ({ ...prev, page: pageNum }))}
                  className={`w-10 h-10 rounded-lg font-medium text-sm transition-colors ${
                    pagination.page === pageNum
                      ? 'bg-indigo-600 text-white'
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  }`}
                >
                  {pageNum + 1}
                </button>
              );
            })}
          </div>

          <button
            onClick={() =>
              setPagination((prev) =>
                (prev.page + 1) * prev.limit < prev.total
                  ? { ...prev, page: prev.page + 1 }
                  : prev
              )
            }
            disabled={(pagination.page + 1) * pagination.limit >= pagination.total}
            className="btn-secondary py-2 px-3 text-sm rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next →
          </button>
        </div>
      </div>
    </div>
  );
}

export default EmployeeTable;
