import React, { useState } from 'react';
import { predictAPI } from '../../services/api';

function ExcelUpload() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [progress, setProgress] = useState(0);
  const [dragActive, setDragActive] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    validateAndSetFile(selectedFile);
  };

  const validateAndSetFile = (selectedFile) => {
    if (
      selectedFile &&
      (selectedFile.type ===
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
        selectedFile.type === 'application/vnd.ms-excel')
    ) {
      setFile(selectedFile);
      setError('');
    } else {
      setError('Please select a valid Excel file (.xlsx or .xls)');
      setFile(null);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setError('');

    try {
      const response = await predictAPI.uploadExcel(file);
      setResult(response.data);

      if (response.data.job_id) {
        pollUploadStatus(response.data.upload_id);
      }
    } catch (err) {
      setError('Failed to upload file. Please try again.');
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  const pollUploadStatus = async (uploadId) => {
    const interval = setInterval(async () => {
      try {
        const response = await predictAPI.getStatus(uploadId);
        setProgress(response.data.progress);

        if (
          response.data.status === 'completed' ||
          response.data.status === 'failed'
        ) {
          clearInterval(interval);
          setResult(response.data);
        }
      } catch (err) {
        clearInterval(interval);
      }
    }, 2000);
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Bulk Upload</h1>
        <p className="text-slate-600 mt-2">
          Upload an Excel file with employee data for batch AI predictions
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Upload Area */}
        <div className="lg:col-span-2 card">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Drag & Drop Area */}
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-xl p-12 transition-all text-center cursor-pointer ${
                dragActive
                  ? 'border-indigo-500 bg-indigo-50'
                  : 'border-slate-300 bg-slate-50 hover:border-slate-400'
              }`}
            >
              <input
                id="file-upload"
                type="file"
                accept=".xlsx,.xls"
                onChange={handleFileChange}
                disabled={uploading}
                className="hidden"
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer flex flex-col items-center justify-center"
              >
                <div className="text-4xl mb-3">📊</div>
                <h3 className="text-lg font-bold text-slate-900">
                  Drop your Excel file here
                </h3>
                <p className="text-slate-600 mt-2">
                  or click to browse from your computer
                </p>
                <p className="text-xs text-slate-500 mt-3">
                  Supported formats: .xlsx, .xls
                </p>
              </label>
            </div>

            {/* File Selected Info */}
            {file && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <span className="text-2xl">✓</span>
                  <div>
                    <p className="font-semibold text-green-900">{file.name}</p>
                    <p className="text-sm text-green-700 mt-1">
                      Size: {(file.size / 1024).toFixed(2)} KB
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setFile(null)}
                  className="text-green-600 hover:text-green-700 font-medium"
                >
                  Remove
                </button>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="error-message">
                <p className="text-sm">{error}</p>
              </div>
            )}

            {/* Upload Progress */}
            {uploading && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <div className="flex items-start gap-3">
                  <div className="loading-spinner" style={{ width: '20px', height: '20px', borderWidth: '2px' }}></div>
                  <div className="flex-1">
                    <p className="font-semibold text-blue-900">Processing your file...</p>
                    <p className="text-sm text-blue-700 mt-1">
                      {progress}% Complete
                    </p>
                    <div className="w-full h-2 bg-blue-200 rounded-full mt-3 overflow-hidden">
                      <div
                        className="h-full bg-blue-600 transition-all"
                        style={{ width: `${progress}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={!file || uploading}
              className="btn-primary w-full py-3 rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploading ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="loading-spinner" style={{ width: '16px', height: '16px', borderWidth: '2px' }}></div>
                  <span>Uploading & Predicting...</span>
                </div>
              ) : (
                '📤 Upload & Predict'
              )}
            </button>
          </form>
        </div>

        {/* Sidebar - Instructions */}
        <div className="space-y-4">
          <div className="card bg-gradient-to-br from-indigo-50 to-indigo-100 border border-indigo-200">
            <h3 className="font-bold text-indigo-900 mb-4">File Requirements</h3>
            <ul className="space-y-3 text-sm text-indigo-800">
              <li className="flex gap-2">
                <span>✓</span>
                <span>Excel format (.xlsx or .xls)</span>
              </li>
              <li className="flex gap-2">
                <span>✓</span>
                <span>Column headers in first row</span>
              </li>
              <li className="flex gap-2">
                <span>✓</span>
                <span>Maximum 10,000 rows</span>
              </li>
              <li className="flex gap-2">
                <span>✓</span>
                <span>Required fields: Age, Department, Role, Income</span>
              </li>
            </ul>
          </div>

          {/* Template Download */}
          <button className="card hover:shadow-md transition-all w-full text-left">
            <div className="flex items-center gap-3">
              <span className="text-2xl">📥</span>
              <div>
                <p className="font-semibold text-slate-900 text-sm">Download Template</p>
                <p className="text-xs text-slate-600">Get started with our sample file</p>
              </div>
            </div>
          </button>
        </div>
      </div>

      {/* Results */}
      {result && (
        <div className="card border-2 border-green-200 bg-green-50">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-green-900">✓ Predictions Complete</h2>
              <p className="text-green-700 mt-2">
                {result.total_rows} employees analyzed
              </p>
            </div>
            <span className="text-4xl">✓</span>
          </div>

          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-white p-4 rounded-lg border border-green-200">
              <p className="text-sm text-slate-600">High Risk</p>
              <p className="text-2xl font-bold text-red-600 mt-2">
                {result.high_risk_count || 0}
              </p>
            </div>
            <div className="bg-white p-4 rounded-lg border border-green-200">
              <p className="text-sm text-slate-600">Medium Risk</p>
              <p className="text-2xl font-bold text-amber-600 mt-2">
                {result.medium_risk_count || 0}
              </p>
            </div>
            <div className="bg-white p-4 rounded-lg border border-green-200">
              <p className="text-sm text-slate-600">Low Risk</p>
              <p className="text-2xl font-bold text-green-600 mt-2">
                {result.low_risk_count || 0}
              </p>
            </div>
          </div>

          {result.status === 'completed' && (
            <div className="flex gap-3">
              <button className="btn-primary py-2 px-4 rounded-lg flex-1">
                📥 Download Results
              </button>
              <button className="btn-secondary py-2 px-4 rounded-lg flex-1">
                👁️ View Predictions
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default ExcelUpload;
