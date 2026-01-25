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
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from src.core.dashboard_analytics import DashboardAnalytics
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
        "https://give-me-marks.vercel.app",  # Your Vercel deployment
        "https://*.vercel.app",
        "*"  # Allow all origins in production (update with your Vercel domain)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
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
    student_name: Optional[str] = None
    roll_number: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    cgpa: Optional[float] = None
    document_status: Optional[str] = None
    
    class Config:
        # Allow None values for all fields
        from_attributes = True

class DocumentResult(BaseModel):
    """Represents a processed document with status."""
    filename: str
    document_status: str
    has_identity: bool
    has_academic_data: bool
    student_name: Optional[str] = None
    roll_number: Optional[str] = None
    error: Optional[str] = None

class BatchResult(BaseModel):
    batch_id: str
    batch_filename: str
    total_documents: int
    successful: int
    failed: int
    success_rate: float
    students: List[StudentData]
    documents: List[DocumentResult]

class SystemStatus(BaseModel):
    status: str
    llm_available: bool
    llm_provider: str
    supabase_available: bool
    documents_in_queue: int


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize evaluator and create demo data on startup."""
    global evaluator
    try:
        # Create demo data if it doesn't exist
        logger.info("Checking for demo data...")
        try:
            from create_demo_data import check_and_create_if_needed
            check_and_create_if_needed()
            logger.info("✓ Demo data check complete")
        except Exception as e:
            logger.warning(f"Could not create demo data: {e}")
        
        # Initialize evaluator
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
        if evaluator is None:
            raise HTTPException(status_code=503, detail="Evaluator not initialized")
        
        info = evaluator.get_system_info()
        
        # Count documents in queue
        doc_count = 0
        try:
            if DOCUMENT_DIR.exists():
                doc_count = len(list(DOCUMENT_DIR.glob("*.pdf")))
        except Exception as e:
            logger.warning(f"Failed to count documents: {e}")
        
        # Get LLM provider name safely
        llm_provider = "none"
        if info.get('llm_available') and info.get('llm_status'):
            llm_status = info['llm_status']
            if isinstance(llm_status, dict):
                llm_provider = llm_status.get('current_provider', 'none') or 'none'
        
        return SystemStatus(
            status="operational",
            llm_available=info.get('llm_available', False),
            llm_provider=llm_provider,
            supabase_available=info.get('supabase_available', False),
            documents_in_queue=doc_count
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")


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
        
        # Parse results - count successful processing (not just identity presence)
        successful = sum(1 for r in results if r.get('_metadata', {}).get('processing_success', True))
        failed = len(results) - successful
        
        # Extract all documents with status
        documents = []
        students = []
        
        for result in results:
            file_info = result.get('_file_info', {})
            filename = file_info.get('filename', 'unknown')
            metadata = result.get('_metadata', {})
            
            # Create document result (always include, regardless of identity)
            doc_result = DocumentResult(
                filename=filename,
                document_status=result.get('_document_status', 'UNKNOWN'),
                has_identity=result.get('_has_identity', False),
                has_academic_data=result.get('_has_academic_data', False),
                student_name=result.get("Student Name"),
                roll_number=result.get("Roll Number"),
                error=metadata.get('error')
            )
            documents.append(doc_result)
            
            # Extract student data (only if identity exists, for display purposes)
            if result.get('_has_identity') and not metadata.get('error'):
                student_name = result.get("Student Name")
                roll_number = result.get("Roll Number")
                
                # Handle CGPA conversion
                cgpa = result.get("CGPA")
                if cgpa is not None:
                    try:
                        cgpa = float(cgpa)
                    except (ValueError, TypeError):
                        cgpa = None
                
                students.append(StudentData(
                    student_name=student_name,
                    roll_number=roll_number,
                    email=result.get("Email"),
                    department=result.get("Department"),
                    cgpa=cgpa,
                    document_status=result.get('_document_status')
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
            success_rate=successful / len(results) * 100 if results else 0,
            students=students,
            documents=documents
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


# ========== NEW ENDPOINTS FOR ENHANCED FEATURES ==========

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """
    Get comprehensive statistics for dashboard visualization
    Returns data for ALL STUDENTS from ALL BATCHES
    """
    try:
        import pandas as pd
        import json
        from collections import Counter
        
        # Read batch metadata
        batch_metadata_file = EXCEL_DIR / "batch_metadata.json"
        if not batch_metadata_file.exists():
            logger.warning("batch_metadata.json not found")
            return {"error": "No batch metadata found", "total_students": 0}
        
        with open(batch_metadata_file, 'r') as f:
            metadata = json.load(f)
        
        batches = metadata.get('batches', [])
        if not batches:
            logger.warning("No batches found")
            return {"error": "No batches found", "total_students": 0}
        
        logger.info(f"Loading data from {len(batches)} batches")
        
        # Read and combine ALL batch files
        all_dfs = []
        for batch in batches:
            batch_filename = batch.get('filename')
            if batch_filename:
                batch_path = EXCEL_DIR / batch_filename
                if batch_path.exists():
                    try:
                        df_temp = pd.read_excel(batch_path, sheet_name='Student Data')
                        all_dfs.append(df_temp)
                        logger.info(f"Loaded {len(df_temp)} students from {batch_filename}")
                    except Exception as e:
                        logger.warning(f"Failed to read {batch_filename}: {e}")
        
        if not all_dfs:
            logger.warning("No valid batch files found")
            return {"error": "No valid batch files", "total_students": 0}
        
        # Combine all dataframes
        df = pd.concat(all_dfs, ignore_index=True)
        logger.info(f"Total combined students: {len(df)}")
        
        # Remove duplicates based on Roll Number
        df = df.drop_duplicates(subset=['Roll Number'], keep='last')
        logger.info(f"After removing duplicates: {len(df)} unique students")
        
        # Convert to list of dicts
        students = df.to_dict('records')
        logger.info(f"Found {len(students)} students in batch")
        
        # Calculate statistics
        cgpa_values = []
        for s in students:
            try:
                cgpa = s.get('CGPA')
                if pd.notna(cgpa):
                    cgpa_values.append(float(cgpa))
            except (ValueError, TypeError):
                continue
        
        departments = [s['Department'] for s in students if pd.notna(s.get('Department'))]
        
        # CGPA Distribution
        cgpa_dist = [
            {"range": "9.0-10.0", "count": sum(1 for c in cgpa_values if 9.0 <= c <= 10.0)},
            {"range": "8.0-8.9", "count": sum(1 for c in cgpa_values if 8.0 <= c < 9.0)},
            {"range": "7.0-7.9", "count": sum(1 for c in cgpa_values if 7.0 <= c < 8.0)},
            {"range": "6.0-6.9", "count": sum(1 for c in cgpa_values if 6.0 <= c < 7.0)},
            {"range": "Below 6.0", "count": sum(1 for c in cgpa_values if c < 6.0)},
        ]
        
        # Department Distribution
        dept_counter = Counter(departments)
        dept_dist = [{"name": dept, "count": count} for dept, count in dept_counter.items()]
        
        # Top Performers
        top_students = sorted(
            [s for s in students if pd.notna(s.get('CGPA'))],
            key=lambda x: float(x.get('CGPA', 0)) if pd.notna(x.get('CGPA')) else 0,
            reverse=True
        )[:10]
        
        top_performers = []
        for s in top_students:
            try:
                cgpa_raw = s.get('CGPA')
                if pd.notna(cgpa_raw):
                    cgpa_float = float(cgpa_raw)
                    if not (pd.isna(cgpa_float) or cgpa_float == float('inf') or cgpa_float == float('-inf')):
                        cgpa_val = round(cgpa_float, 2)
                    else:
                        cgpa_val = 0
                else:
                    cgpa_val = 0
            except (ValueError, TypeError):
                cgpa_val = 0
            
            top_performers.append({
                'name': s.get('Student Name', 'N/A'),
                'roll_number': s.get('Roll Number', 'N/A'),
                'department': s.get('Department', 'N/A'),
                'cgpa': cgpa_val
            })
        
        avg_cgpa = round(sum(cgpa_values) / len(cgpa_values), 2) if cgpa_values else 0
        
        response = {
            "total_students": len(students),
            "average_cgpa": avg_cgpa,
            "cgpa_distribution": cgpa_dist,
            "departments": dept_dist,
            "top_performers": top_performers
        }
        
        logger.info(f"Returning dashboard stats: {len(students)} students, avg CGPA {avg_cgpa}")
        return response
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}", exc_info=True)
        return {"error": str(e), "total_students": 0}


@app.get("/api/dashboard/alerts")
async def get_academic_alerts(batches: str = ""):
    """
    Get academic alerts and recommendations for faculty
    Supports filtering by specific batches via query parameter
    Example: /api/dashboard/alerts?batches=batch1.xlsx,batch2.xlsx
    """
    try:
        import pandas as pd
        import json
        from src.core.academic_alerts import AcademicAlertsGenerator
        
        # Read batch metadata
        batch_metadata_file = EXCEL_DIR / "batch_metadata.json"
        if not batch_metadata_file.exists():
            return {"alerts": []}
        
        with open(batch_metadata_file, 'r') as f:
            metadata = json.load(f)
        
        all_batches = metadata.get('batches', [])
        if not all_batches:
            return {"alerts": []}
        
        # Parse selected batches from query parameter
        selected_batch_filenames = []
        if batches:
            selected_batch_filenames = [b.strip() for b in batches.split(',') if b.strip()]
            logger.info(f"Filtering alerts for {len(selected_batch_filenames)} selected batches")
        else:
            # If no batches specified, use all batches
            selected_batch_filenames = [b.get('filename') for b in all_batches if b.get('filename')]
            logger.info(f"Using all {len(selected_batch_filenames)} batches for alerts")
        
        # Read and combine selected batch files
        all_dfs = []
        for batch_filename in selected_batch_filenames:
            batch_path = EXCEL_DIR / batch_filename
            if batch_path.exists():
                try:
                    df_temp = pd.read_excel(batch_path, sheet_name='Student Data')
                    all_dfs.append(df_temp)
                    logger.info(f"Loaded {len(df_temp)} students from {batch_filename} for alerts")
                except Exception as e:
                    logger.warning(f"Failed to read {batch_filename}: {e}")
        
        if not all_dfs:
            logger.warning("No batch data available for alerts")
            return {"alerts": []}
        
        # Combine all dataframes
        df = pd.concat(all_dfs, ignore_index=True)
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['Roll Number'], keep='last')
        
        # Generate alerts
        alerts = AcademicAlertsGenerator.generate_alerts(df)
        
        logger.info(f"Generated {len(alerts)} alerts for {len(selected_batch_filenames)} batch(es)")
        
        return {"alerts": alerts, "total": len(alerts), "batches_analyzed": len(selected_batch_filenames)}
        
    except Exception as e:
        logger.error(f"Error generating alerts: {e}", exc_info=True)
        return {"alerts": [], "error": str(e)}


@app.get("/api/search/students")
async def search_students(query: str = "", department: str = "", min_cgpa: float = 0.0, max_cgpa: float = 10.0):
    """
    Search students with filters - searches ALL BATCHES
    Query params: query (name/roll), department, min_cgpa, max_cgpa
    """
    try:
        import pandas as pd
        import json
        
        # Read batch metadata
        batch_metadata_file = EXCEL_DIR / "batch_metadata.json"
        if not batch_metadata_file.exists():
            return {"results": [], "count": 0}
        
        with open(batch_metadata_file, 'r') as f:
            metadata = json.load(f)
        
        batches = metadata.get('batches', [])
        if not batches:
            return {"results": [], "count": 0}
        
        logger.info(f"Searching across {len(batches)} batches with query: '{query}'")
        
        # Read and combine ALL batch files
        all_dfs = []
        for batch in batches:
            batch_filename = batch.get('filename')
            if batch_filename:
                batch_path = EXCEL_DIR / batch_filename
                if batch_path.exists():
                    try:
                        df_temp = pd.read_excel(batch_path, sheet_name='Student Data')
                        all_dfs.append(df_temp)
                    except Exception as e:
                        logger.warning(f"Failed to read {batch_filename}: {e}")
        
        if not all_dfs:
            return {"results": [], "count": 0}
        
        # Combine all dataframes
        df = pd.concat(all_dfs, ignore_index=True)
        
        # Remove duplicates based on Roll Number (keep latest)
        df = df.drop_duplicates(subset=['Roll Number'], keep='last')
        
        logger.info(f"Total unique students: {len(df)}")
        
        # Apply filters
        if query:
            df = df[
                df['Student Name'].str.contains(query, case=False, na=False) |
                df['Roll Number'].astype(str).str.contains(query, case=False, na=False)
            ]
        
        if department:
            df = df[df['Department'].str.contains(department, case=False, na=False)]
        
        # CGPA filter
        df['CGPA_numeric'] = pd.to_numeric(df['CGPA'], errors='coerce')
        df = df[(df['CGPA_numeric'] >= min_cgpa) & (df['CGPA_numeric'] <= max_cgpa)]
        
        # Convert to list of dicts and format
        results = []
        for _, row in df.iterrows():
            # Safely handle CGPA conversion
            cgpa_value = 0
            try:
                cgpa_raw = row.get('CGPA')
                if pd.notna(cgpa_raw):
                    cgpa_float = float(cgpa_raw)
                    # Check if CGPA is a valid number (not NaN, not Infinity)
                    if not (pd.isna(cgpa_float) or cgpa_float == float('inf') or cgpa_float == float('-inf')):
                        cgpa_value = round(cgpa_float, 2)
            except (ValueError, TypeError):
                cgpa_value = 0
            
            # Sanitize ALL fields to prevent JSON serialization errors
            def sanitize_value(val):
                """Convert any value to JSON-safe format"""
                if pd.isna(val):
                    return 'N/A'
                if isinstance(val, (int, float, np.number)):
                    if pd.isna(val) or val == float('inf') or val == float('-inf'):
                        return 'N/A'
                    return val
                return str(val) if val is not None else 'N/A'
            
            results.append({
                "name": sanitize_value(row.get('Student Name')),
                "roll_number": sanitize_value(row.get('Roll Number')),
                "department": sanitize_value(row.get('Department')),
                "cgpa": cgpa_value,
                "email": sanitize_value(row.get('Email')),
                "semester": sanitize_value(row.get('Semester'))
            })
        
        logger.info(f"Found {len(results)} matching students")
        
        return {
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error searching students: {e}", exc_info=True)
        return {"error": str(e), "results": [], "count": 0}


@app.get("/api/batches/all")
async def get_all_batches_with_data():
    """
    Get all batches with their metadata and student counts
    """
    try:
        import json
        
        batch_metadata_file = EXCEL_DIR / "batch_metadata.json"
        if not batch_metadata_file.exists():
            return {"batches": []}
        
        with open(batch_metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Format batches with proper structure
        batches = metadata.get('batches', [])
        formatted_batches = []
        
        for batch in batches:
            formatted_batches.append({
                "filename": batch.get('filename'),
                "student_count": batch.get('record_count', 0),  # Map record_count to student_count
                "created_at": batch.get('created_at'),
                "file_path": batch.get('file_path')
            })
        
        return {
            "batches": formatted_batches,
            "current_batch": metadata.get('current_batch')
        }
        
    except Exception as e:
        logger.error(f"Error getting batches: {e}")
        return {"error": str(e), "batches": []}


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

@app.get("/analytics/cgpa-distribution")
async def get_cgpa_distribution():
    """Get CGPA distribution data for Chart 1"""
    students = get_all_students_from_db()  # Your existing function
    distribution = DashboardAnalytics.calculate_cgpa_distribution(students)
    return {"distribution": distribution}

@app.get("/analytics/subject-performance")
async def get_subject_performance():
    """Get subject averages for Chart 2"""
    students = get_all_students_from_db()
    subjects = DashboardAnalytics.calculate_subject_averages(students)
    return {"subjects": subjects}

@app.get("/analytics/at-risk-students")
async def get_at_risk_students():
    """Get at-risk students for Chart 3"""
    students = get_all_students_from_db()
    at_risk = DashboardAnalytics.identify_at_risk_students(students)
    return {"at_risk_students": at_risk}

# AI Query Backend with Cohere
@app.post("/api/ai/query")
async def ai_query_endpoint(request: dict):
    """
    AI Query endpoint - Uses Cohere to answer questions about academic data
    Supports batch selection for efficient querying
    """
    try:
        query = request.get("query", "")
        batch_filenames = request.get("batches", [])  # Accept multiple batches
        
        # Also support single batch for backward compatibility
        single_batch = request.get("batch", None)
        if single_batch and not batch_filenames:
            batch_filenames = [single_batch]
        
        if not query:
            return JSONResponse(
                content={"error": "No query provided", "response": "Please provide a query."},
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Headers": "*"
                }
            )
        
        logger.info(f"AI Query: {query} | Batches: {batch_filenames or 'all'}")
        
        import pandas as pd
        import json
        from src.core.gemini_ai_agent import GeminiAIAgent
        
        # Load batch data for context
        batch_metadata_file = EXCEL_DIR / "batch_metadata.json"
        
        if not batch_metadata_file.exists():
            return JSONResponse(
                content={
                    "response": "No processed data available yet. Please upload and process documents first.",
                    "timestamp": datetime.now().isoformat(),
                    "query": query
                },
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Headers": "*"
                }
            )
        
        with open(batch_metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Load data from all selected batches
        all_dfs = []
        batch_names = []
        
        if batch_filenames:
            # Use specified batches
            for batch_filename in batch_filenames:
                batch_file = EXCEL_DIR / batch_filename
                if batch_file.exists():
                    try:
                        df_temp = pd.read_excel(batch_file, sheet_name='Student Data')
                        all_dfs.append(df_temp)
                        batch_names.append(batch_filename)
                        logger.info(f"Loaded {len(df_temp)} students from {batch_filename}")
                    except Exception as e:
                        logger.warning(f"Failed to read {batch_filename}: {e}")
        else:
            # Use current batch if none specified
            current_batch = metadata.get('current_batch')
            if current_batch:
                batch_file = EXCEL_DIR / current_batch
                if batch_file.exists():
                    df_temp = pd.read_excel(batch_file, sheet_name='Student Data')
                    all_dfs.append(df_temp)
                    batch_names.append(current_batch)
                    logger.info(f"Loaded {len(df_temp)} students from {current_batch}")
        
        if not all_dfs:
            return JSONResponse(
                content={
                    "response": "No batch data found or unable to read batch files.",
                    "timestamp": datetime.now().isoformat(),
                    "query": query
                },
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Headers": "*"
                }
            )
        
        # Combine all dataframes
        df = pd.concat(all_dfs, ignore_index=True)
        logger.info(f"Combined total: {len(df)} students from {len(batch_names)} batch(es)")
        
        # Initialize Gemini AI Agent
        ai_agent = GeminiAIAgent()
        
        # Query with Gemini
        result = ai_agent.query(
            question=query,
            df=df,
            batch_name=f"{len(batch_names)} batches: {', '.join([b.split('_')[-1].replace('.xlsx', '') for b in batch_names])}"
        )
        
        logger.info(f"AI response generated successfully")
        return JSONResponse(
            content=result,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )
        
    except Exception as e:
        logger.error(f"AI Query error: {e}", exc_info=True)
        return JSONResponse(
            content={
                "error": str(e),
                "response": f"Sorry, I encountered an error: {str(e)}. Please try again.",
                "timestamp": datetime.now().isoformat()
            },
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )

@app.post("/api/create-demo-data")
async def create_demo_data_endpoint():
    """Manually trigger demo data creation (for deployment testing)."""
    try:
        from create_demo_data import create_sample_batch
        
        batch_filename, student_count = create_sample_batch()
        
        return {
            "success": True,
            "message": "Demo data created successfully",
            "batch_filename": batch_filename,
            "student_count": student_count
        }
    except Exception as e:
        logger.error(f"Demo data creation error: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }

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
