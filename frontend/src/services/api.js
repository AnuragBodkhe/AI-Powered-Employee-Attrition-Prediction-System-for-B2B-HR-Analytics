import axios from 'axios';

// API Base URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - Handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh-token`, {
            refresh_token: refreshToken,
          });
          localStorage.setItem('access_token', response.data.access_token);
          return api(originalRequest);
        }
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// =====================================
// AUTH API METHODS
// =====================================
const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getCurrentUser: () => api.get('/auth/me'),
  logout: () => api.post('/auth/logout'),
  changePassword: (data) => api.put('/auth/change-password', data),
  refreshToken: (refreshToken) => api.post('/auth/refresh-token', { refresh_token: refreshToken }),
};

// =====================================
// PREDICTION API METHODS
// =====================================
const predictAPI = {
  predictSingle: (data) => api.post('/predict/manual', data),
  uploadExcel: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/predict/excel', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  downloadResults: (uploadId) => api.get(`/predict/download/${uploadId}`),
  getHistory: (skip = 0, limit = 10) => api.get('/predict/history', { params: { skip, limit } }),
  getStatus: (uploadId) => api.get(`/predict/status/${uploadId}`),
};

// =====================================
// DASHBOARD API METHODS
// =====================================
const dashboardAPI = {
  getMetrics: () => api.get('/dashboard/metrics'),
  getRiskDistribution: () => api.get('/dashboard/charts/risk-distribution'),
  getDepartmentComparison: () => api.get('/dashboard/charts/department-comparison'),
  getSalaryImpact: () => api.get('/dashboard/charts/salary-impact'),
  getFilterOptions: () => api.get('/dashboard/filters/options'),
  getEmployees: (params) => api.get('/dashboard/employees', { params }),
  exportToExcel: (params) => api.get('/dashboard/export/excel', { params }),
};

export { authAPI, predictAPI, dashboardAPI };
