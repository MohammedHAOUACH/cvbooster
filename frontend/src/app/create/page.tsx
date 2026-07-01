"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import { api, endpoints } from "@/lib/api-client";
import { useCVStore } from "@/store/cv-store";
import type { Template, OriginalCV, JobPosting } from "@/store/cv-store";
import { Spinner } from "@/components/ui";
import {
  FileText,
  Upload,
  Link,
  FileInput,
  Palette,
  Sparkles,
  Check,
  ChevronLeft,
  ChevronRight,
  X,
  Loader,
} from "lucide-react";

type Step = "upload" | "job" | "template" | "generate";

const TEMPLATE_ICONS: Record<string, React.ReactNode> = {
  clean: <FileText className="w-6 h-6" />,
  modern: <Palette className="w-6 h-6" />,
  minimal: <FileText className="w-6 h-6" />,
  corporate: <FileText className="w-6 h-6" />,
  tech: <FileText className="w-6 h-6" />,
  creative: <Palette className="w-6 h-6" />,
  academic: <FileText className="w-6 h-6" />,
  executive: <FileText className="w-6 h-6" />,
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

  const steps: { key: Step; label: string; icon: React.ReactNode }[] = [
    { key: "upload", label: "Upload CV", icon: <Upload className="w-4 h-4" /> },
    { key: "job", label: "Job Posting", icon: <Link className="w-4 h-4" /> },
    { key: "template", label: "Choose Style", icon: <Palette className="w-4 h-4" /> },
    { key: "generate", label: "Generate", icon: <Sparkles className="w-4 h-4" /> },
  ];
  const stepIndex = steps.findIndex((s) => s.key === step);

  const goToStep = (targetStep: Step) => {
    const targetIndex = steps.findIndex((s) => s.key === targetStep);
    // Can go back freely, but can only go forward if the current step is complete
    if (targetIndex > stepIndex) {
      // Validate we can move forward
      if (targetStep === "job" && !uploadedCV) return;
      if (targetStep === "template" && !jobPosting) return;
      if (targetStep === "generate" && !uploadedCV || !jobPosting) return;
    }
    setStep(targetStep);
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-heading font-bold text-foreground mb-2">Create Your CV</h1>
        <p className="text-muted">Follow the steps below to generate an ATS-optimized resume</p>
      </div>

      {/* Progress Stepper */}
      <nav className="mb-8" aria-label="Progress">
        <div className="flex items-center justify-between">
          {steps.map((s, i) => {
            const isActive = step === s.key;
            const isCompleted = stepIndex > i;
            const isUpcoming = stepIndex < i;

            return (
              <div key={s.key} className="flex items-center flex-1 last:flex-none">
                <button
                  onClick={() => goToStep(s.key)}
                  disabled={isUpcoming}
                  className={`flex items-center gap-2 group ${
                    isActive ? "cursor-default" : isCompleted ? "cursor-pointer" : "cursor-not-allowed opacity-50"
                  }`}
                  aria-current={isActive ? "step" : undefined}
                >
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-semibold transition-all duration-200 ${
                      isActive
                        ? "bg-primary text-white shadow-standard"
                        : isCompleted
                        ? "bg-success text-white"
                        : "bg-gray-200 text-gray-500"
                    }`}
                  >
                    {isCompleted ? (
                      <Check className="w-5 h-5" />
                    ) : (
                      <span>{i + 1}</span>
                    )}
                  </div>
                  <span className={`text-sm hidden sm:inline font-medium ${
                    isActive ? "text-foreground" : isCompleted ? "text-success" : "text-muted"
                  }`}>
                    {s.label}
                  </span>
                </button>
                {i < steps.length - 1 && (
                  <div className={`flex-1 h-0.5 mx-3 transition-colors duration-200 ${
                    stepIndex > i ? "bg-success" : "bg-gray-200"
                  }`} />
                )}
              </div>
            );
          })}
        </div>
      </nav>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-6 text-sm flex items-center justify-between gap-2">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="shrink-0">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* STEP 1: Upload CV */}
      {step === "upload" && (
        <div className="card p-8 animate-fade-in">
          <div className="mb-6">
            <h2 className="text-xl font-heading font-semibold text-foreground mb-2 flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-primary-100 text-primary flex items-center justify-center">
                <Upload className="w-5 h-5" />
              </div>
              Upload Your CV
            </h2>
            <p className="text-muted ml-13">
              Upload your existing resume as a PDF file. We will extract all your
              experience, skills, and education.
            </p>
          </div>

          <div
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-200 ${
              isDragging
                ? "border-primary-400 bg-primary-50"
                : uploadedCV
                ? "border-success-400 bg-success-50"
                : "border-gray-300 hover:border-primary-400 hover:bg-primary-50/50"
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,application/pdf"
              onChange={onFileChange}
              className="hidden"
            />

            {uploadLoading ? (
              <div className="text-center">
                <div className="w-12 h-12 rounded-xl bg-primary-100 text-primary flex items-center justify-center mx-auto mb-4">
                  <Loader className="w-6 h-6 animate-spin" />
                </div>
                <p className="font-medium text-foreground">Analyzing your CV...</p>
                <p className="text-sm text-muted mt-1">Extracting skills, experience, and education</p>
              </div>
            ) : uploadedCV ? (
              <div className="text-center">
                <div className="w-12 h-12 rounded-xl bg-success-100 text-success flex items-center justify-center mx-auto mb-4">
                  <Check className="w-6 h-6" />
                </div>
                <p className="font-medium text-foreground">CV uploaded successfully</p>
                <p className="text-sm text-muted mt-1">
                  {uploadedCV.file_name} &middot; {(uploadedCV.file_size / 1024).toFixed(1)} KB
                </p>
              </div>
            ) : (
              <div className="text-center">
                <div className="w-12 h-12 rounded-xl bg-primary-100 text-primary flex items-center justify-center mx-auto mb-4">
                  <FileInput className="w-6 h-6" />
                </div>
                <p className="font-medium text-foreground">
                  {isDragging ? "Drop your CV here" : "Click to upload or drag and drop"}
                </p>
                <p className="text-sm text-muted mt-2">PDF files only, max 10MB</p>
              </div>
            )}
          </div>

          {fileName && uploadLoading && (
            <p className="text-sm text-muted mt-2">Processing: {fileName}</p>
          )}

          {uploadedCV && !uploadLoading && (
            <div className="flex justify-end mt-6">
              <button
                onClick={() => setStep("job")}
                className="btn btn-primary flex items-center gap-2"
              >
                Continue
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      )}

      {/* STEP 2: Job Posting */}
      {step === "job" && (
        <div className="card p-8 animate-fade-in">
          <div className="mb-6">
            <h2 className="text-xl font-heading font-semibold text-foreground mb-2 flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-primary-100 text-primary flex items-center justify-center">
                <Link className="w-5 h-5" />
              </div>
              Job Posting
            </h2>
            <p className="text-muted ml-13">
              Paste the job URL or description below so we can identify the key requirements.
            </p>
          </div>

          {/* Input Type Toggle */}
          <div className="flex gap-2 mb-4 p-1 bg-gray-100 rounded-lg w-fit">
            <button
              onClick={() => setJobType("url")}
              className={`btn px-4 py-2 text-sm rounded-md transition-all ${
                jobType === "url"
                  ? "bg-white text-foreground shadow-sm"
                  : "text-muted hover:text-foreground"
              }`}
            >
              <Link className="w-4 h-4 inline mr-2" />
              URL
            </button>
            <button
              onClick={() => setJobType("text")}
              className={`btn px-4 py-2 text-sm rounded-md transition-all ${
                jobType === "text"
                  ? "bg-white text-foreground shadow-sm"
                  : "text-muted hover:text-foreground"
              }`}
            >
              <FileInput className="w-4 h-4 inline mr-2" />
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
              onKeyDown={(e) => {
                if (e.key === "Enter" && jobInput && !jobPosting) {
                  handleJobSubmit();
                }
              }}
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
              className="btn btn-primary flex items-center gap-2"
            >
              {jobLoading ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                "Analyze Job Posting"
              )}
            </button>
          )}

          {jobPosting && (
            <div>
              <div className="bg-success-50 text-success-700 p-4 rounded-lg mb-6 flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-success-200 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Check className="w-3.5 h-3.5" />
                </div>
                <div>
                  <p className="font-medium">Job analyzed successfully</p>
                  <p className="text-sm mt-1">
                    {jobPosting.title || "Job posting"}
                    {jobPosting.company ? ` at ${jobPosting.company}` : ""}
                  </p>
                </div>
              </div>
              <div className="flex justify-between">
                <button onClick={() => setStep("upload")} className="btn btn-outline flex items-center gap-2">
                  <ChevronLeft className="w-4 h-4" />
                  Back
                </button>
                <button onClick={() => setStep("template")} className="btn btn-primary flex items-center gap-2">
                  Continue
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* STEP 3: Template Selection */}
      {step === "template" && (
        <div className="card p-8 animate-fade-in">
          <div className="mb-6">
            <h2 className="text-xl font-heading font-semibold text-foreground mb-2 flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-primary-100 text-primary flex items-center justify-center">
                <Palette className="w-5 h-5" />
              </div>
              Choose a Template
            </h2>
            <p className="text-muted ml-13">
              Select the style for your ATS-optimized CV. Each template is designed to pass through ATS systems.
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {(templates.length > 0 ? templates : [
              { name: "clean", display_name: "Clean", description: "Simple & elegant", category: "general" },
              { name: "modern", display_name: "Modern", description: "Color accents", category: "tech" },
              { name: "minimal", display_name: "Minimal", description: "Clean typography", category: "creative" },
              { name: "corporate", display_name: "Corporate", description: "Professional", category: "corporate" },
              { name: "tech", display_name: "Tech", description: "Developer focused", category: "tech" },
              { name: "creative", display_name: "Creative", description: "Bold & expressive", category: "creative" },
              { name: "academic", display_name: "Academic", description: "Research focused", category: "academic" },
              { name: "executive", display_name: "Executive", description: "Leadership", category: "executive" },
            ] as Template[]).map((t) => (
              <button
                key={t.name}
                onClick={() => setSelectedTemplate(t.name)}
                className={`card p-4 text-center transition-all duration-200 ${
                  selectedTemplate === t.name
                    ? "ring-2 ring-primary border-primary-500 shadow-standard scale-105"
                    : "hover:border-primary-300 hover:shadow-sm"
                }`}
              >
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center mx-auto mb-2 ${
                  selectedTemplate === t.name
                    ? "bg-primary text-white"
                    : "bg-gray-100 text-muted"
                }`}>
                  {TEMPLATE_ICONS[t.name] || <FileText className="w-5 h-5" />}
                </div>
                <div className="font-medium text-sm text-foreground">{t.display_name || t.name}</div>
                <div className="text-xs text-muted mt-1">{t.description}</div>
              </button>
            ))}
          </div>

          <div className="flex justify-between mt-8">
            <button onClick={() => setStep("job")} className="btn btn-outline flex items-center gap-2">
              <ChevronLeft className="w-4 h-4" />
              Back
            </button>
            <button onClick={() => setStep("generate")} className="btn btn-primary flex items-center gap-2">
              Continue
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 4: Generate */}
      {step === "generate" && (
        <div className="card p-8 text-center animate-fade-in">
          <div className="mb-6">
            <div className="w-16 h-16 rounded-xl bg-primary-100 text-primary flex items-center justify-center mx-auto mb-4">
              <Sparkles className="w-8 h-8" />
            </div>
            <h2 className="text-xl font-heading font-semibold text-foreground mb-2">Ready to Generate</h2>
            <p className="text-muted">
              Your CV will be optimized with the{" "}
              <strong className="text-foreground">{selectedTemplate}</strong> template.
            </p>
          </div>

          <div className="bg-surface rounded-lg p-5 mb-8 text-sm text-left max-w-md mx-auto space-y-3">
            <div className="flex items-center gap-3">
              <FileText className="w-4 h-4 text-muted shrink-0" />
              <div>
                <span className="text-muted">CV:</span>{" "}
                <span className="font-medium text-foreground">{uploadedCV?.file_name || "Not uploaded"}</span>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Link className="w-4 h-4 text-muted shrink-0" />
              <div>
                <span className="text-muted">Job:</span>{" "}
                <span className="font-medium text-foreground">
                  {jobPosting?.title
                    ? `"${jobPosting.title}" ${jobPosting.company ? `at ${jobPosting.company}` : ""}`
                    : jobType === "url" ? "Scraped from URL" : "Pasted text"}
                </span>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Palette className="w-4 h-4 text-muted shrink-0" />
              <div>
                <span className="text-muted">Template:</span>{" "}
                <span className="font-medium text-foreground">{selectedTemplate}</span>
              </div>
            </div>
          </div>

          {!generating ? (
            <div className="flex gap-3 justify-center">
              <button onClick={() => setStep("template")} className="btn btn-outline flex items-center gap-2">
                <ChevronLeft className="w-4 h-4" />
                Change Template
              </button>
              <button
                onClick={handleGenerate}
                disabled={!uploadedCV || !jobPosting}
                className="btn btn-primary px-8 py-3 text-base flex items-center gap-2"
              >
                <Sparkles className="w-5 h-5" />
                Generate My CV
              </button>
            </div>
          ) : (
            <div className="text-center">
              <div className="w-12 h-12 rounded-xl bg-primary-100 text-primary flex items-center justify-center mx-auto mb-4">
                <Loader className="w-6 h-6 animate-spin" />
              </div>
              <p className="text-lg font-medium text-foreground">Generating your ATS-optimized CV...</p>
              <p className="text-muted text-sm mt-2">This may take up to 2 minutes</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
