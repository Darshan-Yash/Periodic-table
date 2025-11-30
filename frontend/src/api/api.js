import axios from 'axios';

const API_BASE_URL = window.location.origin.includes('localhost') 
  ? 'http://localhost:8000' 
  : `https://${window.location.hostname.replace('-00-', '-00-').split('.')[0]}-00-${window.location.hostname.split('-00-')[1]}`.replace(':5000', '') + ':8000';

const getBaseUrl = () => {
  const hostname = window.location.hostname;
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  }
  return '';
};

const api = axios.create({
  baseURL: getBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const signup = async (email, password) => {
  const response = await api.post('/signup', { email, password });
  return response.data;
};

export const login = async (email, password) => {
  const response = await api.post('/login', { email, password });
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await api.get('/me');
  return response.data;
};

export const getElements = async () => {
  const response = await api.get('/elements');
  return response.data;
};

export const getElement = async (identifier) => {
  const response = await api.get(`/elements/${identifier}`);
  return response.data;
};

export const askQuestion = async (question) => {
  const response = await api.post('/ask', { question });
  return response.data;
};

export default api;
