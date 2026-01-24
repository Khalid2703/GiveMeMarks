"""
Test script for Cohere AI Query functionality
Tests the complete flow from frontend to backend
"""
import requests
import json
from pathlib import Path

# Configuration
API_URL = "http://localhost:8000"

def test_system_status():
    """Test if backend is running"""
    print("\n" + "="*60)
    print("1. TESTING SYSTEM STATUS")
    print("="*60)
    
    try:
        response = requests.get(f"{API_URL}/status")
        data = response.json()
        
        print(f"✅ Backend is running")
        print(f"   LLM Available: {data.get('llm_available')}")
        print(f"   LLM Provider: {data.get('llm_provider')}")
        print(f"   Supabase: {data.get('supabase_available')}")
        print(f"   Documents in Queue: {data.get('documents_in_queue')}")
        
        return True
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def test_get_batches():
    """Test batch retrieval"""
    print("\n" + "="*60)
    print("2. TESTING BATCH RETRIEVAL")
    print("="*60)
    
    try:
        response = requests.get(f"{API_URL}/api/batches/all")
        data = response.json()
        
        batches = data.get('batches', [])
        print(f"✅ Found {len(batches)} batches")
        
        for batch in batches:
            print(f"   - {batch.get('filename')} ({batch.get('student_count')} students)")
        
        return batches
    except Exception as e:
        print(f"❌ Failed to get batches: {e}")
        return []

def test_ai_query(batch_filename=None):
    """Test AI query endpoint"""
    print("\n" + "="*60)
    print("3. TESTING AI QUERY")
    print("="*60)
    
    test_queries = [
        "What is the average CGPA of all students?",
        "How many students are in each department?",
        "Who are the top 5 performers?",
        "What's the CGPA distribution?",
        "Show me students with CGPA above 9.0"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Query {i}: {query}")
        
        try:
            payload = {
                "query": query
            }
            
            if batch_filename:
                payload["batch"] = batch_filename
            
            response = requests.post(
                f"{API_URL}/api/ai/query",
                json=payload
            )
            
            data = response.json()
            
            if "error" in data:
                print(f"❌ Error: {data['error']}")
                continue
            
            print(f"✅ Response received")
            print(f"   Answer: {data.get('response', 'No response')[:200]}...")
            print(f"   Model: {data.get('model', 'unknown')}")
            print(f"   Provider: {data.get('provider', 'unknown')}")
            
            if data.get('context_stats'):
                stats = data['context_stats']
                print(f"   Context: {stats.get('total_students')} students, Avg CGPA: {stats.get('avg_cgpa')}")
            
        except Exception as e:
            print(f"❌ Query failed: {e}")

def test_cohere_directly():
    """Test Cohere directly"""
    print("\n" + "="*60)
    print("4. TESTING COHERE DIRECTLY")
    print("="*60)
    
    try:
        from src.core.cohere_ai_agent import CohereAIAgent
        import pandas as pd
        
        # Create dummy data
        dummy_data = {
            'Student Name': ['Alice Johnson', 'Bob Smith', 'Carol Davis'],
            'Roll Number': ['21CS101', '21CS102', '21CS103'],
            'Department': ['Computer Science', 'Computer Science', 'Mathematics'],
            'CGPA': [9.2, 8.5, 9.0]
        }
        
        df = pd.DataFrame(dummy_data)
        
        agent = CohereAIAgent()
        print("✅ Cohere agent initialized")
        
        # Test query
        result = agent.query(
            question="What is the average CGPA?",
            df=df,
            batch_name="test_batch"
        )
        
        print(f"✅ Query successful")
        print(f"   Response: {result.get('response', 'No response')}")
        print(f"   Model: {result.get('model', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct Cohere test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("COHERE AI QUERY - COMPREHENSIVE TEST")
    print("="*60)
    
    # Test 1: System status
    if not test_system_status():
        print("\n❌ Backend is not running. Start it with: python main.py")
        return
    
    # Test 2: Get batches
    batches = test_get_batches()
    
    batch_to_test = None
    if batches:
        batch_to_test = batches[0].get('filename')
        print(f"\nUsing batch: {batch_to_test}")
    
    # Test 3: AI Query
    test_ai_query(batch_to_test)
    
    # Test 4: Direct Cohere test
    test_cohere_directly()
    
    print("\n" + "="*60)
    print("✅ TESTING COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. Start the backend: python main.py")
    print("2. Start the frontend: cd frontend && npm run dev")
    print("3. Open http://localhost:5173")
    print("4. Go to AI Query page")
    print("5. Select a batch and ask questions!")

if __name__ == "__main__":
    main()
