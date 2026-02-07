/**
 * Form validation functions
 */

/**
 * Validate email
 */
export const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

/**
 * Validate password
 */
export const validatePassword = (password) => {
  return password.length >= 8;
};

/**
 * Validate username
 */
export const validateUsername = (username) => {
  return username.length >= 3 && /^[a-zA-Z0-9_-]+$/.test(username);
};

/**
 * Validate required field
 */
export const validateRequired = (value) => {
  return value !== null && value !== undefined && value !== '';
};

/**
 * Validate number range
 */
export const validateRange = (value, min, max) => {
  const num = parseFloat(value);
  return !isNaN(num) && num >= min && num <= max;
};

/**
 * Validate file
 */
export const validateFile = (file, maxSize = 50 * 1024 * 1024, allowedTypes = []) => {
  if (!file) return false;
  if (file.size > maxSize) return false;
  if (allowedTypes.length > 0 && !allowedTypes.includes(file.type)) return false;
  return true;
};

/**
 * Get validation error message
 */
export const getErrorMessage = (error) => {
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  if (error.message) {
    return error.message;
  }
  return 'An error occurred. Please try again.';
};
