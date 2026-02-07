import React, { useState } from 'react';
import { predictAPI } from '../../services/api';
import { DEPARTMENTS, JOB_ROLES, EDUCATION_LEVELS } from '../../utils/constants';
import { getRiskColor } from '../../utils/helpers';
import PredictionResult from './PredictionResult';

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

  const formSections = [
    {
      title: '👤 Personal Information',
      icon: '👤',
      fields: [
        {
          name: 'age',
          label: 'Age',
          type: 'number',
          min: 18,
          max: 65,
          width: 'col-span-1',
        },
        {
          name: 'distance_from_home',
          label: 'Distance from Home (km)',
          type: 'number',
          min: 0,
          width: 'col-span-1',
        },
      ],
    },
    {
      title: '💼 Job Information',
      icon: '💼',
      fields: [
        {
          name: 'department',
          label: 'Department',
          type: 'select',
          options: DEPARTMENTS,
          width: 'col-span-1',
        },
        {
          name: 'job_role',
          label: 'Job Role',
          type: 'select',
          options: JOB_ROLES,
          width: 'col-span-1',
        },
        {
          name: 'monthly_income',
          label: 'Monthly Income ($)',
          type: 'number',
          min: 0,
          step: 100,
          width: 'col-span-1',
        },
        {
          name: 'education_level',
          label: 'Education Level',
          type: 'select',
          options: EDUCATION_LEVELS,
          width: 'col-span-1',
        },
      ],
    },
    {
      title: '📊 Work Experience',
      icon: '📊',
      fields: [
        {
          name: 'years_at_company',
          label: 'Years at Company',
          type: 'number',
          min: 0,
          max: 40,
          width: 'col-span-1',
        },
        {
          name: 'years_in_current_role',
          label: 'Years in Current Role',
          type: 'number',
          min: 0,
          max: 40,
          width: 'col-span-1',
        },
        {
          name: 'years_since_last_promotion',
          label: 'Years Since Last Promotion',
          type: 'number',
          min: 0,
          max: 40,
          width: 'col-span-1',
        },
        {
          name: 'num_companies_worked',
          label: 'Companies Worked',
          type: 'number',
          min: 0,
          width: 'col-span-1',
        },
      ],
    },
    {
      title: '⭐ Work-Life Metrics',
      icon: '⭐',
      fields: [
        {
          name: 'job_satisfaction',
          label: 'Job Satisfaction (1-4)',
          type: 'slider',
          min: 1,
          max: 4,
          width: 'col-span-1',
        },
        {
          name: 'work_life_balance',
          label: 'Work-Life Balance (1-4)',
          type: 'slider',
          min: 1,
          max: 4,
          width: 'col-span-1',
        },
        {
          name: 'job_involvement',
          label: 'Job Involvement (1-4)',
          type: 'slider',
          min: 1,
          max: 4,
          width: 'col-span-1',
        },
        {
          name: 'performance_rating',
          label: 'Performance Rating (0-4)',
          type: 'number',
          min: 0,
          max: 4,
          step: 0.5,
          width: 'col-span-1',
        },
        {
          name: 'training_times_last_year',
          label: 'Training Times Last Year',
          type: 'number',
          min: 0,
          width: 'col-span-1',
        },
        {
          name: 'over_time',
          label: 'Works Overtime',
          type: 'checkbox',
          width: 'col-span-1',
        },
      ],
    },
  ];

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Single Prediction</h1>
        <p className="text-slate-600 mt-2">
          Analyze an individual employee's attrition risk using AI
        </p>
      </div>

      {result ? (
        <PredictionResult result={result} onBackClick={() => setResult(null)} />
      ) : (
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Form Sections */}
          {formSections.map((section, idx) => (
            <div key={idx} className="card">
              <div className="flex items-center gap-3 mb-6 pb-4 border-b border-slate-200">
                <span className="text-2xl">{section.icon}</span>
                <h2 className="text-lg font-bold text-slate-900">{section.title}</h2>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {section.fields.map((field) => (
                  <div
                    key={field.name}
                    className={`${field.width || 'col-span-1'}`}
                  >
                    {field.type === 'select' ? (
                      <>
                        <label className="block text-sm font-semibold text-slate-700 mb-2">
                          {field.label}
                        </label>
                        <select
                          name={field.name}
                          value={formData[field.name]}
                          onChange={handleChange}
                          className="w-full px-4 py-2.5 rounded-lg border-2 border-slate-200 focus:border-indigo-500 focus:outline-none transition-all bg-white"
                        >
                          {field.options.map((opt, idx) => (
                            <option key={idx} value={opt}>
                              {opt}
                            </option>
                          ))}
                        </select>
                      </>
                    ) : field.type === 'checkbox' ? (
                      <div className="flex items-center h-full pt-2">
                        <input
                          id={field.name}
                          type="checkbox"
                          name={field.name}
                          checked={formData[field.name]}
                          onChange={handleChange}
                          className="w-4 h-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 cursor-pointer"
                        />
                        <label
                          htmlFor={field.name}
                          className="ml-3 text-sm text-slate-700 font-medium cursor-pointer"
                        >
                          {field.label}
                        </label>
                      </div>
                    ) : field.type === 'slider' ? (
                      <>
                        <label className="block text-sm font-semibold text-slate-700 mb-3">
                          {field.label}
                        </label>
                        <div className="space-y-3">
                          <input
                            type="range"
                            name={field.name}
                            value={formData[field.name]}
                            onChange={handleChange}
                            min={field.min}
                            max={field.max}
                            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer"
                            style={{
                              background: `linear-gradient(to right, #4f46e5 0%, #4f46e5 ${
                                ((formData[field.name] - field.min) /
                                  (field.max - field.min)) *
                                100
                              }%, #e5e7eb ${
                                ((formData[field.name] - field.min) /
                                  (field.max - field.min)) *
                                100
                              }%, #e5e7eb 100%)`,
                            }}
                          />
                          <div className="flex justify-between items-center">
                            <span className="text-2xl font-bold text-indigo-600">
                              {formData[field.name]}
                            </span>
                            <span className="text-xs text-slate-500">
                              {field.min} - {field.max}
                            </span>
                          </div>
                        </div>
                      </>
                    ) : (
                      <>
                        <label className="block text-sm font-semibold text-slate-700 mb-2">
                          {field.label}
                        </label>
                        <input
                          type={field.type}
                          name={field.name}
                          value={formData[field.name]}
                          onChange={handleChange}
                          min={field.min}
                          max={field.max}
                          step={field.step}
                          className="w-full px-4 py-2.5 rounded-lg border-2 border-slate-200 focus:border-indigo-500 focus:outline-none transition-all"
                        />
                      </>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}

          {/* Error Message */}
          {error && (
            <div className="error-message">
              <p className="text-sm">{error}</p>
            </div>
          )}

          {/* Submit Button */}
          <div className="flex gap-3">
            <button
              type="submit"
              disabled={loading}
              className="btn-primary py-3 px-6 rounded-lg font-semibold flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="loading-spinner" style={{ width: '16px', height: '16px', borderWidth: '2px' }}></div>
                  <span>Analyzing...</span>
                </div>
              ) : (
                '🔮 Predict Attrition Risk'
              )}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}

export default ManualPrediction;
