import React from 'react';
import { formatPercent } from '../../utils/helpers';
import { RISK_COLORS } from '../../utils/constants';

function MetricsCards({ metrics }) {
  const cards = [
    {
      label: 'Total Employees',
      value: metrics?.total_employees,
      icon: '👥',
      trend: '+2%',
      bgGradient: 'from-blue-50 to-blue-100',
      iconBg: 'bg-blue-200',
    },
    {
      label: 'Attrition Rate',
      value: formatPercent(metrics?.attrition_rate),
      icon: '📉',
      trend: '-0.5%',
      bgGradient: 'from-red-50 to-red-100',
      iconBg: 'bg-red-200',
    },
    {
      label: 'High Risk',
      value: metrics?.high_risk_count,
      icon: '⚠️',
      trend: '+5',
      bgGradient: 'from-red-50 to-orange-100',
      iconBg: 'bg-red-200',
    },
    {
      label: 'Medium Risk',
      value: metrics?.medium_risk_count,
      icon: '⏳',
      trend: '+3',
      bgGradient: 'from-amber-50 to-amber-100',
      iconBg: 'bg-amber-200',
    },
    {
      label: 'Low Risk',
      value: metrics?.low_risk_count,
      icon: '✓',
      trend: '+8',
      bgGradient: 'from-green-50 to-emerald-100',
      iconBg: 'bg-green-200',
    },
    {
      label: 'Avg Risk Score',
      value: formatPercent(metrics?.average_risk_score),
      icon: '📊',
      trend: '+1.2%',
      bgGradient: 'from-indigo-50 to-indigo-100',
      iconBg: 'bg-indigo-200',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
      {cards.map((card, index) => (
        <div
          key={index}
          className={`bg-gradient-to-br ${card.bgGradient} rounded-xl p-6 border border-white shadow-sm hover:shadow-md transition-all duration-300 group cursor-pointer`}
        >
          <div className="flex items-start justify-between mb-4">
            <div className={`${card.iconBg} rounded-lg p-3 text-xl`}>
              {card.icon}
            </div>
            <span className="text-xs font-semibold text-green-700 bg-green-100 px-3 py-1 rounded-full">
              {card.trend}
            </span>
          </div>
          <p className="text-sm text-gray-600 font-medium mb-2">{card.label}</p>
          <div className="flex items-baseline gap-2">
            <h3 className="text-3xl font-bold text-gray-900">{card.value}</h3>
          </div>
          <p className="text-xs text-gray-500 mt-3">This month</p>
        </div>
      ))}
    </div>
  );
}

export default MetricsCards;
