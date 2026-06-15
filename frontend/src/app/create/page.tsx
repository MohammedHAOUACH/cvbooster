"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import { api, endpoints } from "@/lib/api-client";
import { useCVStore } from "@/store/cv-store";
import type { Template, OriginalCV, JobPosting } from "@/store/cv-store";

type Step = "upload" | "job" | "template" | "generate";

const TEMPLATE_ICONS: Record<string, string> = {
  clean: "📝",
  modern: "🎨",
  minimal: "⬜",
  corporate: "👔",
  tech: "💻",
  creative: "🎭",
  academic: "🎓",
  executive: "📊",
};

export default function CreatePage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const step = useCVStore((s) => s.step);
  const setStep = useCVStore((s) => s.setStep);
  const uploadedCV = useCVStore((s) => s.uploadedCV);
  const setUploadedCV = useCVStore((s) => s.setUploadedCV);
  const uploadLoading = useCVStore((s) => s.uploadLoading);
  const setUploadLoading = useCVStore((s) => s.setUploadLoading);
  const jobPosting = useCVStore((s) => s.jobPosting);
  const setJobPosting = useCVStore((s) => s.setJobPosting);
  const jobLoading = useCVStore((s) => s.jobLoading);
  const setJobLoading = useCVStore((s) => s.setJobLoading);
  const selectedTemplate = useCVStore((s) => s.selectedTemplate);
  const setSelectedTemplate = useCVStore((s) => s.setSelectedTemplate);
  const templates = useCVStore((s) => s.templates);
  const setTemplates = useCVStore((s) => s.setTemplates);
  const generating = useCVStore((s) => s.generating);
  const setGenerating = useCVStore((s) => s.setGenerating);

  const [jobInput, setJobInput] = useState("");
  const [jobType, setJobType] = useState<"url" | "text">("url");
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState("");
  const [isDragging, setIsDragging] = useState(false);

  useEffect(() => {
    async function loadTemplates() {
      try {
        const res = await api.get(endpoints.templates.list);
        const tpls: Template[] = res.data.templates || [];
        setTemplates(tpls);
        if (tpls.length > 0 && !tpls.find((t) => t.name === selectedTemplate)) {
          setSelectedTemplate(tpls[0].name);
        }
      } catch {
        // use defaults
      }
    }
    loadTemplates();
  }, [setTemplates, setSelectedTemplate, selectedTemplate]);

  const handleFile = useCallback(
    async (file: File) => {
      if (!file || file.type !== "application/pdf") {
        setError("Please upload a PDF file");
        return;
      }
      if (file.size > 10 * 1024 * 1024) {
        setError("File must be under 10MB");
        return;
      }

      setError(null);
      setFileName(file.name);
      setUploadLoading(true);

      try {
        const formData = new FormData();
        formData.append("file", file);

        const res = await api.post(endpoints.upload.cv, formData, {
          headers: { "Content-Type": "multipart/form-data" },
          timeout: 120000,
        });

        const cv: OriginalCV = res.data.cv;
        setUploadedCV(cv);
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : "Upload failed";
        setError("Upload failed: " + message);
        setFileName("");
      } finally {
        setUploadLoading(false);
      }
    },
    [setUploadedCV, setUploadLoading]
  );

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };
  const onDragLeave = () => setIsDragging(false);
  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFile(file);
  };

  const handleJobSubmit = async () => {
    if (!jobInput.trim()) {
      setError("Please enter a job URL or paste the job description");
      return;
    }
    setError(null);
    setJobLoading(true);

    try {
      let res;
      if (jobType === "url") {
        res = await api.post(endpoints.jobs.scrape, { source_url: jobInput });
      } else {
        res = await api.post(endpoints.jobs.paste, { raw_content: jobInput });
      }
      const job: JobPosting = res.data.job;
      setJobPosting(job);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Job parsing failed";
      setError(message);
    } finally {
      setJobLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!uploadedCV || !jobPosting) {
      setError("Please complete all steps first");
      return;
    }
    setError(null);
    setGenerating(true);

    try {
      const res = await api.post(endpoints.cv.generate, {
        original_cv_id: uploadedCV.id,
        job_posting_id: jobPosting.id,
        template_name: selectedTemplate,
      }, { timeout: 300000 });

      const generatedCV = res.data.generated_cv;
      const score = generatedCV.ats_score || 85;
      router.push(`/preview/${generatedCV.id}?score=${score}`);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Generation failed";
      setError("Generation failed: " + message);
      setGenerating(false);
    }
  };

  const steps: { key: Step; label: string }[] = [
    { key: "upload", label: "Upload CV" },
    { key: "job", label: "Job Posting" },
    { key: "template", label: "Choose Style" },
    { key: "generate", label: "Generate" },
  ];
  const stepIndex = steps.findIndex((s) => s.key === step);

  return (
    <div className="max-w-4xl mx-auto px-6 py-8">
      <div className="flex items-center justify-between mb-8">
        {steps.map((s, i) => (
          <div key={s.key} className="flex items-center">
            <div
              className={`flex items-center gap-2 ${
                step === s.key ? "text-primary-600 font-semibold" : "text-gray-400"
              }`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                  step === s.key
                    ? "bg-primary-600 text-white"
                    : stepIndex > i
                    ? "bg-green-500 text-white"
                    : "bg-gray-200"
                }`}
              >
                {stepIndex > i ? "✓" : i + 1}
              </div>
              <span className="text-sm hidden sm:inline">{s.label}</span>
            </div>
            {i < steps.length - 1 && (
              <div className="w-12 h-0.5 bg-gray-200 mx-2" />
            )}
          </div>
        ))}
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-4 text-sm">
          {error}
        </div>
      )}

      {/* STEP 1 */}
      {step === "upload" && (
        <div className="card p-8">
          <h2 className="text-xl font-semibold mb-4">Upload Your CV</h2>
          <p className="text-gray-600 mb-6">
            Upload your existing resume as a PDF file. We will extract all your
            experience, skills, and education.
          </p>

          <div
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition ${
              isDragging
                ? "border-primary-400 bg-primary-50"
                : "border-gray-300 hover:border-primary-400"
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,application/pdf"
              onChange={onFileChange}
              className="hidden"
            />
            <div className="text-4xl mb-4">
              {uploadLoading ? "⚙️" : uploadedCV ? "✅" : "📄"}
            </div>
            {uploadLoading ? (
              <p className="font-medium text-primary-600">Analyzing your CV...</p>
            ) : uploadedCV ? (
              <div>
                <p className="font-medium text-green-600">
                  CV uploaded: {uploadedCV.file_name}
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  {(uploadedCV.file_size / 1024).toFixed(1)} KB · Parsed successfully
                </p>
              </div>
            ) : (
              <div>
                <p className="font-medium">
                  {isDragging ? "Drop your CV here" : "Click to upload or drag and drop"}
                </p>
                <p className="text-sm text-gray-500 mt-2">PDF files only, max 10MB</p>
              </div>
            )}
          </div>

          {fileName && uploadLoading && (
            <p className="text-sm text-gray-500 mt-2">Processing: {fileName}</p>
          )}

          {uploadedCV && !uploadLoading && (
            <button
              onClick={() => setStep("job")}
              className="btn btn-primary mt-6 ml-auto block"
            >
              Continue →
            </button>
          )}
        </div>
      )}

      {/* STEP 2 */}
      {step === "job" && (
        <div className="card p-8">
          <h2 className="text-xl font-semibold mb-4">Job Posting</h2>
          <p className="text-gray-600 mb-6">
            Paste the job URL or description below.
          </p>

          <div className="flex gap-2 mb-4">
            <button
              onClick={() => setJobType("url")}
              className={`btn ${jobType === "url" ? "btn-primary" : "btn-outline"}`}
            >
              URL
            </button>
            <button
              onClick={() => setJobType("text")}
              className={`btn ${jobType === "text" ? "btn-primary" : "btn-outline"}`}
            >
              Paste Text
            </button>
          </div>

          {jobType === "url" ? (
            <input
              type="url"
              placeholder="https://linkedin.com/jobs/view/..."
              className="input mb-4"
              value={jobInput}
              onChange={(e) => setJobInput(e.target.value)}
            />
          ) : (
            <textarea
              placeholder="Paste the job description here..."
              className="input min-h-[200px] resize-y mb-4"
              value={jobInput}
              onChange={(e) => setJobInput(e.target.value)}
            />
          )}

          {!jobPosting && jobInput && (
            <button
              onClick={handleJobSubmit}
              disabled={jobLoading}
              className="btn btn-primary"
            >
              {jobLoading ? "Analyzing..." : "Analyze Job Posting"}
            </button>
          )}

          {jobPosting && (
            <div>
              <div className="bg-green-50 text-green-700 p-3 rounded-lg mb-4">
                ✓ Job analyzed: {jobPosting.title || "Job posting"}
                {jobPosting.company ? ` at ${jobPosting.company}` : ""}
              </div>
              <div className="flex justify-between">
                <button onClick={() => setStep("upload")} className="btn btn-outline">
                  ← Back
                </button>
                <button onClick={() => setStep("template")} className="btn btn-primary">
                  Continue →
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* STEP 3 */}
      {step === "template" && (
        <div className="card p-8">
          <h2 className="text-xl font-semibold mb-2">Choose a Template</h2>
          <p className="text-gray-600 mb-6">
            Select the style for your ATS-optimized CV.
          </p>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {(templates.length > 0 ? templates : [
              { name: "clean", display_name: "Clean", description: "Simple", category: "general" },
              { name: "modern", display_name: "Modern", description: "Color accents", category: "tech" },
              { name: "minimal", display_name: "Minimal", description: "Clean typography", category: "creative" },
              { name: "corporate", display_name: "Corporate", description: "Professional", category: "corporate" },
              { name: "tech", display_name: "Tech", description: "Developer", category: "tech" },
              { name: "creative", display_name: "Creative", description: "Bold", category: "creative" },
              { name: "academic", display_name: "Academic", description: "Research", category: "academic" },
              { name: "executive", display_name: "Executive", description: "Leadership", category: "executive" },
            ] as Template[]).map((t) => (
              <button
                key={t.name}
                onClick={() => setSelectedTemplate(t.name)}
                className={`card p-4 text-center transition ${
                  selectedTemplate === t.name
                    ? "ring-2 ring-primary-500 border-primary-500"
                    : "hover:border-primary-300"
                }`}
              >
                <div className="text-2xl mb-2">{TEMPLATE_ICONS[t.name] || "📄"}</div>
                <div className="font-medium text-sm">{t.display_name || t.name}</div>
                <div className="text-xs text-gray-500">{t.description}</div>
              </button>
            ))}
          </div>

          <div className="flex justify-between mt-6">
            <button onClick={() => setStep("job")} className="btn btn-outline">
              ← Back
            </button>
            <button onClick={() => setStep("generate")} className="btn btn-primary">
              Continue →
            </button>
          </div>
        </div>
      )}

      {/* STEP 4 */}
      {step === "generate" && (
        <div className="card p-8 text-center">
          <h2 className="text-xl font-semibold mb-2">Ready to Generate</h2>
          <p className="text-gray-600 mb-6">
            Your CV will be optimized with the{" "}
            <strong>{selectedTemplate}</strong> template.
          </p>

          <div className="bg-gray-50 rounded-lg p-4 mb-6 text-sm text-left max-w-md mx-auto space-y-2">
            <div><strong>CV:</strong> {uploadedCV?.file_name || "Not uploaded"}</div>
            <div>
              <strong>Job:</strong>{" "}
              {jobPosting?.title
                ? `"${jobPosting.title}" ${jobPosting.company ? `at ${jobPosting.company}` : ""}`
                : jobType === "url" ? "Scraped from URL" : "Pasted text"}
            </div>
            <div><strong>Template:</strong> {selectedTemplate}</div>
          </div>

          {!generating ? (
            <div className="flex gap-3 justify-center">
              <button onClick={() => setStep("template")} className="btn btn-outline">
                ← Change Template
              </button>
              <button
                onClick={handleGenerate}
                disabled={!uploadedCV || !jobPosting}
                className="btn btn-primary px-8 py-3 text-base"
              >
                Generate My CV
              </button>
            </div>
          ) : (
            <div>
              <div className="text-4xl mb-4">⚙️</div>
              <p className="text-lg font-medium">Generating your ATS-optimized CV...</p>
              <p className="text-gray-500 text-sm mt-2">This may take up to 2 minutes</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
