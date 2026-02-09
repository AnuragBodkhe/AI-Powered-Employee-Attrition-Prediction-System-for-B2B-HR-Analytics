import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../../services/api';
import RiskChart from '../Dashboard/RiskChart';
import DepartmentChart from '../Dashboard/DepartmentChart';
import SalaryChart from '../Dashboard/SalaryChart';

function Analytics() {
  const [riskData, setRiskData] = useState(null);
  const [departmentData, setDepartmentData] = useState(null);
  const [salaryData, setSalaryData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  const fetchAnalyticsData = async () => {
    setLoading(true);
    setError('');
    try {
      const [riskRes, deptRes, salaryRes] = await Promise.all([
        dashboardAPI.getRiskDistribution(),
        dashboardAPI.getDepartmentComparison(),
        dashboardAPI.getSalaryImpact(),
      ]);

      setRiskData(riskRes.data);
      setDepartmentData(deptRes.data);
      setSalaryData(salaryRes.data);
    } catch (err) {
      setError('Failed to load analytics');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="text-slate-600">Loading analytics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-red-700">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Analytics</h1>
        <p className="text-slate-600 mt-1">Deep dive into attrition patterns and trends</p>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risk Distribution */}
        {riskData && (
          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <h2 className="text-lg font-bold text-slate-900 mb-4">Risk Distribution</h2>
            <RiskChart data={riskData} />
          </div>
        )}

        {/* Salary Impact */}
        {salaryData && (
          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <h2 className="text-lg font-bold text-slate-900 mb-4">Salary Impact</h2>
            <SalaryChart data={salaryData} />
          </div>
        )}
      </div>

      {/* Department Comparison - Full Width */}
      {departmentData && (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="text-lg font-bold text-slate-900 mb-4">Department Comparison</h2>
          <DepartmentChart data={departmentData} />
        </div>
      )}

      {/* Insights */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
          <h3 className="font-semibold text-blue-900 mb-2">Key Finding 1</h3>
          <p className="text-sm text-blue-700">
            Employees with lower salaries show 45% higher attrition risk
          </p>
        </div>
        <div className="bg-purple-50 border border-purple-200 rounded-xl p-4">
          <h3 className="font-semibold text-purple-900 mb-2">Key Finding 2</h3>
          <p className="text-sm text-purple-700">
            Sales department has the highest attrition rate at 38%
          </p>
        </div>
        <div className="bg-orange-50 border border-orange-200 rounded-xl p-4">
          <h3 className="font-semibold text-orange-900 mb-2">Key Finding 3</h3>
          <p className="text-sm text-orange-700">
            Job satisfaction is the strongest predictor of retention
          </p>
        </div>
      </div>
    </div>
  );
}

export default Analytics;
