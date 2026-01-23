"""
Quick validation script to check if environment is set up correctly.
"""
import sys
from pathlib import Path

print("🔍 Validating UOH Academic Evaluation System Setup...\n")

# Check Python version
print(f"✓ Python Version: {sys.version.split()[0]}")

# Check directories
print("\n📁 Checking Directories:")
dirs = [
    "config",
    "data/documents",
    "data/excel",
    "data/logs",
    "src/core",
    "src/ui",
    "src/utils",
    "db",
]
for d in dirs:
    path = Path(d)
    status = "✓" if path.exists() else "✗"
    print(f"  {status} {d}")

# Check critical files
print("\n📄 Checking Critical Files:")
files = [
    "config/settings.py",
    "src/core/pdf_processor.py",
    "src/core/ocr_processor.py",
    "src/core/academic_llm_analyzer.py",
    "src/utils/logger.py",
    "requirements.txt",
    ".env.example",
    "db/supabase_schema.sql",
]
for f in files:
    path = Path(f)
    status = "✓" if path.exists() else "✗"
    print(f"  {status} {f}")

# Check .env
print("\n🔐 Environment Configuration:")
env_file = Path(".env")
if env_file.exists():
    print("  ✓ .env file exists")
    # Check for API keys
    content = env_file.read_text()
    if "your_gemini_api_key_here" in content:
        print("  ⚠️  GEMINI_API_KEY not configured (still placeholder)")
    else:
        print("  ✓ GEMINI_API_KEY configured")
    
    if "your_cohere_api_key_here" in content:
        print("  ⚠️  COHERE_API_KEY not configured (still placeholder)")
    else:
        print("  ✓ COHERE_API_KEY configured")
else:
    print("  ✗ .env file missing - copy .env.example to .env")

# Check dependencies
print("\n📦 Checking Dependencies:")
dependencies = [
    ("google.generativeai", "Gemini SDK"),
    ("cohere", "Cohere SDK"),
    ("PyPDF2", "PDF Processing"),
    ("openpyxl", "Excel Support"),
    ("loguru", "Logging"),
    ("streamlit", "UI Framework"),
    ("fastapi", "API Framework"),
]

missing = []
for module, name in dependencies:
    try:
        __import__(module.split(".")[0])
        print(f"  ✓ {name}")
    except ImportError:
        print(f"  ✗ {name} - run: pip install -r requirements.txt")
        missing.append(name)

if missing:
    print(f"\n⚠️  Missing {len(missing)} dependencies. Run:")
    print("   pip install -r requirements.txt")

# Summary
print("\n" + "=" * 70)
print("📊 SUMMARY:")
if not missing and env_file.exists():
    print("   ✅ System is ready for configuration!")
    print("   Next: Add API keys to .env file")
else:
    print("   ⚠️  Setup incomplete. Follow steps above.")
print("=" * 70)
