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
