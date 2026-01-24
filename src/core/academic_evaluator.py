"""
Academic Evaluator - Main Orchestrator
Coordinates PDF processing, LLM analysis, and data storage.

REPAIRED VERSION:
- Adds LLM output normalization
- Fixes Excel empty data issue
- Prevents Supabase numeric crashes
- Keeps batch logic intact

LAST UPDATED: 2026-01-23
"""

import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.core.pdf_processor import PDFProcessor
from src.core.ocr_processor import OCRProcessor
from src.core.academic_llm_analyzer import AcademicLLMAnalyzer
from src.core.excel_handler import ExcelHandler
from src.utils.logger import (
    get_logger,
    log_performance,
    log_user_action,
    log_system_event,
)
from config.settings import DOCUMENT_DIR, EXCEL_DIR, SUPABASE_URL, SUPABASE_KEY, USE_SUPABASE


class AcademicEvaluator:
    """Main orchestrator for academic document processing."""

    def __init__(self):
        self.logger = get_logger("academic_evaluator")

        self.pdf_processor = PDFProcessor(DOCUMENT_DIR)
        self.ocr_processor = OCRProcessor(DOCUMENT_DIR)
        self.excel_handler = ExcelHandler()

        # Initialize LLM
        try:
            self.llm_analyzer = AcademicLLMAnalyzer()
            self.llm_available = True
            self.logger.info("✓ LLM Analyzer initialized")
        except Exception as e:
            self.llm_available = False
            self.llm_error = str(e)
            self.logger.error(f"LLM init failed: {e}")

        # Supabase (optional)
        self.supabase_available = False
        self.supabase_client = None

        if USE_SUPABASE and SUPABASE_URL and SUPABASE_KEY:
            try:
                from src.core.supabase_client import get_client

                self.supabase_client = get_client()
                if self.supabase_client.health_check():
                    self.supabase_available = True
                    self.logger.info("✓ Supabase connected")
            except Exception as e:
                self.logger.error(f"Supabase init failed: {e}")

        log_system_event("AcademicEvaluator initialized", {
            "llm_available": self.llm_available,
            "supabase_available": self.supabase_available,
        })

    # ------------------------------------------------------------------
    # NORMALIZATION LAYER (CRITICAL FIX)
    # ------------------------------------------------------------------

    def _normalize_analysis_result(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        def clean_text(v):
            if v in ["", "N/A", None]:
                return None
            return str(v).strip()

        def clean_number(v):
            if v in ["", "N/A", None]:
                return None
            try:
                return float(v)
            except Exception:
                return None

        normalized = {
            "Student Name": clean_text(raw.get("Student Name") or raw.get("student_name")),
            "Roll Number": clean_text(raw.get("Roll Number") or raw.get("roll_number")),
            "Email": clean_text(raw.get("Email")),
            "Phone": clean_text(raw.get("Phone")),
            "Department": clean_text(raw.get("Department")),
            "Program": clean_text(raw.get("Program")),
            "Semester": clean_text(raw.get("Semester")),
            "Academic Year": clean_text(raw.get("Academic Year")),
            "CGPA": clean_number(raw.get("CGPA")),
            "SGPA": clean_number(raw.get("SGPA")),
            "Percentage": clean_number(raw.get("Percentage")),
            "Courses": raw.get("Courses", []),
            "Academic Projects": raw.get("Academic Projects", []),
            "Internships": raw.get("Internships", []),
            "Certifications": raw.get("Certifications", []),
            "Publications": raw.get("Publications", []),
            "Model Used": raw.get("Model Used"),
            "_metadata": raw.get("_metadata", {}),
            "_file_info": raw.get("_file_info", {}),
        }

        # Determine document status
        has_identity = bool(normalized.get("Student Name") or normalized.get("Roll Number"))
        has_academic_data = bool(
            normalized.get("CGPA") is not None or 
            normalized.get("SGPA") is not None or 
            normalized.get("Courses")
        )
        
        if has_identity and has_academic_data:
            document_status = "COMPLETE"
        elif has_identity:
            document_status = "PARTIAL"
        elif has_academic_data:
            document_status = "INCOMPLETE_IDENTITY"
        else:
            document_status = "MINIMAL_DATA"
        
        normalized["_document_status"] = document_status
        normalized["_has_identity"] = has_identity
        normalized["_has_academic_data"] = has_academic_data

        return normalized

    # ------------------------------------------------------------------
    # SINGLE DOCUMENT PROCESSING
    # ------------------------------------------------------------------

    def process_single_document(
        self,
        document_path: Path,
        custom_prompt: Optional[str] = None,
        save_to_excel: bool = True,
    ) -> Dict[str, Any]:

        if not self.llm_available:
            raise RuntimeError("LLM not available")

        start_time = time.time()
        log_user_action("process_single_document", {"file": document_path.name})

        is_image_based = self.ocr_processor.is_image_based_pdf(document_path)

        if is_image_based:
            text = self.ocr_processor.extract_text_with_ocr(document_path)
            extraction_method = "OCR"
        else:
            text = self.pdf_processor.extract_text_from_pdf(document_path)
            extraction_method = "Regular"

        if not text:
            raise ValueError("Text extraction failed")

        raw_result = self.llm_analyzer.analyze_document(text, custom_prompt)
        result = self._normalize_analysis_result(raw_result)

        result["_file_info"].update({
            "filename": document_path.name,
            "filepath": str(document_path),
            "extraction_method": extraction_method,
            "text_length": len(text),
        })

        duration = time.time() - start_time
        log_performance("process_single_document", duration)

        return result

    # ------------------------------------------------------------------
    # BATCH PROCESSING
    # ------------------------------------------------------------------

    def process_batch_documents(
        self,
        document_paths: List[Path],
        custom_prompt: Optional[str] = None,
        batch_name: Optional[str] = None,
        progress_callback: Optional[callable] = None,
    ) -> tuple[list, str]:

        success, batch_filename = self.excel_handler.create_batch_excel_file(batch_name)
        if not success:
            return [], ""

        results = []
        supabase_success = 0
        supabase_fail = 0

        for idx, doc_path in enumerate(document_paths):
            if progress_callback:
                progress_callback(idx + 1, len(document_paths), doc_path.name)

            try:
                result = self.process_single_document(doc_path, custom_prompt, save_to_excel=False)
                
                # Add processing metadata
                if "_metadata" not in result:
                    result["_metadata"] = {}
                result["_metadata"]["processing_success"] = True
                result["_metadata"]["error"] = None
                
                results.append(result)

                # Excel write (always write, regardless of identity fields)
                self.excel_handler.append_data_to_batch(result, doc_path.name, batch_filename)

                if result.get("Courses"):
                    self.excel_handler.append_courses_data(
                        result["Courses"],
                        result.get("Student Name"),
                        result.get("Roll Number"),
                        doc_path.name,
                        batch_filename,
                    )

                # Supabase write (only if identity exists)
                if result.get("_has_identity"):
                    if self._write_to_supabase(result, doc_path.name):
                        supabase_success += 1
                    else:
                        supabase_fail += 1
                else:
                    self.logger.info(f"Skipping Supabase (no identity): {doc_path.name}")

            except Exception as e:
                self.logger.error(f"Failed {doc_path.name}: {e}")
                # Add error result
                error_result = {
                    "_metadata": {
                        "processing_success": False,
                        "error": str(e),
                    },
                    "_file_info": {
                        "filename": doc_path.name,
                        "filepath": str(doc_path),
                    },
                    "_document_status": "PROCESSING_ERROR",
                    "_has_identity": False,
                    "_has_academic_data": False,
                }
                results.append(error_result)

        self.logger.info(
            f"Supabase writes: {supabase_success} success, {supabase_fail} failed"
        )

        return results, batch_filename

    # ------------------------------------------------------------------
    # SUPABASE WRITE (SAFE)
    # ------------------------------------------------------------------

    def _write_to_supabase(self, data: Dict[str, Any], filename: str) -> bool:
        if not self.supabase_available:
            return False

        if not data.get("Student Name"):
            self.logger.warning(f"Skipping Supabase (no student name): {filename}")
            return False

        try:
            res = self.supabase_client.insert_student(data)
            if not res.get("success"):
                return False

            student_id = res.get("id")

            if data.get("Courses"):
                self.supabase_client.insert_courses(data["Courses"], student_id)
            if data.get("Academic Projects"):
                self.supabase_client.insert_projects(data["Academic Projects"], student_id)
            if data.get("Internships"):
                self.supabase_client.insert_internships(data["Internships"], student_id)
            if data.get("Certifications"):
                self.supabase_client.insert_certifications(data["Certifications"], student_id)
            if data.get("Publications"):
                self.supabase_client.insert_publications(data["Publications"], student_id)

            return True

        except Exception as e:
            self.logger.error(f"Supabase error ({filename}): {e}")
            return False

    # ------------------------------------------------------------------
    # SYSTEM STATUS & VALIDATION
    # ------------------------------------------------------------------

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information for status endpoint."""
        try:
            # Get LLM status
            llm_status = {}
            if self.llm_available and self.llm_analyzer:
                llm_status = self.llm_analyzer.get_provider_status()
            else:
                llm_status = {
                    'current_provider': None,
                    'gemini': {'available': False},
                    'cohere': {'available': False},
                }

            # Get available batches
            try:
                batches = self.excel_handler.get_available_batches()
            except Exception:
                batches = []

            # Get current batch (most recent)
            current_batch = batches[0]['filename'] if batches else None

            return {
                'llm_available': self.llm_available,
                'llm_status': llm_status,
                'supabase_available': self.supabase_available,
                'document_directory': str(DOCUMENT_DIR),
                'excel_directory': str(EXCEL_DIR),
                'current_batch': current_batch,
                'available_batches': len(batches),
            }
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {
                'llm_available': False,
                'llm_status': {'current_provider': None},
                'supabase_available': False,
                'document_directory': str(DOCUMENT_DIR),
                'excel_directory': str(EXCEL_DIR),
                'current_batch': None,
                'available_batches': 0,
                'error': str(e),
            }

    def validate_system(self) -> Dict[str, Any]:
        """Validate all system components."""
        results = {
            'pdf_processor': False,
            'ocr_processor': False,
            'excel_handler': False,
            'llm_analyzer': False,
            'supabase': False,
            'document_directory': False,
            'excel_directory': False,
            'overall_status': 'OK',
        }

        # Validate PDF processor
        try:
            if self.pdf_processor:
                results['pdf_processor'] = True
        except Exception as e:
            self.logger.error(f"PDF processor validation failed: {e}")
            results['overall_status'] = 'ERROR'

        # Validate OCR processor
        try:
            if self.ocr_processor:
                results['ocr_processor'] = True
        except Exception as e:
            self.logger.error(f"OCR processor validation failed: {e}")
            results['overall_status'] = 'ERROR'

        # Validate Excel handler
        try:
            if self.excel_handler:
                results['excel_handler'] = True
        except Exception as e:
            self.logger.error(f"Excel handler validation failed: {e}")
            results['overall_status'] = 'ERROR'

        # Validate LLM analyzer
        try:
            if self.llm_available and self.llm_analyzer:
                results['llm_analyzer'] = True
                # Test LLM connections
                llm_status = self.llm_analyzer.get_provider_status()
                results['llm_connections'] = {
                    'gemini': llm_status.get('gemini', {}).get('available', False),
                    'cohere': llm_status.get('cohere', {}).get('available', False),
                }
        except Exception as e:
            self.logger.error(f"LLM analyzer validation failed: {e}")
            results['overall_status'] = 'ERROR'
            results['llm_connections'] = {'gemini': False, 'cohere': False}

        # Validate Supabase
        try:
            if self.supabase_available and self.supabase_client:
                if self.supabase_client.health_check():
                    results['supabase'] = True
        except Exception as e:
            self.logger.error(f"Supabase validation failed: {e}")

        # Validate directories
        try:
            if DOCUMENT_DIR.exists():
                results['document_directory'] = True
                results['documents_found'] = len(list(DOCUMENT_DIR.glob("*.pdf")))
            else:
                DOCUMENT_DIR.mkdir(parents=True, exist_ok=True)
                results['document_directory'] = True
                results['documents_found'] = 0
        except Exception as e:
            self.logger.error(f"Document directory validation failed: {e}")
            results['overall_status'] = 'ERROR'

        try:
            if EXCEL_DIR.exists():
                results['excel_directory'] = True
            else:
                EXCEL_DIR.mkdir(parents=True, exist_ok=True)
                results['excel_directory'] = True
        except Exception as e:
            self.logger.error(f"Excel directory validation failed: {e}")
            results['overall_status'] = 'ERROR'

        return results
