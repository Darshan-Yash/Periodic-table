import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
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
      const isAuthRequest = error.config?.url === '/login' || error.config?.url === '/signup';
      if (!isAuthRequest) {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
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

export const analyzeMedia = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/analyze-media', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export default api;
