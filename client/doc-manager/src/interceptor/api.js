import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8001', 
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
//   const authHeader = btoa(`${username}:${password}`);

  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

export default api;
