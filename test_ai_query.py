"""
Test Script for AI Query Feature
Tests Cohere integration and query functionality
"""
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
from src.core.cohere_query_handler_simple import query_academic_data_with_cohere
from config.settings import COHERE_API_KEY, COHERE_MODEL


def test_cohere_connection():
    """Test 1: Verify Cohere API connection"""
    print("\n" + "="*60)
    print("TEST 1: Cohere API Connection")
    print("="*60)
    
    if not COHERE_API_KEY:
        print("❌ COHERE_API_KEY not set in .env")
        return False
    
    try:
        import cohere
        client = cohere.Client(COHERE_API_KEY)
        response = client.generate(
            model=COHERE_MODEL or "command",
            prompt="Hello, respond with 'OK'",
            max_tokens=5
        )
        
        if response.generations[0].text:
            print(f"✅ Cohere API connected successfully!")
            print(f"   Model: {COHERE_MODEL or 'command'}")
            print(f"   Response: {response.generations[0].text.strip()}")
            return True
        else:
            print("❌ Cohere API responded but no text generated")
            return False
            
    except Exception as e:
        print(f"❌ Cohere connection failed: {e}")
        return False


def test_query_handler():
    """Test 2: Test query handler with sample data"""
    print("\n" + "="*60)
    print("TEST 2: Query Handler with Sample Data")
    print("="*60)
    
    # Create sample DataFrame
    sample_data = {
        'Student Name': ['Alice Kumar', 'Bob Singh', 'Carol Patel', 'David Sharma', 'Eva Reddy'],
        'Roll Number': ['21CS001', '21CS002', '21PH001', '21MA001', '21CH001'],
        'Department': ['Computer Science', 'Computer Science', 'Physics', 'Mathematics', 'Chemistry'],
        'CGPA': [9.2, 8.5, 8.8, 9.0, 8.3],
        'Email': ['alice@uoh.ac.in', 'bob@uoh.ac.in', 'carol@uoh.ac.in', 'david@uoh.ac.in', 'eva@uoh.ac.in']
    }
    
    df = pd.DataFrame(sample_data)
    
    print(f"\n📊 Sample Data ({len(df)} students):")
    print(df.to_string(index=False))
    
    # Test query
    test_question = "What is the average CGPA of all students?"
    
    print(f"\n❓ Test Question: '{test_question}'")
    print("\n🤖 Querying Cohere AI...")
    
    try:
        result = query_academic_data_with_cohere(
            question=test_question,
            df=df,
            batch_name="test_batch"
        )
        
        if 'error' in result:
            print(f"❌ Query failed: {result['error']}")
            return False
        
        print("\n✅ Query Successful!")
        print(f"\n💬 AI Response:")
        print("-" * 60)
        print(result['response'])
        print("-" * 60)
        
        print(f"\n📈 Context Stats:")
        stats = result.get('context_stats', {})
        print(f"   - Total Students: {stats.get('total_students')}")
        print(f"   - Avg CGPA: {stats.get('avg_cgpa')}")
        print(f"   - Departments: {stats.get('departments')}")
        
        print(f"\n🔧 Metadata:")
        print(f"   - Model: {result.get('model')}")
        print(f"   - Provider: {result.get('provider')}")
        print(f"   - Timestamp: {result.get('timestamp')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Query handler failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_queries():
    """Test 3: Test multiple different queries"""
    print("\n" + "="*60)
    print("TEST 3: Multiple Query Types")
    print("="*60)
    
    # Create larger sample dataset
    sample_data = {
        'Student Name': [
            'Alice Kumar', 'Bob Singh', 'Carol Patel', 'David Sharma', 'Eva Reddy',
            'Frank Lee', 'Grace Chen', 'Henry Wilson', 'Iris Brown', 'Jack Taylor'
        ],
        'Roll Number': [
            '21CS001', '21CS002', '21PH001', '21MA001', '21CH001',
            '21CS003', '21PH002', '21MA002', '21CH002', '21CS004'
        ],
        'Department': [
            'Computer Science', 'Computer Science', 'Physics', 'Mathematics', 'Chemistry',
            'Computer Science', 'Physics', 'Mathematics', 'Chemistry', 'Computer Science'
        ],
        'CGPA': [9.2, 8.5, 8.8, 9.0, 8.3, 7.9, 9.1, 8.6, 8.4, 7.5],
    }
    
    df = pd.DataFrame(sample_data)
    
    test_queries = [
        "How many students are there?",
        "What is the highest CGPA?",
        "How many students are in Computer Science department?",
        "Who is the top performer?",
    ]
    
    success_count = 0
    
    for i, question in enumerate(test_queries, 1):
        print(f"\n{'─'*60}")
        print(f"Query {i}/{len(test_queries)}: {question}")
        print('─'*60)
        
        try:
            result = query_academic_data_with_cohere(
                question=question,
                df=df,
                batch_name="test_batch"
            )
            
            if 'error' not in result:
                print(f"✅ Success!")
                print(f"Response: {result['response'][:150]}...")
                success_count += 1
            else:
                print(f"❌ Failed: {result['error']}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print(f"\n📊 Results: {success_count}/{len(test_queries)} queries successful")
    
    return success_count == len(test_queries)


def main():
    """Run all tests"""
    print("\n" + "🧪 " + "="*58 + " 🧪")
    print("   AI QUERY FEATURE - COMPREHENSIVE TEST SUITE")
    print("🧪 " + "="*58 + " 🧪")
    
    results = {
        'Cohere Connection': False,
        'Query Handler': False,
        'Multiple Queries': False
    }
    
    # Run tests
    results['Cohere Connection'] = test_cohere_connection()
    
    if results['Cohere Connection']:
        results['Query Handler'] = test_query_handler()
        
        if results['Query Handler']:
            results['Multiple Queries'] = test_multiple_queries()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<50} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! AI Query feature is working! 🎉")
    else:
        print("⚠️  Some tests failed. Check configuration and logs.")
    print("="*60 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
