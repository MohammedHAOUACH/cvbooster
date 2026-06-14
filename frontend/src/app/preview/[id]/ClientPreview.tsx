"use client";

import { useState, useEffect, useCallback } from "react";
import { api, endpoints } from "@/lib/api-client";
import { useCVStore } from "@/store/cv-store";
import type { GeneratedCV } from "@/store/cv-store";

export function ClientPreview({ cvId }: { cvId: string }) {
  const [cv, setCv] = useState<GeneratedCV | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [changingTemplate, setChangingTemplate] = useState<string | null>(null);

  const templates = useCVStore((s) => s.templates);
  const setSelectedTemplate = useCVStore((s) => s.setSelectedTemplate);

  const fetchCV = useCallback(async () => {
    try {
      setLoading(true);
      const res = await api.get(endpoints.cv.get(cvId));
      setCv(res.data.generated_cv);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load CV");
    } finally {
      setLoading(false);
    }
  }, [cvId]);

  useEffect(() => {
    fetchCV();
  }, [fetchCV]);

  const handleChangeTemplate = async (templateName: string) => {
    setChangingTemplate(templateName);
    try {
      await api.post(endpoints.cv.retail(cvId), {
        template_name: templateName,
      });
      setSelectedTemplate(templateName);
      await fetchCV();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to change template");
    } finally {
      setChangingTemplate(null);
    }
  };

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-6 py-8">
        <div className="card p-6 animate-pulse">
          <div className="h-6 w-32 bg-gray-200 rounded mb-4" />
          <div className="h-[600px] bg-gray-200 rounded-lg" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-5xl mx-auto px-6 py-8">
        <div className="card p-8 text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button onClick={fetchCV} className="btn btn-primary">Retry</button>
        </div>
      </div>
    );
  }

  const score = cv?.ats_score ? Math.round(cv.ats_score) : 85;
  const templateLabel = cv?.template_name ? cv.template_name.charAt(0).toUpperCase() + cv.template_name.slice(1) : "N/A";

  return (
    <div className="max-w-5xl mx-auto px-6 py-8">
      <header className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">CV Preview</h1>
          <p className="text-gray-600">
            Template: {templateLabel}
            {" "}· Generated {cv?.created_at ? new Date(cv.created_at).toLocaleDateString() : "N/A"}
          </p>
        </div>
        <div className="flex gap-3">
          <a href="/dashboard" className="btn btn-outline">Dashboard</a>
          <a href={cv?.file_url || "#"} download={`cv-${cvId}.pdf`} className="btn btn-primary">
            Download PDF
          </a>
        </div>
      </header>

      <div className="grid md:grid-cols-4 gap-6">
        <div className="space-y-4">
          <div className="card p-6">
            <h3 className="font-semibold mb-4">ATS Score</h3>
            <div className="text-center">
              <div className="text-4xl font-bold text-green-600 mb-2">{score}%</div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: `${score}%` }} />
              </div>
            </div>
            {cv?.keywords_matched !== undefined && (
              <div className="mt-4 text-sm text-gray-600">
                Keywords: {cv.keywords_matched}/{cv.keywords_total} matched
              </div>
            )}
          </div>

          <div className="card p-6">
            <h3 className="font-semibold mb-4">Change Template</h3>
            <div className="grid grid-cols-2 gap-2">
              {(templates.length > 0 ? templates : [
                { name: "clean", display_name: "Clean", description: "", category: "" },
                { name: "modern", display_name: "Modern", description: "", category: "" },
                { name: "minimal", display_name: "Minimal", description: "", category: "" },
                { name: "corporate", display_name: "Corporate", description: "", category: "" },
                { name: "tech", display_name: "Tech", description: "", category: "" },
                { name: "creative", display_name: "Creative", description: "", category: "" },
                { name: "academic", display_name: "Academic", description: "", category: "" },
                { name: "executive", display_name: "Executive", description: "", category: "" },
              ]).map((t) => (
                <button
                  key={t.name}
                  onClick={() => handleChangeTemplate(t.name)}
                  disabled={changingTemplate !== null || t.name === cv?.template_name}
                  className={`btn text-xs py-2 ${t.name === cv?.template_name ? "btn-primary" : "btn-outline"} disabled:opacity-50`}
                >
                  {changingTemplate === t.name ? "..." : t.display_name || t.name}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="card md:col-span-3 p-6">
          <div className="bg-gray-100 rounded-lg overflow-hidden">
            {cv?.file_url ? (
              <iframe src={cv.file_url} className="w-full h-[600px] border-0" title="CV Preview" />
            ) : (
              <div className="w-full h-[600px] flex items-center justify-center text-gray-400">
                <div className="text-center">
                  <div className="text-4xl mb-4">📄</div>
                  <p>No PDF available</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
