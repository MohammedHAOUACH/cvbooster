"use client";

import { useEffect, useState } from "react";
import { api, endpoints } from "@/lib/api-client";
import { useCVStore } from "@/store/cv-store";
import type { GeneratedCV, OriginalCV } from "@/store/cv-store";

export default function DashboardPage() {
  const setAllGeneratedCVs = useCVStore((s) => s.setAllGeneratedCVs);
  const setAllOriginalCVs = useCVStore((s) => s.setAllOriginalCVs);
  const [generatedCVs, setGeneratedCVs] = useState<GeneratedCV[]>([]);
  const [originalCVs, setOriginalCVs] = useState<OriginalCV[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
      setLoading(true);
        const [genRes, origRes] = await Promise.all([
        api.get(endpoints.cv.list),
          api.get(endpoints.upload.cvs),
        ]);

        const generated = genRes.data.generated_cvs || genRes.data.data || [];
        const originals = origRes.data.cvs || origRes.data.data || [];

        setGeneratedCVs(generated);
        setOriginalCVs(originals);
        setAllGeneratedCVs(generated);
        setAllOriginalCVs(originals);
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : "Failed to load data";
        setError(message);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [setAllGeneratedCVs, setAllOriginalCVs]);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card p-4 animate-pulse">
              <div className="h-8 w-12 bg-gray-200 rounded mb-2" />
              <div className="h-4 w-24 bg-gray-200 rounded" />
            </div>
          ))}
        </div>
        <div className="card p-6 animate-pulse">
          <div className="h-6 w-40 bg-gray-200 rounded mb-4" />
          <div className="h-20 bg-gray-200 rounded" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card p-8 text-center">
        <p className="text-red-600 mb-4">{error}</p>
        <button onClick={() => window.location.reload()} className="btn btn-primary">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="card p-4">
          <div className="text-2xl font-bold text-primary-600">{generatedCVs.length}</div>
          <div className="text-sm text-gray-600">CVs Generated</div>
        </div>
        <div className="card p-4">
          <div className="text-2xl font-bold text-primary-600">{originalCVs.length}</div>
          <div className="text-sm text-gray-600">Original CVs</div>
        </div>
        <div className="card p-4">
          <div className="text-2xl font-bold text-primary-600">
            {generatedCVs.length > 0
              ? Math.round(
                  generatedCVs.reduce((sum, cv) => sum + (cv.ats_score || 0), 0) /
                    generatedCVs.length
                )
              : 0}
          </div>
          <div className="text-sm text-gray-600">Avg ATS Score</div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
        <div className="grid md:grid-cols-3 gap-4">
          <a href="/create" className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition text-center">
            <div className="text-2xl mb-2">📄</div>
            <div className="font-medium">Upload Your CV</div>
            <div className="text-sm text-gray-500">Upload your existing PDF resume</div>
          </a>
          <a href="/create" className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition text-center">
            <div className="text-2xl mb-2">🎯</div>
            <div className="font-medium">Add Job Posting</div>
            <div className="text-sm text-gray-500">Paste a URL or job description</div>
          </a>
          <a href="/create" className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition text-center">
            <div className="text-2xl mb-2">✨</div>
            <div className="font-medium">Generate CV</div>
            <div className="text-sm text-gray-500">Create your ATS-optimized resume</div>
          </a>
        </div>
      </div>

      {/* Recent Generated CVs */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold mb-4">Recent Generated CVs</h2>
        {generatedCVs.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            No CVs generated yet. Click &quot;Create New CV&quot; to get started!
          </div>
        ) : (
          <div className="space-y-3">
            {generatedCVs.slice(0, 5).map((cv) => (
              <div key={cv.id} className="flex items-center justify-between p-3 border border-gray-100 rounded-lg hover:bg-gray-50">
                <div>
                  <div className="font-medium">
                    CV — {cv.template_name.charAt(0).toUpperCase() + cv.template_name.slice(1)} Template
                  </div>
                  <div className="text-sm text-gray-500">
                    {new Date(cv.created_at).toLocaleDateString()} · ATS Score: {cv.ats_score?.toFixed(0) || "N/A"}%
                  </div>
                </div>
                <div className="flex gap-2">
                  <a
                    href={cv.file_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-outline text-xs"
                  >
                    Preview
                  </a>
                  <a
                    href={cv.file_url}
                    download={`cv-${cv.id}.pdf`}
                    className="btn btn-primary text-xs"
                  >
                    Download
                  </a>
                  <a
                    href={`/preview?id=${cv.id}&score=${cv.ats_score || 0}`}
                    className="btn btn-ghost text-xs"
                  >
                    Details
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
