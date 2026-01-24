"""
Cohere AI Query Handler for Academic Data Analysis
Provides intelligent question-answering over processed student data
"""
import json
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

try:
    import cohere
    COHERE_AVAILABLE = True
except ImportError:
    COHERE_AVAILABLE = False
    logger.warning("cohere not installed. Install with: pip install cohere")

from config.settings import COHERE_API_KEY, COHERE_MODEL


class CohereQueryHandler:
    """
    Handles AI-powered queries over academic data using Cohere
    Optimized for question-answering over student records
    """
    
    def __init__(self):
        """Initialize Cohere client"""
        if not COHERE_AVAILABLE:
            raise ImportError("Cohere SDK not installed. Run: pip install cohere")
        
        if not COHERE_API_KEY:
            raise ValueError("COHERE_API_KEY not set in .env file")
        
        try:
            self.client = cohere.Client(COHERE_API_KEY)
            self.model = COHERE_MODEL or "command"
            logger.info(f"✓ Cohere Query Handler initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize Cohere: {e}")
            raise
    
    def query(
        self, 
        question: str, 
        context_data: pd.DataFrame,
        batch_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Answer a question about the academic data
        
        Args:
            question: User's question about the data
            context_data: DataFrame containing student records
            batch_name: Optional batch identifier
            
        Returns:
            Dictionary with answer, metadata, and context stats
        """
        try:
            logger.info(f"Processing query: '{question}' over {len(context_data)} records")
            
            # Build comprehensive context
            context = self._build_context(context_data, batch_name)
            
            # Create the prompt
            prompt = self._create_prompt(question, context)
            
            # Get response from Cohere
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                max_tokens=1000,
                temperature=0.3,  # Lower temperature for factual responses
                stop_sequences=["---END---"]
            )
            
            answer = response.generations[0].text.strip()
            
            # Calculate context statistics
            context_stats = self._calculate_stats(context_data)
            
            result = {
                "response": answer,
                "timestamp": datetime.now().isoformat(),
                "query": question,
                "batch_used": batch_name or "all_data",
                "context_stats": context_stats,
                "model": self.model,
                "provider": "cohere"
            }
            
            logger.info(f"✓ Query answered successfully using Cohere")
            return result
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}", exc_info=True)
            return {
                "error": str(e),
                "response": f"Sorry, I encountered an error while processing your question: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "query": question
            }
    
    def _build_context(self, df: pd.DataFrame, batch_name: Optional[str]) -> str:
        """
        Build comprehensive context string from DataFrame
        
        Args:
            df: Student data DataFrame
            batch_name: Optional batch identifier
            
        Returns:
            Formatted context string for the LLM
        """
        total_students = len(df)
        
        # Calculate statistics
        cgpa_stats = {}
        if 'CGPA' in df.columns:
            cgpa_values = pd.to_numeric(df['CGPA'], errors='coerce').dropna()
            if len(cgpa_values) > 0:
                cgpa_stats = {
                    'average': round(cgpa_values.mean(), 2),
                    'highest': round(cgpa_values.max(), 2),
                    'lowest': round(cgpa_values.min(), 2),
                    'median': round(cgpa_values.median(), 2)
                }
        
        # Department distribution
        dept_dist = {}
        if 'Department' in df.columns:
            dept_dist = df['Department'].value_counts().to_dict()
        
        # Top performers
        top_students = []
        if 'CGPA' in df.columns and 'Student Name' in df.columns:
            top_df = df.nlargest(5, 'CGPA')
            top_students = top_df[['Student Name', 'Roll Number', 'CGPA', 'Department']].to_dict('records')
        
        # CGPA distribution
        cgpa_distribution = {}
        if 'CGPA' in df.columns:
            cgpa_values = pd.to_numeric(df['CGPA'], errors='coerce').dropna()
            cgpa_distribution = {
                '9.0-10.0': len(cgpa_values[(cgpa_values >= 9.0) & (cgpa_values <= 10.0)]),
                '8.0-8.9': len(cgpa_values[(cgpa_values >= 8.0) & (cgpa_values < 9.0)]),
                '7.0-7.9': len(cgpa_values[(cgpa_values >= 7.0) & (cgpa_values < 8.0)]),
                '6.0-6.9': len(cgpa_values[(cgpa_values >= 6.0) & (cgpa_values < 7.0)]),
                'Below 6.0': len(cgpa_values[cgpa_values < 6.0])
            }
        
        # Build context string
        context = f"""Academic Data Context:

Batch: {batch_name or 'All Data'}
Total Students: {total_students}

CGPA Statistics:
{json.dumps(cgpa_stats, indent=2)}

CGPA Distribution:
{json.dumps(cgpa_distribution, indent=2)}

Department Distribution:
{json.dumps(dept_dist, indent=2)}

Top 5 Performers:
{json.dumps(top_students, indent=2)}

Sample Student Records (first 10):
{df.head(10).to_string()}
"""
        
        return context
    
    def _create_prompt(self, question: str, context: str) -> str:
        """
        Create a well-structured prompt for Cohere
        
        Args:
            question: User's question
            context: Data context string
            
        Returns:
            Complete prompt for the LLM
        """
        prompt = f"""You are an academic data analyst assistant for the University of Hyderabad Academic Evaluation System.

Your role is to answer questions about student performance, academic trends, and statistics based on the provided data.

INSTRUCTIONS:
- Answer questions accurately using ONLY the data provided below
- Be specific and include actual numbers from the data
- If asked about students, mention names and roll numbers when relevant
- If asked about statistics, provide exact figures
- If the data doesn't contain information to answer the question, say so clearly
- Keep answers concise but informative
- Use professional academic language

{context}

Question: {question}

Answer (be specific and cite actual data):"""
        
        return prompt
    
    def _calculate_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate summary statistics for response metadata
        
        Args:
            df: Student data DataFrame
            
        Returns:
            Dictionary of statistics
        """
        stats = {
            "total_students": len(df),
            "avg_cgpa": 0,
            "departments": 0
        }
        
        if 'CGPA' in df.columns:
            cgpa_values = pd.to_numeric(df['CGPA'], errors='coerce').dropna()
            if len(cgpa_values) > 0:
                stats["avg_cgpa"] = round(cgpa_values.mean(), 2)
        
        if 'Department' in df.columns:
            stats["departments"] = df['Department'].nunique()
        
        return stats
    
    def validate_connection(self) -> bool:
        """
        Test connection to Cohere API
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.client.generate(
                model=self.model,
                prompt="Test connection",
                max_tokens=5
            )
            return bool(response.generations[0].text)
        except Exception as e:
            logger.error(f"Cohere connection validation failed: {e}")
            return False


# Convenience function for quick queries
def query_academic_data(
    question: str,
    data: pd.DataFrame,
    batch_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Quick function to query academic data
    
    Args:
        question: Question about the data
        data: DataFrame with student records
        batch_name: Optional batch identifier
        
    Returns:
        Response dictionary
    """
    handler = CohereQueryHandler()
    return handler.query(question, data, batch_name)
