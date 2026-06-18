-- ============================================================
-- CVBooster Database Setup for Supabase
-- Run this in the Supabase SQL Editor
-- ============================================================

-- 1. Profiles table (extends auth.users)
CREATE TABLE IF NOT EXISTS profiles (
  id            UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  full_name     TEXT DEFAULT '',
  avatar_url    TEXT DEFAULT '',
  provider      TEXT DEFAULT '',
  created_at    TIMESTAMPTZ DEFAULT now(),
  updated_at    TIMESTAMPTZ DEFAULT now()
);

-- 2. Original CVs
CREATE TABLE IF NOT EXISTS original_cvs (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  file_url      TEXT NOT NULL,
  file_name     TEXT,
  file_size     BIGINT,
  extracted_data JSONB DEFAULT '{}',
  created_at    TIMESTAMPTZ DEFAULT now()
);

-- 3. Job Postings
CREATE TABLE IF NOT EXISTS job_postings (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id           UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  source_url        TEXT,
  title             TEXT,
  company           TEXT,
  raw_content       TEXT,
  detected_language TEXT DEFAULT 'en',
  parsed_data       JSONB DEFAULT '{}',
  created_at        TIMESTAMPTZ DEFAULT now()
);

-- 4. Generated CVs
CREATE TABLE IF NOT EXISTS generated_cvs (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id           UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  original_cv_id    UUID NOT NULL REFERENCES original_cvs(id) ON DELETE CASCADE,
  job_posting_id    UUID NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
  template_name     TEXT NOT NULL,
  output_language   TEXT DEFAULT 'en',
  original_cv_style TEXT DEFAULT 'clean',
  file_url          TEXT NOT NULL,
  llm_output        JSONB DEFAULT '{}',
  ats_score         REAL,
  keywords_matched  INTEGER,
  keywords_total    INTEGER,
  created_at        TIMESTAMPTZ DEFAULT now(),
  updated_at        TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- Row Level Security (RLS) Policies
-- ============================================================

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE original_cvs ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_postings ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_cvs ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "Users can view own profile"
  ON profiles FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON profiles FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile"
  ON profiles FOR INSERT WITH CHECK (auth.uid() = id);

-- Original CVs policies
CREATE POLICY "Users can access own original CVs"
  ON original_cvs FOR ALL USING (auth.uid() = user_id);

-- Job Postings policies
CREATE POLICY "Users can access own job postings"
  ON job_postings FOR ALL USING (auth.uid() = user_id);

-- Generated CVs policies
CREATE POLICY "Users can access own generated CVs"
  ON generated_cvs FOR ALL USING (auth.uid() = user_id);

-- ============================================================
-- Trigger: Auto-create profile on signup
-- ============================================================

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name, avatar_url, provider)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
    COALESCE(NEW.raw_user_meta_data->>'avatar_url', ''),
    COALESCE(NEW.raw_user_meta_data->>'provider', '')
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ============================================================
-- Storage Buckets
-- ============================================================

-- Create storage buckets (run these if they don't exist)
INSERT INTO storage.buckets (id, name, public)
VALUES ('original-cvs', 'original-cvs', false)
ON CONFLICT (id) DO NOTHING;

INSERT INTO storage.buckets (id, name, public)
VALUES ('generated-cvs', 'generated-cvs', false)
ON CONFLICT (id) DO NOTHING;

-- Storage policies
CREATE POLICY "Users can upload own CVs"
  ON storage.objects FOR INSERT
  WITH CHECK (
    bucket_id = 'original-cvs' AND
    auth.uid()::text = (storage.foldername(name))[1]
  );

CREATE POLICY "Users can view own CVs"
  ON storage.objects FOR SELECT
  USING (
    bucket_id IN ('original-cvs', 'generated-cvs') AND
    auth.uid()::text = (storage.foldername(name))[1]
  );

CREATE POLICY "Users can delete own CVs"
  ON storage.objects FOR DELETE
  USING (
    bucket_id IN ('original-cvs', 'generated-cvs') AND
    auth.uid()::text = (storage.foldername(name))[1]
  );

-- ============================================================
-- Indexes for performance
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_original_cvs_user_id ON original_cvs(user_id);
CREATE INDEX IF NOT EXISTS idx_job_postings_user_id ON job_postings(user_id);
CREATE INDEX IF NOT EXISTS idx_generated_cvs_user_id ON generated_cvs(user_id);
CREATE INDEX IF NOT EXISTS idx_generated_cvs_original_cv ON generated_cvs(original_cv_id);
CREATE INDEX IF NOT EXISTS idx_generated_cvs_job ON generated_cvs(job_posting_id);
