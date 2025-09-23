import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Customer API calls
export const customerAPI = {
  getCustomers: (params = {}) => api.get('/customers', { params }),
  getCustomer: (customerId) => api.get(`/customers/${customerId}`),
  getCustomerJourney: (customerId) => api.get(`/customers/${customerId}/journey`),
  updateCustomerStage: (customerId, stage) => api.put(`/customers/${customerId}/stage`, { new_stage: stage }),
};

// Analytics API calls
export const analyticsAPI = {
  getLifecycleAnalytics: () => api.get('/analytics/lifecycle'),
  getConversionRates: () => api.get('/analytics/conversion-rates'),
  getRevenueMetrics: (params = {}) => api.get('/analytics/revenue-metrics', { params }),
};

// AI/ML API calls
export const aiAPI = {
  predictChurn: (customerId) => api.get(`/ai/churn-prediction/${customerId}`),
  getChurnRiskCustomers: (threshold = 0.7) => api.get('/ai/churn-risk-customers', { params: { risk_threshold: threshold } }),
  updateLeadScore: (leadData) => api.post('/ai/lead-score', leadData),
  getRevenueForecast: (monthsAhead = 12) => api.get('/ai/revenue-forecast', { params: { months_ahead: monthsAhead } }),
  calculateCLV: (customerId) => api.get(`/ai/clv/${customerId}`),
};

// Pipeline API calls
export const pipelineAPI = {
  getPipelineHealth: () => api.get('/pipeline/health'),
  getPipelineForecast: () => api.get('/pipeline/forecast'),
};

// Data management API calls
export const dataAPI = {
  importData: (filePath) => api.post('/data/import', { file_path: filePath }),
  exportData: (format = 'csv') => api.get('/data/export', { params: { format } }),
};

// Health check
export const healthAPI = {
  getHealth: () => api.get('/health'),
};

export default api;