"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

type Step = "upload" | "job" | "template" | "generate";

const TEMPLATES = [
  { name: "clean", display: "Clean", desc: "Simple, elegant" },
  { name: "modern", display: "Modern", desc: "Color accents" },
  { name: "minimal", display: "Minimal", desc: "Typography only" },
  { name: "corporate", display: "Corporate", desc: "Professional" },
  { name: "tech", display: "Tech", desc: "Developer focused" },
  { name: "creative", display: "Creative", desc: "Bold & vibrant" },
  { name: "academic", display: "Academic", desc: "Publications first" },
  { name: "executive", display: "Executive", desc: "Leadership focus" },
];

export default function CreatePage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>("upload");
  const [uploaded, setUploaded] = useState(false);
  const [jobInput, setJobInput] = useState("");
  const [jobType, setJobType] = useState<"url" | "text">("url");
  const [jobDone, setJobDone] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState("clean");
  const [generating, setGenerating] = useState(false);

  const steps: { key: Step; label: string }[] = [
    { key: "upload", label: "1. Upload CV" },
    { key: "job", label: "2. Job Posting" },
    { key: "template", label: "3. Choose Style" },
    { key: "generate", label: "4. Generate" },
  ];

  return (
    <div className="max-w-4xl mx-auto px-6 py-8">
      {/* Step Indicator */}
      <div className="flex items-center justify-between mb-8">
        {steps.map((s, i) => (
          <div key={s.key} className="flex items-center">
            <div className={`flex items-center gap-2 ${step === s.key ? "text-primary-600 font-semibold" : "text-gray-400"}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                step === s.key ? "bg-primary-600 text-white" :
                ["upload", "job", "template", "generate"].indexOf(step) > i ? "bg-green-500 text-white" : "bg-gray-200"
              }`}>
                {["upload", "job", "template", "generate"].indexOf(step) > i ? "✓" : i + 1}
              </div>
              <span className="text-sm hidden sm:inline">{s.label}</span>
            </div>
            {i < steps.length - 1 && <div className="w-12 h-0.5 bg-gray-200 mx-2" />}
          </div>
        ))}
      </div>

      {/* Step Content */}
      {step === "upload" && (
        <div className="card p-8">
          <h2 className="text-xl font-semibold mb-4">Upload Your CV</h2>
          <p className="text-gray-600 mb-6">Upload your existing resume as a PDF file</p>
          <div
            className="border-2 border-dashed border-gray-300 rounded-xl p-12 text-center hover:border-primary-400 transition cursor-pointer"
            onClick={() => setUploaded(true)}
          >
            <div className="text-4xl mb-4">{uploaded ? "✅" : "📄"}</div>
            {uploaded ? (
              <div>
                <p className="font-medium text-green-600">CV uploaded successfully!</p>
                <p className="text-sm text-gray-500 mt-2">Your resume has been analyzed</p>
              </div>
            ) : (
              <div>
                <p className="font-medium">Click to upload or drag and drop</p>
                <p className="text-sm text-gray-500 mt-2">PDF files only, max 10MB</p>
              </div>
            )}
          </div>
          {uploaded && (
            <button
              onClick={() => setStep("job")}
              className="btn btn-primary mt-6 ml-auto block"
            >
              Continue
            </button>
          )}
        </div>
      )}

      {step === "job" && (
        <div className="card p-8">
          <h2 className="text-xl font-semibold mb-4">Job Posting</h2>
          <p className="text-gray-600 mb-6">Paste the job URL or description</p>

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
            <div>
              <input
                type="url"
                placeholder="https://linkedin.com/jobs/view/..."
                className="input mb-4"
                value={jobInput}
                onChange={(e) => setJobInput(e.target.value)}
              />
            </div>
          ) : (
            <textarea
              placeholder="Paste the job description here..."
              className="input min-h-[200px] resize-y"
              value={jobInput}
              onChange={(e) => setJobInput(e.target.value)}
            />
          )}

          {!jobDone && jobInput && (
            <button
              onClick={() => { setJobDone(true); }}
              className="btn btn-primary mt-4"
            >
              Analyze Job Posting
            </button>
          )}

          {jobDone && (
            <div>
              <div className="bg-green-50 text-green-700 p-3 rounded-lg mb-4">
                Job posting analyzed! Key skills identified.
              </div>
              <button
                onClick={() => setStep("template")}
                className="btn btn-primary"
              >
                Continue
              </button>
            </div>
          )}
        </div>
      )}

      {step === "template" && (
        <div className="card p-8">
          <h2 className="text-xl font-semibold mb-2">Choose a Template</h2>
          <p className="text-gray-600 mb-6">Select the style for your ATS-optimized CV</p>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {TEMPLATES.map((t) => (
              <button
                key={t.name}
                onClick={() => setSelectedTemplate(t.name)}
                className={`card p-4 text-center transition ${
                  selectedTemplate === t.name
                    ? "ring-2 ring-primary-500 border-primary-500"
                    : "hover:border-primary-300"
                }`}
              >
                <div className="text-2xl mb-2">
                  {t.name === "clean" ? "📝" :
                   t.name === "modern" ? "🎨" :
                   t.name === "minimal" ? "⬜" :
                   t.name === "corporate" ? "👔" :
                   t.name === "tech" ? "💻" :
                   t.name === "creative" ? "🎭" :
                   t.name === "academic" ? "🎓" : "📊"}
                </div>
                <div className="font-medium text-sm">{t.display}</div>
                <div className="text-xs text-gray-500">{t.desc}</div>
              </button>
            ))}
          </div>

          <div className="flex justify-between mt-6">
            <button onClick={() => setStep("job")} className="btn btn-outline">
              Back
            </button>
            <button
              onClick={() => setStep("generate")}
              className="btn btn-primary"
            >
              Continue
            </button>
          </div>
        </div>
      )}

      {step === "generate" && (
        <div className="card p-8 text-center">
          <h2 className="text-xl font-semibold mb-2">Ready to Generate</h2>
          <p className="text-gray-600 mb-6">
            Your CV will be optimized for ATS compatibility
          </p>

          {!generating ? (
            <>
              <div className="bg-gray-50 rounded-lg p-4 mb-6 text-sm">
                <div>Template: <strong>{selectedTemplate}</strong></div>
                <div>Input: <strong>PDF CV + {jobType === "url" ? "Scraped URL" : "Pasted text"}</strong></div>
              </div>
              <button
                onClick={() => setGenerating(true)}
                className="btn btn-primary px-8 py-3 text-base"
              >
                Generate My CV
              </button>
            </>
          ) : (
            <div>
              <div className="animate-spin text-4xl mb-4">⚙️</div>
              <p className="text-lg font-medium">Generating your ATS-optimized CV...</p>
              <p className="text-gray-500 text-sm mt-2">This usually takes 15-30 seconds</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
