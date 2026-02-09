import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

function RiskChart({ data }) {
  const chartData = [
    { name: 'Low Risk', value: data?.low_risk_count || 0, fill: '#10b981' },
    { name: 'Medium Risk', value: data?.medium_risk_count || 0, fill: '#f59e0b' },
    { name: 'High Risk', value: data?.high_risk_count || 0, fill: '#ef4444' },
  ];

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 rounded-lg shadow-lg border border-slate-200">
          <p className="text-sm font-semibold text-slate-900">{payload[0].name}</p>
          <p className="text-sm font-bold text-slate-700">{payload[0].value} employees</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, value }) => `${name}: ${value}`}
            outerRadius={100}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="bottom"
            height={36}
            formatter={(value, entry) => (
              <span className="text-sm text-slate-600">{value}</span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
      
      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mt-6">
        {chartData.map((item, idx) => (
          <div key={idx} className="text-center p-3 bg-slate-50 rounded-lg">
            <div
              className="w-3 h-3 rounded-full inline-block mb-2"
              style={{ backgroundColor: item.fill }}
            ></div>
            <p className="text-sm text-slate-600">{item.name}</p>
            <p className="text-xl font-bold text-slate-900 mt-1">{item.value}</p>
            <p className="text-xs text-slate-500 mt-1">
              {((item.value / (chartData.reduce((sum, d) => sum + d.value, 0) || 1)) * 100).toFixed(1)}%
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default RiskChart;
