/**
 * Centralized Axios instance.
 *
 * All API calls in the app go through this client so the base URL,
 * headers, and error handling are configured in exactly one place.
 * The backend URL is read from an environment variable so it can be
 * changed per environment (dev/staging/prod) without touching code.
 */

import axios from "axios";

const BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

const axiosClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

// Normalize error responses so components/thunks can rely on a
// consistent shape: { message, status }.
axiosClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status || 0;
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      "Something went wrong. Please try again.";
    return Promise.reject({ message, status });
  }
);

export default axiosClient;