/**
 * Utility Helper Functions
 * Common functions used throughout the application
 */

// ==================== NUMBER FORMATTING ====================

/**
 * Format number as currency
 * @param {number} value - The number to format
 * @param {boolean} compact - Whether to use compact notation (e.g., $1.5M)
 * @returns {string} Formatted currency string
 */
export const formatCurrency = (value, compact = false) => {
  if (value === null || value === undefined || isNaN(value)) {
    return '$0';
  }

  if (compact) {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    }
    if (value >= 1000) {
      return `$${(value / 1000).toFixed(1)}K`;
    }
  }

  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value);
};

/**
 * Format number as percentage
 * @param {number} value - The number to format
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted percentage string
 */
export const formatPercentage = (value, decimals = 1) => {
  if (value === null || value === undefined || isNaN(value)) {
    return '0%';
  }

  return `${value.toFixed(decimals)}%`;
};

/**
 * Format large numbers with K, M, B suffixes
 * @param {number} value - The number to format
 * @returns {string} Formatted number string
 */
export const formatCompactNumber = (value) => {
  if (value === null || value === undefined || isNaN(value)) {
    return '0';
  }

  if (value >= 1000000000) {
    return `${(value / 1000000000).toFixed(1)}B`;
  }
  if (value >= 1000000) {
    return `${(value / 1000000).toFixed(1)}M`;
  }
  if (value >= 1000) {
    return `${(value / 1000).toFixed(1)}K`;
  }

  return value.toFixed(0);
};

/**
 * Format number with commas
 * @param {number} value - The number to format
 * @returns {string} Formatted number string
 */
export const formatNumber = (value) => {
  if (value === null || value === undefined || isNaN(value)) {
    return '0';
  }

  return new Intl.NumberFormat('en-US').format(value);
};

// ==================== DATE FORMATTING ====================

/**
 * Format date to readable string
 * @param {Date|string|number} date - The date to format
 * @param {string} format - Format type ('short', 'long', 'time')
 * @returns {string} Formatted date string
 */
export const formatDate = (date, format = 'short') => {
  if (!date) return '';

  const dateObj = new Date(date);

  if (isNaN(dateObj.getTime())) {
    return '';
  }

  switch (format) {
    case 'short':
      return dateObj.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      });
    case 'long':
      return dateObj.toLocaleDateString('en-US', {
        month: 'long',
        day: 'numeric',
        year: 'numeric'
      });
    case 'time':
      return dateObj.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit'
      });
    case 'datetime':
      return `${formatDate(dateObj, 'short')} ${formatDate(dateObj, 'time')}`;
    default:
      return dateObj.toLocaleDateString('en-US');
  }
};

/**
 * Get relative time (e.g., "2 hours ago")
 * @param {Date|string|number} date - The date to compare
 * @returns {string} Relative time string
 */
export const getRelativeTime = (date) => {
  if (!date) return '';

  const dateObj = new Date(date);
  const now = new Date();
  const diffMs = now - dateObj;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  
  return formatDate(dateObj, 'short');
};

// ==================== CALCULATION HELPERS ====================

/**
 * Calculate percentage change between two values
 * @param {number} oldValue - Original value
 * @param {number} newValue - New value
 * @returns {number} Percentage change
 */
export const calculatePercentageChange = (oldValue, newValue) => {
  if (!oldValue || oldValue === 0) return 0;
  return ((newValue - oldValue) / oldValue) * 100;
};

/**
 * Calculate total return (dollar amount and percentage)
 * @param {number} invested - Amount invested
 * @param {number} currentValue - Current value
 * @returns {object} Object with value and percentage
 */
export const calculateReturn = (invested, currentValue) => {
  const value = currentValue - invested;
  const percentage = calculatePercentageChange(invested, currentValue);
  
  return {
    value,
    percentage,
    isPositive: value > 0
  };
};

/**
 * Calculate portfolio risk score based on allocation
 * @param {Array} allocation - Array of portfolio allocations
 * @returns {number} Risk score (0-10)
 */
export const calculateRiskScore = (allocation) => {
  if (!allocation || allocation.length === 0) return 5;

  // Risk weights for different asset types
  const riskWeights = {
    'tech': 8,
    'technology': 8,
    'crypto': 10,
    'options': 10,
    'growth': 7,
    'emerging': 8,
    'small cap': 7,
    'stocks': 6,
    'etf': 5,
    'healthcare': 4,
    'dividend': 3,
    'bonds': 2,
    'cash': 1,
    'real estate': 4,
    'blue chip': 3
  };

  let weightedRisk = 0;
  let totalWeight = 0;

  allocation.forEach(asset => {
    const assetName = asset.name.toLowerCase();
    let riskWeight = 5; // Default moderate risk

    // Find matching risk weight
    Object.keys(riskWeights).forEach(key => {
      if (assetName.includes(key)) {
        riskWeight = riskWeights[key];
      }
    });

    weightedRisk += riskWeight * asset.percentage;
    totalWeight += asset.percentage;
  });

  return totalWeight > 0 ? (weightedRisk / totalWeight).toFixed(1) : 5;
};

/**
 * Calculate portfolio diversification score
 * @param {Array} allocation - Array of portfolio allocations
 * @returns {number} Diversification score (0-10)
 */
export const calculateDiversityScore = (allocation) => {
  if (!allocation || allocation.length === 0) return 0;

  // Herfindahl-Hirschman Index (HHI) for concentration
  const hhi = allocation.reduce((sum, asset) => {
    const share = asset.percentage / 100;
    return sum + (share * share);
  }, 0);

  // Convert HHI to score (lower HHI = better diversity)
  // HHI ranges from 1/n to 1, where n is number of assets
  // Perfect diversity (equal weights): HHI = 1/n
  const perfectHHI = 1 / allocation.length;
  const diversityScore = 10 - ((hhi - perfectHHI) / (1 - perfectHHI)) * 10;

  return Math.max(0, Math.min(10, diversityScore)).toFixed(1);
};

/**
 * Calculate compound annual growth rate (CAGR)
 * @param {number} beginValue - Starting value
 * @param {number} endValue - Ending value
 * @param {number} years - Number of years
 * @returns {number} CAGR percentage
 */
export const calculateCAGR = (beginValue, endValue, years) => {
  if (!beginValue || !endValue || !years || years <= 0) return 0;
  return (Math.pow(endValue / beginValue, 1 / years) - 1) * 100;
};

// ==================== COLOR UTILITIES ====================

/**
 * Get color based on positive/negative value
 * @param {number} value - The value to check
 * @param {boolean} returnClass - Return Tailwind class instead of color
 * @returns {string} Color code or Tailwind class
 */
export const getChangeColor = (value, returnClass = false) => {
  if (value > 0) {
    return returnClass ? 'text-green-600' : '#10B981';
  } else if (value < 0) {
    return returnClass ? 'text-red-600' : '#EF4444';
  }
  return returnClass ? 'text-gray-600' : '#6B7280';
};

/**
 * Get color for risk score
 * @param {number} score - Risk score (0-10)
 * @returns {object} Object with color, bgColor, and label
 */
export const getRiskColor = (score) => {
  if (score < 4) {
    return {
      color: '#10B981',
      bgColor: '#ECFDF5',
      textColor: '#065F46',
      label: 'Conservative'
    };
  } else if (score < 7) {
    return {
      color: '#F59E0B',
      bgColor: '#FFFBEB',
      textColor: '#92400E',
      label: 'Moderate'
    };
  } else {
    return {
      color: '#EF4444',
      bgColor: '#FEF2F2',
      textColor: '#991B1B',
      label: 'Aggressive'
    };
  }
};

/**
 * Generate color palette for charts
 * @param {number} count - Number of colors needed
 * @returns {Array} Array of color codes
 */
export const generateColorPalette = (count) => {
  const baseColors = [
    '#4F46E5', // Indigo
    '#06B6D4', // Cyan
    '#8B5CF6', // Purple
    '#10B981', // Green
    '#F59E0B', // Amber
    '#EC4899', // Pink
    '#3B82F6', // Blue
    '#14B8A6', // Teal
    '#F97316', // Orange
    '#6366F1'  // Violet
  ];

  if (count <= baseColors.length) {
    return baseColors.slice(0, count);
  }

  // If need more colors, repeat with variations
  const colors = [...baseColors];
  while (colors.length < count) {
    colors.push(...baseColors);
  }
  return colors.slice(0, count);
};

// ==================== VALIDATION UTILITIES ====================

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} True if valid
 */
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validate password strength
 * @param {string} password - Password to validate
 * @returns {object} Object with isValid and strength
 */
export const validatePassword = (password) => {
  const hasMinLength = password.length >= 8;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumber = /\d/.test(password);
  const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

  const score = [hasMinLength, hasUpperCase, hasLowerCase, hasNumber, hasSpecialChar].filter(Boolean).length;

  return {
    isValid: hasMinLength && hasUpperCase && hasLowerCase && hasNumber,
    strength: score <= 2 ? 'weak' : score <= 3 ? 'medium' : score <= 4 ? 'good' : 'strong',
    score,
    requirements: {
      minLength: hasMinLength,
      upperCase: hasUpperCase,
      lowerCase: hasLowerCase,
      number: hasNumber,
      specialChar: hasSpecialChar
    }
  };
};

/**
 * Validate phone number format
 * @param {string} phone - Phone number to validate
 * @returns {boolean} True if valid
 */
export const isValidPhone = (phone) => {
  const phoneRegex = /^[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,9}$/;
  return phoneRegex.test(phone);
};

// ==================== STRING UTILITIES ====================

/**
 * Truncate string with ellipsis
 * @param {string} str - String to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated string
 */
export const truncateString = (str, maxLength = 50) => {
  if (!str || str.length <= maxLength) return str;
  return `${str.substring(0, maxLength)}...`;
};

/**
 * Capitalize first letter of string
 * @param {string} str - String to capitalize
 * @returns {string} Capitalized string
 */
export const capitalizeFirst = (str) => {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
};

/**
 * Convert string to title case
 * @param {string} str - String to convert
 * @returns {string} Title case string
 */
export const toTitleCase = (str) => {
  if (!str) return '';
  return str.toLowerCase().split(' ').map(word => capitalizeFirst(word)).join(' ');
};

/**
 * Generate initials from name
 * @param {string} name - Full name
 * @returns {string} Initials (max 2 characters)
 */
export const getInitials = (name) => {
  if (!name) return 'U';
  
  const words = name.trim().split(' ');
  if (words.length === 1) {
    return words[0].charAt(0).toUpperCase();
  }
  
  return (words[0].charAt(0) + words[words.length - 1].charAt(0)).toUpperCase();
};

// ==================== ARRAY UTILITIES ====================

/**
 * Sort array by property
 * @param {Array} array - Array to sort
 * @param {string} property - Property to sort by
 * @param {string} order - 'asc' or 'desc'
 * @returns {Array} Sorted array
 */
export const sortByProperty = (array, property, order = 'asc') => {
  if (!array || !Array.isArray(array)) return [];
  
  return [...array].sort((a, b) => {
    const aVal = a[property];
    const bVal = b[property];
    
    if (order === 'asc') {
      return aVal > bVal ? 1 : -1;
    }
    return aVal < bVal ? 1 : -1;
  });
};

/**
 * Group array by property
 * @param {Array} array - Array to group
 * @param {string} property - Property to group by
 * @returns {Object} Grouped object
 */
export const groupBy = (array, property) => {
  if (!array || !Array.isArray(array)) return {};
  
  return array.reduce((groups, item) => {
    const key = item[property];
    if (!groups[key]) {
      groups[key] = [];
    }
    groups[key].push(item);
    return groups;
  }, {});
};

/**
 * Get unique values from array
 * @param {Array} array - Array to process
 * @param {string} property - Property to extract (optional)
 * @returns {Array} Array of unique values
 */
export const getUniqueValues = (array, property = null) => {
  if (!array || !Array.isArray(array)) return [];
  
  if (property) {
    return [...new Set(array.map(item => item[property]))];
  }
  return [...new Set(array)];
};

// ==================== PORTFOLIO UTILITIES ====================

/**
 * Calculate total portfolio value
 * @param {Array} holdings - Array of holdings
 * @returns {number} Total value
 */
export const calculateTotalValue = (holdings) => {
  if (!holdings || !Array.isArray(holdings)) return 0;
  return holdings.reduce((sum, holding) => sum + (holding.value || 0), 0);
};

/**
 * Calculate weighted average
 * @param {Array} items - Array of items with value and weight
 * @returns {number} Weighted average
 */
export const calculateWeightedAverage = (items) => {
  if (!items || items.length === 0) return 0;
  
  const totalWeight = items.reduce((sum, item) => sum + item.weight, 0);
  const weightedSum = items.reduce((sum, item) => sum + (item.value * item.weight), 0);
  
  return totalWeight > 0 ? weightedSum / totalWeight : 0;
};

/**
 * Get performance label based on percentage
 * @param {number} percentage - Performance percentage
 * @returns {string} Performance label
 */
export const getPerformanceLabel = (percentage) => {
  if (percentage >= 20) return 'Excellent';
  if (percentage >= 10) return 'Very Good';
  if (percentage >= 5) return 'Good';
  if (percentage >= 0) return 'Positive';
  if (percentage >= -5) return 'Slight Loss';
  if (percentage >= -10) return 'Moderate Loss';
  return 'Significant Loss';
};

// ==================== DEBOUNCE UTILITY ====================

/**
 * Debounce function to limit execution rate
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
export const debounce = (func, wait = 300) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

// ==================== LOCAL STORAGE HELPERS ====================

/**
 * Safely get item from localStorage
 * @param {string} key - Storage key
 * @param {*} defaultValue - Default value if not found
 * @returns {*} Retrieved value or default
 */
export const getFromStorage = (key, defaultValue = null) => {
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : defaultValue;
  } catch (error) {
    console.error('Error reading from localStorage:', error);
    return defaultValue;
  }
};

/**
 * Safely set item to localStorage
 * @param {string} key - Storage key
 * @param {*} value - Value to store
 */
export const setToStorage = (key, value) => {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (error) {
    console.error('Error writing to localStorage:', error);
  }
};

/**
 * Remove item from localStorage
 * @param {string} key - Storage key
 */
export const removeFromStorage = (key) => {
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.error('Error removing from localStorage:', error);
  }
};

// ==================== EXPORT ALL ====================

export default {
  // Number formatting
  formatCurrency,
  formatPercentage,
  formatCompactNumber,
  formatNumber,
  
  // Date formatting
  formatDate,
  getRelativeTime,
  
  // Calculations
  calculatePercentageChange,
  calculateReturn,
  calculateRiskScore,
  calculateDiversityScore,
  calculateCAGR,
  
  // Colors
  getChangeColor,
  getRiskColor,
  generateColorPalette,
  
  // Validation
  isValidEmail,
  validatePassword,
  isValidPhone,
  
  // String utilities
  truncateString,
  capitalizeFirst,
  toTitleCase,
  getInitials,
  
  // Array utilities
  sortByProperty,
  groupBy,
  getUniqueValues,
  
  // Portfolio utilities
  calculateTotalValue,
  calculateWeightedAverage,
  getPerformanceLabel,
  
  // Other utilities
  debounce,
  getFromStorage,
  setToStorage,
  removeFromStorage
};