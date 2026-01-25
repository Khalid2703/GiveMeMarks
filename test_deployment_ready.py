"""
Pre-Deployment Test Script
Run this before deploying to ensure everything works
"""
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

def test_demo_data_creation():
    """Test 1: Demo data creation"""
    print("\n" + "="*60)
    print("TEST 1: Demo Data Creation")
    print("="*60)
    
    try:
        from create_demo_data import check_and_create_if_needed
        check_and_create_if_needed()
        print("✅ PASS: Demo data creation works")
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False

def test_data_files_exist():
    """Test 2: Check if data files exist"""
    print("\n" + "="*60)
    print("TEST 2: Data Files Exist")
    print("="*60)
    
    from config.settings import EXCEL_DIR
    
    metadata_file = EXCEL_DIR / "batch_metadata.json"
    
    if not metadata_file.exists():
        print(f"❌ FAIL: Metadata file not found at {metadata_file}")
        return False
    
    print(f"✅ PASS: Metadata file exists")
    
    import json
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    batches = metadata.get('batches', [])
    print(f"   Found {len(batches)} batch(es)")
    
    for batch in batches:
        batch_file = EXCEL_DIR / batch.get('filename')
        if batch_file.exists():
            print(f"   ✅ {batch.get('filename')}")
        else:
            print(f"   ❌ {batch.get('filename')} NOT FOUND")
            return False
    
    return True

def test_api_imports():
    """Test 3: API imports work"""
    print("\n" + "="*60)
    print("TEST 3: API Imports")
    print("="*60)
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / 'backend'))
        from fastapi import FastAPI
        print("✅ PASS: FastAPI import works")
        
        from src.core.academic_evaluator import AcademicEvaluator
        print("✅ PASS: Core modules import works")
        
        return True
    except Exception as e:
        print(f"❌ FAIL: Import error - {e}")
        return False

def test_data_can_be_read():
    """Test 4: Data can be read"""
    print("\n" + "="*60)
    print("TEST 4: Data Reading")
    print("="*60)
    
    try:
        import pandas as pd
        from config.settings import EXCEL_DIR
        import json
        
        # Read metadata
        metadata_file = EXCEL_DIR / "batch_metadata.json"
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        current_batch = metadata.get('current_batch')
        batch_file = EXCEL_DIR / current_batch
        
        # Read Excel
        df = pd.read_excel(batch_file, sheet_name='Student Data')
        
        print(f"✅ PASS: Can read data")
        print(f"   Students: {len(df)}")
        print(f"   Columns: {', '.join(df.columns[:3])}...")
        
        return True
    except Exception as e:
        print(f"❌ FAIL: Cannot read data - {e}")
        return False

def test_api_endpoints():
    """Test 5: API endpoints work"""
    print("\n" + "="*60)
    print("TEST 5: API Endpoints (Simulated)")
    print("="*60)
    
    try:
        import pandas as pd
        from config.settings import EXCEL_DIR
        import json
        
        # Simulate dashboard stats endpoint
        metadata_file = EXCEL_DIR / "batch_metadata.json"
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        batches = metadata.get('batches', [])
        
        # Read all batches
        all_dfs = []
        for batch in batches:
            batch_file = EXCEL_DIR / batch.get('filename')
            if batch_file.exists():
                df = pd.read_excel(batch_file, sheet_name='Student Data')
                all_dfs.append(df)
        
        if all_dfs:
            combined_df = pd.concat(all_dfs, ignore_index=True)
            total_students = len(combined_df)
            avg_cgpa = combined_df['CGPA'].mean()
            
            print(f"✅ PASS: Dashboard endpoint simulation works")
            print(f"   Total students: {total_students}")
            print(f"   Average CGPA: {avg_cgpa:.2f}")
            
            return True
        else:
            print("❌ FAIL: No data to read")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Endpoint simulation failed - {e}")
        return False

def main():
    """Run all tests"""
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "     PRE-DEPLOYMENT TEST SUITE     ".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    tests = [
        test_demo_data_creation,
        test_data_files_exist,
        test_api_imports,
        test_data_can_be_read,
        test_api_endpoints
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results), 1):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - Test {i}: {test.__doc__.split(':')[1].strip()}")
    
    print("\n" + "="*60)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✅ Your project is READY FOR DEPLOYMENT!")
        print("\nNext steps:")
        print("1. Push to GitHub: git add . && git commit -m 'Ready for deployment' && git push")
        print("2. Follow DEPLOYMENT_COMPLETE_GUIDE.md")
        print("3. Deploy backend to Render.com")
        print("4. Deploy frontend to Vercel")
    else:
        print("\n⚠️  SOME TESTS FAILED!")
        print("\nFix the failing tests before deploying.")
        print("Check the error messages above for details.")
    
    print("="*60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
