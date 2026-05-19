import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

export const api = axios.create({
  baseURL: API,
  withCredentials: true,
});

// Allow attaching a session token from localStorage (fallback when cookies blocked)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("vw_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
