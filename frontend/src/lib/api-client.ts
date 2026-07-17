import axios from "axios";
import { getToken } from "@/lib/auth/client";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
});

// Attach JWT token before each request
api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  // Set JSON content type for POST/PUT/PATCH if not already set
  if ((config.method === 'post' || config.method === 'put' || config.method === 'patch') && 
      !(config.data instanceof FormData)) {
    config.headers['Content-Type'] = 'application/json';
  }
  return config;
});

// Response error handler
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);

export const endpoints = {
  auth: {
    session: "/auth/session",
    profile: {
      get: "/auth/profile",
      update: "/auth/profile",
    },
  },
  upload: {
    cv: "/upload/cv",
    cvs: "/upload/cvs",
    get: (id: string) => `/upload/cv/${id}`,
    delete: (id: string) => `/upload/cv/${id}`,
  },
  jobs: {
    scrape: "/jobs/scrape",
    paste: "/jobs/paste",
    list: "/jobs",
    get: (id: string) => `/jobs/${id}`,
    delete: (id: string) => `/jobs/${id}`,
  },
  cv: {
    generate: "/cv/generate",
    list: "/cv",
    get: (id: string) => `/cv/${id}`,
    download: (id: string) => `/cv/${id}/download`,
    retail: (id: string) => `/cv/${id}/retail`,
  },
  templates: {
    list: "/templates",
    get: (name: string) => `/templates/${name}`,
  },
};
