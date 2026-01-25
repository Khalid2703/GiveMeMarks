# 🚀 DEPLOYMENT GUIDE - WITH DATA FIX

## The Problem You Had:
- Deployed app showed "No batches available"
- Dashboard, Results, AI Query all empty
- This happened because data files don't get pushed to GitHub

## The Solution:
We now automatically create demo data on deployment!

---

## STEP 1: Prepare for Deployment

### 1.1 Test Demo Data Locally

```bash
cd C:\Users\hp\UOH_Hackathon
python create_demo_data.py
```

This creates 6 sample students. You should see:
```
✅ Created sample batch: demo_batch_YYYYMMDD_HHMMSS.xlsx
✅ Created batch metadata: batch_metadata.json
```

### 1.2 Test Locally

```bash
# Terminal 1: Start backend
cd backend
python api.py

# Terminal 2: Start frontend  
cd frontend
npm run dev
```

Open http://localhost:5173 and verify:
- ✅ Homepage shows system status
- ✅ Dashboard shows 6 students
- ✅ Results tab shows students
- ✅ AI Query works

---

## STEP 2: Deploy Backend (Render.com)

### 2.1 Push to GitHub

```bash
git add .
git commit -m "Add demo data creation for deployment"
git push origin main
```

### 2.2 Deploy on Render.com

1. Go to https://dashboard.render.com/
2. Click "New +" → "Web Service"
3. Connect your GitHub: `Khalid2703/GiveMeMarks`
4. **Settings:**
   - **Name:** `uoh-academic-backend` (or your choice)
   - **Region:** Oregon (Free tier)
   - **Branch:** `main`
   - **Root Directory:** (leave empty)
   - **Runtime:** Python 3
   - **Build Command:** 
     ```
     pip install -r requirements.txt && python create_demo_data.py
     ```
   - **Start Command:**
     ```
     cd backend && uvicorn api:app --host 0.0.0.0 --port $PORT
     ```

5. **Environment Variables** (Add these):
   ```
   GEMINI_API_KEY=your_gemini_key
   GEMINI_MODEL=gemini-2.0-flash-exp
   COHERE_API_KEY=your_cohere_key
   SUPABASE_URL=your_supabase_url (optional)
   SUPABASE_KEY=your_supabase_key (optional)
   PYTHON_VERSION=3.9.0
   ```
   
   **Note:** We're using `gemini-2.0-flash-exp` which is the latest stable model.

6. Click "Create Web Service"

7. **Wait for deployment** (~5-10 minutes)

8. **Copy your backend URL:** 
   - Example: `https://uoh-academic-backend.onrender.com`

### 2.3 Test Backend

Visit: `https://your-backend-url.onrender.com/status`

Should return:
```json
{
  "status": "operational",
  "llm_provider": "gemini",
  "llm_available": true
}
```

Test data endpoint:
`https://your-backend-url.onrender.com/api/search/students?query=`

Should return 6 demo students!

---

## STEP 3: Update Frontend for Production

### 3.1 Update API URLs

Replace `YOUR_BACKEND_URL` with your actual Render URL in these 3 files:

**File 1: `frontend/src/App.jsx`**
```javascript
// Change from:
const API_URL = 'http://localhost:8000'

// To:
const API_URL = 'https://your-backend-url.onrender.com'
```

**File 2: `frontend/src/components/ResultsPage.jsx`**
```javascript
// Change from:
const API_URL = 'http://localhost:8000'

// To:
const API_URL = 'https://your-backend-url.onrender.com'
```

**File 3: `frontend/src/components/AIQueryPage.jsx`**
```javascript
// Change from:
const API_URL = 'http://localhost:8000'

// To:
const API_URL = 'https://your-backend-url.onrender.com'
```

### 3.2 Commit Changes

```bash
git add frontend/src/App.jsx frontend/src/components/ResultsPage.jsx frontend/src/components/AIQueryPage.jsx
git commit -m "Update API URLs for production deployment"
git push origin main
```

---

## STEP 4: Deploy Frontend (Vercel)

### 4.1 Deploy on Vercel

1. Go to https://vercel.com/
2. Click "Add New" → "Project"
3. Import your GitHub repo: `Khalid2703/GiveMeMarks`
4. **Settings:**
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Output Directory:** `dist`
   - **Install Command:** `npm install`

5. Click "Deploy"

6. **Wait for deployment** (~2-3 minutes)

7. **Get your frontend URL:**
   - Example: `https://give-me-marks.vercel.app`

---

## STEP 5: Update Backend CORS

### 5.1 Add Vercel Domain to CORS

Edit `backend/api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://give-me-marks.vercel.app",  # Add your Vercel URL here
        "https://*.vercel.app",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
```

### 5.2 Push Update

```bash
git add backend/api.py
git commit -m "Add Vercel domain to CORS"
git push origin main
```

Render will auto-deploy the update (~2 minutes).

---

## STEP 6: Test Production App

### 6.1 Open Your App

Visit: `https://your-app.vercel.app`

### 6.2 Verify All Features

✅ **Homepage:**
- Shows "6 students" in metrics
- System status shows green

✅ **Dashboard:**
- Shows 6 students
- Average CGPA: ~8.7
- Charts with data
- Top performers table

✅ **Results:**
- Search shows 6 students
- Filters work
- Student cards display

✅ **AI Query:**
- Can ask "What is the average CGPA?"
- Returns answer with data
- Batch selector shows demo batch

---

## Common Issues & Fixes

### Issue 1: "No batches available" on deployed app

**Cause:** Demo data not created during build

**Fix:**
1. Check Render build logs - should see "✅ Created sample batch"
2. If not, manually trigger redeploy on Render
3. Ensure `create_demo_data.py` is in root directory

### Issue 2: CORS errors in browser console

**Cause:** Vercel domain not in CORS whitelist

**Fix:**
1. Add your Vercel URL to `backend/api.py` CORS config
2. Push to GitHub
3. Wait for Render auto-deploy

### Issue 3: Frontend shows old localhost URL

**Cause:** Forgot to update API_URL in components

**Fix:**
1. Update all 3 files with production URL
2. Commit and push
3. Vercel will auto-deploy

### Issue 4: Backend shows 500 errors

**Cause:** Missing environment variables

**Fix:**
1. Go to Render dashboard → Your service → Environment
2. Add all required API keys
3. Manually redeploy

---

## Deployment Checklist

### Before Deployment:
- [ ] Test demo data locally: `python create_demo_data.py`
- [ ] Verify local app works with demo data
- [ ] All changes committed and pushed

### Backend (Render):
- [ ] Service created and deployed
- [ ] Environment variables added
- [ ] Build command includes demo data creation
- [ ] `/status` endpoint returns 200
- [ ] `/api/search/students` returns demo data

### Frontend (Vercel):
- [ ] Project imported and deployed
- [ ] Root directory set to `frontend`
- [ ] Build successful
- [ ] API URLs updated in 3 files

### Final Verification:
- [ ] Production app opens
- [ ] Homepage shows 6 students
- [ ] Dashboard displays charts
- [ ] Results search works
- [ ] AI Query responds
- [ ] No CORS errors in console

---

## Environment Variables Needed

### Render.com (Backend):
```
GEMINI_API_KEY=your_key_here
COHERE_API_KEY=your_key_here
SUPABASE_URL=your_url_here (optional)
SUPABASE_KEY=your_key_here (optional)
PYTHON_VERSION=3.9.0
```

### Vercel (Frontend):
No environment variables needed if you hardcode the API URL.

Alternatively, use environment variable:
```
VITE_API_URL=https://your-backend-url.onrender.com
```

Then in code:
```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
```

---

## URLs After Deployment

**Backend (Render):**
- URL: `https://your-backend-url.onrender.com`
- Status: `https://your-backend-url.onrender.com/status`
- Docs: `https://your-backend-url.onrender.com/docs`

**Frontend (Vercel):**
- URL: `https://your-app.vercel.app`
- Preview: Updates on every push

---

## Quick Reference

### Test Demo Data:
```bash
python create_demo_data.py
```

### Start Local Development:
```bash
# Backend
cd backend && python api.py

# Frontend
cd frontend && npm run dev
```

### Deploy Commands:
```bash
git add .
git commit -m "Your message"
git push origin main
```

---

## Need to Add Real Data Later?

After deployment, you can:

1. **Upload documents** through the frontend
2. **Process them** to create real batches
3. Demo data will be supplemented with real data
4. Both will show in Results/Dashboard

---

That's it! Your app will now work perfectly in production with demo data showing immediately! 🎉
