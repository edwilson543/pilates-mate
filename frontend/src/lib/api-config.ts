import { client } from "./apiClient/client.gen";
import {
  clearAccessToken,
  getAccessToken,
  setAccessToken,
} from "./token-storage";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

client.setConfig({ baseURL: API_BASE_URL, withCredentials: true });

client.instance.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let isRefreshing = false;

client.instance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status !== 401 || originalRequest._retried) {
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return Promise.reject(error);
    }

    isRefreshing = true;
    originalRequest._retried = true;

    try {
      const response = await client.instance.post<{
        access_token: string;
      }>("/auth/token/refresh");
      setAccessToken(response.data.access_token);
      originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`;
      return client.instance(originalRequest);
    } catch {
      clearAccessToken();
      window.location.href = "/login";
      return Promise.reject(error);
    } finally {
      isRefreshing = false;
    }
  },
);

export { API_BASE_URL };
