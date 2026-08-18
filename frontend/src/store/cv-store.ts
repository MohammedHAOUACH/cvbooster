import { create } from "zustand";

export interface Template {
  name: string;
  display_name: string;
  description: string;
  category: string;
}

export interface OriginalCV {
  id: string;
  file_url: string;
  file_name: string;
  file_size: number;
  extracted_data: Record<string, unknown>;
  detected_style?: string;
  created_at: string;
}

export interface JobPosting {
  id: string;
  source_url?: string;
  title?: string;
  company?: string;
  raw_content: string;
  detected_language?: string;
  parsed_data?: Record<string, unknown>;
  created_at: string;
}

export interface GeneratedCV {
  id: string;
  original_cv_id: string;
  job_posting_id: string;
  template_name: string;
  output_language?: string;
  original_cv_style?: string;
  file_url: string;
  ats_score?: number;
  keywords_matched?: number;
  keywords_total?: number;
  created_at: string;
}

type Step = "upload" | "job" | "template" | "generate";

interface CVStore {
  // Wizard state
  step: Step;
  setStep: (step: Step) => void;

  // Upload
  uploadedCV: OriginalCV | null;
  uploadLoading: boolean;
  setUploadedCV: (cv: OriginalCV | null) => void;
  setUploadLoading: (loading: boolean) => void;

  // Job
  jobPosting: JobPosting | null;
  jobLoading: boolean;
  setJobPosting: (job: JobPosting | null) => void;
  setJobLoading: (loading: boolean) => void;

  // Template
  selectedTemplate: string;
  templates: Template[];
  templatesLoading: boolean;
  setSelectedTemplate: (name: string) => void;
  setTemplates: (templates: Template[]) => void;
  setTemplatesLoading: (loading: boolean) => void;

  // Generation
  generating: boolean;
  generatedCV: GeneratedCV | null;
  setGenerating: (loading: boolean) => void;
  setGeneratedCV: (cv: GeneratedCV | null) => void;

  // History (dashboard)
  allGeneratedCVs: GeneratedCV[];
  allOriginalCVs: OriginalCV[];
  setAllGeneratedCVs: (cvs: GeneratedCV[]) => void;
  setAllOriginalCVs: (cvs: OriginalCV[]) => void;

  // Reset
  reset: () => void;
}

export const useCVStore = create<CVStore>((set) => ({
  step: "upload",
  setStep: (step) => set({ step }),

  uploadedCV: null,
  uploadLoading: false,
  setUploadedCV: (cv) => set({ uploadedCV: cv }),
  setUploadLoading: (loading) => set({ uploadLoading: loading }),

  jobPosting: null,
  jobLoading: false,
  setJobPosting: (job) => set({ jobPosting: job }),
  setJobLoading: (loading) => set({ jobLoading: loading }),

  selectedTemplate: "clean",
  templates: [],
  templatesLoading: false,
  setSelectedTemplate: (name) => set({ selectedTemplate: name }),
  setTemplates: (templates) => set({ templates }),
  setTemplatesLoading: (loading) => set({ templatesLoading: loading }),

  generating: false,
  generatedCV: null,
  setGenerating: (loading) => set({ generating: loading }),
  setGeneratedCV: (cv) => set({ generatedCV: cv }),

  allGeneratedCVs: [],
  allOriginalCVs: [],
  setAllGeneratedCVs: (cvs) => set({ allGeneratedCVs: cvs }),
  setAllOriginalCVs: (cvs) => set({ allOriginalCVs: cvs }),

  reset: () =>
    set({
      step: "upload",
      uploadedCV: null,
      uploadLoading: false,
      jobPosting: null,
      jobLoading: false,
      selectedTemplate: "clean",
      generating: false,
      generatedCV: null,
    }),
}));
