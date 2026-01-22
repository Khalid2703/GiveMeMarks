"""
FastAPI Backend for UOH Academic Evaluation System
Deployment-ready REST API for Render.com

COMPONENT STATUS: ✅ COMPLETE
LAST UPDATED: 2025-01-21
DEPLOYMENT: Render.com ready
"""
import os
import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import uuid
import shutil

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from src.core.academic_evaluator import AcademicEvaluator
from src.utils.logger import get_logger
from config.settings import DOCUMENT_DIR, EXCEL_DIR

# Initialize FastAPI app
app = FastAPI(
    title="UOH Academic Evaluation API",
    description="AI-powered academic document processing for University of Hyderabad",
    version="1.0.0"
)

# CORS configuration for Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://*.vercel.app",
        "*"  # Allow all origins in production (update with your Vercel domain)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize logger
logger = get_logger("api")

# Global evaluator instance
evaluator = None

# Request/Response Models
class ProcessingStatus(BaseModel):
    status: str
    message: str
    batch_id: Optional[str] = None
    total_files: Optional[int] = None
    processed: Optional[int] = None
    progress: Optional[float] = None

class StudentData(BaseModel):
    student_name: str
    roll_number: str
    email: str
    department: str
    cgpa: str

class BatchResult(BaseModel):
    batch_id: str
    batch_filename: str
    total_documents: int
    successful: int
    failed: int
    success_rate: float
    students: List[StudentData]

class SystemStatus(BaseModel):
    status: str
    llm_available: bool
    llm_provider: str
    supabase_available: bool
    documents_in_queue: int


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize evaluator on startup."""
    global evaluator
    try:
        evaluator = AcademicEvaluator()
        logger.info("✓ API started successfully")
    except Exception as e:
        logger.error(f"Failed to initialize evaluator: {e}")
        raise


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "message": "UOH Academic Evaluation API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    try:
        validation = evaluator.validate_system()
        return {
            "status": "healthy" if validation['overall_status'] == 'OK' else "degraded",
            "components": validation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status", response_model=SystemStatus)
async def get_status():
    """Get system status."""
    try:
        info = evaluator.get_system_info()
        
        # Count documents in queue
        doc_count = len(list(DOCUMENT_DIR.glob("*.pdf"))) if DOCUMENT_DIR.exists() else 0
        
        return SystemStatus(
            status="operational",
            llm_available=info['llm_available'],
            llm_provider=info['llm_status']['current_provider'] if info['llm_available'] else "none",
            supabase_available=info['supabase_available'],
            documents_in_queue=doc_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload PDF documents for processing.
    
    Args:
        files: List of PDF files
        
    Returns:
        Upload confirmation with file details
    """
    try:
        # Ensure upload directory exists
        DOCUMENT_DIR.mkdir(exist_ok=True)
        
        uploaded_files = []
        for file in files:
            # Validate file type
            if not file.filename.endswith('.pdf'):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type: {file.filename}. Only PDF files allowed."
                )
            
            # Generate unique filename to avoid conflicts
            unique_filename = f"{uuid.uuid4().hex[:8]}_{file.filename}"
            file_path = DOCUMENT_DIR / unique_filename
            
            # Save file
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            uploaded_files.append({
                "original_name": file.filename,
                "saved_name": unique_filename,
                "size": len(content),
                "path": str(file_path)
            })
            
            logger.info(f"Uploaded file: {unique_filename}")
        
        return {
            "status": "success",
            "message": f"Uploaded {len(uploaded_files)} files",
            "files": uploaded_files
        }
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process")
async def process_documents(
    background_tasks: BackgroundTasks,
    batch_name: Optional[str] = None
):
    """Process all uploaded documents in batch.
    
    Args:
        background_tasks: FastAPI background tasks
        batch_name: Optional custom batch name
        
    Returns:
        Processing status and batch ID
    """
    try:
        # Get all PDFs in upload directory
        pdf_files = list(DOCUMENT_DIR.glob("*.pdf"))
        
        if not pdf_files:
            raise HTTPException(
                status_code=400,
                detail="No PDF files found. Please upload documents first."
            )
        
        logger.info(f"Starting batch processing: {len(pdf_files)} files")
        
        # Process batch
        results, batch_filename = evaluator.process_batch_documents(
            pdf_files,
            batch_name=batch_name
        )
        
        # Parse results
        successful = sum(1 for r in results if not r.get('_metadata', {}).get('error'))
        failed = len(results) - successful
        
        # Extract student data
        students = []
        for result in results:
            if not result.get('_metadata', {}).get('error'):
                students.append(StudentData(
                    student_name=result.get('Student Name', 'N/A'),
                    roll_number=result.get('Roll Number', 'N/A'),
                    email=result.get('Email', 'N/A'),
                    department=result.get('Department', 'N/A'),
                    cgpa=result.get('CGPA', 'N/A')
                ))
        
        # Clean up processed files
        for pdf_file in pdf_files:
            try:
                pdf_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete {pdf_file}: {e}")
        
        batch_result = BatchResult(
            batch_id=batch_filename.replace('.xlsx', ''),
            batch_filename=batch_filename,
            total_documents=len(results),
            successful=successful,
            failed=failed,
            success_rate=successful / len(results) * 100,
            students=students
        )
        
        logger.info(f"Batch completed: {successful}/{len(results)} successful")
        
        return {
            "status": "completed",
            "message": "Batch processing completed",
            "result": batch_result
        }
        
    except Exception as e:
        logger.error(f"Processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/batches")
async def list_batches():
    """List all available batch files."""
    try:
        batches = evaluator.excel_handler.get_available_batches()
        return {
            "status": "success",
            "count": len(batches),
            "batches": batches
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/batches/{batch_id}/download")
async def download_batch(batch_id: str):
    """Download a batch Excel file.
    
    Args:
        batch_id: Batch filename (without .xlsx)
        
    Returns:
        Excel file
    """
    try:
        batch_filename = f"{batch_id}.xlsx"
        batch_path = EXCEL_DIR / batch_filename
        
        if not batch_path.exists():
            raise HTTPException(status_code=404, detail="Batch file not found")
        
        return FileResponse(
            path=batch_path,
            filename=batch_filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        logger.error(f"Download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents")
async def clear_documents():
    """Clear all uploaded documents."""
    try:
        deleted_count = 0
        for pdf_file in DOCUMENT_DIR.glob("*.pdf"):
            pdf_file.unlink()
            deleted_count += 1
        
        return {
            "status": "success",
            "message": f"Deleted {deleted_count} documents"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents/count")
async def count_documents():
    """Count uploaded documents."""
    try:
        count = len(list(DOCUMENT_DIR.glob("*.pdf")))
        return {
            "status": "success",
            "count": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Global error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc)
        }
    )


# Development server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
