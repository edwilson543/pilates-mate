import { client } from "./apiClient/client.gen";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

// Configure the API client base URL
client.setConfig({
  baseURL: API_BASE_URL,
});

export { API_BASE_URL };
