"""
Academic Document Analyzer with Dual LLM Provider (Gemini + Cohere fallback).
UPDATED: Simplified robust prompt for presentation demo
"""
import json
import os
import re
from typing import Dict, Optional, Any
from loguru import logger
from datetime import datetime

# Import both SDKs
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai not installed. Install with: pip install google-generativeai")

try:
    import cohere
    COHERE_AVAILABLE = True
except ImportError:
    COHERE_AVAILABLE = False
    logger.warning("cohere not installed. Install with: pip install cohere")

from config.settings import (
    GEMINI_API_KEY,
    COHERE_API_KEY,
    GEMINI_MODEL,
    COHERE_MODEL,
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
    ACADEMIC_ANALYSIS_PROMPT,
)


def _clean_model_output(text: str) -> str:
    """Clean common wrappers around LLM output for JSON parsing."""
    if not isinstance(text, str):
        return text

    s = text.strip()

    # Remove triple backtick fence blocks
    m = re.search(r"```(?:\w+)?\s*([\s\S]*?)\s*```", s)
    if m:
        s = m.group(1).strip()

    # Remove single backticks
    if s.startswith("`") and s.endswith("`"):
        s = s[1:-1].strip()

    # Extract JSON if embedded in prose
    if not s.startswith("{") and not s.startswith("["):
        first_obj = s.find("{")
        last_obj = s.rfind("}")
        if first_obj != -1 and last_obj != -1 and last_obj > first_obj:
            s = s[first_obj:last_obj + 1]

    return s


class AcademicLLMAnalyzer:
    """Academic document analyzer with Gemini primary + Cohere fallback.
    
    UPDATED: Simplified for reliable demo performance
    """
    
    def __init__(self):
        """Initialize dual LLM provider with quota tracking."""
        self.gemini_client = None
        self.cohere_client = None
        self.gemini_available = False
        self.cohere_available = False
        self.current_provider = None
        self.quota_exceeded = False
        
        # Quota tracking
        self.gemini_calls = 0
        self.cohere_calls = 0
        
        # Initialize Gemini
        if GEMINI_AVAILABLE and GEMINI_API_KEY:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel(GEMINI_MODEL)
                self.gemini_available = True
                self.current_provider = "gemini"
                logger.info(f"✓ Gemini API initialized: {GEMINI_MODEL}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
        
        # Initialize Cohere
        if COHERE_AVAILABLE and COHERE_API_KEY:
            try:
                self.cohere_client = cohere.Client(COHERE_API_KEY)
                self.cohere_available = True
                logger.info(f"✓ Cohere API initialized: {COHERE_MODEL}")
            except Exception as e:
                logger.error(f"Failed to initialize Cohere: {e}")
        
        if not self.gemini_available and not self.cohere_available:
            raise ValueError(
                "No LLM provider available. Install 'google-generativeai' or 'cohere' "
                "and configure API keys in .env file."
            )
        
        logger.info(f"✓ LLM Analyzer initialized with SIMPLIFIED DEMO PROMPT")
        logger.info(f"Primary provider: {self.current_provider}")
    
    def _get_production_prompt(self) -> str:
        """
        Get simplified robust prompt for demo.
        
        This prompt is designed to:
        - Extract basic student information reliably
        - Return valid JSON every time
        - Work with incomplete data
        - Be fast for presentations
        
        Returns:
            Complete system prompt for academic analysis
        """
        return """You are a data extraction assistant for academic documents. Your job is to extract student information from academic reports.

CRITICAL RULES:
1. Return ONLY valid JSON, nothing else
2. Use null for missing fields
3. DO NOT invent data
4. DO NOT add comments or explanations

Extract the following fields from the document:

Required Output Format (JSON only):
{
  "Student Name": "full name or null",
  "Roll Number": "roll number or null",
  "Email": "email or null",
  "Phone": "phone or null",
  "Department": "department or null",
  "Program": "program or null",
  "Semester": "semester or null",
  "Academic Year": "year or null",
  "CGPA": "cgpa value or null",
  "SGPA": "sgpa value or null",
  "Attendance Percentage": "attendance or null",
  "Date of Birth": "dob or null",
  "Gender": "gender or null",
  "Category": "category or null",
  "Awards and Honors": "awards or null",
  "Extracurricular Activities": "activities or null",
  "Remarks": "any remarks or null"
}

EXAMPLES:

Example 1 - Complete Data:
Document: "Anjali Sharma, Roll No: 21PH2034, Department: Physics, CGPA: 7.85"
Output:
{
  "Student Name": "Anjali Sharma",
  "Roll Number": "21PH2034",
  "Email": null,
  "Phone": null,
  "Department": "Physics",
  "Program": null,
  "Semester": null,
  "Academic Year": null,
  "CGPA": "7.85",
  "SGPA": null,
  "Attendance Percentage": null,
  "Date of Birth": null,
  "Gender": null,
  "Category": null,
  "Awards and Honors": null,
  "Extracurricular Activities": null,
  "Remarks": null
}

Example 2 - Minimal Data:
Document: "Student report for 2024"
Output:
{
  "Student Name": null,
  "Roll Number": null,
  "Email": null,
  "Phone": null,
  "Department": null,
  "Program": null,
  "Semester": null,
  "Academic Year": "2024",
  "CGPA": null,
  "SGPA": null,
  "Attendance Percentage": null,
  "Date of Birth": null,
  "Gender": null,
  "Category": null,
  "Awards and Honors": null,
  "Extracurricular Activities": null,
  "Remarks": null
}

REMEMBER:
- Return ONLY the JSON object
- Use null for missing data
- No markdown formatting
- No explanations
- No code blocks"""

    def _call_gemini(self, prompt: str) -> tuple[str, Dict[str, Any]]:
        """Call Gemini API with retry and quota handling."""
        try:
            generation_config = {
                "temperature": 0.1,  # Low temperature for consistency
                "max_output_tokens": LLM_MAX_TOKENS,
            }
            
            # Add safety settings to avoid blocking
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            # Check if response was blocked
            if not response.parts:
                logger.error("Gemini response was blocked by safety settings")
                raise ValueError("Response blocked by safety filter")
            
            response_text = response.text
            
            metadata = {
                "provider": "gemini",
                "model": GEMINI_MODEL,
                "total_tokens": getattr(response, 'total_token_count', None),
                "prompt_version": "simplified_demo_v1"
            }
            
            self.gemini_calls += 1
            logger.info(f"Gemini call successful (total: {self.gemini_calls})")
            
            return response_text, metadata
            
        except Exception as e:
            error_msg = str(e).lower()
            
            if "quota" in error_msg or "rate limit" in error_msg or "429" in error_msg:
                logger.warning(f"Gemini quota exceeded: {e}")
                self.quota_exceeded = True
                self.current_provider = "cohere" if self.cohere_available else None
                raise ValueError("QUOTA_EXCEEDED")
            
            logger.error(f"Gemini API error: {e}")
            raise
    
    def _call_cohere(self, prompt: str) -> tuple[str, Dict[str, Any]]:
        """Call Cohere API using Chat API."""
        try:
            response = self.cohere_client.chat(
                model=COHERE_MODEL,
                message=prompt,
                max_tokens=LLM_MAX_TOKENS,
                temperature=0.1,
            )
            
            response_text = response.text
            
            metadata = {
                "provider": "cohere",
                "model": COHERE_MODEL,
                "total_tokens": None,
                "prompt_version": "simplified_demo_v1"
            }
            
            self.cohere_calls += 1
            logger.info(f"Cohere call successful (total: {self.cohere_calls})")
            
            return response_text, metadata
            
        except Exception as e:
            logger.error(f"Cohere API error: {e}")
            raise
    
    def analyze_document(
        self, 
        document_text: str, 
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze an academic document with automatic provider failover.
        
        UPDATED: Simplified for demo reliability
        
        Args:
            document_text: Extracted text from academic document
            custom_prompt: Optional custom prompt (overrides production prompt)
            
        Returns:
            Structured analysis dict with student data and insights
        """
        try:
            logger.info("Starting academic document analysis with SIMPLIFIED PROMPT")
            
            # Use simplified prompt for demo
            if custom_prompt:
                full_prompt = custom_prompt
                logger.info("Using custom prompt")
            else:
                system_prompt = self._get_production_prompt()
                user_message = f"\n\nDocument text:\n\n{document_text}\n\nExtract the student information and return ONLY the JSON object:"
                full_prompt = system_prompt + user_message
                logger.info("Using SIMPLIFIED demo prompt for reliability")
            
            response_text = None
            metadata = {}
            
            # Try Gemini first
            if self.gemini_available and not self.quota_exceeded:
                try:
                    response_text, metadata = self._call_gemini(full_prompt)
                except ValueError as e:
                    if "QUOTA_EXCEEDED" in str(e):
                        logger.warning("Gemini quota exceeded, switching to Cohere")
            
            # Fallback to Cohere
            if response_text is None and self.cohere_available:
                logger.info("Using Cohere API (Gemini unavailable or quota exceeded)")
                response_text, metadata = self._call_cohere(full_prompt)
            
            if response_text is None:
                raise RuntimeError("All LLM providers failed")
            
            # Parse response with multiple attempts
            cleaned = _clean_model_output(response_text)
            
            # Log the cleaned response for debugging
            logger.info(f"Cleaned response preview: {cleaned[:200]}...")
            
            parsed = None
            parse_error = None
            
            # Attempt 1: Direct parsing
            try:
                parsed = json.loads(cleaned)
            except json.JSONDecodeError as e1:
                parse_error = e1
                logger.warning(f"Attempt 1 failed: {e1}")
                
                # Attempt 2: Try to fix common JSON issues
                try:
                    # Replace single quotes with double quotes
                    fixed = cleaned.replace("'", '"')
                    # Remove trailing commas
                    fixed = re.sub(r',\s*}', '}', fixed)
                    fixed = re.sub(r',\s*]', ']', fixed)
                    parsed = json.loads(fixed)
                    logger.info("Attempt 2 succeeded with fixes")
                except json.JSONDecodeError as e2:
                    logger.warning(f"Attempt 2 failed: {e2}")
                    
                    # Attempt 3: Extract key-value pairs manually
                    try:
                        logger.info("Attempting manual extraction from text...")
                        parsed = self._manual_extract(cleaned)
                        if parsed:
                            logger.info("Attempt 3 succeeded with manual extraction")
                    except Exception as e3:
                        logger.warning(f"Attempt 3 failed: {e3}")
                        parse_error = e2  # Use error from attempt 2
            
            if parsed:
                
                # Convert nulls to empty strings for Excel compatibility
                for key in parsed:
                    if parsed[key] is None:
                        parsed[key] = ''
                
                # Add metadata
                parsed.setdefault('_metadata', {})
                parsed['_metadata'].update({
                    **metadata,
                    'analysis_timestamp': datetime.now().isoformat(),
                    'error': False,
                })
                
                logger.info(f"✓ Successfully parsed response (provider: {metadata.get('provider')})")
                logger.info(f"✓ Extracted: {parsed.get('Student Name', 'N/A')} - {parsed.get('Roll Number', 'N/A')}")
                return parsed
            else:
                # All parsing attempts failed
                logger.error(f"All parsing attempts failed: {parse_error}")
                logger.error(f"Raw response: {response_text[:500]}")
                logger.error(f"Cleaned response: {cleaned[:500]}")
                return self._create_parse_error_response(str(parse_error), response_text, metadata)
        
        except Exception as ex:
            logger.exception(f"Unexpected error: {ex}")
            return self._create_error_response(str(ex))
    
    def _manual_extract(self, text: str) -> Optional[Dict[str, Any]]:
        """Manually extract student information from text as last resort."""
        try:
            result = {
                'Student Name': '',
                'Roll Number': '',
                'Email': '',
                'Phone': '',
                'Department': '',
                'Program': '',
                'Semester': '',
                'Academic Year': '',
                'CGPA': '',
                'SGPA': '',
                'Attendance Percentage': '',
                'Date of Birth': '',
                'Gender': '',
                'Category': '',
                'Awards and Honors': '',
                'Extracurricular Activities': '',
                'Remarks': 'Extracted via manual parsing'
            }
            
            # Extract patterns
            patterns = {
                'Student Name': r'(?:Student Name|Name)\s*[:"]\s*([^,"\n]+)',
                'Roll Number': r'(?:Roll Number|Roll No|Roll)\s*[:"]\s*([^,"\n]+)',
                'Email': r'(?:Email)\s*[:"]\s*([^,"\n]+)',
                'Department': r'(?:Department)\s*[:"]\s*([^,"\n]+)',
                'CGPA': r'(?:CGPA)\s*[:"]\s*([0-9.]+)',
            }
            
            for field, pattern in patterns.items():
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    result[field] = match.group(1).strip()
            
            # Only return if we found at least one key field
            if result.get('Student Name') or result.get('Roll Number'):
                logger.info(f"Manual extraction found: {result.get('Student Name')} - {result.get('Roll Number')}")
                return result
            
            return None
        except Exception as e:
            logger.error(f"Manual extraction failed: {e}")
            return None
    
    def _create_parse_error_response(
        self, 
        error_msg: str, 
        raw_response: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create standardized parse error response."""
        logger.error(f"Parse error - returning None to skip document: {error_msg}")
        # Return None to signal this document should be skipped
        # instead of storing "Parse Error" in Excel
        return None
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create standardized error response."""
        logger.error(f"System error - returning None to skip document: {error_message}")
        # Return None to signal this document should be skipped
        return None
    
    def validate_api_connection(self) -> Dict[str, bool]:
        """Test connections to both LLM providers."""
        results = {'gemini': False, 'cohere': False}
        
        if self.gemini_available:
            try:
                response = self.gemini_model.generate_content("Test")
                results['gemini'] = bool(response.text)
                logger.info("✓ Gemini validated")
            except Exception as e:
                logger.error(f"Gemini validation failed: {e}")
        
        if self.cohere_available:
            try:
                response = self.cohere_client.chat(
                    model=COHERE_MODEL, message="Test", max_tokens=5
                )
                results['cohere'] = bool(response.text)
                logger.info("✓ Cohere validated")
            except Exception as e:
                logger.error(f"Cohere validation failed: {e}")
        
        return results
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get current provider status."""
        return {
            'current_provider': self.current_provider,
            'prompt_version': 'simplified_demo_v1',
            'gemini': {
                'available': self.gemini_available,
                'quota_exceeded': self.quota_exceeded,
                'calls_made': self.gemini_calls,
            },
            'cohere': {
                'available': self.cohere_available,
                'calls_made': self.cohere_calls,
            },
        }
