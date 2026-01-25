"""
Startup script for deployment
Ensures demo data exists when app starts
"""
from pathlib import Path
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def ensure_demo_data():
    """Ensure demo data exists on startup"""
    try:
        from create_demo_data import check_and_create_if_needed
        
        print("=" * 60)
        print("DEPLOYMENT STARTUP - Checking for data...")
        print("=" * 60)
        
        check_and_create_if_needed()
        
        print("=" * 60)
        print("✅ Data check complete - App ready to start")
        print("=" * 60)
        
    except Exception as e:
        print(f"⚠️  Warning: Could not create demo data: {e}")
        print("   App will start but may show 'no data' messages")

if __name__ == "__main__":
    ensure_demo_data()
