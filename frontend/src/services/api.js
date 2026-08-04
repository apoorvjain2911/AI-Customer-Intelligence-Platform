import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
export const AUTH_TOKEN_KEY = "ai_customer_intelligence_token";
export const AUTH_USER_KEY = "ai_customer_intelligence_user";

const api = axios.create({
  baseURL: API_BASE_URL,
});

const readStorage = (key) => {
  try {
    return window.localStorage.getItem(key);
  } catch {
    return null;
  }
};

const writeStorage = (key, value) => {
  try {
    if (value === null || value === undefined) {
      window.localStorage.removeItem(key);
    } else {
      window.localStorage.setItem(key, value);
    }
  } catch {
    // no-op for server rendering or restricted storage environments
  }
};

export const getStoredToken = () => readStorage(AUTH_TOKEN_KEY);

export const getStoredUser = () => {
  const raw = readStorage(AUTH_USER_KEY);

  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
};

export const setAuthSession = (token, user = null) => {
  writeStorage(AUTH_TOKEN_KEY, token || null);
  if (user) {
    writeStorage(AUTH_USER_KEY, JSON.stringify(user));
  }
};

export const clearAuthSession = () => {
  writeStorage(AUTH_TOKEN_KEY, null);
  writeStorage(AUTH_USER_KEY, null);
};

api.interceptors.request.use((config) => {
  const token = getStoredToken();

  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      clearAuthSession();
    }

    return Promise.reject(error);
  },
);

export const registerUser = (payload) => api.post("/auth/register", payload);
export const loginUser = (payload) => api.post("/auth/login", payload);
export const getCurrentUser = () => api.get("/auth/me");
export const getAdminDashboard = () => api.get("/admin/dashboard");
export const getAdminUsers = () => api.get("/admin/users");
export const updateAdminUserRole = (userId, payload) => api.patch(`/admin/users/${userId}/role`, payload);
export const updateAdminUserStatus = (userId, payload) => api.patch(`/admin/users/${userId}/status`, payload);
export const getModelStatus = () => api.get("/admin/model-status");
export const retrainModel = () => api.post("/admin/retrain");

export const getCustomers = (params = {}) => api.get("/customers", { params });
export const getCustomer = (customerId) => api.get(`/customers/${customerId}`);
export const createCustomer = (payload) => api.post("/customers", payload);
export const updateCustomer = (customerId, payload) => api.put(`/customers/${customerId}`, payload);
export const deleteCustomer = (customerId) => api.delete(`/customers/${customerId}`);

export const getDashboardSummary = () => api.get("/dashboard/summary");
export const uploadDataset = (file) => {
  const formData = new FormData();
  formData.append("file", file);

  return api.post("/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

export const trainModel = () => api.post("/train");
export const predictBatch = () => api.post("/predict/batch");
export const predictCustomer = (payload) => api.post("/predict", payload);
export const getHistory = () => api.get("/history");

export const getClvSummary = () => api.get("/clv/summary");
export const getTopClvCustomers = () => api.get("/clv/top");
export const refreshCustomerClv = (customerId) => api.post(`/clv/refresh/${customerId}`);

export const getCopilotResponse = (payload) => api.post("/copilot/chat", payload);

export const getXaiExplanation = (customerId) => api.get(`/xai/customers/${customerId}`);

export const getReports = (params = {}) => api.get("/reports", { params });
export const getReport = (reportId) => api.get(`/reports/${reportId}`);
export const createReport = (payload) => api.post("/reports", payload);
export const updateReport = (reportId, payload) => api.put(`/reports/${reportId}`, payload);
export const deleteReport = (reportId) => api.delete(`/reports/${reportId}`);

export const getSegments = (params = {}) => api.get("/segments", { params });
export const getSegment = (segmentId) => api.get(`/segments/${segmentId}`);
export const createSegment = (payload) => api.post("/segments", payload);
export const updateSegment = (segmentId, payload) => api.put(`/segments/${segmentId}`, payload);
export const deleteSegment = (segmentId) => api.delete(`/segments/${segmentId}`);
export const assignSegment = (customerId) => api.post(`/segments/assign/${customerId}`);
export const getSegmentStats = () => api.get("/segments/stats/summary");

export const getRootMessage = () => api.get("/");

export default api;