import axios from "axios";

const ACCESS_KEY = "sensetrade.access";
const REFRESH_KEY = "sensetrade.refresh";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/"
});

let isRefreshing = false;
let refreshPromise = null;

function getAccessToken() {
  return localStorage.getItem(ACCESS_KEY);
}

function getRefreshToken() {
  return localStorage.getItem(REFRESH_KEY);
}

function setTokens(access, refresh = null) {
  if (access) localStorage.setItem(ACCESS_KEY, access);
  if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
}

function clearTokens() {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

async function refreshAccessToken() {
  const refresh = getRefreshToken();
  if (!refresh) throw new Error("No refresh token");

  const response = await axios.post(
    (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/") + "auth/refresh/",
    { refresh }
  );

  const newAccess = response?.data?.access;
  const newRefresh = response?.data?.refresh || null;

  if (!newAccess) throw new Error("Refresh failed: no access token");
  setTokens(newAccess, newRefresh);
  return newAccess;
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error?.config;

    if (!originalRequest || error?.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    try {
      if (!isRefreshing) {
        isRefreshing = true;
        refreshPromise = refreshAccessToken().finally(() => {
          isRefreshing = false;
        });
      }

      const newAccess = await refreshPromise;
      originalRequest.headers.Authorization = `Bearer ${newAccess}`;
      return api(originalRequest);
    } catch (refreshErr) {
      clearTokens();
      return Promise.reject(refreshErr);
    }
  }
);

export function setAuthTokens({ access, refresh }) {
  setTokens(access, refresh);
}

export function clearAuthTokens() {
  clearTokens();
}

export default api;
