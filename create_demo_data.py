"""
Create Sample/Demo Data for Deployment
Generates realistic academic data when batch_metadata.json doesn't exist
"""
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import EXCEL_DIR

def create_sample_students():
    """Create sample student data"""
    students = [
        {
            "Student Name": "Rahul Sharma",
            "Roll Number": "21CS1001",
            "Email": "rahul.sharma@uohyd.ac.in",
            "Department": "Computer Science",
            "Semester": "6",
            "CGPA": 8.5,
            "Attendance": 92.5,
            "Courses": "Data Structures, Algorithms, AI",
            "Status": "Active"
        },
        {
            "Student Name": "Priya Reddy",
            "Roll Number": "21EE1002",
            "Email": "priya.reddy@uohyd.ac.in",
            "Department": "Electrical Engineering",
            "Semester": "6",
            "CGPA": 9.2,
            "Attendance": 95.0,
            "Courses": "Power Systems, Control Systems",
            "Status": "Active"
        },
        {
            "Student Name": "Arjun Kumar",
            "Roll Number": "21ME1003",
            "Email": "arjun.kumar@uohyd.ac.in",
            "Department": "Mechanical Engineering",
            "Semester": "6",
            "CGPA": 7.8,
            "Attendance": 88.5,
            "Courses": "Thermodynamics, Fluid Mechanics",
            "Status": "Active"
        },
        {
            "Student Name": "Sneha Iyer",
            "Roll Number": "21CH1004",
            "Email": "sneha.iyer@uohyd.ac.in",
            "Department": "Chemistry",
            "Semester": "6",
            "CGPA": 8.9,
            "Attendance": 94.0,
            "Courses": "Organic Chemistry, Physical Chemistry",
            "Status": "Active"
        },
        {
            "Student Name": "Karthik Rao",
            "Roll Number": "21PH1005",
            "Email": "karthik.rao@uohyd.ac.in",
            "Department": "Physics",
            "Semester": "6",
            "CGPA": 8.3,
            "Attendance": 90.0,
            "Courses": "Quantum Mechanics, Electromagnetism",
            "Status": "Active"
        },
        {
            "Student Name": "Ananya Nair",
            "Roll Number": "21MA1006",
            "Email": "ananya.nair@uohyd.ac.in",
            "Department": "Mathematics",
            "Semester": "6",
            "CGPA": 9.5,
            "Attendance": 97.0,
            "Courses": "Linear Algebra, Real Analysis",
            "Status": "Active"
        }
    ]
    
    return pd.DataFrame(students)

def create_sample_batch():
    """Create a sample batch file with metadata"""
    
    # Ensure excel directory exists
    EXCEL_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create sample data
    df = create_sample_students()
    
    # Create batch filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_filename = f"demo_batch_{timestamp}.xlsx"
    batch_path = EXCEL_DIR / batch_filename
    
    # Save to Excel
    with pd.ExcelWriter(batch_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Student Data', index=False)
    
    print(f"✅ Created sample batch: {batch_filename}")
    print(f"   Location: {batch_path}")
    print(f"   Students: {len(df)}")
    
    # Create batch metadata
    metadata = {
        "batches": [
            {
                "filename": batch_filename,
                "created_at": datetime.now().isoformat(),
                "file_path": str(batch_path),
                "record_count": len(df)
            }
        ],
        "current_batch": batch_filename
    }
    
    # Save metadata
    metadata_path = EXCEL_DIR / "batch_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✅ Created batch metadata: batch_metadata.json")
    
    return batch_filename, len(df)

def check_and_create_if_needed():
    """Check if data exists, create if not"""
    metadata_path = EXCEL_DIR / "batch_metadata.json"
    
    # ALWAYS check if we have valid data, even if metadata exists
    has_valid_data = False
    
    if metadata_path.exists():
        print("✅ Batch metadata file exists")
        print(f"   Location: {metadata_path}")
        
        try:
            # Check if batch files actually exist
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            batches = metadata.get('batches', [])
            print(f"   Batches in metadata: {len(batches)}")
            
            valid_batches = 0
            for batch in batches:
                batch_file = EXCEL_DIR / batch.get('filename')
                if batch_file.exists():
                    print(f"   ✅ {batch.get('filename')} - {batch.get('record_count')} students")
                    valid_batches += 1
                else:
                    print(f"   ⚠️  {batch.get('filename')} - FILE MISSING!")
            
            if valid_batches > 0:
                has_valid_data = True
                print(f"   Found {valid_batches} valid batch file(s)")
            else:
                print("   ⚠️  No valid batch files found!")
        
        except Exception as e:
            print(f"   ⚠️  Error reading metadata: {e}")
            has_valid_data = False
    
    # If no valid data, create demo data
    if not has_valid_data:
        print("⚠️  No valid batch data found")
        print("   Creating demo data for deployment...")
        create_sample_batch()
        return True
    
    return False

if __name__ == "__main__":
    print("=" * 60)
    print("DEMO DATA GENERATOR FOR DEPLOYMENT")
    print("=" * 60)
    print()
    
    created = check_and_create_if_needed()
    
    print()
    print("=" * 60)
    if created:
        print("✅ DEMO DATA CREATED SUCCESSFULLY!")
        print()
        print("Your deployment will now have:")
        print("  • 6 sample students")
        print("  • Working dashboard")
        print("  • Working results search")
        print("  • Working AI query")
    else:
        print("✅ DATA ALREADY EXISTS - No action needed")
    
    print("=" * 60)
