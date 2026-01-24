"""
Debug script to find invalid CGPA values in Excel files
"""
import pandas as pd
import numpy as np
from pathlib import Path
import json

# Path to excel directory
EXCEL_DIR = Path("C:/Users/hp/UOH_Hackathon/data/excel")

# Read batch metadata
with open(EXCEL_DIR / "batch_metadata.json", 'r') as f:
    metadata = json.load(f)

print("="*60)
print("CHECKING ALL BATCH FILES FOR INVALID CGPA VALUES")
print("="*60)

all_issues = []

for batch in metadata['batches']:
    filename = batch['filename']
    filepath = EXCEL_DIR / filename
    
    if not filepath.exists():
        print(f"\n❌ File not found: {filename}")
        continue
    
    print(f"\n📄 Checking: {filename}")
    
    try:
        df = pd.read_excel(filepath, sheet_name='Student Data')
        print(f"   Total rows: {len(df)}")
        
        # Check each row
        for idx, row in df.iterrows():
            student_name = row.get('Student Name', 'Unknown')
            roll_number = row.get('Roll Number', 'Unknown')
            cgpa_raw = row.get('CGPA')
            
            # Check if CGPA is problematic
            is_problem = False
            problem_type = ""
            
            if pd.isna(cgpa_raw):
                is_problem = True
                problem_type = "NaN/Missing"
            else:
                try:
                    cgpa_float = float(cgpa_raw)
                    if np.isinf(cgpa_float):
                        is_problem = True
                        problem_type = "Infinity"
                    elif np.isnan(cgpa_float):
                        is_problem = True
                        problem_type = "NaN (after conversion)"
                except (ValueError, TypeError) as e:
                    is_problem = True
                    problem_type = f"Conversion Error: {type(e).__name__}"
            
            if is_problem:
                issue = {
                    'file': filename,
                    'row': idx + 2,  # +2 because Excel rows start at 1 and header is row 1
                    'student': student_name,
                    'roll': roll_number,
                    'cgpa_raw': str(cgpa_raw),
                    'problem': problem_type
                }
                all_issues.append(issue)
                print(f"   ⚠️  Row {idx+2}: {student_name} ({roll_number}) - CGPA: {cgpa_raw} - Problem: {problem_type}")
        
        if not any(issue['file'] == filename for issue in all_issues):
            print(f"   ✅ All CGPA values are valid")
            
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)

if all_issues:
    print(f"\n🚨 Found {len(all_issues)} problematic CGPA values:\n")
    for issue in all_issues:
        print(f"  • {issue['file']} - Row {issue['row']}")
        print(f"    Student: {issue['student']} ({issue['roll']})")
        print(f"    CGPA Value: {issue['cgpa_raw']}")
        print(f"    Problem: {issue['problem']}")
        print()
else:
    print("\n✅ No problematic CGPA values found!")
    print("   The issue might be elsewhere in the code.")

print("="*60)
