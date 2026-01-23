"""
Academic Evaluator - Main Orchestrator
Coordinates PDF processing, LLM analysis, and data storage.

COMPONENT STATUS: ✅ COMPLETE  
LAST UPDATED: 2025-01-21
DEPENDENCIES: All core modules, batch processing ready
"""
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.core.pdf_processor import PDFProcessor
from src.core.ocr_processor import OCRProcessor
from src.core.academic_llm_analyzer import AcademicLLMAnalyzer
from src.core.excel_handler import ExcelHandler
from src.utils.logger import get_logger, log_performance, log_user_action, log_system_event
from config.settings import DOCUMENT_DIR, EXCEL_DIR, SUPABASE_URL, SUPABASE_KEY, USE_SUPABASE


class AcademicEvaluator:
    """Main orchestrator for academic document processing.
    
    Features:
    - Batch document processing
    - Automatic OCR fallback
    - Dual storage (Excel + Supabase)
    - Progress tracking
    - Comprehensive error handling
    """
    
    def __init__(self):
        """Initialize the Academic Evaluator."""
        self.logger = get_logger("academic_evaluator")
        
        # Initialize components
        self.pdf_processor = PDFProcessor(DOCUMENT_DIR)
        self.ocr_processor = OCRProcessor(DOCUMENT_DIR)
        self.excel_handler = ExcelHandler()
        
        # Initialize LLM analyzer
        try:
            self.llm_analyzer = AcademicLLMAnalyzer()
            self.llm_available = True
            self.logger.info("LLM Analyzer initialized successfully")
        except Exception as e:
            self.llm_available = False
            self.llm_error = str(e)
            self.logger.error(f"Failed to initialize LLM Analyzer: {e}")
        
        # Initialize Supabase client (optional)
        self.supabase_available = False
        self.supabase_client = None
        
        if USE_SUPABASE:
            if not SUPABASE_URL or not SUPABASE_KEY:
                self.logger.warning("USE_SUPABASE enabled but credentials missing")
            else:
                try:
                    from src.core.supabase_client import get_client
                    self.supabase_client = get_client()
                    
                    if self.supabase_client.health_check():
                        self.supabase_available = True
                        self.logger.info("✓ Supabase client initialized")
                    else:
                        self.logger.error("Supabase health check failed")
                except Exception as e:
                    self.logger.error(f"Failed to initialize Supabase: {e}")
        else:
            self.logger.info("Supabase dual-write disabled")
        
        log_system_event("AcademicEvaluator initialized", {
            "llm_available": self.llm_available,
            "supabase_available": self.supabase_available,
            "document_directory": str(DOCUMENT_DIR),
            "excel_directory": str(EXCEL_DIR)
        })
    
    def process_single_document(
        self,
        document_path: Path,
        custom_prompt: Optional[str] = None,
        save_to_excel: bool = True
    ) -> Dict[str, Any]:
        """Process a single academic document.
        
        Args:
            document_path: Path to the PDF/document
            custom_prompt: Optional custom analysis prompt
            save_to_excel: Whether to save to Excel
            
        Returns:
            Dictionary containing analysis results
        """
        if not self.llm_available:
            raise RuntimeError(f"LLM Analyzer not available: {self.llm_error}")
        
        start_time = time.time()
        log_user_action("process_single_document", details={"path": str(document_path)})
        
        try:
            # Determine document type and extract text
            self.logger.info(f"Analyzing document type: {document_path}")
            is_image_based = self.ocr_processor.is_image_based_pdf(document_path)
            
            if is_image_based:
                self.logger.info(f"Image-based document, using OCR: {document_path}")
                text_content = self.ocr_processor.extract_text_with_ocr(document_path)
                extraction_method = "OCR"
            else:
                self.logger.info(f"Text-based document: {document_path}")
                text_content = self.pdf_processor.extract_text_from_pdf(document_path)
                extraction_method = "Regular"
                
                # Fallback to OCR if regular extraction fails
                if not text_content:
                    self.logger.info(f"Regular extraction failed, trying OCR: {document_path}")
                    text_content = self.ocr_processor.extract_text_with_ocr(document_path)
                    extraction_method = "OCR_Fallback"
            
            if not text_content:
                raise ValueError(f"Failed to extract text from {document_path}")
            
            # Analyze with LLM
            self.logger.info(f"Analyzing document with LLM: {document_path}")
            analysis_result = self.llm_analyzer.analyze_document(text_content, custom_prompt)
            
            # Add file information
            analysis_result['_file_info'] = {
                'filename': document_path.name,
                'filepath': str(document_path),
                'text_length': len(text_content),
                'extraction_method': extraction_method
            }
            
            # Save to Excel
            if save_to_excel:
                self.logger.info(f"Saving to Excel: {document_path.name}")
                current_batch = self.excel_handler.get_current_batch()
                if current_batch:
                    self.excel_handler.append_data_to_batch(
                        analysis_result,
                        document_path.name,
                        current_batch
                    )
                    
                    # Save courses data
                    courses = analysis_result.get('Courses', [])
                    if courses and isinstance(courses, list):
                        self.excel_handler.append_courses_data(
                            courses,
                            analysis_result.get('Student Name', ''),
                            analysis_result.get('Roll Number', ''),
                            document_path.name,
                            current_batch
                        )
            
            duration = time.time() - start_time
            log_performance("process_single_document", duration, {
                "filename": document_path.name,
                "text_length": len(text_content)
            })
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Error processing document {document_path}: {e}")
            raise
    
    def process_batch_documents(
        self,
        document_paths: List[Path],
        custom_prompt: Optional[str] = None,
        batch_name: str = None,
        progress_callback: Optional[callable] = None
    ) -> tuple[List[Dict[str, Any]], str]:
        """Process multiple documents in batch.
        
        Args:
            document_paths: List of document paths
            custom_prompt: Optional custom prompt
            batch_name: Optional batch name
            progress_callback: Optional progress callback function
            
        Returns:
            Tuple of (results list, batch_filename)
        """
        if not self.llm_available:
            raise RuntimeError(f"LLM Analyzer not available: {self.llm_error}")
        
        start_time = time.time()
        log_user_action("process_batch_documents", details={"count": len(document_paths)})
        
        # Create new batch Excel file
        success, batch_filename = self.excel_handler.create_batch_excel_file(batch_name)
        if not success:
            self.logger.error("Failed to create batch Excel file")
            return [], ""
        
        self.logger.info(f"Created batch file: {batch_filename}")
        
        results = []
        successful_count = 0
        supabase_success = 0
        supabase_fail = 0
        
        try:
            for i, doc_path in enumerate(document_paths):
                self.logger.info(f"Processing {i+1}/{len(document_paths)}: {doc_path.name}")
                
                # Update progress
                if progress_callback:
                    progress_callback(i + 1, len(document_paths), doc_path.name)
                
                try:
                    # Process document (saves to Excel automatically)
                    result = self.process_single_document(doc_path, custom_prompt, save_to_excel=False)
                    results.append(result)
                    
                    # Save to batch Excel
                    if not result.get('_metadata', {}).get('error'):
                        # Save student data
                        self.excel_handler.append_data_to_batch(
                            result,
                            doc_path.name,
                            batch_filename
                        )
                        
                        # Save courses
                        courses = result.get('Courses', [])
                        if courses and isinstance(courses, list):
                            self.excel_handler.append_courses_data(
                                courses,
                                result.get('Student Name', ''),
                                result.get('Roll Number', ''),
                                doc_path.name,
                                batch_filename
                            )
                        
                        # Write to Supabase
                        if self._write_to_supabase(result, doc_path.name):
                            supabase_success += 1
                        else:
                            supabase_fail += 1
                        
                        successful_count += 1
                    
                except Exception as e:
                    self.logger.error(f"Failed to process {doc_path}: {e}")
                    
                    # Create error result
                    error_result = {
                        'Student Name': 'Error',
                        'Roll Number': 'Error',
                        'Email': 'Error',
                        'Phone': 'Error',
                        'Department': 'Error',
                        'Program': 'Error',
                        'Semester': 'Error',
                        'CGPA': 'Error',
                        'Academic Year': 'Error',
                        '_metadata': {
                            'error': True,
                            'error_message': str(e)
                        },
                        '_file_info': {
                            'filename': doc_path.name,
                            'filepath': str(doc_path)
                        }
                    }
                    results.append(error_result)
            
            duration = time.time() - start_time
            
            if self.supabase_available:
                self.logger.info(
                    f"Supabase writes: {supabase_success} successful, {supabase_fail} failed"
                )
            
            log_performance("process_batch_documents", duration, {
                "total_files": len(document_paths),
                "successful": successful_count,
                "failed": len(document_paths) - successful_count,
                "batch_filename": batch_filename,
                "supabase_success": supabase_success,
                "supabase_failed": supabase_fail
            })
            
            self.logger.info(f"Batch completed: {successful_count}/{len(document_paths)} successful")
            
            # Final progress update
            if progress_callback:
                progress_callback(len(document_paths), len(document_paths), "Completed")
            
            return results, batch_filename
            
        except Exception as e:
            self.logger.error(f"Error during batch processing: {e}")
            raise
    
    def _write_to_supabase(self, analysis_result: Dict[str, Any], filename: str) -> bool:
        """Write analysis result to Supabase.
        
        Args:
            analysis_result: Analysis dictionary
            filename: Document filename
            
        Returns:
            True if successful, False otherwise
        """
        if not self.supabase_available:
            return False
        
        try:
            # Insert student record
            result = self.supabase_client.insert_student(analysis_result)
            
            if result.get('success'):
                student_id = result.get('id')
                self.logger.info(f"✓ Supabase: Inserted student {filename} (ID: {student_id})")
                
                # Insert courses
                courses = analysis_result.get('Courses', [])
                if courses:
                    self.supabase_client.insert_courses(courses, student_id)
                
                # Insert projects
                projects = analysis_result.get('Academic Projects', [])
                if projects:
                    self.supabase_client.insert_projects(projects, student_id)
                
                # Insert internships
                internships = analysis_result.get('Internships', [])
                if internships:
                    self.supabase_client.insert_internships(internships, student_id)
                
                # Insert certifications
                certifications = analysis_result.get('Certifications', [])
                if certifications:
                    self.supabase_client.insert_certifications(certifications, student_id)
                
                # Insert publications
                publications = analysis_result.get('Publications', [])
                if publications:
                    self.supabase_client.insert_publications(publications, student_id)
                
                return True
            else:
                self.logger.error(f"Supabase insert failed for {filename}")
                return False
                
        except Exception as e:
            self.logger.error(f"Supabase write error for {filename}: {e}")
            return False
    
    def validate_system(self) -> Dict[str, Any]:
        """Validate all system components.
        
        Returns:
            Dictionary with validation results
        """
        results = {
            'pdf_processor': True,
            'ocr_processor': True,
            'excel_handler': True,
            'llm_analyzer': self.llm_available,
            'supabase': self.supabase_available,
            'document_directory': DOCUMENT_DIR.exists(),
            'excel_directory': EXCEL_DIR.exists(),
        }
        
        # Test LLM connection
        if self.llm_available:
            try:
                connections = self.llm_analyzer.validate_api_connection()
                results['llm_connections'] = connections
            except Exception as e:
                results['llm_error'] = str(e)
        
        # Count documents
        if DOCUMENT_DIR.exists():
            results['documents_found'] = len(list(DOCUMENT_DIR.glob("*.pdf")))
        
        # Overall status
        if all([results['pdf_processor'], results['excel_handler'], results['llm_analyzer']]):
            results['overall_status'] = 'OK'
        else:
            results['overall_status'] = 'ERROR'
        
        return results
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        return {
            'document_directory': str(DOCUMENT_DIR),
            'excel_directory': str(EXCEL_DIR),
            'llm_available': self.llm_available,
            'llm_status': self.llm_analyzer.get_provider_status() if self.llm_available else None,
            'supabase_available': self.supabase_available,
            'current_batch': self.excel_handler.get_current_batch(),
            'available_batches': len(self.excel_handler.get_available_batches())
        }
