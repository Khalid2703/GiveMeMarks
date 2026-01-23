"""
Academic Document Analyzer with Dual LLM Provider (Gemini + Cohere fallback).
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
    """Academic document analyzer with Gemini primary + Cohere fallback."""
    
    def __init__(self):
        """Initialize dual LLM provider with quota tracking."""
        self.gemini_client = None
        self.cohere_client = None
        self.gemini_available = False
        self.cohere_available = False
        self.current_provider = None
        self.quota_exceeded = False
        
        # Quota tracking
        self.gemini_calls = 5
        self.cohere_calls = 5
        
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
        
        logger.info(f"LLM Analyzer initialized. Primary: {self.current_provider}")
    
    def _call_gemini(self, prompt: str) -> tuple[str, Dict[str, Any]]:
        """Call Gemini API with retry and quota handling."""
        try:
            generation_config = {
                "temperature": LLM_TEMPERATURE,
                "max_output_tokens": LLM_MAX_TOKENS,
            }
            
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            response_text = response.text
            
            metadata = {
                "provider": "gemini",
                "model": GEMINI_MODEL,
                "total_tokens": getattr(response, 'total_token_count', None),
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
        """Call Cohere API."""
        try:
            response = self.cohere_client.generate(
                model=COHERE_MODEL,
                prompt=prompt,
                max_tokens=LLM_MAX_TOKENS,
                temperature=LLM_TEMPERATURE,
            )
            
            response_text = response.generations[0].text
            
            metadata = {
                "provider": "cohere",
                "model": COHERE_MODEL,
                "total_tokens": None,
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
        """Analyze an academic document with automatic provider failover."""
        try:
            logger.info("Starting academic document analysis")
            prompt = custom_prompt or ACADEMIC_ANALYSIS_PROMPT.format(
                document_text=document_text
            )
            
            response_text = None
            metadata = {}
            
            # Try Gemini first
            if self.gemini_available and not self.quota_exceeded:
                try:
                    response_text, metadata = self._call_gemini(prompt)
                except ValueError as e:
                    if "QUOTA_EXCEEDED" in str(e):
                        logger.warning("Gemini quota exceeded, switching to Cohere")
            
            # Fallback to Cohere
            if response_text is None and self.cohere_available:
                logger.info("Using Cohere API")
                response_text, metadata = self._call_cohere(prompt)
            
            if response_text is None:
                raise RuntimeError("All LLM providers failed")
            
            # Parse response
            cleaned = _clean_model_output(response_text)
            
            try:
                parsed = json.loads(cleaned)
                
                parsed.setdefault('_metadata', {})
                parsed['_metadata'].update({
                    **metadata,
                    'analysis_timestamp': datetime.now().isoformat(),
                    'error': False,
                })
                
                logger.info(f"Successfully parsed response (provider: {metadata.get('provider')})")
                return parsed
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {e}")
                return self._create_parse_error_response(str(e), response_text, metadata)
        
        except Exception as ex:
            logger.exception(f"Unexpected error: {ex}")
            return self._create_error_response(str(ex))
    
    def _create_parse_error_response(
        self, 
        error_msg: str, 
        raw_response: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create standardized parse error response."""
        return {
            'Student Name': 'Parse Error',
            'Roll Number': 'Parse Error',
            'Email': 'Parse Error',
            'Phone': 'Parse Error',
            'Department': 'Parse Error',
            'Program': 'Parse Error',
            'Semester': 'Parse Error',
            'CGPA': 'Parse Error',
            'Academic Year': 'Parse Error',
            '_metadata': {
                **metadata,
                'error': True,
                'error_type': 'parse_error',
                'error_message': f"Failed to parse: {error_msg}",
                'raw_response': raw_response[:500],
            }
        }
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
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
                'provider': self.current_provider or 'unknown',
                'model': 'unknown',
                'tokens_used': 0,
                'error': True,
                'error_type': 'system_error',
                'error_message': error_message,
            }
        }
    
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
                response = self.cohere_client.generate(
                    model=COHERE_MODEL, prompt="Test", max_tokens=5
                )
                results['cohere'] = bool(response.generations[0].text)
                logger.info("✓ Cohere validated")
            except Exception as e:
                logger.error(f"Cohere validation failed: {e}")
        
        return results
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get current provider status."""
        return {
            'current_provider': self.current_provider,
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
