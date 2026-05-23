import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export const API_BASE = `${BACKEND_URL}/api`;

export const api = axios.create({
  baseURL: API_BASE,
  withCredentials: true,
});

export const fetchIdeas = (params = {}) => api.get("/ideas", { params }).then((r) => r.data);
export const fetchIdeaFilters = () => api.get("/ideas/filters").then((r) => r.data);
export const fetchIdea = (slug) => api.get(`/ideas/${slug}`).then((r) => r.data);
export const fetchRelatedIdeas = (slug) => api.get(`/ideas/${slug}/related`).then((r) => r.data);
export const fetchSavedIdeas = () => api.get("/ideas/saved").then((r) => r.data);
export const toggleSaveIdea = (slug) => api.post(`/ideas/${slug}/save`).then((r) => r.data);

export const exchangeSession = (session_id) =>
  api.post("/auth/session", { session_id }).then((r) => r.data);
export const fetchMe = () => api.get("/auth/me").then((r) => r.data);
export const logout = () => api.post("/auth/logout").then((r) => r.data);

export const formatINR = (n) => {
  if (n >= 10000000) return `₹${(n / 10000000).toFixed(n % 10000000 === 0 ? 0 : 1)}Cr`;
  if (n >= 100000) return `₹${(n / 100000).toFixed(n % 100000 === 0 ? 0 : 1)}L`;
  if (n >= 1000) return `₹${(n / 1000).toFixed(0)}K`;
  return `₹${n}`;
};
