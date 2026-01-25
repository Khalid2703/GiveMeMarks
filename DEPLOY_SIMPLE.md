# Deployment Guide - SIMPLE VERSION

## Backend Deployment (Render.com)

1. **Create New Web Service on Render.com**
   - Connect your GitHub repo
   - Root directory: leave empty
   - Build command: `pip install -r requirements.txt`
   - Start command: `cd backend && uvicorn api:app --host 0.0.0.0 --port $PORT`
   - OR use the start command: `cd backend && python api.py`

2. **Environment Variables**
   Add these in Render dashboard:
   ```
   GEMINI_API_KEY=your_key
   COHERE_API_KEY=your_key
   SUPABASE_URL=your_url
   SUPABASE_KEY=your_key
   ```

3. **Get Backend URL**
   - After deployment, copy the URL (e.g., https://your-app.onrender.com)

---

## Frontend Deployment (Vercel)

1. **Update API URL in Frontend**
   
   Edit these 3 files and change `localhost:8000` to your Render URL:
   
   **File 1: `frontend/src/App.jsx`**
   ```javascript
   const API_URL = 'https://your-backend-url.onrender.com'
   ```
   
   **File 2: `frontend/src/components/ResultsPage.jsx`**
   ```javascript
   const API_URL = 'https://your-backend-url.onrender.com'
   ```
   
   **File 3: `frontend/src/components/AIQueryPage.jsx`**
   ```javascript
   const API_URL = 'https://your-backend-url.onrender.com'
   ```

2. **Deploy to Vercel**
   - Import project from GitHub
   - Framework: Vite
   - Root directory: `frontend`
   - Build command: `npm install && npm run build`
   - Output directory: `dist`

3. **Done!**
   - Your app should now be live

---

## Quick Checklist

### Before Deployment:
- [ ] Backend code pushed to GitHub
- [ ] Frontend code pushed to GitHub
- [ ] Environment variables ready

### Backend (Render):
- [ ] Web service created
- [ ] Environment variables added
- [ ] Build successful
- [ ] Backend URL copied

### Frontend (Vercel):
- [ ] Updated API URLs in 3 files
- [ ] Changes committed and pushed
- [ ] Vercel project created
- [ ] Build successful

---

## Common Issues

### CORS Errors
Backend `api.py` should have:
```python
allow_origins=[
    "http://localhost:3000",
    "http://localhost:5173",
    "https://*.vercel.app",
    "*"
]
```

### Frontend Can't Connect
- Check API URLs are correct
- Verify backend is running on Render
- Check browser console for exact error

### Build Fails
**Backend**: Check `requirements.txt` has all dependencies
**Frontend**: Run `npm install` locally first to test

---

## That's It!

Simple deployment in 3 steps:
1. Deploy backend to Render
2. Update frontend API URLs
3. Deploy frontend to Vercel

No complicated configs needed!
