import React, { useState, useEffect } from 'react';

function Reports() {
  const [selectedReport, setSelectedReport] = useState('attrition');

  const reports = [
    {
      id: 'attrition',
      name: 'Attrition Analysis',
      icon: '📊',
      description: 'Comprehensive attrition risk analysis report',
      metrics: [
        { label: 'Total Employees', value: '1,245', change: '+2.3%' },
        { label: 'Attrition Rate', value: '8.2%', change: '-0.5%' },
        { label: 'High Risk', value: '156', change: '+12' },
        { label: 'Predicted Loss', value: '$2.4M', change: '+$156K' },
      ],
    },
    {
      id: 'department',
      name: 'Department Report',
      icon: '🏢',
      description: 'Risk analysis by department',
      metrics: [
        { label: 'Highest Risk Dept', value: 'Sales', change: '42%' },
        { label: 'Most Stable Dept', value: 'HR', change: '2%' },
        { label: 'Biggest Change', value: 'IT', change: '+8%' },
        { label: 'Total Departments', value: '6', change: 'Unchanged' },
      ],
    },
    {
      id: 'predictions',
      name: 'Predictions Report',
      icon: '🤖',
      description: 'Model performance and predictions',
      metrics: [
        { label: 'Total Predictions', value: '3,847', change: '+341' },
        { label: 'Avg Accuracy', value: '94.2%', change: '+1.3%' },
        { label: 'Last Updated', value: 'Today', change: 'Now' },
        { label: 'Processed Files', value: '28', change: '+3' },
      ],
    },
  ];

  const currentReport = reports.find((r) => r.id === selectedReport);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Reports</h1>
        <p className="text-slate-600 mt-1">Generate and view comprehensive analytics reports</p>
      </div>

      {/* Report Selector */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {reports.map((report) => (
          <button
            key={report.id}
            onClick={() => setSelectedReport(report.id)}
            className={`p-4 rounded-xl border-2 transition-all text-left ${
              selectedReport === report.id
                ? 'border-indigo-600 bg-indigo-50'
                : 'border-slate-200 bg-white hover:border-slate-300'
            }`}
          >
            <div className="text-2xl mb-2">{report.icon}</div>
            <h3 className="font-semibold text-slate-900">{report.name}</h3>
            <p className="text-xs text-slate-600 mt-1">{report.description}</p>
          </button>
        ))}
      </div>

      {/* Report Content */}
      {currentReport && (
        <div className="space-y-6">
          {/* Header */}
          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-2xl font-bold text-slate-900">
                  {currentReport.name}
                </h2>
                <p className="text-slate-600 mt-1">
                  {currentReport.description}
                </p>
              </div>
              <button className="btn-primary py-2 px-4 rounded-lg text-sm font-medium">
                📥 Download PDF
              </button>
            </div>
          </div>

          {/* Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {currentReport.metrics.map((metric, idx) => (
              <div
                key={idx}
                className="bg-white rounded-xl border border-slate-200 p-4"
              >
                <p className="text-sm text-slate-600 font-medium">
                  {metric.label}
                </p>
                <div className="mt-2 flex items-end justify-between">
                  <div className="text-2xl font-bold text-slate-900">
                    {metric.value}
                  </div>
                  <span className="text-xs font-medium text-green-600 bg-green-50 px-2 py-1 rounded">
                    {metric.change}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Insights */}
          <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-xl border border-indigo-200 p-6">
            <h3 className="font-bold text-indigo-900 mb-4">Key Insights</h3>
            <ul className="space-y-3">
              <li className="flex gap-3">
                <span className="text-indigo-600 font-bold">•</span>
                <span className="text-indigo-900">
                  Sales department shows highest attrition risk (42%)
                </span>
              </li>
              <li className="flex gap-3">
                <span className="text-indigo-600 font-bold">•</span>
                <span className="text-indigo-900">
                  Employees with low job satisfaction are 3x more likely to leave
                </span>
              </li>
              <li className="flex gap-3">
                <span className="text-indigo-600 font-bold">•</span>
                <span className="text-indigo-900">
                  Model accuracy continues to improve with more data
                </span>
              </li>
            </ul>
          </div>

          {/* Export Options */}
          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <h3 className="font-bold text-slate-900 mb-4">Export Options</h3>
            <div className="flex flex-wrap gap-3">
              <button className="px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium hover:bg-slate-50">
                📄 PDF
              </button>
              <button className="px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium hover:bg-slate-50">
                📊 Excel
              </button>
              <button className="px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium hover:bg-slate-50">
                📧 Email
              </button>
              <button className="px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium hover:bg-slate-50">
                🔗 Share
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Reports;
