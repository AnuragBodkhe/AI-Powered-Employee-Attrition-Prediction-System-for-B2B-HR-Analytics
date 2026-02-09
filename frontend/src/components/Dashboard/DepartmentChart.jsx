import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';

function DepartmentChart({ data }) {
  const chartData = data?.departments || [];
  const colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#06b6d4'];

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 rounded-lg shadow-lg border border-slate-200">
          <p className="text-sm font-semibold text-slate-900">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div>
      <ResponsiveContainer width="100%" height={350}>
        <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="department" stroke="#6b7280" />
          <YAxis stroke="#6b7280" />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ paddingTop: '20px' }}
            formatter={(value) => <span className="text-sm text-slate-600">{value}</span>}
          />
          <Bar dataKey="attrition_rate" fill="#ef4444" name="Attrition Rate (%)" radius={[8, 8, 0, 0]} />
          <Bar dataKey="avg_risk_score" fill="#f59e0b" name="Avg Risk Score" radius={[8, 8, 0, 0]} />
          <Bar dataKey="employee_count" fill="#4f46e5" name="Employees" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>

      {/* Department Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mt-6">
        {chartData.slice(0, 5).map((dept, idx) => (
          <div key={idx} className="bg-slate-50 rounded-lg p-4 border border-slate-200">
            <div className="flex items-center gap-2 mb-3">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: colors[idx % colors.length] }}
              ></div>
              <p className="text-sm font-semibold text-slate-900 truncate">{dept.department}</p>
            </div>
            <p className="text-2xl font-bold text-slate-900">{dept.employee_count}</p>
            <p className="text-xs text-slate-600 mt-2">Employees</p>
            <p className="text-sm text-red-600 font-semibold mt-2">{dept.attrition_rate?.toFixed(1)}%</p>
            <p className="text-xs text-slate-500">Attrition Rate</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default DepartmentChart;
