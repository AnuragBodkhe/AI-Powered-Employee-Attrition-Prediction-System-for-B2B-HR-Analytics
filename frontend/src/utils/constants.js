/**
 * Application constants
 */

export const RISK_LEVELS = {
  HIGH: 'High',
  MEDIUM: 'Medium',
  LOW: 'Low',
};

export const RISK_THRESHOLDS = {
  HIGH: 0.7,
  MEDIUM: 0.4,
};

export const RISK_COLORS = {
  High: '#ef4444',
  Medium: '#f97316',
  Low: '#22c55e',
};

export const DEPARTMENTS = [
  'Sales',
  'Research & Development',
  'Human Resources',
];

export const JOB_ROLES = [
  'Sales Manager',
  'Technical Architect',
  'Research Scientist',
  'Manager',
  'Associate',
  'Sales Representative',
  'Analyst',
];

export const EDUCATION_LEVELS = [
  'Below College',
  'College',
  'Bachelor',
  'Master',
  'Doctor',
];

export const BUSINESS_TRAVEL = [
  'Non-Travel',
  'Travel Rarely',
  'Travel Frequently',
];

export const API_ENDPOINTS = {
  HEALTH: '/health',
  AUTH_REGISTER: '/auth/register',
  AUTH_LOGIN: '/auth/login',
  AUTH_ME: '/auth/me',
  PREDICT_MANUAL: '/predict/manual',
  PREDICT_EXCEL: '/predict/excel',
  DASHBOARD_METRICS: '/dashboard/metrics',
};
