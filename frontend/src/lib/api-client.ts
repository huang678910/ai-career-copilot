import axios from "axios";

const API_BASE_URL = typeof window !== "undefined" ? "" : (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8004");

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 30000,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let isRefreshing = false;
let refreshPromise: Promise<any> | null = null;

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Wait for the existing refresh to complete, then retry
        try {
          await refreshPromise;
          originalRequest.headers.Authorization = `Bearer ${localStorage.getItem("access_token")}`;
          return apiClient(originalRequest);
        } catch {
          return Promise.reject(error);
        }
      }

      originalRequest._retry = true;
      const refreshToken = localStorage.getItem("refresh_token");

      if (refreshToken) {
        isRefreshing = true;
        refreshPromise = axios.post(
          `${API_BASE_URL}/api/v1/auth/refresh`,
          { refresh_token: refreshToken },
        );

        try {
          const { data } = await refreshPromise;
          const accessToken = data.access_token;
          const newRefreshToken = data.refresh_token;
          if (accessToken) localStorage.setItem("access_token", accessToken);
          if (newRefreshToken) localStorage.setItem("refresh_token", newRefreshToken);
          originalRequest.headers.Authorization = `Bearer ${accessToken}`;
          return apiClient(originalRequest);
        } catch {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          window.location.href = "/login";
          return Promise.reject(error);
        } finally {
          isRefreshing = false;
          refreshPromise = null;
        }
      } else {
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  },
);
