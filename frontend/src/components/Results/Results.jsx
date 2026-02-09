import React, { useState, useEffect } from 'react';
import { predictAPI } from '../../services/api';

function Results() {
  const [uploadHistory, setUploadHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await predictAPI.getHistory(0, 20);
      setUploadHistory(response.data || []);
    } catch (err) {
      setError('Failed to load results history');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (uploadId) => {
    try {
      const response = await predictAPI.downloadResults(uploadId);
      alert('Download started! Check your downloads folder.');
    } catch (err) {
      alert('Download failed');
      console.error(err);
    }
  };

  const getStatusColor = (status) => {
    if (status === 'completed')
      return 'bg-green-100 text-green-800 border-green-300';
    if (status === 'processing')
      return 'bg-blue-100 text-blue-800 border-blue-300';
    if (status === 'failed')
      return 'bg-red-100 text-red-800 border-red-300';
    return 'bg-yellow-100 text-yellow-800 border-yellow-300';
  };

  const getRiskColor = (riskLevel) => {
    if (riskLevel === 'high')
      return 'bg-red-50 text-red-900 border-l-4 border-red-500';
    if (riskLevel === 'medium')
      return 'bg-yellow-50 text-yellow-900 border-l-4 border-yellow-500';
    return 'bg-green-50 text-green-900 border-l-4 border-green-500';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Prediction Results</h1>
          <p className="text-slate-600 mt-1">View and manage your prediction history</p>
        </div>
        <button
          onClick={fetchHistory}
          className="btn-secondary py-2 px-4 rounded-lg text-sm font-medium"
        >
          🔄 Refresh
        </button>
      </div>

      {/* Results */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="text-slate-600">Loading results...</div>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-red-700">
          {error}
        </div>
      ) : uploadHistory.length === 0 ? (
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-8 text-center text-slate-600">
          <p className="text-lg font-medium">No results yet</p>
          <p className="text-sm mt-1">
            Upload a file or make predictions to see results here
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {uploadHistory.map((upload) => (
            <div
              key={upload.upload_id}
              className="bg-white rounded-xl border border-slate-200 overflow-hidden hover:border-slate-300 transition-colors"
            >
              {/* Summary */}
              <div
                className="p-4 sm:p-6 cursor-pointer"
                onClick={() =>
                  setExpandedId(
                    expandedId === upload.upload_id ? null : upload.upload_id
                  )
                }
              >
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  <div className="flex-1">
                    <h3 className="font-bold text-slate-900">{upload.file_name}</h3>
                    <p className="text-sm text-slate-600 mt-1">
                      {upload.total_rows} employees analyzed • Created{' '}
                      {new Date(upload.created_at).toLocaleDateString()}
                    </p>
                  </div>

                  <div className="flex items-center gap-3">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold border ${getStatusColor(
                        upload.status
                      )}`}
                    >
                      {upload.status.charAt(0).toUpperCase() +
                        upload.status.slice(1)}
                    </span>
                    <span className="text-2xl">
                      {expandedId === upload.upload_id ? '▼' : '▶'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Details */}
              {expandedId === upload.upload_id && (
                <div className="border-t border-slate-200 bg-slate-50 p-4 sm:p-6 space-y-4">
                  {/* Risk Summary */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div className={`rounded-lg p-4 ${getRiskColor('high')}`}>
                      <div className="text-2xl font-bold">
                        {upload.high_risk_count}
                      </div>
                      <div className="text-sm font-medium">High Risk</div>
                    </div>
                    <div className={`rounded-lg p-4 ${getRiskColor('medium')}`}>
                      <div className="text-2xl font-bold">
                        {upload.medium_risk_count}
                      </div>
                      <div className="text-sm font-medium">Medium Risk</div>
                    </div>
                    <div className={`rounded-lg p-4 ${getRiskColor('low')}`}>
                      <div className="text-2xl font-bold">
                        {upload.low_risk_count}
                      </div>
                      <div className="text-sm font-medium">Low Risk</div>
                    </div>
                  </div>

                  {/* Action Button */}
                  {upload.status === 'completed' && (
                    <button
                      onClick={() => handleDownload(upload.upload_id)}
                      className="w-full btn-primary py-2 px-4 rounded-lg text-sm font-medium"
                    >
                      📥 Download Results
                    </button>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Results;
