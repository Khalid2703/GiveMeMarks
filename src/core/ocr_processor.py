"""
OCR processing module for extracting text from image-based PDFs and scanned documents.
"""
import io
import os
from pathlib import Path
from typing import List, Optional
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from loguru import logger


class OCRProcessor:
    """Handles OCR-based text extraction from image-based PDFs and scanned documents."""
    
    def __init__(self, pdf_directory: Path):
        """
        Initialize OCR processor.
        
        Args:
            pdf_directory: Path to directory containing PDF files
        """
        self.pdf_directory = Path(pdf_directory)
        self.pdf_directory.mkdir(exist_ok=True)
        
        # Configure Tesseract (you may need to adjust the path)
        # pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'  # macOS
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
        
        logger.info(f"OCR Processor initialized with directory: {self.pdf_directory}")
    
    def extract_text_with_ocr(self, pdf_path: Path) -> Optional[str]:
        """
        Extract text from PDF using OCR (Optical Character Recognition).
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content or None if extraction fails
        """
        try:
            logger.info(f"Starting OCR extraction from: {pdf_path}")
            
            # Open PDF with PyMuPDF
            pdf_document = fitz.open(pdf_path)
            text_content = ""
            
            for page_num in range(len(pdf_document)):
                try:
                    page = pdf_document[page_num]
                    
                    # First, try to extract text directly (in case it's a hybrid PDF)
                    page_text = page.get_text()
                    
                    if page_text.strip():
                        # If direct text extraction works, use it
                        text_content += page_text + "\n"
                        logger.info(f"Page {page_num + 1}: Direct text extraction successful")
                    else:
                        # If no text, convert page to image and use OCR
                        logger.info(f"Page {page_num + 1}: No direct text, using OCR")
                        
                        # Convert page to image
                        mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better OCR
                        pix = page.get_pixmap(matrix=mat)
                        img_data = pix.tobytes("png")
                        
                        # Convert to PIL Image
                        image = Image.open(io.BytesIO(img_data))
                        
                        # Perform OCR
                        ocr_text = pytesseract.image_to_string(image, lang='eng')
                        
                        if ocr_text.strip():
                            text_content += ocr_text + "\n"
                            logger.info(f"Page {page_num + 1}: OCR extraction successful")
                        else:
                            logger.warning(f"Page {page_num + 1}: OCR extraction failed")
                            
                except Exception as e:
                    logger.error(f"Error processing page {page_num + 1}: {e}")
                    continue
            
            pdf_document.close()
            
            if text_content.strip():
                logger.info(f"Successfully extracted {len(text_content)} characters using OCR from {pdf_path}")
                return text_content.strip()
            else:
                logger.warning(f"No text content extracted using OCR from {pdf_path}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to extract text using OCR from {pdf_path}: {e}")
            return None
    
    def is_image_based_pdf(self, pdf_path: Path) -> bool:
        """
        Check if a PDF is image-based (scanned document).
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            True if PDF appears to be image-based, False otherwise
        """
        try:
            pdf_document = fitz.open(pdf_path)
            
            # Check first few pages
            pages_to_check = min(3, len(pdf_document))
            image_based_count = 0
            
            for page_num in range(pages_to_check):
                page = pdf_document[page_num]
                
                # Get text content
                text_content = page.get_text().strip()
                
                # Get images
                image_list = page.get_images()
                
                # If page has very little text but has images, it's likely image-based
                if len(text_content) < 50 and len(image_list) > 0:
                    image_based_count += 1
            
            pdf_document.close()
            
            # If most pages are image-based, consider the whole PDF as image-based
            is_image_based = image_based_count >= pages_to_check * 0.7
            
            logger.info(f"PDF {pdf_path.name}: {image_based_count}/{pages_to_check} pages appear image-based")
            return is_image_based
            
        except Exception as e:
            logger.error(f"Error checking if PDF is image-based: {e}")
            return False
    
    def process_failed_pdfs(self, failed_pdf_paths: List[Path]) -> List[dict]:
        """
        Process PDFs that failed regular text extraction using OCR.
        
        Args:
            failed_pdf_paths: List of paths to PDFs that failed regular extraction
            
        Returns:
            List of dictionaries containing file info and extracted text
        """
        processed_files = []
        
        for pdf_path in failed_pdf_paths:
            logger.info(f"Processing failed PDF with OCR: {pdf_path.name}")
            
            # Check if it's likely an image-based PDF
            if self.is_image_based_pdf(pdf_path):
                text_content = self.extract_text_with_ocr(pdf_path)
                
                file_info = {
                    'filename': pdf_path.name,
                    'filepath': str(pdf_path),
                    'text_content': text_content,
                    'processed_successfully': text_content is not None,
                    'extraction_method': 'OCR',
                    'file_size': pdf_path.stat().st_size
                }
            else:
                # If it's not image-based, mark as failed
                text_content = None
                file_info = {
                    'filename': pdf_path.name,
                    'filepath': str(pdf_path),
                    'text_content': None,
                    'processed_successfully': False,
                    'extraction_method': 'OCR_ATTEMPTED',
                    'file_size': pdf_path.stat().st_size,
                    'error': 'Not an image-based PDF'
                }
            
            processed_files.append(file_info)
            
            if text_content:
                logger.info(f"Successfully processed with OCR: {pdf_path.name}")
            else:
                logger.error(f"Failed to process with OCR: {pdf_path.name}")
        
        return processed_files
    
    def get_ocr_capable_files(self, pdf_paths: List[Path]) -> List[Path]:
        """
        Identify PDFs that are likely to benefit from OCR processing.
        
        Args:
            pdf_paths: List of PDF file paths
            
        Returns:
            List of PDFs that appear to be image-based
        """
        ocr_candidates = []
        
        for pdf_path in pdf_paths:
            if self.is_image_based_pdf(pdf_path):
                ocr_candidates.append(pdf_path)
        
        logger.info(f"Found {len(ocr_candidates)} OCR candidates out of {len(pdf_paths)} PDFs")
        return ocr_candidates
class EnhancedOCRProcessor:
    """OCR with confidence scoring and multi-pass extraction"""
    
    def extract_with_confidence(self, pdf_path: str) -> dict:
        """
        3-pass extraction strategy from TASK_SPECIFICATIONS.md
        
        Returns:
            {
                "data": {...},
                "confidence_metadata": {...},
                "requires_review": bool,
                "flagged_fields": [...]
            }
        """
        # Pass 1: Standard PDF extraction
        result = self._extract_text(pdf_path)
        confidence = self._calculate_confidence(result)
        
        # Pass 2: OCR if confidence low
        if confidence < 0.5:
            result = self._ocr_fallback(pdf_path)
            confidence = self._calculate_confidence(result)
        
        # Pass 3: Enhanced OCR with preprocessing
        if confidence < 0.7:
            result = self._enhanced_ocr(pdf_path)
            confidence = self._calculate_confidence(result)
        
        return {
            "data": result,
            "confidence_metadata": {
                "overall_confidence": confidence,
                "field_confidence": self._field_confidence(result)
            },
            "requires_review": confidence < 0.8,
            "flagged_fields": self._get_low_confidence_fields(result)
        }
    
    def _calculate_confidence(self, data: dict) -> float:
        """Calculate overall confidence score"""
        scores = []
        
        # Critical fields must be present
        if data.get('student_name'): scores.append(1.0)
        else: scores.append(0.0)
        
        if data.get('roll_number'): scores.append(1.0)
        else: scores.append(0.0)
        
        # CGPA validation
        cgpa = data.get('cgpa', -1)
        if 0 <= cgpa <= 10: scores.append(0.9)
        elif cgpa == -1: scores.append(0.3)
        else: scores.append(0.0)
        
        # Email validation
        email = data.get('email', '')
        if '@' in email and '.' in email: scores.append(0.9)
        elif email == '': scores.append(0.5)
        else: scores.append(0.2)
        
        return sum(scores) / len(scores) if scores else 0.0
