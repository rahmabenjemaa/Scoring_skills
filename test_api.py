"""
Test Script for Olive Soft Job Scoring System
Run this to verify the system works end-to-end
"""

import json
import time
import requests
from typing import Dict, List


# ============================================================================
# CONFIGURATION
# ============================================================================

API_URL = "http://localhost:8000"
HEALTH_ENDPOINT = f"{API_URL}/health"
SCORE_ENDPOINT = f"{API_URL}/score"
DEMO_ENDPOINT = f"{API_URL}/demo"

# Test jobs
TEST_JOBS = [
    {
        "title": "Senior Machine Learning Engineer",
        "description": """
        Join our AI team as a Senior Machine Learning Engineer.
        
        Responsibilities:
        - Develop and deploy ML models using Python and PyTorch
        - Work with NLP and transformers for text understanding
        - Build data pipelines with Apache Spark
        - Mentor junior engineers
        
        Requirements:
        - 5+ years ML experience
        - Strong Python, SQL, Linux
        - Experience with TensorFlow or PyTorch
        - AWS or Azure cloud experience
        """,
        "company": "TechCorp AI",
        "location": "Paris, France",
        "source": "LinkedIn"
    },
    {
        "title": "AI Strategy Consultant at McKinsey",
        "description": """
        Join McKinsey's AI & Analytics practice.
        
        We're seeking an experienced AI consultant to:
        - Lead transformation projects for Fortune 500 clients
        - Develop AI/ML strategies
        - Work with C-level executives
        - Build and present client recommendations
        
        Requirements:
        - Consulting background
        - Machine learning knowledge
        - Excellent communication and client management
        - Strategic thinking and problem-solving
        """,
        "company": "McKinsey & Company",
        "location": "Paris, France",
        "source": "LinkedIn"
    },
    {
        "title": "Data Science Intern",
        "description": """
        Summer internship in our Data Science team.
        
        Tasks:
        - Analyze datasets using Python
        - Support ML model development
        - Learn industry best practices
        
        Requirements:
        - Student pursuing degree in CS, Statistics, or similar
        - Basic Python knowledge
        - Enthusiasm for data science
        """,
        "company": "StartupXYZ",
        "location": "Remote",
        "source": "Indeed"
    },
]


# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_health() -> bool:
    """Test API health endpoint."""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        data = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200 and data.get("models_loaded"):
            print("✅ Health check PASSED")
            return True
        else:
            print("❌ Models not loaded")
            return False
    
    except Exception as e:
        print(f"❌ Health check FAILED: {e}")
        return False


def test_demo() -> bool:
    """Test demo endpoint."""
    print("\n" + "="*60)
    print("TEST 2: Demo Scoring")
    print("="*60)
    
    try:
        response = requests.post(DEMO_ENDPOINT, timeout=10)
        data = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Score: {data.get('final_score', 0):.1%}")
        print(f"Reason: {data.get('top_reason', 'N/A')}")
        print(f"Seniority: {data.get('seniority', 'unknown')}")
        print(f"Skills: {', '.join(data.get('skills_detected', [])[:5])}")
        
        if response.status_code == 200 and data.get("success"):
            print("✅ Demo scoring PASSED")
            return True
        else:
            print("❌ Demo scoring FAILED")
            return False
    
    except Exception as e:
        print(f"❌ Demo scoring FAILED: {e}")
        return False


def test_single_job_scoring() -> bool:
    """Test single job scoring."""
    print("\n" + "="*60)
    print("TEST 3: Single Job Scoring")
    print("="*60)
    
    try:
        job = TEST_JOBS[0]
        
        payload = {
            "title": job["title"],
            "description": job["description"],
            "company": job["company"],
            "location": job["location"],
        }
        
        print(f"Scoring: {job['title']}")
        
        start = time.time()
        response = requests.post(SCORE_ENDPOINT, json=payload, timeout=15)
        elapsed = time.time() - start
        
        data = response.json()
        
        print(f"Response time: {elapsed:.2f}s")
        print(f"Status: {response.status_code}")
        print(f"\nResults:")
        print(f"  Final Score: {data.get('final_score', 0):.3f}")
        print(f"  Match: {data.get('match_percentage', 0):.1%}")
        print(f"  Seniority: {data.get('seniority', 'unknown')}")
        print(f"  Top Reason: {data.get('top_reason', 'N/A')}")
        print(f"\nDimension Scores:")
        for dim, score in data.get('dimensions', {}).items():
            print(f"  {dim}: {score:.3f}")
        
        if response.status_code == 200 and data.get("success"):
            print("✅ Single job scoring PASSED")
            return True
        else:
            print("❌ Single job scoring FAILED")
            print(f"Error: {data.get('error', 'Unknown')}")
            return False
    
    except Exception as e:
        print(f"❌ Single job scoring FAILED: {e}")
        return False


def test_batch_scoring() -> bool:
    """Test batch scoring."""
    print("\n" + "="*60)
    print("TEST 4: Batch Scoring")
    print("="*60)
    
    try:
        payload = {
            "jobs": [
                {
                    "title": job["title"],
                    "description": job["description"],
                    "company": job["company"],
                    "location": job["location"],
                }
                for job in TEST_JOBS
            ],
            "use_consulting_mode": False
        }
        
        print(f"Scoring {len(TEST_JOBS)} jobs...")
        
        start = time.time()
        response = requests.post(f"{API_URL}/score/batch", json=payload, timeout=30)
        elapsed = time.time() - start
        
        data = response.json()
        
        print(f"Response time: {elapsed:.2f}s")
        print(f"Status: {response.status_code}")
        print(f"\nBatch Results:")
        print(f"  Total jobs: {data.get('total_jobs', 0)}")
        print(f"  Successful: {data.get('successful_scores', 0)}")
        print(f"  Failed: {data.get('failed_scores', 0)}")
        print(f"  Average score: {data.get('average_score', 0):.3f}")
        
        print(f"\nIndividual Scores:")
        for i, result in enumerate(data.get('results', []), 1):
            if result.get('success'):
                print(f"  Job {i}: {result.get('final_score', 0):.3f} - {result.get('top_reason', 'N/A')}")
            else:
                print(f"  Job {i}: ERROR - {result.get('error', 'Unknown')}")
        
        if response.status_code == 200 and data.get("success"):
            print("✅ Batch scoring PASSED")
            return True
        else:
            print("❌ Batch scoring FAILED")
            return False
    
    except Exception as e:
        print(f"❌ Batch scoring FAILED: {e}")
        return False


def test_consulting_mode() -> bool:
    """Test consulting-focused scoring."""
    print("\n" + "="*60)
    print("TEST 5: Consulting Mode Scoring")
    print("="*60)
    
    try:
        job = TEST_JOBS[1]  # McKinsey consulting job
        
        payload = {
            "title": job["title"],
            "description": job["description"],
            "company": job["company"],
            "location": job["location"],
        }
        
        print(f"Scoring (consulting mode): {job['title']}")
        
        response = requests.post(
            SCORE_ENDPOINT,
            json=payload,
            params={"consulting_mode": True},
            timeout=15
        )
        
        data = response.json()
        
        print(f"Final Score: {data.get('final_score', 0):.3f}")
        print(f"Is consulting: {data.get('is_consulting_opportunity', False)}")
        print(f"Prestige firm: {data.get('prestige_firm', 'N/A')}")
        print(f"Top Reason: {data.get('top_reason', 'N/A')}")
        
        if response.status_code == 200 and data.get("success"):
            print("✅ Consulting mode PASSED")
            return True
        else:
            print("❌ Consulting mode FAILED")
            return False
    
    except Exception as e:
        print(f"❌ Consulting mode FAILED: {e}")
        return False


def test_error_handling() -> bool:
    """Test error handling."""
    print("\n" + "="*60)
    print("TEST 6: Error Handling")
    print("="*60)
    
    try:
        # Test with empty description
        payload = {
            "title": "Test",
            "description": "Too short"
        }
        
        response = requests.post(SCORE_ENDPOINT, json=payload, timeout=10)
        data = response.json()
        
        if not data.get("success"):
            print(f"✅ Correctly rejected invalid input: {data.get('error', 'Unknown')}")
            return True
        else:
            print("❌ Should have rejected empty description")
            return False
    
    except Exception as e:
        print(f"❌ Error handling test FAILED: {e}")
        return False


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all tests and report results."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "Olive Soft Job Scoring API - Test Suite" + " "*8 + "║")
    print("╚" + "="*58 + "╝")
    
    # Check if API is running
    try:
        requests.get(API_URL, timeout=2)
    except:
        print(f"\n❌ ERROR: API is not running at {API_URL}")
        print(f"   Start with: python -m uvicorn api:app --reload")
        return False
    
    # Run tests
    results = {
        "Health Check": test_health(),
        "Demo Scoring": test_demo(),
        "Single Job": test_single_job_scoring(),
        "Batch Scoring": test_batch_scoring(),
        "Consulting Mode": test_consulting_mode(),
        "Error Handling": test_error_handling(),
    }
    
    # Report
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:8} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready for use.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check logs above.")
        return False


# ============================================================================
# PERFORMANCE BENCHMARK
# ============================================================================

def benchmark_performance():
    """Benchmark API performance."""
    print("\n" + "="*60)
    print("PERFORMANCE BENCHMARK")
    print("="*60)
    
    try:
        # Warm up
        requests.post(DEMO_ENDPOINT, timeout=10)
        
        # Single job benchmark
        print("\nBenchmarking single job scoring (10 iterations)...")
        times = []
        for _ in range(10):
            start = time.time()
            requests.post(DEMO_ENDPOINT, timeout=15)
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"  Average: {avg_time:.2f}s")
        print(f"  Min: {min_time:.2f}s")
        print(f"  Max: {max_time:.2f}s")
        
        # Throughput estimate
        jobs_per_hour = 3600 / avg_time
        print(f"\nEstimated throughput: {jobs_per_hour:.0f} jobs/hour")
        
        if avg_time < 2:
            print("✅ Performance is good")
        elif avg_time < 5:
            print("⚠️  Performance is acceptable")
        else:
            print("❌ Performance is slow")
    
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Run tests
    success = run_all_tests()
    
    # Optional benchmark
    if success and len(sys.argv) > 1 and sys.argv[1] == "--benchmark":
        benchmark_performance()
    
    sys.exit(0 if success else 1)
