"""
PDF processing module for extracting text from academic documents.
"""
import os
from pathlib import Path
from typing import List, Optional
import PyPDF2
from loguru import logger


class PDFProcessor:
    """Handles PDF file processing and text extraction."""
    
    def __init__(self, pdf_directory: Path):
        """
        Initialize PDF processor.
        
        Args:
            pdf_directory: Path to directory containing PDF files
        """
        self.pdf_directory = Path(pdf_directory)
        self.pdf_directory.mkdir(exist_ok=True)
        logger.info(f"PDF Processor initialized with directory: {self.pdf_directory}")
    
    def get_pdf_files(self) -> List[Path]:
        """
        Get list of PDF files in the directory.
        
        Returns:
            List of Path objects for PDF files
        """
        pdf_files = list(self.pdf_directory.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files in {self.pdf_directory}")
        return pdf_files
    
    def extract_text_from_pdf(self, pdf_path: Path) -> Optional[str]:
        """
        Extract text content from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content or None if extraction fails
        """
        try:
            logger.info(f"Extracting text from: {pdf_path}")
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""
                
                # Extract text from all pages
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n"
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                        continue
                
                if text_content.strip():
                    logger.info(f"Successfully extracted {len(text_content)} characters from {pdf_path}")
                    return text_content.strip()
                else:
                    logger.warning(f"No text content extracted from {pdf_path}")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to extract text from {pdf_path}: {e}")
            return None
    
    def process_all_pdfs(self) -> List[dict]:
        """
        Process all PDF files in the directory and extract text.
        
        Returns:
            List of dictionaries containing file info and extracted text
        """
        pdf_files = self.get_pdf_files()
        processed_files = []
        
        for pdf_file in pdf_files:
            logger.info(f"Processing PDF: {pdf_file.name}")
            
            text_content = self.extract_text_from_pdf(pdf_file)
            
            file_info = {
                'filename': pdf_file.name,
                'filepath': str(pdf_file),
                'text_content': text_content,
                'processed_successfully': text_content is not None,
                'file_size': pdf_file.stat().st_size
            }
            
            processed_files.append(file_info)
            
            if text_content:
                logger.info(f"Successfully processed: {pdf_file.name}")
            else:
                logger.error(f"Failed to process: {pdf_file.name}")
        
        logger.info(f"Processed {len(processed_files)} PDF files")
        return processed_files
    
    def validate_pdf(self, pdf_path: Path) -> bool:
        """
        Validate if a file is a readable PDF.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            True if PDF is valid and readable, False otherwise
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                # Try to access the first page to validate
                if len(pdf_reader.pages) > 0:
                    return True
                else:
                    logger.warning(f"PDF has no pages: {pdf_path}")
                    return False
        except Exception as e:
            logger.error(f"Invalid PDF file: {pdf_path} - {e}")
            return False
    
    def get_pdf_info(self, pdf_path: Path) -> dict:
        """
        Get basic information about a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with PDF information
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                info = {
                    'filename': pdf_path.name,
                    'filepath': str(pdf_path),
                    'num_pages': len(pdf_reader.pages),
                    'file_size': pdf_path.stat().st_size,
                    'is_valid': True
                }
                
                # Try to get PDF metadata
                if pdf_reader.metadata:
                    info['title'] = pdf_reader.metadata.get('/Title', 'Unknown')
                    info['author'] = pdf_reader.metadata.get('/Author', 'Unknown')
                    info['creator'] = pdf_reader.metadata.get('/Creator', 'Unknown')
                
                return info
                
        except Exception as e:
            logger.error(f"Failed to get PDF info for {pdf_path}: {e}")
            return {
                'filename': pdf_path.name,
                'filepath': str(pdf_path),
                'num_pages': 0,
                'file_size': pdf_path.stat().st_size if pdf_path.exists() else 0,
                'is_valid': False,
                'error': str(e)
            }
