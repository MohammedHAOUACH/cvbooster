import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

// Attach Supabase Bearer token before each request
api.interceptors.request.use(async (config) => {
  try {
    const { createClient } = await import("@/lib/supabase/client");
    const supabase = createClient();
    const { data } = await supabase.auth.getSession();
    if (data?.session?.access_token) {
      config.headers.Authorization = `Bearer ${data.session.access_token}`;
    }
  } catch {
    // Silently fail — let the backend handle auth errors
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
    session: "/api/auth/session",
    profile: {
      get: "/api/auth/profile",
      update: "/api/auth/profile",
    },
  },
  upload: {
    cv: "/api/upload/cv",
    cvs: "/api/upload/cvs",
    get: (id: string) => `/api/upload/cv/${id}`,
    delete: (id: string) => `/api/upload/cv/${id}`,
  },
  jobs: {
    scrape: "/api/jobs/scrape",
    paste: "/api/jobs/paste",
    list: "/api/jobs",
    get: (id: string) => `/api/jobs/${id}`,
    delete: (id: string) => `/api/jobs/${id}`,
  },
  cv: {
    generate: "/api/cv/generate",
    list: "/api/cv",
    get: (id: string) => `/api/cv/${id}`,
    download: (id: string) => `/api/cv/${id}/download`,
    retail: (id: string) => `/api/cv/${id}/retail`,
  },
  templates: {
    list: "/api/templates",
    get: (name: string) => `/api/templates/${name}`,
  },
};
