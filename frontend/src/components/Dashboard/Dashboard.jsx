import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../../services/api';
import MetricsCards from './MetricsCards';
import RiskChart from './RiskChart';
import DepartmentChart from './DepartmentChart';
import SalaryChart from './SalaryChart';
import FilterPanel from './FilterPanel';
import EmployeeTable from './EmployeeTable';

function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [riskData, setRiskData] = useState(null);
  const [departmentData, setDepartmentData] = useState(null);
  const [salaryData, setSalaryData] = useState(null);
  const [filterOptions, setFilterOptions] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({});

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError('');
    try {
      const [metricsRes, riskRes, deptRes, salaryRes, filtersRes] = await Promise.all([
        dashboardAPI.getMetrics(),
        dashboardAPI.getRiskDistribution(),
        dashboardAPI.getDepartmentComparison(),
        dashboardAPI.getSalaryImpact(),
        dashboardAPI.getFilterOptions(),
      ]);

      setMetrics(metricsRes.data);
      setRiskData(riskRes.data);
      setDepartmentData(deptRes.data);
      setSalaryData(salaryRes.data);
      setFilterOptions(filtersRes.data);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-slate-600 font-medium">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-6">
        <div className="flex items-start gap-4">
          <span className="text-2xl">⚠️</span>
          <div>
            <h3 className="font-semibold text-red-900">Unable to Load Dashboard</h3>
            <p className="text-red-700 text-sm mt-1">{error}</p>
            <button
              onClick={fetchDashboardData}
              className="btn-secondary py-2 px-4 text-sm rounded-lg mt-4"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">HR Analytics Dashboard</h1>
          <p className="text-slate-600 mt-2">Real-time employee attrition insights powered by AI</p>
        </div>
        <button className="btn-primary py-3 px-6 rounded-lg mt-4 sm:mt-0">
          📥 Export Report
        </button>
      </div>

      {/* KPI Cards */}
      {metrics && <MetricsCards metrics={metrics} />}

      {/* Filters */}
      {filterOptions && (
        <div className="card">
          <h2 className="text-lg font-bold text-slate-900 mb-4">Filters</h2>
          <FilterPanel
            options={filterOptions}
            onFilterChange={setFilters}
          />
        </div>
      )}

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {riskData && (
          <div className="card">
            <h2 className="text-lg font-bold text-slate-900 mb-4">Risk Distribution</h2>
            <RiskChart data={riskData} />
          </div>
        )}
        {salaryData && (
          <div className="card">
            <h2 className="text-lg font-bold text-slate-900 mb-4">Salary Impact Analysis</h2>
            <SalaryChart data={salaryData} />
          </div>
        )}
      </div>

      {/* Department Comparison */}
      {departmentData && (
        <div className="card">
          <h2 className="text-lg font-bold text-slate-900 mb-4">Department Comparison</h2>
          <DepartmentChart data={departmentData} />
        </div>
      )}

      {/* Employee Table */}
      <div className="card p-0">
        <div className="px-6 py-4 border-b border-slate-200">
          <h2 className="text-lg font-bold text-slate-900">Employees Overview</h2>
          <p className="text-slate-600 text-sm mt-1">All employees with risk assessment</p>
        </div>
        <div className="p-6">
          <EmployeeTable filters={filters} />
        </div>
      </div>

      {/* AI Insights Card */}
      <div className="bg-gradient-to-br from-teal-50 to-teal-100 rounded-xl p-6 border border-teal-200">
        <div className="flex items-start gap-4">
          <div className="text-4xl">💡</div>
          <div className="flex-1">
            <h3 className="text-lg font-bold text-teal-900">AI Insights</h3>
            <p className="text-teal-800 mt-2">
              Based on recent data analysis, we've identified that employees in the Sales department with 3-5 years 
              of experience have a 35% higher attrition risk. Consider implementing retention strategies for this group.
            </p>
            <div className="flex gap-3 mt-4">
              <button className="btn-success py-2 px-4 text-sm rounded-lg">
                View Recommendations
              </button>
              <button className="btn-secondary py-2 px-4 text-sm rounded-lg">
                Learn More
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
