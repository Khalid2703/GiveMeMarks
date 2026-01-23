# 🚀 DEPLOYMENT INSTRUCTIONS

## ✅ **SYSTEM COMPLETE - READY TO DEPLOY!**

Your UOH Academic Evaluation System is now **100% complete** with:
- ✅ FastAPI Backend
- ✅ React Frontend (Mobile & Laptop Responsive)
- ✅ All configuration files
- ✅ Deployment ready for Vercel + Render

---

## 📋 **PRE-DEPLOYMENT CHECKLIST**

### Local Testing:
- [ ] Backend runs: `cd backend && python api.py`
- [ ] Frontend runs: `cd frontend && npm run dev`
- [ ] Can upload PDFs
- [ ] Can process documents
- [ ] Can download Excel
- [ ] Mobile responsive (test in Chrome DevTools)

---

## 🚀 **DEPLOYMENT STEPS**

### **STEP 1: Deploy Backend to Render.com** (10 minutes)

#### 1.1 Push to GitHub
```bash
cd C:\Users\hp\UOH_Hackathon
git init
git add .
git commit -m "Initial commit - UOH Academic Evaluation System"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/uoh-academic-eval.git
git push -u origin main
```

#### 1.2 Create Render Web Service
1. Go to https://render.com/
2. Sign in with GitHub
3. Click **"New +"** → **"Web Service"**
4. Connect your GitHub repository
5. Configure:
   ```
   Name: uoh-academic-backend
   Environment: Python 3
   Region: Choose closest (e.g., Singapore)
   Branch: main
   Root Directory: (leave empty)
   Build Command: pip install -r requirements.txt
   Start Command: cd backend && uvicorn api:app --host 0.0.0.0 --port $PORT
   ```

#### 1.3 Add Environment Variables
In Render dashboard, go to **Environment** tab and add:
```
GEMINI_API_KEY=your_gemini_key_here
COHERE_API_KEY=your_cohere_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
USE_SUPABASE=true
ACADEMIC_YEAR_DEFAULT=2024-2025
LOG_LEVEL=INFO
```

#### 1.4 Deploy
- Click **"Create Web Service"**
- Wait 5-10 minutes for deployment
- Once deployed, copy your backend URL (e.g., `https://uoh-academic-backend.onrender.com`)

#### 1.5 Test Backend
Visit: `https://your-backend-url.onrender.com/docs`
- You should see the API documentation
- Test the `/health` endpoint

---

### **STEP 2: Deploy Frontend to Vercel** (5 minutes)

#### 2.1 Update API URL
Edit `frontend/src/App.jsx` line 25:
```javascript
const API_URL = import.meta.env.PROD 
  ? 'https://YOUR-ACTUAL-BACKEND-URL.onrender.com'  // ← Update this!
  : 'http://localhost:8000'
```

#### 2.2 Install Dependencies & Test Build
```bash
cd frontend
npm install
npm run build
```

If build succeeds, you'll see a `dist/` folder created.

#### 2.3 Deploy to Vercel
```bash
# Install Vercel CLI globally
npm i -g vercel

# Deploy
vercel

# Follow the prompts:
# - Set up and deploy? Yes
# - Which scope? (select your account)
# - Link to existing project? No
# - Project name: uoh-academic-evaluation
# - In which directory is your code? ./
# - Want to modify settings? No
```

#### 2.4 Get Your URL
After deployment, Vercel will give you:
```
https://uoh-academic-evaluation.vercel.app
```

---

### **STEP 3: Update CORS on Backend**

After deploying frontend, update `backend/api.py` line 32:

```python
allow_origins=[
    "http://localhost:3000",
    "http://localhost:5173",
    "https://uoh-academic-evaluation.vercel.app",  # ← Add your actual Vercel URL
    "https://*.vercel.app",
],
```

Then redeploy backend (Render auto-deploys on git push):
```bash
git add backend/api.py
git commit -m "Update CORS for Vercel"
git push
```

---

## 📱 **TESTING ON MOBILE & LAPTOP**

### Desktop Testing:
1. Open: `https://your-app.vercel.app`
2. Upload test PDFs
3. Click "Process Documents"
4. Download Excel results

### Mobile Testing:
1. Open on phone: `https://your-app.vercel.app`
2. Test upload (use phone camera to scan document)
3. Check responsive layout
4. Test all buttons (should be touch-friendly)

### Responsive Design Testing (Desktop):
1. Open app in Chrome
2. Press `F12` (DevTools)
3. Click device toolbar icon (Ctrl+Shift+M)
4. Test on:
   - iPhone 12 (390x844)
   - iPad (768x1024)
   - Android phones

---

## 🔧 **LOCAL DEVELOPMENT**

### Backend:
```bash
cd C:\Users\hp\UOH_Hackathon

# Activate virtual environment
venv\Scripts\activate

# Run backend
cd backend
python api.py

# API available at: http://localhost:8000
# API docs at: http://localhost:8000/docs
```

### Frontend:
```bash
# Open new terminal
cd C:\Users\hp\UOH_Hackathon\frontend

# Install dependencies (first time only)
npm install

# Run dev server
npm run dev

# App available at: http://localhost:3000
```

---

## 📊 **API ENDPOINTS**

### Production: `https://your-backend.onrender.com`
### Local: `http://localhost:8000`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Health check |
| GET | /health | Detailed system health |
| GET | /status | System status (LLM, DB) |
| GET | /documents/count | Count queued documents |
| POST | /upload | Upload PDF files |
| POST | /process | Process batch |
| DELETE | /documents | Clear all uploads |
| GET | /batches | List all batches |
| GET | /batches/{id}/download | Download Excel file |

---

## 🎯 **FEATURES**

### ✅ Mobile Responsive
- Adaptive layouts (mobile/tablet/laptop/desktop)
- Touch-friendly buttons
- Swipe-friendly tables
- Mobile-optimized file upload

### ✅ Real-time Features
- Live document count
- Processing status
- System health indicators
- Error notifications

### ✅ Batch Management
- Upload multiple PDFs
- Process in batches
- View previous batches
- Download Excel reports

### ✅ Student Data
- 23 fields extracted per student
- Course-wise data
- Mobile-friendly card view (small screens)
- Table view (large screens)

---

## 🚨 **TROUBLESHOOTING**

### Issue: Frontend can't connect to backend
**Solution:**
1. Check CORS is updated with your Vercel URL
2. Verify API_URL in App.jsx is correct
3. Check backend is running (visit /health endpoint)

### Issue: Build fails on Vercel
**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Issue: Backend fails on Render
**Solution:**
1. Check Render logs (Dashboard → Your Service → Logs)
2. Verify all environment variables are set
3. Ensure `requirements.txt` includes all dependencies

### Issue: Mobile layout broken
**Solution:**
- Clear browser cache
- Check viewport meta tag in index.html
- Test in incognito mode

---

## 📚 **TECH STACK**

### Frontend:
- React 18
- Vite (build tool)
- Tailwind CSS (styling)
- Axios (API calls)
- Lucide React (icons)

### Backend:
- FastAPI (Python)
- Uvicorn (ASGI server)
- Academic LLM Analyzer (Gemini + Cohere)
- Excel Handler
- Supabase Client

### Deployment:
- Frontend: Vercel (CDN, auto-scaling)
- Backend: Render (container, auto-scaling)
- Database: Supabase (PostgreSQL)

---

## ✅ **FINAL CHECKLIST**

### Before Going Live:
- [ ] Backend deployed to Render
- [ ] Frontend deployed to Vercel
- [ ] Environment variables set on Render
- [ ] CORS updated with Vercel URL
- [ ] API URL updated in App.jsx
- [ ] Tested upload on mobile
- [ ] Tested processing
- [ ] Tested download
- [ ] Tested on iPhone/Android
- [ ] Tested on iPad/tablet
- [ ] Tested on laptop
- [ ] All API endpoints working

### Post-Deployment:
- [ ] Monitor Render logs for errors
- [ ] Check Vercel analytics
- [ ] Test with real academic documents
- [ ] Verify Supabase data is saving
- [ ] Share URL with team

---

## 🎓 **YOUR DEPLOYMENT URLs**

After deployment, you'll have:

```
Frontend: https://uoh-academic-evaluation.vercel.app
Backend: https://uoh-academic-backend.onrender.com
API Docs: https://uoh-academic-backend.onrender.com/docs
```

---

## 🏆 **SUCCESS!**

Your system is now:
- ✅ Deployed to production
- ✅ Accessible on mobile & laptop
- ✅ Scalable and reliable
- ✅ Ready for the hackathon!

**Need help?** Check:
- Render logs: Dashboard → Service → Logs
- Vercel logs: Dashboard → Deployments → View logs
- API docs: `/docs` endpoint

**Good luck with your hackathon! 🚀**
