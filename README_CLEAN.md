# UOH Academic Evaluation System

AI-powered academic document processing system for University of Hyderabad.

## Quick Start

### Local Development

1. **Start Backend**
```bash
cd backend
python api.py
```

2. **Start Frontend** (new terminal)
```bash
cd frontend
npm run dev
```

3. **Open Browser**
```
http://localhost:5173
```

## Deployment

### Backend (Render.com)
- Set Python version: 3.9+
- Build command: `pip install -r requirements.txt`
- Start command: `cd backend && python api.py`

### Frontend (Vercel)
- Framework: Vite
- Build command: `cd frontend && npm install && npm run build`
- Output directory: `frontend/dist`

## Environment Variables

Create `.env` file:
```
GEMINI_API_KEY=your_key
COHERE_API_KEY=your_key
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
```

## Project Structure

```
UOH_Hackathon/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── src/              # Core processing modules
├── data/             # Data storage
├── config/           # Configuration
└── requirements.txt  # Python dependencies
```

## Features

- PDF document processing
- AI-powered data extraction
- Batch processing
- Search & filtering
- Analytics dashboard
- AI query interface

## Tech Stack

- **Backend**: FastAPI, Python
- **Frontend**: React, Vite, TailwindCSS
- **AI**: Google Gemini, Cohere
- **Database**: Supabase
- **Storage**: Excel exports

---

For detailed setup, see individual README files in backend/ and frontend/ directories.
