import React, { useState } from 'react';
import { predictAPI } from '../../services/api';
import './Prediction.css';

function ExcelUpload() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [progress, setProgress] = useState(0);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && (selectedFile.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || selectedFile.type === 'application/vnd.ms-excel')) {
      setFile(selectedFile);
      setError('');
    } else {
      setError('Please select a valid Excel file (.xlsx or .xls)');
      setFile(null);
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
      
      // Poll for status updates
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

        if (response.data.status === 'completed' || response.data.status === 'failed') {
          clearInterval(interval);
          setResult(response.data);
        }
      } catch (err) {
        clearInterval(interval);
      }
    }, 2000);
  };

  return (
    <div className="prediction-container">
      <h1>Bulk Employee Prediction</h1>
      <p>Upload an Excel file with employee data for batch predictions</p>

      <div className="excel-upload-wrapper">
        <form onSubmit={handleSubmit} className="upload-form">
          <div className="form-group">
            <label htmlFor="file">Select Excel File</label>
            <input
              id="file"
              type="file"
              accept=".xlsx,.xls"
              onChange={handleFileChange}
              disabled={uploading}
            />
            {file && <p className="file-name">Selected: {file.name}</p>}
          </div>

          {error && <div className="error-message">{error}</div>}

          {uploading && (
            <div className="upload-progress">
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${progress}%` }}></div>
              </div>
              <p>{progress}% Complete</p>
            </div>
          )}

          <button type="submit" disabled={!file || uploading} className="btn-primary">
            {uploading ? 'Uploading...' : 'Upload & Predict'}
          </button>
        </form>

        {result && (
          <div className="upload-result">
            <h3>Upload Result</h3>
            <div className="result-info">
              <p><strong>Status:</strong> {result.status}</p>
              <p><strong>Total Rows:</strong> {result.total_rows}</p>
              <p><strong>Upload ID:</strong> {result.upload_id}</p>
              {result.high_risk_count !== undefined && (
                <>
                  <p><strong>High Risk:</strong> {result.high_risk_count}</p>
                  <p><strong>Medium Risk:</strong> {result.medium_risk_count}</p>
                  <p><strong>Low Risk:</strong> {result.low_risk_count}</p>
                </>
              )}
            </div>
            {result.status === 'completed' && (
              <button className="btn-secondary">Download Results</button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default ExcelUpload;
