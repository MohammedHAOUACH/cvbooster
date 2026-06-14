import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add auth token from Supabase session
export async function attachAuthToken() {
  const { data } = await import("@/lib/supabase/client").then((m) => {
    const client = m.createClient();
    return client.auth.getSession();
  });

  if (data.session?.access_token) {
    api.defaults.headers.common["Authorization"] = `Bearer ${data.session.access_token}`;
  }

  return data.session;
}

// API endpoints
export const apiEndpoints = {
  auth: {
    session: "/api/auth/session",
    profile: "/api/auth/profile",
  },
  upload: {
    cv: "/api/upload/cv",
    cvs: "/api/upload/cvs",
  },
  jobs: {
    scrape: "/api/jobs/scrape",
    paste: "/api/jobs/paste",
    list: "/api/jobs",
    get: (id: string) => `/api/jobs/${id}`,
  },
  cv: {
    generate: "/api/cv/generate",
    list: "/api/cv",
    get: (id: string) => `/api/cv/${id}`,
    download: (id: string) => `/api/cv/${id}/download`,
    preview: (id: string) => `/api/cv/${id}/preview`,
    retail: (id: string) => `/api/cv/${id}/retail`,
  },
  templates: {
    list: "/api/templates",
    get: (name: string) => `/api/templates/${name}`,
  },
};
