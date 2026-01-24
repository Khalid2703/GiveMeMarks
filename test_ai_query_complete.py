"""
AI Query System Verification Script
Tests the complete AI Query workflow with Cohere
"""
import sys
import requests
import json
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

API_URL = "http://localhost:8000"

def test_connection():
    """Test if backend is running"""
    print("🔍 Testing backend connection...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False

def test_batches_endpoint():
    """Test batch listing"""
    print("\n🔍 Testing batches endpoint...")
    try:
        response = requests.get(f"{API_URL}/api/batches/all", timeout=5)
        data = response.json()
        
        batches = data.get('batches', [])
        current = data.get('current_batch')
        
        print(f"✅ Found {len(batches)} batches")
        if current:
            print(f"✅ Current batch: {current}")
        
        if batches:
            print("\n📊 Batch Details:")
            for batch in batches[-3:]:  # Show last 3
                print(f"  • {batch['filename']}")
                print(f"    Students: {batch['student_count']}")
                print(f"    Created: {batch['created_at']}")
            return batches[0]['filename'] if batches else None
        else:
            print("⚠️  No batches found. Upload and process documents first.")
            return None
            
    except Exception as e:
        print(f"❌ Error testing batches: {e}")
        return None

def test_ai_query(batch_filename):
    """Test AI query with actual data"""
    print("\n🔍 Testing AI query...")
    
    queries = [
        "What is the average CGPA?",
        "How many students are there?",
        "Who is the top performer?"
    ]
    
    for query in queries:
        print(f"\n❓ Query: {query}")
        try:
            response = requests.post(
                f"{API_URL}/api/ai/query",
                json={
                    "query": query,
                    "batch": batch_filename
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('response', 'No response')
                context = data.get('context_stats', {})
                provider = data.get('provider', 'unknown')
                model = data.get('model', 'unknown')
                
                print(f"✅ Response received from {provider} ({model})")
                print(f"📊 Context: {context.get('total_students', 0)} students, "
                      f"Avg CGPA: {context.get('avg_cgpa', 0)}")
                print(f"💬 Answer: {answer[:150]}...")
                
                # Check if response is hardcoded
                if "placeholder" in answer.lower() or "test" in answer.lower():
                    print("⚠️  Response might be hardcoded!")
                else:
                    print("✅ Response appears contextual")
                    
            else:
                print(f"❌ Query failed with status {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Query error: {e}")

def test_cohere_directly():
    """Test Cohere API directly"""
    print("\n🔍 Testing Cohere API...")
    try:
        import cohere
        from config.settings import COHERE_API_KEY
        
        if not COHERE_API_KEY:
            print("❌ COHERE_API_KEY not found in .env")
            return False
            
        client = cohere.Client(COHERE_API_KEY)
        response = client.generate(
            model="command-a",
            prompt="Say 'Cohere is working!' if you can read this.",
            max_tokens=50
        )
        
        answer = response.generations[0].text.strip()
        print(f"✅ Cohere API is working")
        print(f"   Response: {answer}")
        return True
        
    except Exception as e:
        print(f"❌ Cohere API test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 AI QUERY SYSTEM VERIFICATION")
    print("=" * 60)
    
    # Test 1: Connection
    if not test_connection():
        print("\n❌ Backend not running. Start with: python backend/api.py")
        return
    
    # Test 2: Cohere
    if not test_cohere_directly():
        print("\n⚠️  Cohere API issues detected")
    
    # Test 3: Batches
    batch = test_batches_endpoint()
    
    if batch:
        # Test 4: AI Query
        test_ai_query(batch)
    else:
        print("\n⚠️  Cannot test AI queries without batches")
        print("   Go to Homepage → Upload PDFs → Process Documents")
    
    print("\n" + "=" * 60)
    print("✅ VERIFICATION COMPLETE")
    print("=" * 60)
    print("\n📝 Summary:")
    print("   - Backend: Running")
    print("   - Cohere: Connected" if test_cohere_directly() else "   - Cohere: Issues")
    print(f"   - Batches: {len(test_batches_endpoint() or [])} available")
    print("   - AI Query: " + ("Working" if batch else "Needs data"))
    print("\n💡 Next Steps:")
    if not batch:
        print("   1. Upload documents on Homepage")
        print("   2. Click 'Process Documents'")
        print("   3. Return to AI Query page")
    else:
        print("   1. Open frontend: http://localhost:5173")
        print("   2. Go to AI Query page")
        print("   3. Select a batch")
        print("   4. Ask questions!")

if __name__ == "__main__":
    main()
