# UOH Academic Evaluation & Reporting Assistant

AI-powered academic document processing system for University of Hyderabad.

## 🚀 Features

- **Dual LLM Provider**: Gemini (primary) + Cohere (fallback) for reliability
- **Batch Processing**: Process multiple academic documents simultaneously
- **OCR Support**: Extract text from scanned documents
- **Structured Storage**: Excel + Supabase dual-write
- **Analytics Dashboard**: Streamlit-based UI with insights
- **Comprehensive Logging**: Audit trail for all operations

## 📁 Project Structure

```
UOH_Hackathon/
├── config/
│   └── settings.py         # Configuration
├── data/
│   ├── documents/          # Input PDFs
│   ├── excel/              # Excel exports
│   └── logs/               # Application logs
├── src/
│   ├── core/
│   │   ├── academic_llm_analyzer.py
│   │   ├── pdf_processor.py
│   │   └── ocr_processor.py
│   ├── ui/
│   └── utils/
│       └── logger.py
├── db/
│   └── supabase_schema.sql
├── .env.example
├── requirements.txt
└── README.md
```

## 🛠️ Installation

### 1. Clone/Navigate to Project

```bash
cd C:\Users\hp\UOH_Hackathon
```

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install Tesseract OCR

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install to: `C:\Program Files\Tesseract-OCR\`

### 5. Configure Environment

```bash
# Copy example env file
copy .env.example .env

# Edit .env and add your API keys
```

**Get API Keys:**
- **Gemini**: https://makersuite.google.com/app/apikey
- **Cohere**: https://dashboard.cohere.com/
- **Supabase**: https://supabase.com/ → Create Project → Settings → API

### 6. Set Up Supabase

1. Create project at https://supabase.com/
2. Go to SQL Editor
3. Run: `db/supabase_schema.sql`
4. Copy URL and Key to `.env`

## 🚀 Usage

### Streamlit UI (Recommended)

```bash
python main.py --mode streamlit
```

Access at: `http://localhost:8501`

### Command Line

```bash
# Process all documents in data/documents/
python main.py --mode cli

# Validate system
python main.py --mode validate
```

## 📊 Data Output

### Excel Structure

**Sheet 1: Student Data**
- Student info, CGPA, attendance, etc.

**Sheet 2: Course Details**
- Course-wise grades and credits

### Supabase Tables

- `students` - Main academic data
- `courses` - Course enrollments
- `academic_projects` - Projects
- `internships` - Internships

## 🔧 Configuration

Edit `.env` file:

```bash
# Switch between providers
GEMINI_MODEL=gemini-1.5-flash  # Fast and cheap
COHERE_MODEL=command-r          # Fallback

# Enable/disable Supabase
USE_SUPABASE=true

# Logging level
LOG_LEVEL=INFO
```

## 🧪 Testing

```bash
# Validate all components
python main.py --mode validate

# Check LLM connections
python -c "from src.core.academic_llm_analyzer import AcademicLLMAnalyzer; a = AcademicLLMAnalyzer(); print(a.get_provider_status())"
```

## 📝 API Usage Limits (Free Tier)

**Gemini:**
- 60 requests/minute
- 1500 requests/day
- 1M tokens/month

**Cohere:**
- 100 requests/minute
- 5000 requests/month

**Supabase:**
- 500MB database
- 1GB file storage
- 2GB bandwidth/month

## 🚨 Troubleshooting

### Tesseract not found
```bash
# Add to ocr_processor.py line 20:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Gemini quota exceeded
- System auto-switches to Cohere
- Wait 24h for quota reset
- Or upgrade Gemini plan

### Import errors
```bash
pip install google-generativeai cohere supabase
```

## 📄 License

MIT License

## 🤝 Contributing

Built for University of Hyderabad Academic Evaluation System.

---

**Next Steps:**
1. Add API keys to `.env`
2. Upload test PDFs to `data/documents/`
3. Run: `python main.py --mode streamlit`
