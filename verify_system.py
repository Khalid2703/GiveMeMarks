#!/usr/bin/env python3
"""
UOH Academic System - File Verification Script
Checks if all critical files exist and are valid
"""
import os
import sys

def check_file(path, min_size_kb=None, file_type=None):
    """Check if file exists and meets requirements"""
    if not os.path.exists(path):
        return False, f"❌ MISSING: {path}"
    
    size_kb = os.path.getsize(path) / 1024
    
    if min_size_kb and size_kb < min_size_kb:
        return False, f"⚠️  TOO SMALL ({size_kb:.1f}KB): {path} (expected >{min_size_kb}KB)"
    
    return True, f"✅ OK ({size_kb:.1f}KB): {path}"

def main():
    print("=" * 70)
    print("🔍 UOH ACADEMIC SYSTEM - FILE VERIFICATION")
    print("=" * 70)
    print()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    checks = [
        # Frontend Files
        ("Frontend - Main App", "frontend/src/App.jsx", 20),
        ("Frontend - Enhanced App", "frontend/src/App_Enhanced.jsx", 20),
        ("Frontend - Main Entry", "frontend/src/main.jsx", 0.2),
        ("Frontend - Package", "frontend/package.json", 0.5),
        ("Frontend - Index HTML", "frontend/index.html", 0.3),
        ("Frontend - CSS", "frontend/src/index.css", 0.1),
        
        # Backend Files
        ("Backend - API Server", "backend/api.py", 5),
        ("Backend - Requirements", "backend/requirements.txt", 0.1),
        ("Core - Document Processor", "src/core/document_processor.py", 1),
        ("Core - LLM Client", "src/core/llm_client.py", 1),
        ("Core - FutureHouse Client", "src/core/futurehouse_client.py", 0.5),
        
        # Documentation
        ("Documentation - Fixes Applied", "FIXES_APPLIED.md", 2),
        ("Documentation - Context", "CONTEXT_FOR_NEXT_SESSION.md", 3),
        ("Documentation - README", "README.md", 1),
    ]
    
    all_ok = True
    
    for name, rel_path, min_kb in checks:
        full_path = os.path.join(base_dir, rel_path)
        ok, message = check_file(full_path, min_kb)
        print(message)
        if not ok:
            all_ok = False
    
    print()
    print("=" * 70)
    
    # Check data directory
    data_excel_dir = os.path.join(base_dir, "data", "excel")
    if os.path.exists(data_excel_dir):
        excel_files = [f for f in os.listdir(data_excel_dir) if f.endswith('.xlsx')]
        print(f"✅ Data Files: {len(excel_files)} batch Excel files found")
    else:
        print("⚠️  Data directory not found")
        all_ok = False
    
    print("=" * 70)
    print()
    
    if all_ok:
        print("🎉 ALL CHECKS PASSED!")
        print()
        print("Next steps:")
        print("  1. cd backend && python api.py")
        print("  2. cd frontend && npm run dev")
        print("  3. Open http://localhost:3000")
        return 0
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("Please review the issues above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
