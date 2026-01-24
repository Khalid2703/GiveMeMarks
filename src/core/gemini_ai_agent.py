"""
Gemini AI Agent for Academic Data Querying
Replaces Cohere which deprecated all models
"""
import google.generativeai as genai
import pandas as pd
import json
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger
from config.settings import GEMINI_API_KEY, GEMINI_MODEL


class GeminiAIAgent:
    """AI Agent that uses Gemini to answer questions about academic data"""
    
    def __init__(self):
        """Initialize Gemini client"""
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set in environment variables")
        
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        logger.info(f"✓ Gemini AI Agent initialized with model: {GEMINI_MODEL}")
    
    def _prepare_context(self, df: pd.DataFrame, batch_name: str = None) -> str:
        """
        Prepare comprehensive context from DataFrame
        
        Args:
            df: Student data DataFrame
            batch_name: Name of the batch
            
        Returns:
            Formatted context string for Gemini
        """
        # Basic stats
        total_students = len(df)
        
        # CGPA statistics
        cgpa_col = df.get('CGPA')
        if cgpa_col is not None:
            cgpa_values = pd.to_numeric(cgpa_col, errors='coerce').dropna()
            avg_cgpa = round(cgpa_values.mean(), 2) if len(cgpa_values) > 0 else 0
            max_cgpa = round(cgpa_values.max(), 2) if len(cgpa_values) > 0 else 0
            min_cgpa = round(cgpa_values.min(), 2) if len(cgpa_values) > 0 else 0
        else:
            avg_cgpa = max_cgpa = min_cgpa = 0
            cgpa_values = pd.Series([])
        
        # Department distribution
        dept_counts = {}
        if 'Department' in df.columns:
            dept_counts = df['Department'].value_counts().to_dict()
        
        # Department-wise averages
        dept_avg = {}
        if 'Department' in df.columns and 'CGPA' in df.columns:
            dept_groups = df.groupby('Department')['CGPA']
            for dept, values in dept_groups:
                numeric_values = pd.to_numeric(values, errors='coerce').dropna()
                if len(numeric_values) > 0:
                    dept_avg[dept] = round(numeric_values.mean(), 2)
        
        # Top performers
        top_students_list = []
        if 'CGPA' in df.columns and 'Student Name' in df.columns:
            top_df = df.nlargest(10, 'CGPA')
            for idx, row in top_df.iterrows():
                student_info = {
                    'name': str(row.get('Student Name', 'N/A')),
                    'roll_number': str(row.get('Roll Number', 'N/A')),
                    'cgpa': round(float(row.get('CGPA', 0)), 2) if pd.notna(row.get('CGPA')) else 0,
                    'department': str(row.get('Department', 'N/A'))
                }
                top_students_list.append(student_info)
        
        # Build comprehensive context
        context = f"""You are an intelligent academic data analyst for the University of Hyderabad.

DATASET INFORMATION:
- Batch: {batch_name or 'Current Academic Data'}
- Total Students: {total_students}

CGPA STATISTICS:
- Average CGPA: {avg_cgpa}
- Highest CGPA: {max_cgpa}
- Lowest CGPA: {min_cgpa}

DEPARTMENT BREAKDOWN:
Student Count by Department:
{json.dumps(dept_counts, indent=2)}

Average CGPA by Department:
{json.dumps(dept_avg, indent=2)}

TOP PERFORMERS:
{json.dumps(top_students_list, indent=2)}

COMPLETE STUDENT DATA:
{df.to_string()}

INSTRUCTIONS:
1. Answer ONLY based on the COMPLETE STUDENT DATA table above
2. Be specific with numbers, names, and percentages
3. Calculate averages from the actual CGPA values in the table
4. Include roll numbers when mentioning students
5. If CGPA column shows 0 or NaN, mention that data quality issue
6. Format numbers properly (CGPA to 2 decimal places)
7. Be conversational but professional
8. Keep answers concise (2-4 sentences for simple queries)
"""
        return context
    
    def query(
        self, 
        question: str, 
        df: pd.DataFrame, 
        batch_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query the academic data using Gemini AI
        
        Args:
            question: User's question
            df: Student data DataFrame
            batch_name: Name of the batch
            
        Returns:
            Response dictionary with answer and metadata
        """
        try:
            # Prepare context from data
            context = self._prepare_context(df, batch_name)
            
            # Build the full prompt
            prompt = f"""{context}

USER QUESTION: {question}

Provide a clear, data-driven answer based on the information above:"""
            
            logger.info(f"Querying Gemini with: {question[:100]}...")
            
            # Get response from Gemini
            try:
                response = self.model.generate_content(prompt)
                answer = response.text.strip()
            except Exception as gemini_error:
                logger.error(f"Gemini API call failed: {type(gemini_error).__name__}: {str(gemini_error)}")
                raise Exception(f"Gemini API error: {str(gemini_error)}")
            
            # Calculate context stats
            cgpa_values = pd.to_numeric(df['CGPA'], errors='coerce').dropna()
            avg_cgpa = round(cgpa_values.mean(), 2) if len(cgpa_values) > 0 else 0
            dept_count = len(df['Department'].unique()) if 'Department' in df.columns else 0
            
            result = {
                "response": answer,
                "timestamp": datetime.now().isoformat(),
                "query": question,
                "batch_used": batch_name or "all_data",
                "context_stats": {
                    "total_students": len(df),
                    "avg_cgpa": avg_cgpa,
                    "departments": dept_count
                },
                "model": GEMINI_MODEL,
                "provider": "gemini"
            }
            
            logger.info(f"✓ Generated response: {len(answer)} chars")
            return result
            
        except Exception as e:
            logger.error(f"Gemini query error: {e}", exc_info=True)
            return {
                "error": str(e),
                "response": f"I apologize, but I encountered an error while processing your query: {str(e)}. Please try rephrasing your question.",
                "timestamp": datetime.now().isoformat(),
                "query": question
            }
    
    def health_check(self) -> bool:
        """Check if Gemini is accessible"""
        try:
            test_response = self.model.generate_content("Say 'OK' if you can read this.")
            return bool(test_response.text)
        except Exception as e:
            logger.error(f"Gemini health check failed: {e}")
            return False
