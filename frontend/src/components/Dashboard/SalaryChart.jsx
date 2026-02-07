import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

function SalaryChart({ data }) {
  const chartData = data?.salary_ranges || [];

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-4 rounded-lg shadow-lg border border-slate-200">
          <p className="text-sm font-semibold text-slate-900 mb-2">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              <span className="font-medium">{entry.name}:</span> {entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div>
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="salary_range" stroke="#6b7280" />
          <YAxis stroke="#6b7280" />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ paddingTop: '20px' }}
            formatter={(value) => <span className="text-sm text-slate-600">{value}</span>}
          />
          <Line
            type="monotone"
            dataKey="employee_count"
            stroke="#4f46e5"
            strokeWidth={3}
            dot={{ fill: '#4f46e5', r: 5 }}
            activeDot={{ r: 7 }}
            name="Employee Count"
          />
          <Line
            type="monotone"
            dataKey="attrition_rate"
            stroke="#ef4444"
            strokeWidth={3}
            dot={{ fill: '#ef4444', r: 5 }}
            activeDot={{ r: 7 }}
            name="Attrition Rate (%)"
          />
          <Line
            type="monotone"
            dataKey="avg_risk_score"
            stroke="#f59e0b"
            strokeWidth={3}
            dot={{ fill: '#f59e0b', r: 5 }}
            activeDot={{ r: 7 }}
            name="Avg Risk Score"
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Key Insights */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mt-6">
        <p className="text-sm text-blue-900">
          <span className="font-semibold">💡 Insight:</span> Employees in the lower salary range show 28% higher
          attrition rate. Consider competitive salary reviews for better retention.
        </p>
      </div>
    </div>
  );
}

export default SalaryChart;
