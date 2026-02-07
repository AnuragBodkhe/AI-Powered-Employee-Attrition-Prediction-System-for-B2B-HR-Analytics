import React, { useState } from 'react';
import { predictAPI } from '../../services/api';
import { DEPARTMENTS, JOB_ROLES, EDUCATION_LEVELS } from '../../utils/constants';
import { getRiskColor } from '../../utils/helpers';
import PredictionResult from './PredictionResult';
import './Prediction.css';

function ManualPrediction() {
  const [formData, setFormData] = useState({
    age: 30,
    department: 'Sales',
    job_role: 'Sales Manager',
    monthly_income: 5000,
    years_at_company: 5,
    over_time: false,
    job_satisfaction: 3,
    work_life_balance: 3,
    job_involvement: 3,
    education_level: 2,
    performance_rating: 3.5,
    num_companies_worked: 1,
    years_in_current_role: 2,
    years_since_last_promotion: 1,
    distance_from_home: 1,
    training_times_last_year: 2,
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : isNaN(value) ? value : parseFloat(value),
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await predictAPI.predictSingle(formData);
      setResult(response.data);
    } catch (err) {
      setError('Failed to make prediction. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="prediction-container">
      <h1>Manual Employee Prediction</h1>

      <div className="prediction-form-wrapper">
        <form onSubmit={handleSubmit} className="prediction-form">
          <div className="form-section">
            <h3>Personal Information</h3>
            <div className="form-row">
              <div className="form-group">
                <label>Age</label>
                <input
                  type="number"
                  name="age"
                  value={formData.age}
                  onChange={handleChange}
                  min="18"
                  max="65"
                />
              </div>
              <div className="form-group">
                <label>Distance from Home (km)</label>
                <input
                  type="number"
                  name="distance_from_home"
                  value={formData.distance_from_home}
                  onChange={handleChange}
                  min="0"
                />
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>Job Information</h3>
            <div className="form-row">
              <div className="form-group">
                <label>Department</label>
                <select name="department" value={formData.department} onChange={handleChange}>
                  {DEPARTMENTS.map((dept) => (
                    <option key={dept} value={dept}>
                      {dept}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Job Role</label>
                <select name="job_role" value={formData.job_role} onChange={handleChange}>
                  {JOB_ROLES.map((role) => (
                    <option key={role} value={role}>
                      {role}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Monthly Income ($)</label>
                <input
                  type="number"
                  name="monthly_income"
                  value={formData.monthly_income}
                  onChange={handleChange}
                  min="0"
                  step="100"
                />
              </div>
              <div className="form-group">
                <label>Education Level</label>
                <select name="education_level" value={formData.education_level} onChange={handleChange}>
                  {EDUCATION_LEVELS.map((level, idx) => (
                    <option key={idx} value={idx + 1}>
                      {level}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>Work Experience</h3>
            <div className="form-row">
              <div className="form-group">
                <label>Years at Company</label>
                <input
                  type="number"
                  name="years_at_company"
                  value={formData.years_at_company}
                  onChange={handleChange}
                  min="0"
                  max="40"
                />
              </div>
              <div className="form-group">
                <label>Years in Current Role</label>
                <input
                  type="number"
                  name="years_in_current_role"
                  value={formData.years_in_current_role}
                  onChange={handleChange}
                  min="0"
                  max="40"
                />
              </div>
              <div className="form-group">
                <label>Years Since Last Promotion</label>
                <input
                  type="number"
                  name="years_since_last_promotion"
                  value={formData.years_since_last_promotion}
                  onChange={handleChange}
                  min="0"
                  max="40"
                />
              </div>
              <div className="form-group">
                <label>Companies Worked</label>
                <input
                  type="number"
                  name="num_companies_worked"
                  value={formData.num_companies_worked}
                  onChange={handleChange}
                  min="0"
                />
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>Work-Life Metrics</h3>
            <div className="form-row">
              <div className="form-group">
                <label>Job Satisfaction (1-4)</label>
                <input
                  type="range"
                  name="job_satisfaction"
                  value={formData.job_satisfaction}
                  onChange={handleChange}
                  min="1"
                  max="4"
                />
                <span>{formData.job_satisfaction}</span>
              </div>
              <div className="form-group">
                <label>Work-Life Balance (1-4)</label>
                <input
                  type="range"
                  name="work_life_balance"
                  value={formData.work_life_balance}
                  onChange={handleChange}
                  min="1"
                  max="4"
                />
                <span>{formData.work_life_balance}</span>
              </div>
              <div className="form-group">
                <label>Job Involvement (1-4)</label>
                <input
                  type="range"
                  name="job_involvement"
                  value={formData.job_involvement}
                  onChange={handleChange}
                  min="1"
                  max="4"
                />
                <span>{formData.job_involvement}</span>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Performance Rating</label>
                <input
                  type="number"
                  name="performance_rating"
                  value={formData.performance_rating}
                  onChange={handleChange}
                  min="0"
                  max="4"
                  step="0.5"
                />
              </div>
              <div className="form-group">
                <label>Training Times Last Year</label>
                <input
                  type="number"
                  name="training_times_last_year"
                  value={formData.training_times_last_year}
                  onChange={handleChange}
                  min="0"
                />
              </div>
              <div className="form-group checkbox">
                <label>
                  <input
                    type="checkbox"
                    name="over_time"
                    checked={formData.over_time}
                    onChange={handleChange}
                  />
                  Works Overtime
                </label>
              </div>
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Predicting...' : 'Predict Risk'}
          </button>
        </form>

        {result && <PredictionResult result={result} />}
      </div>
    </div>
  );
}

export default ManualPrediction;
