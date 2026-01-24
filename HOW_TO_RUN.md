# 🚀 HOW TO RUN YOUR UOH SYSTEM

**You have 2 architectures available!**

---

## 📊 ARCHITECTURE COMPARISON

### Option 1: Separate Backend + Frontend (Full-Stack Mode)
```
Backend (FastAPI) → Port 8000
Frontend (React) → Port 5173
User → React UI → API Calls → Backend → Processing
```

### Option 2: Single File (CLI/Streamlit Mode)
```
main.py → Streamlit UI → Direct Processing
User → Streamlit → No API → Direct Functions
```

---

## 🎯 WHICH ONE TO USE?

### **Use Option 1 (Separate) IF:**
- ✅ You want the React frontend you already built
- ✅ You're deploying to production (Render + Vercel)
- ✅ You want API endpoints for future integration
- ✅ You built the React app in `frontend/`

### **Use Option 2 (Single File) IF:**
- ✅ Quick local testing
- ✅ Simple demo/presentation
- ✅ Don't need fancy React UI
- ✅ Streamlit is enough for you

---

## 🚀 OPTION 1: SEPARATE BACKEND + FRONTEND (Recommended for You!)

You already have both built! Here's how to run them:

### Step 1: Start Backend (FastAPI)

**Terminal 1:**
```bash
cd C:\Users\hp\UOH_Hackathon

# Activate virtual environment
venv\Scripts\activate

# Start FastAPI backend
cd backend
uvicorn api:app --reload --port 8000

# Should show:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete.
```

**Test Backend:**
```
Open browser: http://localhost:8000/status
Should return: {"status": "operational", ...}
```

---

### Step 2: Start Frontend (React)

**Terminal 2 (Keep Terminal 1 running!):**
```bash
cd C:\Users\hp\UOH_Hackathon\frontend

# Install dependencies (first time only)
npm install

# Start React dev server
npm run dev

# Should show:
# VITE v5.x.x ready in xxx ms
# ➜ Local: http://localhost:5173/
```

**Access Application:**
```
Open browser: http://localhost:5173
```

---

### How They Work Together:

```
1. User opens http://localhost:5173 (React UI)
2. User uploads PDFs
3. React sends POST to http://localhost:8000/upload
4. Backend processes PDFs
5. React displays results
```

**Both terminals must stay open!**

---

## 🎯 OPTION 2: SINGLE FILE (main.py)

### Mode A: CLI Batch Processing

```bash
cd C:\Users\hp\UOH_Hackathon
venv\Scripts\activate

# Process all PDFs in data/documents/
python main.py --mode cli

# Output:
# ✅ Processes all PDFs
# ✅ Creates Excel batch file
# ✅ Shows progress
```

**Use this for:** Quick batch processing without UI

---

### Mode B: Streamlit UI (NOT BUILT YET!)

```bash
python main.py --mode streamlit
```

**Currently shows:**
```
❌ Streamlit app not found
   Run this first: (Streamlit UI not yet built)
```

**This won't work because** you built React frontend, not Streamlit!

---

### Mode C: Validation

```bash
python main.py --mode validate

# Output:
# 🔍 SYSTEM VALIDATION
# ✅ Component statuses
# ✅ LLM connections
# ✅ Directory checks
```

**Use this for:** Testing system health

---

## ✅ RECOMMENDED SETUP FOR YOU

Based on your project structure, you should use **Option 1 (Separate)**:

### Quick Start Commands:

**Terminal 1 - Backend:**
```bash
cd C:\Users\hp\UOH_Hackathon
venv\Scripts\activate
cd backend
uvicorn api:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd C:\Users\hp\UOH_Hackathon\frontend
npm run dev
```

**Then open:** http://localhost:5173

---

## 🧪 TEST YOUR SETUP

### Test 1: Backend Only
```bash
# Terminal 1
cd C:\Users\hp\UOH_Hackathon\backend
uvicorn api:app --reload

# Open browser
http://localhost:8000/status
http://localhost:8000/docs  # FastAPI auto-docs
```

### Test 2: Frontend Only (will fail without backend)
```bash
# Terminal 2
cd C:\Users\hp\UOH_Hackathon\frontend
npm run dev

# Open browser
http://localhost:5173
# Will show UI but API calls will fail without backend
```

### Test 3: Both Together (Full System)
```bash
# Start both terminals
# Then test upload workflow
```

---

## 📁 YOUR PROJECT STRUCTURE

```
C:\Users\hp\UOH_Hackathon\
│
├── backend/
│   └── api.py              ← FastAPI server (Port 8000)
│
├── frontend/
│   ├── src/App.jsx         ← React UI (Port 5173)
│   └── package.json
│
├── main.py                 ← CLI/Streamlit launcher
│
└── src/core/               ← Shared processing logic
    ├── academic_llm_analyzer.py
    ├── dashboard_analytics.py
    └── ...
```

**Backend and Frontend are SEPARATE but use the SAME core logic!**

---

## 🎯 QUICK COMPARISON

| Feature | Separate (Backend+Frontend) | Single (main.py) |
|---------|---------------------------|------------------|
| UI | React (Beautiful!) | Streamlit (Not built) or CLI |
| Setup | 2 terminals | 1 terminal |
| API | Yes (port 8000) | No API |
| Deployment | Production-ready | Local only |
| Your Setup | ✅ Built and ready | ⚠️ CLI works, Streamlit missing |

---

## ✅ FINAL RECOMMENDATION

**FOR YOU: Use Separate Backend + Frontend**

### Why?
1. ✅ You already built both!
2. ✅ React UI is more professional than Streamlit
3. ✅ Ready for production deployment
4. ✅ Judges will be impressed by full-stack

### How?
```bash
# Terminal 1
cd C:\Users\hp\UOH_Hackathon\backend
uvicorn api:app --reload

# Terminal 2  
cd C:\Users\hp\UOH_Hackathon\frontend
npm run dev

# Browser
http://localhost:5173
```

---

## 🚨 COMMON ISSUES

**Issue 1: "Module not found" in backend**
```bash
# Make sure you're in backend directory and venv is activated
cd C:\Users\hp\UOH_Hackathon\backend
..\venv\Scripts\activate
uvicorn api:app --reload
```

**Issue 2: Frontend can't connect to backend**
```bash
# Check backend is running on port 8000
# Check frontend/src/App.jsx has correct API_URL
# Should be: http://localhost:8000
```

**Issue 3: "npm: command not found"**
```bash
# Install Node.js first
# Download from: https://nodejs.org/
```

---

## 📝 SUMMARY

**Answer to your question:**

❌ **NO** - `main.py` does NOT handle everything  
✅ **YES** - You need to run backend AND frontend separately

**Why?** You built a full-stack app with:
- Backend: FastAPI (backend/api.py)
- Frontend: React (frontend/src/App.jsx)

**They communicate via HTTP API calls!**

---

**Next Step:** Start both terminals and test the full system! 🚀

Let me know if you need help starting either component!
