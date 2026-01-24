# 🚀 QUICK START GUIDE - UOH Academic System

## ⚡ TL;DR (2 Minutes to Running)

```bash
# Terminal 1: Backend
cd C:\Users\hp\UOH_Hackathon\backend
python api.py

# Terminal 2: Frontend  
cd C:\Users\hp\UOH_Hackathon\frontend
npm run dev

# Browser
# Open: http://localhost:3000
```

**That's it! Your app is running!** 🎉

---

## 🔍 WHAT WAS FIXED?

Your screenshots showed 3 pages not working:
1. ❌ Dashboard: "Chart visualization coming soon"
2. ❌ Results: "Results Search Coming Soon"  
3. ❌ AI Query: Not responding to messages

### ✅ All Fixed!
- Dashboard now shows **REAL DATA** (6 students, CGPA 8.45)
- Results page has **WORKING SEARCH**
- AI Query **RESPONDS TO MESSAGES**

---

## 📊 TEST YOUR FIXES

### 1. Dashboard (30 seconds)
```
1. Open http://localhost:3000
2. Click "Dashboard" in left sidebar
3. ✅ Should see: 6 students, avg CGPA 8.45
4. ✅ Should see: CGPA distribution bars
5. ✅ Should see: Department distribution bars
6. ✅ Should see: Top 10 performers table
```

### 2. Results Search (30 seconds)
```
1. Click "Results" in sidebar
2. Type "Rahul" in search box
3. Click "Search" button
4. ✅ Should see: Student card with name, roll, CGPA
```

### 3. AI Query (30 seconds)
```
1. Click "AI Query" in sidebar
2. Type "What is the average CGPA?"
3. Press Enter or click "Send"
4. ✅ Should see: Your message (blue bubble)
5. ✅ Should see: AI response (gray bubble) with data
```

---

## 🐛 Troubleshooting

### Backend won't start?
```bash
cd C:\Users\hp\UOH_Hackathon
python verify_system.py
```
This checks if all files are present.

### Frontend shows errors?
```bash
# Check if backend is running
# Look for: "Uvicorn running on http://0.0.0.0:8000"

# Test backend separately
python test_api.py
```

### No data showing?
```bash
# Check if Excel files exist
dir C:\Users\hp\UOH_Hackathon\data\excel\

# Should see: batch_metadata.json and .xlsx files
```

---

## 📚 Documentation

Full details in:
- `COMPLETE_FIX_SUMMARY.md` - Everything that was fixed
- `ALL_FEATURES_WORKING.md` - How to test each feature
- `CONTEXT_FOR_NEXT_SESSION.md` - Project overview

---

## 🎯 Next Steps

### Want Better Charts?
```bash
cd frontend
npm install recharts
# Then replace progress bars with real charts
```

### Want Full AI Integration?
Edit `backend/api.py` line ~640 and integrate Gemini LLM

### Want Advanced Filters?
Add dropdowns to Results page for department, CGPA range, etc.

---

## ✅ Success Checklist

- [ ] Backend starts without errors
- [ ] Frontend starts without errors  
- [ ] Dashboard shows 6 students
- [ ] Dashboard shows CGPA 8.45
- [ ] Search works for "Rahul"
- [ ] AI Query responds to messages

**All checked?** You're ready to demo! 🎉

---

*Questions? Check the other .md files or run `python verify_system.py`*
