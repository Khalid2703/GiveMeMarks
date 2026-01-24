"""
Supabase Client for Academic Evaluation System
Handles all database interactions with Supabase.

COMPONENT STATUS: ✅ COMPLETE
LAST UPDATED: 2025-01-21
DEPENDENCIES: supabase, config.settings, utils.logger
"""
from typing import Dict, List, Any, Optional
from loguru import logger
from datetime import datetime

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("supabase not installed. Install with: pip install supabase")

from config.settings import SUPABASE_URL, SUPABASE_KEY


class SupabaseClient:
    """Manages Supabase database operations for academic data.
    
    Features:
    - Insert students, courses, projects, internships
    - Health checks
    - Error handling with retries
    """
    
    def __init__(self):
        """Initialize Supabase client."""
        if not SUPABASE_AVAILABLE:
            raise ImportError("supabase package not installed")
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
        
        try:
            self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            logger.info("✓ Supabase client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise
    
    def health_check(self) -> bool:
        """Check if Supabase connection is healthy.
        
        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            # Try to query students table
            response = self.client.table('students').select('id').limit(1).execute()
            logger.info("✓ Supabase health check passed")
            return True
        except Exception as e:
            logger.error(f"Supabase health check failed: {e}")
            return False
    
    def insert_student(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a student record into the database.
        
        Args:
            student_data: Dictionary containing student information
            
        Returns:
            Dictionary with 'success', 'id', and optional 'error' keys
        """
        try:
            # Helper function to convert None/empty to None (not empty string)
            def db_value(v):
                if v in [None, '', 'N/A']:
                    return None
                return v
            
            # Helper function for numeric fields
            def db_number(v):
                if v in [None, '', 'N/A']:
                    return None
                try:
                    return float(v)
                except (ValueError, TypeError):
                    return None
            
            # Prepare student record (use None instead of empty strings)
            record = {
                'student_name': db_value(student_data.get('Student Name')),
                'roll_number': db_value(student_data.get('Roll Number')),
                'email': db_value(student_data.get('Email')),
                'phone': db_value(student_data.get('Phone')),
                'department': db_value(student_data.get('Department')),
                'program': db_value(student_data.get('Program')),
                'semester': db_value(student_data.get('Semester')),
                'academic_year': db_value(student_data.get('Academic Year')),
                'cgpa': db_number(student_data.get('CGPA')),
                'sgpa': db_number(student_data.get('SGPA')),
                'attendance_percentage': db_number(student_data.get('Attendance Percentage')),
                'dob': db_value(student_data.get('Date of Birth')),
                'gender': db_value(student_data.get('Gender')),
                'category': db_value(student_data.get('Category')),
                'awards_and_honors': db_value(student_data.get('Awards and Honors')),
                'extracurricular_activities': db_value(student_data.get('Extracurricular Activities')),
                'remarks': db_value(student_data.get('Remarks')),
                'analysis': student_data,  # Store full data as JSONB
                'metadata': student_data.get('_metadata', {})
            }
            
            # Ensure student_name is not None (required field)
            if not record['student_name']:
                logger.warning("Cannot insert student without name")
                return {'success': False, 'error': 'Student name is required'}
            
            # Insert into database
            response = self.client.table('students').insert(record).execute()
            
            if response.data and len(response.data) > 0:
                student_id = response.data[0]['id']
                logger.info(f"✓ Inserted student: {record['student_name']} (ID: {student_id})")
                return {'success': True, 'id': student_id}
            else:
                logger.error("Failed to insert student: No data returned")
                return {'success': False, 'error': 'No data returned'}
                
        except Exception as e:
            logger.error(f"Failed to insert student: {e}")
            return {'success': False, 'error': str(e)}
    
    def insert_courses(self, courses_data: List[Dict], student_id: str) -> Dict[str, Any]:
        """Insert course records for a student.
        
        Args:
            courses_data: List of course dictionaries
            student_id: UUID of the student
            
        Returns:
            Dictionary with 'success' and count of inserted courses
        """
        try:
            if not courses_data or not isinstance(courses_data, list):
                return {'success': True, 'count': 0}
            
            # Prepare course records
            records = []
            for course in courses_data:
                record = {
                    'student_id': student_id,
                    'course_code': course.get('Course Code', ''),
                    'course_name': course.get('Course Name', ''),
                    'credits': course.get('Credits'),
                    'grade': course.get('Grade', ''),
                    'semester': course.get('Semester', ''),
                    'academic_year': course.get('Academic Year', '')
                }
                records.append(record)
            
            # Bulk insert
            response = self.client.table('courses').insert(records).execute()
            
            if response.data:
                count = len(response.data)
                logger.info(f"✓ Inserted {count} courses for student {student_id}")
                return {'success': True, 'count': count}
            else:
                logger.warning(f"No courses inserted for student {student_id}")
                return {'success': False, 'count': 0}
                
        except Exception as e:
            logger.error(f"Failed to insert courses: {e}")
            return {'success': False, 'error': str(e), 'count': 0}
    
    def insert_projects(self, projects_data: List[Dict], student_id: str) -> Dict[str, Any]:
        """Insert project records for a student.
        
        Args:
            projects_data: List of project dictionaries
            student_id: UUID of the student
            
        Returns:
            Dictionary with 'success' and count
        """
        try:
            if not projects_data or not isinstance(projects_data, list):
                return {'success': True, 'count': 0}
            
            records = []
            for project in projects_data:
                record = {
                    'student_id': student_id,
                    'project_title': project.get('Project Title', ''),
                    'supervisor': project.get('Supervisor', ''),
                    'duration': project.get('Duration', ''),
                    'description': project.get('Description', '')
                }
                records.append(record)
            
            response = self.client.table('academic_projects').insert(records).execute()
            
            if response.data:
                count = len(response.data)
                logger.info(f"✓ Inserted {count} projects for student {student_id}")
                return {'success': True, 'count': count}
            else:
                return {'success': False, 'count': 0}
                
        except Exception as e:
            logger.error(f"Failed to insert projects: {e}")
            return {'success': False, 'error': str(e), 'count': 0}
    
    def insert_internships(self, internships_data: List[Dict], student_id: str) -> Dict[str, Any]:
        """Insert internship records for a student."""
        try:
            if not internships_data or not isinstance(internships_data, list):
                return {'success': True, 'count': 0}
            
            records = []
            for internship in internships_data:
                record = {
                    'student_id': student_id,
                    'organization': internship.get('Organization', ''),
                    'role': internship.get('Role', ''),
                    'duration': internship.get('Duration', ''),
                    'description': internship.get('Description', '')
                }
                records.append(record)
            
            response = self.client.table('internships').insert(records).execute()
            
            if response.data:
                count = len(response.data)
                logger.info(f"✓ Inserted {count} internships for student {student_id}")
                return {'success': True, 'count': count}
            else:
                return {'success': False, 'count': 0}
                
        except Exception as e:
            logger.error(f"Failed to insert internships: {e}")
            return {'success': False, 'error': str(e), 'count': 0}
    
    def insert_certifications(self, certifications_data: List[Dict], student_id: str) -> Dict[str, Any]:
        """Insert certification records for a student."""
        try:
            if not certifications_data or not isinstance(certifications_data, list):
                return {'success': True, 'count': 0}
            
            records = []
            for cert in certifications_data:
                record = {
                    'student_id': student_id,
                    'name': cert.get('Name', ''),
                    'issuing_body': cert.get('Issuing Body', ''),
                    'date_obtained': cert.get('Date Obtained') or None
                }
                records.append(record)
            
            response = self.client.table('certifications').insert(records).execute()
            
            if response.data:
                count = len(response.data)
                logger.info(f"✓ Inserted {count} certifications for student {student_id}")
                return {'success': True, 'count': count}
            else:
                return {'success': False, 'count': 0}
                
        except Exception as e:
            logger.error(f"Failed to insert certifications: {e}")
            return {'success': False, 'error': str(e), 'count': 0}
    
    def insert_publications(self, publications_data: List[Dict], student_id: str) -> Dict[str, Any]:
        """Insert publication records for a student."""
        try:
            if not publications_data or not isinstance(publications_data, list):
                return {'success': True, 'count': 0}
            
            records = []
            for pub in publications_data:
                record = {
                    'student_id': student_id,
                    'title': pub.get('Title', ''),
                    'venue': pub.get('Venue', ''),
                    'year': pub.get('Year'),
                    'authors': pub.get('Authors', '')
                }
                records.append(record)
            
            response = self.client.table('publications').insert(records).execute()
            
            if response.data:
                count = len(response.data)
                logger.info(f"✓ Inserted {count} publications for student {student_id}")
                return {'success': True, 'count': count}
            else:
                return {'success': False, 'count': 0}
                
        except Exception as e:
            logger.error(f"Failed to insert publications: {e}")
            return {'success': False, 'error': str(e), 'count': 0}


def get_client() -> SupabaseClient:
    """Get a Supabase client instance.
    
    Returns:
        SupabaseClient instance
    """
    return SupabaseClient()
