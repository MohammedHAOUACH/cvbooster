import axios from "axios";
import { getToken } from "@/lib/auth/client";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "/api";

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

/**
 * Fetch a protected resource (e.g. a PDF) as a Blob.
 * Uses native fetch (same-origin absolute path + Authorization header):
 * plain <iframe>/<a> navigation cannot send the header, and axios would
 * double-prefix the /api baseURL onto file URLs that already contain /api.
 */
export async function fetchAuthedBlob(path: string): Promise<Blob> {
  const token = getToken();
  const res = await fetch(path, {
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  });
  if (!res.ok) throw new Error(`Failed to fetch ${path}: ${res.status}`);
  return res.blob();
}

/** Trigger a browser download for an in-memory Blob. */
export function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

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
    delete: (id: string) => `/cv/${id}`,
    download: (id: string) => `/cv/${id}/download`,
    retemplate: (id: string) => `/cv/${id}/retemplate`,
  },
  templates: {
    list: "/templates",
    get: (name: string) => `/templates/${name}`,
  },
};
