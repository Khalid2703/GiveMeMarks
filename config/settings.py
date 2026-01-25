"""
Configuration settings for the Academic Evaluation & Reporting Assistant.
University of Hyderabad - Academic Document Processing System
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DOCUMENT_DIR = DATA_DIR / "documents"
EXCEL_DIR = DATA_DIR / "excel"
LOG_DIR = DATA_DIR / "logs"

# Create directories if they don't exist
for directory in [DATA_DIR, DOCUMENT_DIR, EXCEL_DIR, LOG_DIR]:
    directory.mkdir(exist_ok=True)

# ==================== LLM CONFIGURATION ====================

# Gemini API (Primary)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

# Cohere API (Fallback)
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "").strip()
COHERE_MODEL = os.getenv("COHERE_MODEL", "command-r")

# General LLM settings
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2000"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))

# ==================== EXCEL CONFIGURATION ====================

EXCEL_FILENAME = "academic_evaluation_results.xlsx"
EXCEL_SHEET_NAME = "Student Data"
EXCEL_COURSES_SHEET_NAME = "Course Details"

# ==================== LOGGING CONFIGURATION ====================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"

# ==================== STREAMLIT CONFIGURATION ====================

STREAMLIT_PAGE_TITLE = "UOH Academic Evaluation Assistant"
STREAMLIT_PAGE_ICON = "🎓"
STREAMLIT_LAYOUT = "wide"

# ==================== SUPABASE CONFIGURATION ====================

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "").strip()
USE_SUPABASE = os.environ.get("USE_SUPABASE", "false").lower() in ("1", "true", "yes")

# ==================== INSTITUTION METADATA ====================

INSTITUTION_NAME = "University of Hyderabad"
INSTITUTION_LOCATION = "Hyderabad, Telangana, India"
ACADEMIC_YEAR_DEFAULT = "2024-2025"

# ==================== ACADEMIC ANALYSIS PROMPT ====================

ACADEMIC_ANALYSIS_PROMPT = """
You are an academic data extraction assistant for the University of Hyderabad.

From the following student academic document, extract academic information and return it in strict JSON format.

Document Text:
{document_text}

Extract the following information and return as JSON with these exact keys:

{{
    "Student Name": "full name",
    "Roll Number": "university ID",
    "Email": "email address",
    "Phone": "contact number",
    "Department": "department name",
    "Program": "degree program (B.Tech, M.Sc, Ph.D, M.Tech)",
    "Semester": "current semester",
    "Academic Year": "year of study (e.g., 2024-2025)",
    "CGPA": "cumulative GPA (e.g., 8.5/10)",
    "SGPA": "semester GPA if mentioned",
    "Attendance Percentage": "attendance % (e.g., 85%)",
    "Date of Birth": "YYYY-MM-DD format",
    "Gender": "Male/Female/Other",
    "Category": "general/OBC/SC/ST/EWS",
    "Courses": [
        {{
            "Course Code": "code (e.g., CS501)",
            "Course Name": "full title",
            "Credits": "credit hours",
            "Grade": "grade (A+, B, 85/100)",
            "Semester": "which semester"
        }}
    ],
    "Academic Projects": [
        {{
            "Project Title": "name",
            "Supervisor": "faculty guide",
            "Duration": "time period",
            "Description": "brief description"
        }}
    ],
    "Internships": [
        {{
            "Organization": "company/institution",
            "Role": "position",
            "Duration": "dates",
            "Description": "brief description"
        }}
    ],
    "Certifications": [
        {{
            "Name": "certification title",
            "Issuing Body": "organization",
            "Date Obtained": "date"
        }}
    ],
    "Publications": [
        {{
            "Title": "paper title",
            "Venue": "conference/journal",
            "Year": "year",
            "Authors": "list of authors"
        }}
    ],
    "Awards and Honors": "academic distinctions summary",
    "Extracurricular Activities": "clubs, sports, cultural activities summary",
    "Remarks": "additional notes"
}}

Guidelines:
1. Return ONLY valid JSON. No explanations or markdown.
2. If field missing, use "" (not null).
3. For arrays, return [] if no data.
4. Extract Roll Number as primary university ID.
5. Normalize phone to digits only with country code.
6. Use university email (@uohyd.ac.in) if multiple emails.
7. Extract ALL courses from grade sheet.
8. Keep summaries concise (2-3 sentences max).
9. Use YYYY-MM-DD for dates.
10. Be accurate - don't invent data.
"""
