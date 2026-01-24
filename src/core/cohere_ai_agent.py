"""
Cohere AI Agent for Academic Data Querying
Improved implementation with proper document context
"""
import cohere
import pandas as pd
import json
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger
from config.settings import COHERE_API_KEY, COHERE_MODEL


class CohereAIAgent:
    """AI Agent that uses Cohere to answer questions about academic data"""
    
    def __init__(self):
        """Initialize Cohere client"""
        if not COHERE_API_KEY:
            raise ValueError("COHERE_API_KEY not set in environment variables")
        
        self.client = cohere.Client(COHERE_API_KEY)
        self.model = COHERE_MODEL or "command"
        logger.info(f"✓ Cohere AI Agent initialized with model: {self.model}")
    
    def _prepare_context(self, df: pd.DataFrame, batch_name: str = None) -> str:
        """
        Prepare comprehensive context from DataFrame
        
        Args:
            df: Student data DataFrame
            batch_name: Name of the batch
            
        Returns:
            Formatted context string for Cohere
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
        
        # CGPA distribution
        cgpa_dist = {
            '9.0-10.0': len(cgpa_values[(cgpa_values >= 9.0) & (cgpa_values <= 10.0)]) if len(cgpa_values) > 0 else 0,
            '8.0-8.9': len(cgpa_values[(cgpa_values >= 8.0) & (cgpa_values < 9.0)]) if len(cgpa_values) > 0 else 0,
            '7.0-7.9': len(cgpa_values[(cgpa_values >= 7.0) & (cgpa_values < 8.0)]) if len(cgpa_values) > 0 else 0,
            '6.0-6.9': len(cgpa_values[(cgpa_values >= 6.0) & (cgpa_values < 7.0)]) if len(cgpa_values) > 0 else 0,
            'Below 6.0': len(cgpa_values[cgpa_values < 6.0]) if len(cgpa_values) > 0 else 0
        }
        
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
        
        # Department-wise averages
        dept_avg = {}
        if 'Department' in df.columns and 'CGPA' in df.columns:
            dept_groups = df.groupby('Department')['CGPA']
            for dept, values in dept_groups:
                numeric_values = pd.to_numeric(values, errors='coerce').dropna()
                if len(numeric_values) > 0:
                    dept_avg[dept] = round(numeric_values.mean(), 2)
        
        # Build comprehensive context
        context = f"""You are an intelligent academic data analyst for the University of Hyderabad.

==================================================
DATASET INFORMATION
==================================================
Batch: {batch_name or 'Current Academic Data'}
Total Students: {total_students}
Data Source: Processed PDF documents containing grade sheets and academic records

==================================================
CGPA STATISTICS
==================================================
Average CGPA: {avg_cgpa}
Highest CGPA: {max_cgpa}
Lowest CGPA: {min_cgpa}

CGPA Distribution Across All Students:
{json.dumps(cgpa_dist, indent=2)}

==================================================
DEPARTMENT BREAKDOWN
==================================================
Total Departments: {len(dept_counts)}

Student Count by Department:
{json.dumps(dept_counts, indent=2)}

Average CGPA by Department:
{json.dumps(dept_avg, indent=2)}

==================================================
TOP 10 PERFORMING STUDENTS
==================================================
{json.dumps(top_students_list, indent=2)}

==================================================
SAMPLE DATA (First 10 Students)
==================================================
{df.head(10).to_string()}

==================================================
AVAILABLE DATA COLUMNS
==================================================
{list(df.columns)}

==================================================
INSTRUCTIONS FOR ANSWERING
==================================================
1. Answer ONLY based on the data provided above
2. Be specific - cite actual numbers, names, and percentages
3. When mentioning students, include their names and roll numbers
4. If asked about specific students/departments, search the data carefully
5. If the data doesn't contain information to answer, say so clearly
6. Format numbers properly (e.g., CGPA to 2 decimal places)
7. Be conversational but professional
8. Provide context when giving statistics
9. If comparing data, show clear comparisons
10. Keep answers concise but informative (2-4 sentences for simple queries, more for complex)

"""
        return context
    
    def query(
        self, 
        question: str, 
        df: pd.DataFrame, 
        batch_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query the academic data using Cohere AI
        
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

==================================================
USER QUESTION
==================================================
{question}

==================================================
YOUR ANSWER
==================================================
(Provide a clear, data-driven answer based on the information above)
"""
            
            logger.info(f"Querying Cohere with: {question[:100]}...")
            
            # Get response from Cohere using Chat API (generate was removed)
            try:
                response = self.client.chat(
                    model=self.model,
                    message=question,
                    preamble=context,
                    max_tokens=1000,
                    temperature=0.3,
                )
            except Exception as cohere_error:
                logger.error(f"Cohere API call failed: {type(cohere_error).__name__}: {str(cohere_error)}")
                raise Exception(f"Cohere API error: {str(cohere_error)}")
            
            answer = response.text.strip()
            
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
                "model": self.model,
                "provider": "cohere"
            }
            
            logger.info(f"✓ Generated response: {len(answer)} chars")
            return result
            
        except Exception as e:
            logger.error(f"Cohere query error: {e}", exc_info=True)
            return {
                "error": str(e),
                "response": f"I apologize, but I encountered an error while processing your query: {str(e)}. Please try rephrasing your question or contact support if the issue persists.",
                "timestamp": datetime.now().isoformat(),
                "query": question
            }
    
    def health_check(self) -> bool:
        """Check if Cohere is accessible"""
        try:
            test_response = self.client.chat(
                model=self.model,
                message="Say 'OK' if you can read this.",
                max_tokens=10
            )
            return bool(test_response.text)
        except Exception as e:
            logger.error(f"Cohere health check failed: {e}")
            return False


# Convenience function for backward compatibility
def query_academic_data_with_cohere(
    question: str, 
    df: pd.DataFrame, 
    batch_name: str = None
) -> Dict[str, Any]:
    """
    Legacy function - creates agent and queries
    
    Args:
        question: User's question
        df: DataFrame with student data
        batch_name: Name of the batch
        
    Returns:
        Response dictionary
    """
    agent = CohereAIAgent()
    return agent.query(question, df, batch_name)
