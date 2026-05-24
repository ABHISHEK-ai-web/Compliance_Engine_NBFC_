import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 60000,
});

const longRunning = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 300000,
});

export const uploadRegulation = (file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/upload-regulation', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000,
    onUploadProgress: (e) => onProgress?.(Math.round((e.loaded * 100) / e.total)),
  });
};

export const uploadPolicy = (file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/upload-policy', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000,
    onUploadProgress: (e) => onProgress?.(Math.round((e.loaded * 100) / e.total)),
  });
};

export const runAnalysis = (params = {}) =>
  longRunning.post('/analyze', params);

export const getViolations = (params = {}) => api.get('/violations', { params });

export const getDashboardMetrics = () => api.get('/dashboard-metrics');

export const queryAudit = (question) => longRunning.post('/audit-query', { question });

export const getRbiSyncStatus = () => api.get('/sync-regulations/status');

export const syncRegulations = (params = {}) =>
  longRunning.post('/sync-regulations', null, { params });

/** Notify dashboard/violations pages to reload after sync or analysis */
export const emitComplianceRefresh = () => {
  window.dispatchEvent(new CustomEvent('compliance:refresh'));
};

export default api;
