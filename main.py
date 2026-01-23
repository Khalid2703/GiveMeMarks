"""
UOH Academic Evaluation & Reporting Assistant
Main Entry Point - CLI Application

COMPONENT STATUS: ✅ COMPLETE
LAST UPDATED: 2025-01-21
"""
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.academic_evaluator import AcademicEvaluator
from src.utils.logger import get_logger, log_system_event
from config.settings import DOCUMENT_DIR, EXCEL_DIR


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="UOH Academic Evaluation & Reporting Assistant"
    )
    parser.add_argument(
        "--mode",
        choices=["streamlit", "cli", "validate"],
        default="streamlit",
        help="Application mode"
    )
    parser.add_argument(
        "--document-dir",
        type=Path,
        default=DOCUMENT_DIR,
        help="Directory containing PDF documents"
    )
    parser.add_argument(
        "--batch-name",
        type=str,
        help="Custom batch name"
    )
    parser.add_argument(
        "--custom-prompt",
        type=str,
        help="Custom analysis prompt"
    )
    
    args = parser.parse_args()
    
    logger = get_logger("main")
    log_system_event("Application started", {"mode": args.mode})
    
    try:
        if args.mode == "streamlit":
            launch_streamlit()
        elif args.mode == "cli":
            run_cli_mode(args)
        elif args.mode == "validate":
            run_validation_mode()
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


def launch_streamlit():
    """Launch Streamlit UI."""
    import subprocess
    
    streamlit_app = Path(__file__).parent / "src" / "ui" / "streamlit_app.py"
    
    if not streamlit_app.exists():
        print("❌ Streamlit app not found")
        print("   Run this first: (Streamlit UI not yet built)")
        sys.exit(1)
    
    print("🚀 Launching Streamlit UI...")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        str(streamlit_app),
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ])


def run_cli_mode(args):
    """Run in CLI mode."""
    logger = get_logger("cli")
    
    print("\n" + "=" * 70)
    print("🎓 UOH ACADEMIC EVALUATION - BATCH PROCESSING MODE")
    print("=" * 70)
    
    # Initialize evaluator
    evaluator = AcademicEvaluator()
    
    # Show LLM status
    if not evaluator.llm_available:
        print(f"\n❌ LLM Analyzer not available: {evaluator.llm_error}")
        print("   Please check API keys in .env file")
        sys.exit(1)
    
    # Show provider status
    status = evaluator.get_system_info()
    print(f"\n✓ LLM Provider: {status['llm_status']['current_provider']}")
    print(f"✓ Supabase: {'Enabled' if status['supabase_available'] else 'Disabled'}")
    
    # Get PDF files
    if args.document_dir.exists():
        pdf_files = list(args.document_dir.glob("*.pdf"))
    else:
        print(f"\n❌ Directory not found: {args.document_dir}")
        sys.exit(1)
    
    if not pdf_files:
        print(f"\n⚠️  No PDF files found in {args.document_dir}")
        print("   Upload PDFs to data/documents/ and try again")
        return
    
    print(f"\n📄 Found {len(pdf_files)} PDF files")
    print("🔄 Starting batch processing...")
    print()
    
    # Progress callback
    def show_progress(current, total, filename):
        print(f"  [{current}/{total}] Processing: {filename}")
    
    try:
        # Process batch
        results, batch_filename = evaluator.process_batch_documents(
            pdf_files,
            args.custom_prompt,
            args.batch_name,
            show_progress
        )
        
        # Show results
        successful = sum(1 for r in results if not r.get('_metadata', {}).get('error'))
        failed = len(results) - successful
        
        print("\n" + "=" * 70)
        print("✅ BATCH PROCESSING COMPLETED")
        print("=" * 70)
        print(f"   Total Documents: {len(results)}")
        print(f"   Successful: {successful}")
        print(f"   Failed: {failed}")
        print(f"   Success Rate: {successful/len(results)*100:.1f}%")
        print()
        print(f"📊 Excel File: {EXCEL_DIR / batch_filename}")
        print(f"📁 Location: {EXCEL_DIR}")
        print("=" * 70)
        
    except Exception as e:
        logger.error(f"Batch processing error: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


def run_validation_mode():
    """Run system validation."""
    logger = get_logger("validation")
    
    print("\n" + "=" * 70)
    print("🔍 SYSTEM VALIDATION")
    print("=" * 70)
    
    # Initialize evaluator
    try:
        evaluator = AcademicEvaluator()
    except Exception as e:
        print(f"\n❌ Failed to initialize evaluator: {e}")
        sys.exit(1)
    
    # Run validation
    results = evaluator.validate_system()
    
    # Display results
    print("\n📋 Component Status:")
    print(f"   PDF Processor: {'✅' if results['pdf_processor'] else '❌'}")
    print(f"   OCR Processor: {'✅' if results['ocr_processor'] else '❌'}")
    print(f"   Excel Handler: {'✅' if results['excel_handler'] else '❌'}")
    print(f"   LLM Analyzer: {'✅' if results['llm_analyzer'] else '❌'}")
    print(f"   Supabase: {'✅' if results['supabase'] else '⚠️  Disabled'}")
    print(f"   Document Directory: {'✅' if results['document_directory'] else '❌'}")
    print(f"   Excel Directory: {'✅' if results['excel_directory'] else '❌'}")
    
    # LLM connections
    if 'llm_connections' in results:
        print("\n🔌 LLM Connections:")
        for provider, status in results['llm_connections'].items():
            print(f"   {provider.title()}: {'✅' if status else '❌'}")
    
    # Document count
    if 'documents_found' in results:
        print(f"\n📄 Documents Found: {results['documents_found']}")
    
    # System info
    info = evaluator.get_system_info()
    print("\n🔧 System Info:")
    print(f"   Document Directory: {info['document_directory']}")
    print(f"   Excel Directory: {info['excel_directory']}")
    print(f"   Current Batch: {info['current_batch'] or 'None'}")
    print(f"   Available Batches: {info['available_batches']}")
    
    # Overall status
    print("\n" + "=" * 70)
    if results['overall_status'] == 'OK':
        print("✅ SYSTEM VALIDATION PASSED")
    else:
        print("❌ SYSTEM VALIDATION FAILED")
    print("=" * 70)


if __name__ == "__main__":
    main()
