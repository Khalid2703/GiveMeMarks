"""
Convert sample .txt documents to PDFs for demo
"""
import os
from pathlib import Path

print("""
╔═══════════════════════════════════════════════════════════════╗
║         SAMPLE DOCUMENTS - TEXT TO PDF CONVERTER             ║
╚═══════════════════════════════════════════════════════════════╝

This script helps you convert the sample .txt files to PDFs for
a more realistic demo.

METHOD 1: Using Microsoft Word (Recommended)
─────────────────────────────────────────────────────────────────
1. Open each .txt file in Microsoft Word
2. The text will auto-format nicely
3. File → Save As → PDF
4. Save in sample_documents folder

METHOD 2: Using Google Docs (Online)
─────────────────────────────────────────────────────────────────
1. Upload .txt file to Google Drive
2. Right-click → Open with → Google Docs
3. File → Download → PDF Document
4. Save in sample_documents folder

METHOD 3: Using Online Converter (Quick)
─────────────────────────────────────────────────────────────────
1. Visit: https://txt2pdf.com or https://www.online-convert.com
2. Upload the .txt file
3. Click Convert
4. Download the PDF

METHOD 4: Keep as .txt files (Also Works!)
─────────────────────────────────────────────────────────────────
Your system can process .txt files too! PDFs just look more
professional in demos.

═══════════════════════════════════════════════════════════════

Current Sample Documents:
""")

sample_dir = Path("C:/Users/hp/UOH_Hackathon/sample_documents")

if sample_dir.exists():
    txt_files = list(sample_dir.glob("*.txt"))
    txt_files = [f for f in txt_files if not f.name.startswith("README")]
    
    print(f"Found {len(txt_files)} sample documents:\n")
    
    for i, file in enumerate(txt_files, 1):
        size_kb = file.stat().st_size / 1024
        print(f"{i}. {file.name}")
        print(f"   Size: {size_kb:.1f} KB")
        print()
    
    print("═══════════════════════════════════════════════════════════════")
    print("\n✅ All sample documents are ready to use!")
    print("✅ You can use them as .txt files OR convert to PDF")
    print("✅ Either format works with your system\n")
else:
    print("❌ Sample documents folder not found!")
    print(f"Expected location: {sample_dir}")

print("""
QUICK START:
────────────────────────────────────────────────────────────────
1. Open http://localhost:3000 in browser
2. Click "Upload Documents" area
3. Select one or more sample files
4. Click "Process Documents"
5. Wait 5-10 seconds per document
6. View extracted data in results table!

For best presentation demo:
• Convert to PDF for professional look (optional)
• Start with Sample_1 (simplest)
• Then try Sample_4 or Sample_6 (complex)
• Show the Excel export at the end
────────────────────────────────────────────────────────────────
""")

input("Press Enter to close...")
