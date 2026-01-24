"""
Academic Alerts Generator
Rule-based system for generating faculty action items
"""
import pandas as pd
from typing import List, Dict, Any
from loguru import logger


class AcademicAlertsGenerator:
    """Generate academic alerts and recommendations for faculty"""
    
    @staticmethod
    def generate_alerts(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Generate alerts from student data
        
        Args:
            df: Student data DataFrame
            
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        try:
            # Alert 1: Students with low CGPA
            alerts.extend(AcademicAlertsGenerator._check_low_cgpa(df))
            
            # Alert 2: Missing data/incomplete records
            alerts.extend(AcademicAlertsGenerator._check_incomplete_records(df))
            
            # Alert 3: Department performance variance
            alerts.extend(AcademicAlertsGenerator._check_department_variance(df))
            
            # Alert 4: Top performers recognition
            alerts.extend(AcademicAlertsGenerator._check_top_performers(df))
            
            # Alert 5: At-risk students
            alerts.extend(AcademicAlertsGenerator._check_at_risk_students(df))
            
            logger.info(f"Generated {len(alerts)} academic alerts")
            return alerts
            
        except Exception as e:
            logger.error(f"Error generating alerts: {e}")
            return []
    
    @staticmethod
    def _check_low_cgpa(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Alert for students with CGPA below threshold"""
        alerts = []
        
        if 'CGPA' not in df.columns:
            return alerts
        
        cgpa_values = pd.to_numeric(df['CGPA'], errors='coerce')
        low_cgpa_students = df[cgpa_values < 6.0]
        
        if len(low_cgpa_students) > 0:
            student_names = low_cgpa_students['Student Name'].tolist()[:3]
            alerts.append({
                'type': 'warning',
                'severity': 'high',
                'title': 'Low CGPA Alert',
                'description': f'{len(low_cgpa_students)} student(s) with CGPA below 6.0 need academic support',
                'details': f"Students: {', '.join([str(s) for s in student_names])}" + 
                          (f" and {len(low_cgpa_students) - 3} more" if len(low_cgpa_students) > 3 else ""),
                'action': 'Schedule counseling sessions',
                'count': len(low_cgpa_students)
            })
        
        return alerts
    
    @staticmethod
    def _check_incomplete_records(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Alert for incomplete or missing data"""
        alerts = []
        
        # Check for missing CGPA
        missing_cgpa = df[df['CGPA'].isna() | (pd.to_numeric(df['CGPA'], errors='coerce') == 0)]
        if len(missing_cgpa) > 0:
            alerts.append({
                'type': 'info',
                'severity': 'medium',
                'title': 'Incomplete Records',
                'description': f'{len(missing_cgpa)} student(s) have missing or invalid CGPA data',
                'details': 'Data quality issue - verify grade sheets',
                'action': 'Review and update student records',
                'count': len(missing_cgpa)
            })
        
        # Check for missing department
        missing_dept = df[df['Department'].isna() | (df['Department'] == '')]
        if len(missing_dept) > 0:
            alerts.append({
                'type': 'info',
                'severity': 'low',
                'title': 'Missing Department Info',
                'description': f'{len(missing_dept)} student(s) without department assignment',
                'details': 'Administrative update required',
                'action': 'Assign students to departments',
                'count': len(missing_dept)
            })
        
        return alerts
    
    @staticmethod
    def _check_department_variance(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Alert for departments with high CGPA variance"""
        alerts = []
        
        if 'Department' not in df.columns or 'CGPA' not in df.columns:
            return alerts
        
        df_clean = df[pd.to_numeric(df['CGPA'], errors='coerce') > 0].copy()
        df_clean['CGPA_numeric'] = pd.to_numeric(df_clean['CGPA'], errors='coerce')
        
        if len(df_clean) == 0:
            return alerts
        
        dept_stats = df_clean.groupby('Department')['CGPA_numeric'].agg(['mean', 'std', 'count'])
        
        # Alert for departments with high variance (std > 1.5)
        high_variance = dept_stats[dept_stats['std'] > 1.5]
        
        if len(high_variance) > 0:
            dept_list = high_variance.index.tolist()
            alerts.append({
                'type': 'warning',
                'severity': 'medium',
                'title': 'High CGPA Variance',
                'description': f'{len(high_variance)} department(s) show inconsistent student performance',
                'details': f"Departments: {', '.join(dept_list)}",
                'action': 'Review curriculum and teaching methods',
                'count': len(high_variance)
            })
        
        # Alert for departments with low average CGPA
        low_avg = dept_stats[dept_stats['mean'] < 7.0]
        if len(low_avg) > 0:
            dept_list = low_avg.index.tolist()
            alerts.append({
                'type': 'warning',
                'severity': 'high',
                'title': 'Department Below Expected Performance',
                'description': f'{len(low_avg)} department(s) with average CGPA below 7.0',
                'details': f"Departments: {', '.join(dept_list)}",
                'action': 'Investigate and provide departmental support',
                'count': len(low_avg)
            })
        
        return alerts
    
    @staticmethod
    def _check_top_performers(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Recognition alert for top performers"""
        alerts = []
        
        if 'CGPA' not in df.columns:
            return alerts
        
        df_clean = df[pd.to_numeric(df['CGPA'], errors='coerce') > 0].copy()
        df_clean['CGPA_numeric'] = pd.to_numeric(df_clean['CGPA'], errors='coerce')
        
        top_performers = df_clean[df_clean['CGPA_numeric'] >= 9.0]
        
        if len(top_performers) > 0:
            student_names = top_performers['Student Name'].tolist()[:5]
            alerts.append({
                'type': 'success',
                'severity': 'low',
                'title': 'Outstanding Performance',
                'description': f'{len(top_performers)} student(s) achieved CGPA ≥ 9.0',
                'details': f"Recognition candidates: {', '.join([str(s) for s in student_names])}" +
                          (f" and {len(top_performers) - 5} more" if len(top_performers) > 5 else ""),
                'action': 'Consider for awards and scholarships',
                'count': len(top_performers)
            })
        
        return alerts
    
    @staticmethod
    def _check_at_risk_students(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Alert for at-risk students (CGPA between 6.0-7.0)"""
        alerts = []
        
        if 'CGPA' not in df.columns:
            return alerts
        
        cgpa_values = pd.to_numeric(df['CGPA'], errors='coerce')
        at_risk = df[(cgpa_values >= 6.0) & (cgpa_values < 7.0)]
        
        if len(at_risk) > 0:
            alerts.append({
                'type': 'warning',
                'severity': 'medium',
                'title': 'At-Risk Students',
                'description': f'{len(at_risk)} student(s) with CGPA 6.0-7.0 may need additional support',
                'details': 'Early intervention recommended',
                'action': 'Provide tutoring and mentorship',
                'count': len(at_risk)
            })
        
        return alerts
