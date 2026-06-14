"use client";

import { useSearchParams } from "next/navigation";

export default function PreviewPage() {
  const searchParams = useSearchParams();
  const cvId = searchParams.get("id");
  const score = searchParams.get("score") || "85";

  return (
    <div className="max-w-5xl mx-auto px-6 py-8">
      <header className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">CV Preview</h1>
        <div className="flex gap-3">
          <button className="btn btn-outline">
            Change Template
          </button>
          <a href="#" className="btn btn-primary">
            Download PDF
          </a>
        </div>
      </header>

      <div className="grid md:grid-cols-4 gap-6">
        {/* ATS Score */}
        <div className="card p-6 md:col-span-1">
          <h3 className="font-semibold mb-4">ATS Score</h3>
          <div className="text-center">
            <div className="text-4xl font-bold text-green-600 mb-2">{score}%</div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-green-500 h-2 rounded-full"
                style={{ width: `${score}%` }}
              />
            </div>
          </div>
          <div className="mt-6 text-sm text-gray-600">
            <p className="font-medium mb-2">Keywords Matched</p>
            <p>Good keyword coverage detected. Your CV is well-optimized for ATS systems.</p>
          </div>
        </div>

        {/* PDF Preview */}
        <div className="card md:col-span-3 p-6">
          <div className="bg-gray-100 rounded-lg h-[600px] flex items-center justify-center">
            {cvId ? (
              <iframe
                src={`http://localhost:8000/api/cv/${cvId}/preview`}
                className="w-full h-full rounded-lg"
                title="CV Preview"
              />
            ) : (
              <div className="text-center text-gray-400">
                <div className="text-4xl mb-4">📄</div>
                <p>Generate a CV to see the preview here</p>
                <a href="/create" className="btn btn-primary mt-4">
                  Create New CV
                </a>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
