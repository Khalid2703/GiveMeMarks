"""
Simple Cohere AI Query Handler for Academic Data
"""
import cohere
import json
import pandas as pd
from typing import Dict, Any
from datetime import datetime
from loguru import logger
from config.settings import COHERE_API_KEY, COHERE_MODEL


def query_academic_data_with_cohere(question: str, df: pd.DataFrame, batch_name: str = None) -> Dict[str, Any]:
    """
    Query academic data using Cohere AI
    
    Args:
        question: User's question
        df: DataFrame with student data
        batch_name: Name of the batch
        
    Returns:
        Response dictionary with answer and metadata
    """
    try:
        # Initialize Cohere
        client = cohere.Client(COHERE_API_KEY)
        
        # Calculate statistics
        total_students = len(df)
        cgpa_values = pd.to_numeric(df['CGPA'], errors='coerce').dropna()
        
        avg_cgpa = round(cgpa_values.mean(), 2) if len(cgpa_values) > 0 else 0
        max_cgpa = round(cgpa_values.max(), 2) if len(cgpa_values) > 0 else 0
        min_cgpa = round(cgpa_values.min(), 2) if len(cgpa_values) > 0 else 0
        
        # Department distribution
        dept_counts = df['Department'].value_counts().to_dict() if 'Department' in df.columns else {}
        
        # Top performers
        top_students = []
        if 'CGPA' in df.columns and 'Student Name' in df.columns:
            top_df = df.nlargest(5, 'CGPA')
            top_students = top_df[['Student Name', 'Roll Number', 'CGPA', 'Department']].to_dict('records')
        
        # CGPA distribution
        cgpa_dist = {
            '9.0-10.0': len(cgpa_values[(cgpa_values >= 9.0) & (cgpa_values <= 10.0)]),
            '8.0-8.9': len(cgpa_values[(cgpa_values >= 8.0) & (cgpa_values < 9.0)]),
            '7.0-7.9': len(cgpa_values[(cgpa_values >= 7.0) & (cgpa_values < 8.0)]),
            '6.0-6.9': len(cgpa_values[(cgpa_values >= 6.0) & (cgpa_values < 7.0)]),
            'Below 6.0': len(cgpa_values[cgpa_values < 6.0])
        }
        
        # Build context
        context = f"""You are an academic data analyst for University of Hyderabad.

DATA OVERVIEW:
Batch: {batch_name or 'Current Data'}
Total Students: {total_students}

CGPA STATISTICS:
- Average CGPA: {avg_cgpa}
- Highest CGPA: {max_cgpa}
- Lowest CGPA: {min_cgpa}

CGPA DISTRIBUTION:
{json.dumps(cgpa_dist, indent=2)}

DEPARTMENT BREAKDOWN:
{json.dumps(dept_counts, indent=2)}

TOP 5 PERFORMERS:
{json.dumps(top_students, indent=2)}

SAMPLE STUDENT DATA (First 10 Records):
{df.head(10).to_string()}

INSTRUCTIONS:
- Answer the question using ONLY the data provided above
- Be specific and cite actual numbers
- Mention student names/roll numbers when relevant
- If data is insufficient, say so clearly
- Keep answers concise but informative

QUESTION: {question}

ANSWER (be factual and data-driven):"""
        
        # Get response from Cohere
        response = client.generate(
            model=COHERE_MODEL or "command",
            prompt=context,
            max_tokens=800,
            temperature=0.3
        )
        
        answer = response.generations[0].text.strip()
        
        return {
            "response": answer,
            "timestamp": datetime.now().isoformat(),
            "query": question,
            "batch_used": batch_name or "all_data",
            "context_stats": {
                "total_students": total_students,
                "avg_cgpa": avg_cgpa,
                "departments": len(dept_counts)
            },
            "model": COHERE_MODEL or "command",
            "provider": "cohere"
        }
        
    except Exception as e:
        logger.error(f"Cohere query error: {e}", exc_info=True)
        return {
            "error": str(e),
            "response": f"Sorry, I encountered an error: {str(e)}. Please try again.",
            "timestamp": datetime.now().isoformat(),
            "query": question
        }
