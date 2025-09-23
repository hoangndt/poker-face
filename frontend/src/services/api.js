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

// Sprint Board API calls
export const sprintAPI = {
  getSprintBoard: () => api.get('/sprint/board'),
  // Deal operations
  getDeals: (params = {}) => api.get('/sprint/deals', { params }),
  getDeal: (dealId) => api.get(`/sprint/deals/${dealId}`),
  getDealDetailed: (dealId) => api.get(`/sprint/deals/${dealId}/detailed`),
  createDeal: (dealData) => api.post('/sprint/deals', dealData),
  updateDeal: (dealId, dealData) => api.put(`/sprint/deals/${dealId}`, dealData),
  updateDealStatus: (dealId, statusData) => api.put(`/sprint/deals/${dealId}/status`, statusData),
  deleteDeal: (dealId) => api.delete(`/sprint/deals/${dealId}`),
  
  // Person management
  getPersons: () => api.get('/sprint/persons'),
  createPerson: (personData) => api.post('/sprint/persons', personData),
  
  // AI Insights
  triggerAIInsight: (dealId, currentStatus) => api.post(`/sprint/ai/insight/${dealId}`, { current_status: currentStatus }),
  getAIInsights: (dealId) => api.get(`/sprint/ai/insights/${dealId}`),
  
  // AI Actions for different stages
  triggerAIQualification: (dealId) => api.post(`/sprint/ai/qualification/${dealId}`),
  triggerAISolution: (dealId) => api.post(`/sprint/ai/solution/${dealId}`),
  triggerAIResourceAllocation: (dealId) => api.post(`/sprint/ai/resource-allocation/${dealId}`),
  triggerAIProposal: (dealId) => api.post(`/sprint/ai/proposal/${dealId}`),
  
  // Dashboard
  getDashboard: () => api.get('/sprint/dashboard'),
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