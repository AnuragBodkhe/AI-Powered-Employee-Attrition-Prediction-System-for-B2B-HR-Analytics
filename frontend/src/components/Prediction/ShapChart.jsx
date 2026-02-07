import React from 'react';
import './Prediction.css';

function ShapChart({ shapValues }) {
  return (
    <div className="shap-chart-container">
      <h3>SHAP Explainability</h3>
      <p>SHAP visualization placeholder - Integrate with SHAP.js or custom visualization</p>
      <pre>{JSON.stringify(shapValues, null, 2)}</pre>
    </div>
  );
}

export default ShapChart;
