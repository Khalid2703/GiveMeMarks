"""
Debug script to find ALL invalid float values in the response
"""
import pandas as pd
import numpy as np
from pathlib import Path
import json
import math

# Path to excel directory
EXCEL_DIR = Path("C:/Users/hp/UOH_Hackathon/data/excel")

# Read batch metadata
with open(EXCEL_DIR / "batch_metadata.json", 'r') as f:
    metadata = json.load(f)

print("="*60)
print("CHECKING ALL FIELDS FOR INVALID FLOAT VALUES")
print("="*60)

all_issues = []

for batch in metadata['batches']:
    filename = batch['filename']
    filepath = EXCEL_DIR / filename
    
    if not filepath.exists():
        continue
    
    print(f"\n📄 Checking: {filename}")
    
    try:
        df = pd.read_excel(filepath, sheet_name='Student Data')
        
        # Check each row and each column
        for idx, row in df.iterrows():
            student_name = row.get('Student Name', 'Unknown')
            roll_number = row.get('Roll Number', 'Unknown')
            
            # Check ALL columns for invalid floats
            for col in df.columns:
                value = row.get(col)
                
                # Skip if not numeric type
                if not isinstance(value, (int, float, np.number)):
                    continue
                
                # Check for problematic values
                is_problem = False
                problem_type = ""
                
                if pd.isna(value):
                    is_problem = True
                    problem_type = "NaN"
                elif isinstance(value, float):
                    if math.isinf(value):
                        is_problem = True
                        problem_type = "Infinity"
                    elif math.isnan(value):
                        is_problem = True
                        problem_type = "NaN (float)"
                
                if is_problem:
                    issue = {
                        'file': filename,
                        'row': idx + 2,
                        'student': student_name,
                        'roll': roll_number,
                        'column': col,
                        'value': str(value),
                        'problem': problem_type
                    }
                    all_issues.append(issue)
                    print(f"   ⚠️  Row {idx+2}, Column '{col}': {value} - {problem_type}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "="*60)
print("SUMMARY - ALL INVALID FLOAT VALUES")
print("="*60)

if all_issues:
    print(f"\n🚨 Found {len(all_issues)} problematic values:\n")
    for issue in all_issues:
        print(f"  • {issue['file']} - Row {issue['row']}")
        print(f"    Student: {issue['student']} ({issue['roll']})")
        print(f"    Column: {issue['column']}")
        print(f"    Value: {issue['value']}")
        print(f"    Problem: {issue['problem']}")
        print()
else:
    print("\n✅ No problematic values found!")

print("="*60)
