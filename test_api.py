#!/usr/bin/env python3
"""
Quick API Test Script
Tests all backend endpoints to ensure they're working
"""
import requests
import json

API_URL = "http://localhost:8000"

def test_status():
    """Test /status endpoint"""
    print("\n1. Testing /status endpoint...")
    try:
        response = requests.get(f"{API_URL}/status")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {data.get('status')}")
            print(f"   ✅ LLM: {data.get('llm_provider')}")
            print(f"   ✅ Documents in queue: {data.get('documents_in_queue')}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_dashboard():
    """Test /api/dashboard/stats endpoint"""
    print("\n2. Testing /api/dashboard/stats endpoint...")
    try:
        response = requests.get(f"{API_URL}/api/dashboard/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Total Students: {data.get('total_students')}")
            print(f"   ✅ Average CGPA: {data.get('average_cgpa')}")
            print(f"   ✅ CGPA Distribution: {len(data.get('cgpa_distribution', []))} ranges")
            print(f"   ✅ Departments: {len(data.get('departments', []))} departments")
            print(f"   ✅ Top Performers: {len(data.get('top_performers', []))} students")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_search():
    """Test /api/search/students endpoint"""
    print("\n3. Testing /api/search/students endpoint...")
    try:
        response = requests.get(f"{API_URL}/api/search/students?query=")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Results found: {data.get('count')}")
            if data.get('results'):
                first = data['results'][0]
                print(f"   ✅ Sample: {first.get('name')} - {first.get('roll_number')}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_batches():
    """Test /api/batches/all endpoint"""
    print("\n4. Testing /api/batches/all endpoint...")
    try:
        response = requests.get(f"{API_URL}/api/batches/all")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Batches found: {len(data.get('batches', []))}")
            if data.get('batches'):
                latest = data['batches'][-1]
                print(f"   ✅ Latest: {latest.get('filename')}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_ai_query():
    """Test /api/ai/query endpoint"""
    print("\n5. Testing /api/ai/query endpoint...")
    try:
        payload = {"query": "What is the average CGPA?"}
        response = requests.post(f"{API_URL}/api/ai/query", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Response received: {data.get('response')[:100]}...")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    print("=" * 70)
    print("🔍 UOH ACADEMIC SYSTEM - API ENDPOINT TESTS")
    print("=" * 70)
    print(f"\nTesting API at: {API_URL}")
    print("\nMake sure the backend is running:")
    print("  cd backend && python api.py")
    print("\n" + "=" * 70)
    
    test_status()
    test_dashboard()
    test_search()
    test_batches()
    test_ai_query()
    
    print("\n" + "=" * 70)
    print("✅ API TESTING COMPLETE!")
    print("\nIf all tests passed, your backend is working correctly.")
    print("Now test the frontend at: http://localhost:3000")
    print("=" * 70)

if __name__ == "__main__":
    main()
