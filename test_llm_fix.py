"""
Quick test to verify LLM parsing is working
"""
from src.core.academic_llm_analyzer import AcademicLLMAnalyzer

# Sample document text
sample_text = """
Academic Evaluation Report – Semester V

Student Information:
Name: Anjali Sharma
Roll Number: 21PH2034
Email: anjali.sharma@uohyd.ac.in
Department: Physics
Program: B.Sc. (Honors)
Semester: V
Academic Year: 2024-25

Academic Performance:
CGPA: 7.85
SGPA (Semester V): 8.12
Attendance: 82.5%

Courses Completed:
1. PH301 - Quantum Mechanics I - Grade: A - Credits: 4
2. MA201 - Mathematical Physics - Grade: C - Credits: 3
3. PH302 - Statistical Mechanics - Grade: B+ - Credits: 4
"""

print("Initializing analyzer...")
analyzer = AcademicLLMAnalyzer()

print("\nAnalyzing document...")
result = analyzer.analyze_document(sample_text)

print("\n" + "="*60)
print("ANALYSIS RESULT:")
print("="*60)

import json
print(json.dumps(result, indent=2))

print("\n" + "="*60)
print("KEY FIELDS EXTRACTED:")
print("="*60)
print(f"Student Name: {result.get('Student Name')}")
print(f"Roll Number: {result.get('Roll Number')}")
print(f"Department: {result.get('Department')}")
print(f"CGPA: {result.get('CGPA')}")
print(f"Email: {result.get('Email')}")

if result.get('_metadata', {}).get('error'):
    print("\n⚠️  ERROR DETECTED!")
    print(f"Error: {result['_metadata'].get('error_message')}")
else:
    print("\n✅ SUCCESS! Data extracted properly")
