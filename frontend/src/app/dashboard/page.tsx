"use client";

import { useEffect, useState } from "react";
import { api, endpoints, fetchAuthedBlob, downloadBlob } from "@/lib/api-client";
import { useCVStore } from "@/store/cv-store";
import type { GeneratedCV, OriginalCV } from "@/store/cv-store";
import { FileText, FolderOpen, Star, Plus, Eye, Download, Trash2, FileUp, Target, Zap } from "lucide-react";

export default function DashboardPage() {
  const setAllGeneratedCVs = useCVStore((s) => s.setAllGeneratedCVs);
  const setAllOriginalCVs = useCVStore((s) => s.setAllOriginalCVs);
  const [generatedCVs, setGeneratedCVs] = useState<GeneratedCV[]>([]);
  const [originalCVs, setOriginalCVs] = useState<OriginalCV[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);

  const load = async () => {
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
      setError(null);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to load data";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [setAllGeneratedCVs, setAllOriginalCVs]);

  const handleDownload = async (cv: GeneratedCV) => {
    try {
      const blob = await fetchAuthedBlob(cv.file_url);
      downloadBlob(blob, `cv-${cv.id}.pdf`);
    } catch {
      setError("Download failed");
    }
  };

  const handleDeleteGenerated = async (cv: GeneratedCV) => {
    if (!confirm(`Delete this generated CV? This cannot be undone.`)) return;
    setBusyId(cv.id);
    try {
      await api.delete(endpoints.cv.delete(cv.id));
      await load();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Delete failed");
    } finally {
      setBusyId(null);
    }
  };

  const handleDeleteOriginal = async (cv: OriginalCV) => {
    if (!confirm("Delete this original CV and the CVs generated from it? This cannot be undone.")) return;
    setBusyId(cv.id);
    try {
      await api.delete(endpoints.upload.delete(cv.id));
      await load();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Delete failed");
    } finally {
      setBusyId(null);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card p-5 animate-pulse">
              <div className="h-3 w-16 bg-gray-200 rounded mb-3" />
              <div className="h-7 w-10 bg-gray-200 rounded mb-1" />
              <div className="h-2 w-20 bg-gray-200 rounded" />
            </div>
          ))}
        </div>
        <div className="card p-6 animate-pulse">
          <div className="h-5 w-32 bg-gray-200 rounded mb-4" />
          <div className="h-20 bg-gray-200 rounded" />
        </div>
      </div>
    );
  }

  if (error && generatedCVs.length === 0 && originalCVs.length === 0) {
    return (
      <div className="card p-8 text-center">
        <p className="text-red-600 mb-4">{error}</p>
        <button onClick={() => window.location.reload()} className="btn btn-primary">
          Retry
        </button>
      </div>
    );
  }

  const avgScore = generatedCVs.length > 0
    ? Math.round(generatedCVs.reduce((sum, cv) => sum + (cv.ats_score || 0), 0) / generatedCVs.length)
    : 0;

  return (
    <div className="space-y-6">
      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg text-sm">{error}</div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="card p-5">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-8 h-8 rounded-lg bg-primary-100 text-primary flex items-center justify-center">
              <FileText className="w-4 h-4" />
            </div>
            <span className="text-sm font-medium text-muted">CVs Generated</span>
          </div>
          <div className="text-2xl font-heading font-bold text-foreground">{generatedCVs.length}</div>
        </div>
        <div className="card p-5">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-8 h-8 rounded-lg bg-primary-100 text-primary flex items-center justify-center">
              <FolderOpen className="w-4 h-4" />
            </div>
            <span className="text-sm font-medium text-muted">Original CVs</span>
          </div>
          <div className="text-2xl font-heading font-bold text-foreground">{originalCVs.length}</div>
        </div>
        <div className="card p-5">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-8 h-8 rounded-lg bg-primary-100 text-primary flex items-center justify-center">
              <Star className="w-4 h-4" />
            </div>
            <span className="text-sm font-medium text-muted">Avg ATS Score</span>
          </div>
          <div className="text-2xl font-heading font-bold text-foreground">
            {generatedCVs.length > 0 ? `${avgScore}%` : "—"}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card p-6">
        <h2 className="text-lg font-heading font-semibold text-foreground mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          <a href="/create" className="group flex flex-col items-center text-center p-5 border border-border rounded-lg hover:border-primary-300 hover:bg-primary-50/50 transition-all duration-200">
            <div className="w-10 h-10 rounded-lg bg-primary-100 text-primary flex items-center justify-center mb-3 group-hover:scale-110 transition-transform duration-200">
              <FileUp className="w-5 h-5" />
            </div>
            <div className="font-medium text-foreground">Upload Your CV</div>
            <div className="text-sm text-muted mt-1">Upload your existing PDF resume</div>
          </a>
          <a href="/create" className="group flex flex-col items-center text-center p-5 border border-border rounded-lg hover:border-primary-300 hover:bg-primary-50/50 transition-all duration-200">
            <div className="w-10 h-10 rounded-lg bg-primary-100 text-primary flex items-center justify-center mb-3 group-hover:scale-110 transition-transform duration-200">
              <Target className="w-5 h-5" />
            </div>
            <div className="font-medium text-foreground">Add Job Posting</div>
            <div className="text-sm text-muted mt-1">Paste a URL or job description</div>
          </a>
          <a href="/create" className="group flex flex-col items-center text-center p-5 border border-border rounded-lg hover:border-primary-300 hover:bg-primary-50/50 transition-all duration-200">
            <div className="w-10 h-10 rounded-lg bg-primary-100 text-primary flex items-center justify-center mb-3 group-hover:scale-110 transition-transform duration-200">
              <Zap className="w-5 h-5" />
            </div>
            <div className="font-medium text-foreground">Generate CV</div>
            <div className="text-sm text-muted mt-1">Create your ATS-optimized resume</div>
          </a>
        </div>
      </div>

      {/* Recent Generated CVs */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-heading font-semibold text-foreground">Recent Generated CVs</h2>
          {generatedCVs.length > 0 && (
            <a href="/create" className="btn btn-primary text-xs flex items-center gap-1">
              <Plus className="w-3.5 h-3.5" />
              New CV
            </a>
          )}
        </div>
        {generatedCVs.length === 0 ? (
          <div className="text-center py-12 text-muted">
            <div className="w-12 h-12 rounded-xl bg-gray-100 text-gray-400 flex items-center justify-center mx-auto mb-4">
              <FileText className="w-6 h-6" />
            </div>
            <p className="font-medium text-foreground mb-1">No CVs generated yet</p>
            <p className="text-sm mb-4">Click "Create New CV" to get started!</p>
            <a href="/create" className="btn btn-primary">Create Your First CV</a>
          </div>
        ) : (
          <div className="space-y-3">
            {generatedCVs.slice(0, 5).map((cv) => {
              const score = cv.ats_score != null ? Math.round(cv.ats_score) : null;
              const scoreColor = score !== null
                ? score >= 80 ? "text-success" : score >= 60 ? "text-amber-500" : "text-red-500"
                : "text-muted";

              return (
                <div key={cv.id} className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-4 border border-border rounded-lg hover:bg-surface transition-colors">
                  <div className="min-w-0">
                    <div className="font-medium text-foreground truncate">
                      {cv.template_name.charAt(0).toUpperCase() + cv.template_name.slice(1)} Template
                    </div>
                    <div className="text-sm text-muted flex flex-wrap items-center gap-x-3 gap-y-1">
                      <span>{new Date(cv.created_at).toLocaleDateString()}</span>
                      {score !== null && (
                        <span className={`font-medium ${scoreColor}`}>ATS: {score}%</span>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2 shrink-0">
                    <a
                      href={`/preview/${cv.id}`}
                      className="btn btn-ghost text-xs flex items-center gap-1"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      Preview
                    </a>
                    <button
                      onClick={() => handleDownload(cv)}
                      className="btn btn-outline text-xs flex items-center gap-1"
                    >
                      <Download className="w-3.5 h-3.5" />
                      Download
                    </button>
                    <button
                      onClick={() => handleDeleteGenerated(cv)}
                      disabled={busyId === cv.id}
                      className="btn btn-outline text-xs flex items-center gap-1 text-red-500 hover:bg-red-50 disabled:opacity-50"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                      Delete
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Original CVs */}
      <div className="card p-6">
        <h2 className="text-lg font-heading font-semibold text-foreground mb-4">Original CVs</h2>
        {originalCVs.length === 0 ? (
          <p className="text-sm text-muted py-6 text-center">No original CVs uploaded yet.</p>
        ) : (
          <div className="space-y-3">
            {originalCVs.map((cv) => (
              <div key={cv.id} className="flex items-center justify-between gap-3 p-4 border border-border rounded-lg">
                <div className="min-w-0">
                  <div className="font-medium text-foreground truncate">{cv.file_name || "CV"}</div>
                  <div className="text-sm text-muted flex flex-wrap items-center gap-x-3 gap-y-1">
                    <span>{new Date(cv.created_at).toLocaleDateString()}</span>
                    {cv.detected_style && <span>Style: {cv.detected_style}</span>}
                  </div>
                </div>
                <div className="flex gap-2 shrink-0">
                  <button
                    onClick={() => handleDeleteOriginal(cv)}
                    disabled={busyId === cv.id}
                    className="btn btn-outline text-xs flex items-center gap-1 text-red-500 hover:bg-red-50 disabled:opacity-50"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
