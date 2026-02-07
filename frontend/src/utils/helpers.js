/**
 * Helper utility functions
 */

/**
 * Format number as percentage
 */
export const formatPercent = (value) => {
  return `${(value * 100).toFixed(2)}%`;
};

/**
 * Format number as currency
 */
export const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
  }).format(value);
};

/**
 * Format date
 */
export const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

/**
 * Get risk level color
 */
export const getRiskColor = (riskLevel) => {
  const colors = {
    High: '#ef4444',
    Medium: '#f97316',
    Low: '#22c55e',
  };
  return colors[riskLevel] || '#6b7280';
};

/**
 * Truncate text
 */
export const truncateText = (text, length = 50) => {
  return text.length > length ? `${text.substring(0, length)}...` : text;
};

/**
 * Sort array of objects
 */
export const sortBy = (array, key, direction = 'asc') => {
  return [...array].sort((a, b) => {
    if (a[key] < b[key]) return direction === 'asc' ? -1 : 1;
    if (a[key] > b[key]) return direction === 'asc' ? 1 : -1;
    return 0;
  });
};

/**
 * Sleep function for delays
 */
export const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
