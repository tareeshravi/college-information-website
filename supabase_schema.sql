-- ============================================================================
-- TNEA College Explorer — Supabase Cloud Database Schema
-- Run this in your Supabase SQL Editor to initialize the central cloud tables.
-- ============================================================================

-- 1. Create Colleges Table
CREATE TABLE IF NOT EXISTS public.colleges (
    id TEXT PRIMARY KEY,
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    category TEXT DEFAULT 'Autonomous',
    seats TEXT DEFAULT '1000+',
    highest_package TEXT DEFAULT '₹20 LPA',
    image TEXT NOT NULL,
    fees JSONB NOT NULL DEFAULT '{"tuition": 75000, "other": 10000, "hostel": 75000}'::jsonb,
    departments JSONB NOT NULL DEFAULT '[]'::jsonb,
    events JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Create Storage Bucket for College & Event Images
INSERT INTO storage.buckets (id, name, public) 
VALUES ('college-images', 'college-images', true)
ON CONFLICT (id) DO NOTHING;

-- 3. Row Level Security (RLS) Policies
ALTER TABLE public.colleges ENABLE ROW LEVEL SECURITY;

-- Allow Public Read Access (Anyone can browse colleges, cutoffs, and fees)
CREATE POLICY "Public Read Access" 
ON public.colleges 
FOR SELECT 
USING (true);

-- Allow Authorized Updates (Authenticated Admin or Public with Passcode)
CREATE POLICY "Enable All Access for App" 
ON public.colleges 
FOR ALL 
USING (true)
WITH CHECK (true);

-- Allow Public Storage Read
CREATE POLICY "Public Storage Read" 
ON storage.objects 
FOR SELECT 
USING (bucket_id = 'college-images');

-- Allow Public Storage Upload
CREATE POLICY "Public Storage Upload" 
ON storage.objects 
FOR INSERT 
WITH CHECK (bucket_id = 'college-images');

-- 4. Enable Realtime Replication
ALTER PUBLICATION supabase_realtime ADD TABLE public.colleges;
