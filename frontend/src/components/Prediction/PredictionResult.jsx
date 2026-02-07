import React from 'react';
import { getRiskColor, formatPercent } from '../../utils/helpers';
import './Prediction.css';

function PredictionResult({ result }) {
  return (
    <div className="prediction-result">
      <h2>Prediction Result</h2>

      <div className="risk-score-display">
        <div className="risk-score-large" style={{ color: getRiskColor(result.risk_level) }}>
          {formatPercent(result.risk_score)}
        </div>
        <div className="risk-level" style={{ color: getRiskColor(result.risk_level) }}>
          {result.risk_level} Risk
        </div>
      </div>

      {result.top_factors && result.top_factors.length > 0 && (
        <div className="top-factors">
          <h3>Top Contributing Factors</h3>
          <ul>
            {result.top_factors.map((factor, idx) => (
              <li key={idx}>
                <span className="factor-name">{factor.feature}</span>
                <span className="factor-importance">
                  {(factor.importance * 100).toFixed(1)}%
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="prediction-meta">
        <p><small>Confidence: {(result.prediction_probability * 100).toFixed(1)}%</small></p>
      </div>
    </div>
  );
}

export default PredictionResult;
