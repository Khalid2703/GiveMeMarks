# 🚨 SECURITY INCIDENT REPORT & FIX

**Date:** January 23, 2026  
**Issue:** Gemini API Key Leaked and Disabled

---

## ⚠️ WHAT HAPPENED

Your Gemini API key was **exposed publicly** and Google disabled it for security.

**Error:**
```
ERROR: 403 Your API key was reported as leaked. 
Please use another API key.
```

**Leaked Key:** `AIzaSyBB1UkfWxfL3v1DwXLGn1zTXFXl0Au2bpc` (NOW DISABLED)

---

## ✅ WHAT I FIXED

### 1. Removed Real Keys from `.env.example`

**Before:**
```bash
GEMINI_API_KEY=AIzaSyBB1UkfWxfL3v1DwXLGn1zTXFXl0Au2bpc  # REAL KEY - LEAKED!
COHERE_API_KEY=dTCydbTQA1grxDigMdfzqec7ty5oPsKU1ecoTh8a  # REAL KEY - EXPOSED!
SUPABASE_URL=https://bckznqgomxzbpnmlewaz.supabase.co    # REAL URL - PUBLIC!
```

**After:**
```bash
GEMINI_API_KEY=your_gemini_api_key_here        # PLACEHOLDER
COHERE_API_KEY=your_cohere_api_key_here        # PLACEHOLDER
SUPABASE_URL=your_supabase_project_url_here    # PLACEHOLDER
```

### 2. Updated `.env` Placeholder

Changed your `.env` to use placeholder too (you need to add your NEW key).

---

## 🔥 URGENT: WHAT YOU MUST DO NOW

### Step 1: Get New Gemini API Key

1. **Go to:** https://makersuite.google.com/app/apikey
2. **Delete old key:** Find `AIzaSyBB1Uk...` and DELETE IT
3. **Create new key:** Click "Create API Key"
4. **Copy the new key**

### Step 2: Update Your `.env` File

```bash
cd C:\Users\hp\UOH_Hackathon

# Open .env file
notepad .env

# Replace this line:
GEMINI_API_KEY=YOUR_NEW_KEY_HERE

# With your actual new key:
GEMINI_API_KEY=AIzaSy___YOUR_NEW_KEY_HERE___
```

### Step 3: Restart Backend

```bash
# Stop backend (Ctrl+C in terminal)
# Then restart:
cd C:\Users\hp\UOH_Hackathon\backend
uvicorn api:app --reload
```

---

## 🔒 PREVENT FUTURE LEAKS

### Rule 1: NEVER Commit Real Keys

```bash
# Check your .gitignore includes:
.env
*.env
.env.local
.env.production

# Verify:
cat .gitignore | grep .env
```

### Rule 2: Only Use Placeholders in `.env.example`

```bash
# .env.example should ALWAYS look like:
GEMINI_API_KEY=your_api_key_here
COHERE_API_KEY=your_api_key_here

# NOT:
GEMINI_API_KEY=AIzaSy...  # NEVER DO THIS!
```

### Rule 3: Check Before Committing

```bash
# Before git push, check:
git diff

# If you see real API keys, DON'T PUSH!
```

### Rule 4: Use Environment Variables in Production

```bash
# In Render/Vercel, set environment variables in dashboard
# NEVER hardcode keys in code
```

---

## 📋 CHECKLIST - DO THIS NOW

- [ ] **Get new Gemini API key** from https://makersuite.google.com/app/apikey
- [ ] **Delete old key** (the leaked one)
- [ ] **Update `.env`** with new key
- [ ] **Restart backend** server
- [ ] **Test system** works with new key
- [ ] **Check `.gitignore`** includes `.env`
- [ ] **Verify `.env.example`** has only placeholders
- [ ] **NEVER commit `.env`** file to Git

---

## 🧪 TEST AFTER FIX

### Test 1: Verify New Key Works

```bash
cd C:\Users\hp\UOH_Hackathon

python -c "from config.settings import GEMINI_API_KEY; print('Key length:', len(GEMINI_API_KEY))"

# Should show: Key length: 39 (or similar)
# Should NOT show: YOUR_NEW_KEY_HERE
```

### Test 2: Test LLM Connection

```bash
python -c "from src.core.academic_llm_analyzer import AcademicLLMAnalyzer; a = AcademicLLMAnalyzer(); print(a.validate_api_connection())"

# Should show: {'gemini': True, 'cohere': True}
```

### Test 3: Process Test Document

```bash
# Restart backend
cd backend
uvicorn api:app --reload

# Upload test PDF in frontend
# Should process successfully
```

---

## 🔍 HOW DID IT LEAK?

**Most Likely Causes:**

1. **GitHub:** You pushed `.env.example` with real keys
2. **Public Repository:** Your repo is public with real keys
3. **Shared File:** You shared the file containing keys
4. **Screenshot:** You shared screenshot with keys visible

**Google scans GitHub for leaked keys automatically!**

---

## 💡 GOOD SECURITY PRACTICES

### ✅ DO:
- Use `.env` for local development (git-ignored)
- Use environment variables in production
- Use placeholders in `.env.example`
- Rotate keys regularly
- Keep `.env` in `.gitignore`

### ❌ DON'T:
- Commit `.env` to Git
- Put real keys in `.env.example`
- Share `.env` files
- Screenshot code with keys visible
- Hardcode keys in source code

---

## 📊 CURRENT STATUS

| Item | Status | Action Needed |
|------|--------|---------------|
| Leaked Key | ❌ Disabled by Google | Get new key |
| .env.example | ✅ Fixed (placeholders) | None |
| .env | ⚠️ Has placeholder | Add new key |
| Cohere Key | ⚠️ May be exposed | Consider rotating |
| Supabase | ⚠️ May be exposed | Consider rotating |
| .gitignore | ⚠️ Check it | Verify .env is listed |

---

## 🚀 AFTER YOU GET NEW KEY

**Your system will work perfectly!**

The good news:
- ✅ Your system uses **dual LLM** (Gemini + Cohere)
- ✅ If Gemini fails, it auto-switches to Cohere
- ✅ Just get new Gemini key and you're back online!

---

## 📞 NEED HELP?

**Get new key:** https://makersuite.google.com/app/apikey

**After you get it:**
1. Update `.env` file
2. Restart backend
3. Test upload → Everything will work!

---

**CRITICAL: Get new key NOW before continuing!** 🔑
