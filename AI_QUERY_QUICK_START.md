# 🚀 AI Query System - Quick Start Guide

## What Was Fixed?

Your AI Query system was returning hardcoded responses instead of analyzing real data. Now it:

✅ **Uses Cohere AI** for intelligent responses (not Gemini - that's for document processing)  
✅ **Loads context** from your processed Excel batch files  
✅ **Allows batch selection** so you can query specific datasets  
✅ **Shows context info** (student count, avg CGPA, departments) with each response  

---

## 🏃 Quick Start (2 Minutes)

### Step 1: Verify Backend is Running
```bash
# Start backend (if not running)
cd C:\Users\hp\UOH_Hackathon
python backend/api.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
✓ API started successfully
```

### Step 2: Verify Frontend is Running
```bash
# In another terminal
cd C:\Users\hp\UOH_Hackathon\frontend
npm run dev
```

You should see:
```
VITE v5.x.x ready in xxx ms
➜  Local:   http://localhost:5173/
```

### Step 3: Open AI Query Page
1. Go to http://localhost:5173
2. Click "AI Query" in navigation
3. You should see:
   - Batch selector with your processed batches
   - Student count for each batch
   - Suggested questions

### Step 4: Test It!

**Try these questions:**
1. Click any suggested question (or type your own)
2. Wait 2-4 seconds
3. See AI response with context info

**Example questions:**
- "What is the average CGPA?"
- "How many students are in Computer Science?"
- "Who are the top 5 performers?"

---

## 🧪 Verify Everything Works

Run this test script:
```bash
python test_ai_query_complete.py
```

It will check:
- ✅ Backend connection
- ✅ Cohere API connection
- ✅ Batch files available
- ✅ AI queries working

---

## 🔍 What's Different Now?

### BEFORE (Hardcoded):
```
User: "What's the average CGPA?"
AI: "This is a placeholder response. The AI query system is still being developed."
```

### AFTER (Real Analysis):
```
User: "What's the average CGPA?"
AI: "Based on the analysis of 6 students in this batch, the average CGPA is 8.45. 
     The Computer Science department has the highest average at 8.8, while Mechanical 
     Engineering averages 8.1. The top performer is Raj Kumar with a CGPA of 9.2."

Context: 6 students analyzed, Avg CGPA: 8.45, 3 departments, AI: Cohere command-a
```

---

## 📊 How It Works

```
1. YOU SELECT A BATCH
   ↓
2. FRONTEND SENDS QUERY TO BACKEND
   POST /api/ai/query
   { query: "What's the average?", batch: "academic_batch_xxx.xlsx" }
   ↓
3. BACKEND LOADS EXCEL FILE
   Reads: data/excel/academic_batch_xxx.xlsx
   ↓
4. PREPARES CONTEXT
   - Total students: 6
   - Average CGPA: 8.45
   - Departments: CS, ME, EE
   - Top performers: [list]
   - Department averages: {...}
   ↓
5. SENDS TO COHERE API
   Context + Your Question → Cohere AI
   ↓
6. COHERE ANALYZES & RESPONDS
   Returns intelligent, data-driven answer
   ↓
7. FRONTEND DISPLAYS
   Shows answer with context info
```

---

## 🎯 Key Features

### 1. Batch Selection
- **See all your processed batches**
- Student count for each
- ⭐ Current batch indicator
- Date processed
- Refresh button

### 2. Smart Context Display
Each AI response shows:
- 📊 Students analyzed
- 📈 Average CGPA
- 🏢 Number of departments
- 🤖 AI model used (Cohere)

### 3. Suggested Questions
Click to auto-send:
- Statistics queries
- Department analysis
- Performance rankings
- Distribution questions
- Comparisons

### 4. Better UI
- Gradient backgrounds
- Icons everywhere
- Loading states with batch info
- Error handling
- Auto-scroll to new messages

---

## ❓ Troubleshooting

### "No batches found"
**Solution:** You need to process documents first
```
1. Go to Homepage
2. Upload PDFs
3. Click "Process Documents"
4. Wait for completion
5. Return to AI Query
```

### "AI response is weird/empty"
**Check:**
```bash
# 1. Is Cohere API key valid?
cat .env | grep COHERE_API_KEY

# 2. Test Cohere directly
python -c "import cohere; client = cohere.Client('YOUR_KEY'); print('OK')"

# 3. Check if batch file has data
# Open: data/excel/[your_batch].xlsx
# Should have rows with student data
```

### "Cannot connect to backend"
```bash
# Check if backend is running
curl http://localhost:8000/health

# Should return:
# {"status": "healthy", ...}

# If not, start backend:
python backend/api.py
```

### "Frontend shows error"
```bash
# Check browser console (F12)
# Look for:
# - Network errors (CORS, 404, 500)
# - JavaScript errors

# Check frontend is running:
npm run dev

# Should show: http://localhost:5173
```

---

## 🎓 Understanding the System

### Two AI Models:

**Gemini (Document Processing):**
- Reads PDFs
- Extracts student data
- Fills Excel files
- Used in: Homepage processing

**Cohere (AI Query):**
- Analyzes Excel data
- Answers questions
- Conversational interface
- Used in: AI Query page

### Data Storage:

```
data/
├── excel/
│   ├── academic_batch_xxx.xlsx    ← Your processed data
│   ├── academic_batch_yyy.xlsx
│   └── batch_metadata.json        ← Tracks all batches
└── documents/                      ← Temporary PDF uploads
```

### API Endpoints:

```
GET  /api/batches/all          → List all batches
POST /api/ai/query             → Ask AI questions
GET  /health                   → Check system status
POST /upload                   → Upload PDFs
POST /process                  → Process documents
```

---

## 💡 Tips for Best Results

### Good Questions:
✅ "What is the average CGPA?"  
✅ "Compare CS and EE departments"  
✅ "Who are the top 10 students?"  
✅ "How many students have CGPA below 7?"  
✅ "What's the distribution of grades?"  

### Questions that Won't Work:
❌ "What will the weather be tomorrow?"  
❌ "Tell me about artificial intelligence"  
❌ "Show me student photos"  
❌ Questions about data not in the batch  

**Why?** The AI only knows about the data in your selected batch.

---

## 🚀 Next Steps

1. **Try Different Batches:**
   - Switch between batches
   - See how answers change
   - Compare different datasets

2. **Ask Complex Questions:**
   - "Which department improved the most?"
   - "Identify students needing support"
   - "What patterns do top performers share?"

3. **Explore Features:**
   - Refresh batches
   - Try all suggested questions
   - Check context info cards
   - Watch loading animations

---

## 📞 Need Help?

### Check Logs:
```bash
# Backend logs
# Terminal where you ran: python backend/api.py

# System logs
# Folder: data/logs/
```

### Test Everything:
```bash
python test_ai_query_complete.py
```

### Still Issues?
1. Restart backend
2. Restart frontend
3. Clear browser cache
4. Check .env file has COHERE_API_KEY
5. Verify batch files exist in data/excel/

---

## ✅ Success Checklist

- [ ] Backend running (port 8000)
- [ ] Frontend running (port 5173)
- [ ] Can see batches in dropdown
- [ ] Batches show student counts
- [ ] Can select different batches
- [ ] Suggested questions work
- [ ] AI responses are contextual (not hardcoded)
- [ ] Context info shows at bottom of responses
- [ ] Can ask follow-up questions
- [ ] Response time is under 5 seconds

---

**Status:** ✅ FULLY WORKING  
**Last Updated:** January 24, 2026  
**Time to Setup:** < 2 minutes  
**Time to First Query:** < 10 seconds  

🎉 **Enjoy your AI-powered academic analytics!**
