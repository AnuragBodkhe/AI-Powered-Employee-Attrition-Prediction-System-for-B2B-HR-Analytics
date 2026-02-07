import React from 'react';
import { getRiskColor, formatPercent } from '../../utils/helpers';

function PredictionResult({ result, onBackClick }) {
  const getRiskBadgeInfo = (riskLevel) => {
    const info = {
      High: {
        icon: '🔴',
        bg: 'from-red-50 to-red-100',
        border: 'border-red-200',
        text: 'text-red-900',
        subbg: 'bg-red-100',
        recommendation: 'Immediate focus required. Consider targeted retention initiatives.',
      },
      Medium: {
        icon: '🟡',
        bg: 'from-amber-50 to-amber-100',
        border: 'border-amber-200',
        text: 'text-amber-900',
        subbg: 'bg-amber-100',
        recommendation: 'Monitor closely. Proactive engagement recommended.',
      },
      Low: {
        icon: '🟢',
        bg: 'from-green-50 to-green-100',
        border: 'border-green-200',
        text: 'text-green-900',
        subbg: 'bg-green-100',
        recommendation: 'Employee appears satisfied. Continue regular engagement.',
      },
    };
    return info[riskLevel] || info.Low;
  };

  const riskInfo = getRiskBadgeInfo(result.risk_level);

  return (
    <div className="space-y-8">
      {/* Back Button */}
      {onBackClick && (
        <button
          onClick={onBackClick}
          className="btn-secondary py-2 px-4 rounded-lg text-sm"
        >
          ← Back to Prediction Form
        </button>
      )}

      {/* Main Risk Display */}
      <div className={`bg-gradient-to-br ${riskInfo.bg} border-2 ${riskInfo.border} rounded-2xl p-8 md:p-12`}>
        <div className="flex items-center justify-between mb-8">
          <div>
            <p className="text-sm font-semibold text-slate-600 uppercase tracking-wide mb-2">
              Attrition Risk Assessment
            </p>
            <h1 className={`text-5xl md:text-6xl font-bold ${riskInfo.text}`}>
              {formatPercent(result.risk_score)}
            </h1>
          </div>
          <div className="text-7xl">{riskInfo.icon}</div>
        </div>

        <div className="flex items-center justify-between">
          <div>
            <p className={`text-2xl font-bold ${riskInfo.text}`}>
              {result.risk_level} Risk
            </p>
            <p className={`text-sm mt-2 ${riskInfo.text} opacity-75`}>
              {riskInfo.recommendation}
            </p>
          </div>
          <div className={`text-right p-4 rounded-lg ${riskInfo.subbg}`}>
            <p className="text-xs text-slate-600 font-medium mb-1">Confidence Score</p>
            <p className={`text-3xl font-bold ${riskInfo.text}`}>
              {(result.prediction_probability * 100).toFixed(0)}%
            </p>
          </div>
        </div>
      </div>

      {/* Risk Score Meter */}
      <div className="card">
        <h2 className="text-lg font-bold text-slate-900 mb-4">Risk Score Distribution</h2>
        <div className="space-y-4">
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-slate-700">Attrition Probability</span>
              <span className="text-sm font-bold text-indigo-600">
                {(result.risk_score * 100).toFixed(1)}%
              </span>
            </div>
            <div className="w-full h-3 bg-slate-200 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all ${
                  result.risk_score > 0.7
                    ? 'bg-red-500'
                    : result.risk_score > 0.4
                    ? 'bg-amber-500'
                    : 'bg-green-500'
                }`}
                style={{ width: `${result.risk_score * 100}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Top Contributing Factors */}
      {result.top_factors && result.top_factors.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-bold text-slate-900 mb-6">Key Factors Influencing Risk</h2>
          <div className="space-y-4">
            {result.top_factors.map((factor, idx) => {
              const importance = factor.importance * 100;
              return (
                <div key={idx} className="flex items-center gap-4">
                  <div className="flex-1">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium text-slate-900 text-sm">
                        {idx + 1}. {factor.feature}
                      </span>
                      <span className="text-sm font-bold text-indigo-600">
                        {importance.toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-indigo-500 to-indigo-600 transition-all"
                        style={{ width: `${importance}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
          <p className="text-xs text-slate-500 mt-6">
            💡 These factors have the highest correlation with employee attrition in your organization.
          </p>
        </div>
      )}

      {/* Recommendations */}
      <div className="bg-gradient-to-br from-blue-50 to-blue-100 border-2 border-blue-200 rounded-xl p-6">
        <h3 className="text-lg font-bold text-blue-900 mb-4 flex items-center gap-2">
          <span>💡</span> Recommendations
        </h3>
        <ul className="space-y-3 text-sm text-blue-800">
          {result.risk_level === 'High' && (
            <>
              <li className="flex gap-3">
                <span>✓</span>
                <span>Schedule immediate one-on-one meeting to understand concerns</span>
              </li>
              <li className="flex gap-3">
                <span>✓</span>
                <span>Review compensation and growth opportunities</span>
              </li>
              <li className="flex gap-3">
                <span>✓</span>
                <span>Discuss career development and mentorship programs</span>
              </li>
              <li className="flex gap-3">
                <span>✓</span>
                <span>Monitor engagement and satisfaction metrics closely</span>
              </li>
            </>
          )}
          {result.risk_level === 'Medium' && (
            <>
              <li className="flex gap-3">
                <span>✓</span>
                <span>Increase regular check-ins and feedback sessions</span>
              </li>
              <li className="flex gap-3">
                <span>✓</span>
                <span>Assess work-life balance and project assignments</span>
              </li>
              <li className="flex gap-3">
                <span>✓</span>
                <span>Explore skill development and training opportunities</span>
              </li>
            </>
          )}
          {result.risk_level === 'Low' && (
            <>
              <li className="flex gap-3">
                <span>✓</span>
                <span>Employee appears engaged. Continue nurturing the relationship</span>
              </li>
              <li className="flex gap-3">
                <span>✓</span>
                <span>Maintain regular feedback and recognition programs</span>
              </li>
              <li className="flex gap-3">
                <span>✓</span>
                <span>Leverage employee as mentor or ambassador</span>
              </li>
            </>
          )}
        </ul>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button className="btn-primary py-3 px-6 rounded-lg font-semibold flex-1">
          📄 Generate Report
        </button>
        <button className="btn-secondary py-3 px-6 rounded-lg font-semibold flex-1">
          💾 Save Assessment
        </button>
      </div>
    </div>
  );
}

export default PredictionResult;
