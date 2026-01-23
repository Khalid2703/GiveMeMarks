"""
Dashboard Analytics Logic
Implements 3 essential charts from TASK_SPECIFICATIONS.md
"""
from typing import List, Dict
import json

class DashboardAnalytics:
    """Generate analytics data for faculty dashboard"""
    
    @staticmethod
    def calculate_cgpa_distribution(students: List[dict]) -> dict:
        """
        CHART 1: CGPA Distribution Histogram
        
        Returns:
            {"0-4": count, "4-5": count, ..., "9-10": count}
        """
        ranges = {
            "0-4": 0, "4-5": 0, "5-6": 0, "6-7": 0,
            "7-8": 0, "8-9": 0, "9-10": 0
        }
        
        for student in students:
            cgpa = float(student.get('cgpa', -1))
            if cgpa < 0: continue
            
            if cgpa < 4: ranges["0-4"] += 1
            elif cgpa < 5: ranges["4-5"] += 1
            elif cgpa < 6: ranges["5-6"] += 1
            elif cgpa < 7: ranges["6-7"] += 1
            elif cgpa < 8: ranges["7-8"] += 1
            elif cgpa < 9: ranges["8-9"] += 1
            else: ranges["9-10"] += 1
        
        return ranges
    
    @staticmethod
    def calculate_subject_averages(students: List[dict]) -> dict:
        """
        CHART 2: Subject-Wise Performance
        
        Returns:
            {
                "CS301": {
                    "name": "Data Structures",
                    "average": 7.85,
                    "count": 45,
                    "difficulty": "Moderate"
                },
                ...
            }
        """
        course_data = {}
        
        for student in students:
            for course in student.get('courses', []):
                code = course['course_code']
                grade_points = DashboardAnalytics._grade_to_points(
                    course['grade']
                )
                
                if code not in course_data:
                    course_data[code] = {
                        "name": course.get('course_name', code),
                        "total": 0,
                        "count": 0
                    }
                
                course_data[code]["total"] += grade_points
                course_data[code]["count"] += 1
        
        # Calculate averages and difficulty
        for code, data in course_data.items():
            avg = data["total"] / data["count"]
            data["average"] = round(avg, 2)
            
            # Determine difficulty
            if avg >= 8:
                data["difficulty"] = "Easy"
            elif avg >= 6.5:
                data["difficulty"] = "Moderate"
            else:
                data["difficulty"] = "Difficult"
        
        return course_data
    
    @staticmethod
    def identify_at_risk_students(students: List[dict]) -> List[dict]:
        """
        CHART 3: At-Risk Students Dashboard
        
        Returns:
            [
                {
                    "name": "...",
                    "roll": "...",
                    "risks": [...],
                    "priority": "High/Medium/Low",
                    "score": int
                },
                ...
            ]
        """
        at_risk = []
        
        for student in students:
            risk_factors = []
            priority_score = 0
            
            # CGPA check
            cgpa = float(student.get('cgpa', 10))
            if cgpa < 6.0:
                risk_factors.append(f"Low CGPA: {cgpa}")
                priority_score += 3
            
            # Attendance check
            attendance = float(student.get('attendance_percentage', 100))
            if attendance < 75:
                risk_factors.append(f"Low Attendance: {attendance}%")
                priority_score += 2
            
            # Backlogs check
            backlogs = int(student.get('backlogs_count', 0))
            if backlogs >= 3:
                risk_factors.append(f"Multiple Backlogs: {backlogs}")
                priority_score += 3
            
            # Only add if there are risk factors
            if risk_factors:
                priority = "High" if priority_score >= 4 else \
                          "Medium" if priority_score >= 2 else "Low"
                
                at_risk.append({
                    "name": student['student_name'],
                    "roll": student['roll_number'],
                    "dept": student['department'],
                    "cgpa": cgpa,
                    "attendance": attendance,
                    "risks": risk_factors,
                    "priority": priority,
                    "score": priority_score
                })
        
        # Sort by priority score (descending)
        at_risk.sort(key=lambda x: x['score'], reverse=True)
        
        return at_risk
    
    @staticmethod
    def _grade_to_points(grade: str) -> float:
        """Convert letter grade to grade points"""
        grade_map = {
            "A+": 10, "A": 9, "B+": 8, "B": 7,
            "C": 6, "D": 5, "F": 0, "I": 0, "W": 0, "N/A": 0
        }
        return grade_map.get(grade, 0)
