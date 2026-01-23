-- =============================================================================
-- Supabase Schema for Academic Evaluation System
-- University of Hyderabad
-- =============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- MAIN TABLES
-- =============================================================================

-- Students table (core academic data)
CREATE TABLE IF NOT EXISTS public.students (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Identity
  student_name TEXT NOT NULL,
  roll_number TEXT UNIQUE,
  email TEXT,
  phone TEXT,
  
  -- Academic info
  department TEXT,
  program TEXT,
  semester TEXT,
  academic_year TEXT DEFAULT '2024-2025',
  
  -- Performance
  cgpa TEXT,
  sgpa TEXT,
  attendance_percentage TEXT,
  
  -- Personal
  dob DATE,
  gender TEXT,
  category TEXT,
  
  -- Summaries
  awards_and_honors TEXT,
  extracurricular_activities TEXT,
  remarks TEXT,
  
  -- Full data (JSONB)
  analysis JSONB,
  metadata JSONB,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Courses table
CREATE TABLE IF NOT EXISTS public.courses (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  student_id UUID REFERENCES public.students(id) ON DELETE CASCADE,
  
  course_code TEXT NOT NULL,
  course_name TEXT NOT NULL,
  credits INTEGER,
  grade TEXT,
  semester TEXT,
  academic_year TEXT,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Academic Projects table
CREATE TABLE IF NOT EXISTS public.academic_projects (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  student_id UUID REFERENCES public.students(id) ON DELETE CASCADE,
  
  project_title TEXT NOT NULL,
  supervisor TEXT,
  duration TEXT,
  description TEXT,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Internships table
CREATE TABLE IF NOT EXISTS public.internships (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  student_id UUID REFERENCES public.students(id) ON DELETE CASCADE,
  
  organization TEXT NOT NULL,
  role TEXT,
  duration TEXT,
  description TEXT,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Certifications table
CREATE TABLE IF NOT EXISTS public.certifications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  student_id UUID REFERENCES public.students(id) ON DELETE CASCADE,
  
  name TEXT NOT NULL,
  issuing_body TEXT,
  date_obtained DATE,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Publications table
CREATE TABLE IF NOT EXISTS public.publications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  student_id UUID REFERENCES public.students(id) ON DELETE CASCADE,
  
  title TEXT NOT NULL,
  venue TEXT,
  year INTEGER,
  authors TEXT,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- INDEXES
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_students_roll_number ON public.students(roll_number);
CREATE INDEX IF NOT EXISTS idx_students_email ON public.students(email);
CREATE INDEX IF NOT EXISTS idx_students_department ON public.students(department);
CREATE INDEX IF NOT EXISTS idx_students_program ON public.students(program);
CREATE INDEX IF NOT EXISTS idx_courses_student_id ON public.courses(student_id);
CREATE INDEX IF NOT EXISTS idx_projects_student_id ON public.academic_projects(student_id);
CREATE INDEX IF NOT EXISTS idx_internships_student_id ON public.internships(student_id);

-- =============================================================================
-- AUTO-UPDATE TRIGGER
-- =============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_students_updated_at
  BEFORE UPDATE ON public.students
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
