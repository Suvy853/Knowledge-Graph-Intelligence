"""
Test Phase 3: FastAPI endpoints
"""
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check"""
    print("\n[1/5] Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200

def test_stats():
    """Test stats endpoint"""
    print("\n[2/5] Testing /stats endpoint...")
    response = requests.get(f"{BASE_URL}/stats")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200

def test_query():
    """Test query endpoint"""
    print("\n[3/5] Testing /query endpoint...")
    payload = {
        "question": "What products does Apple manufacture?"
    }
    response = requests.post(f"{BASE_URL}/query", json=payload)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Question: {result['question']}")
    print(f"Answer: {result['answer'][:100]}...")
    print(f"Cypher: {result['cypher']}")
    assert response.status_code == 200

def test_graph():
    """Test graph endpoint"""
    print("\n[4/5] Testing /graph endpoint...")
    response = requests.get(f"{BASE_URL}/graph")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Nodes: {len(result['nodes'])}")
    print(f"Edges: {len(result['edges'])}")
    print(f"Sample node: {result['nodes'][0] if result['nodes'] else 'None'}")
    assert response.status_code == 200

def test_upload():
    """Test upload endpoint"""
    print("\n[5/5] Testing /upload endpoint...")
    
    filing_path = r"C:\Users\suvee\Downloads\SEC_fillings\Apple SEC_filings.html"
    
    if not Path(filing_path).exists():
        print(f"⚠️  Filing not found at {filing_path}")
        print("Skipping upload test")
        return
    
    with open(filing_path, "rb") as f:
        files = {"file": ("Apple SEC_filings.html", f, "text/html")}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Message: {result['message']}")
    print(f"Entities: {result['entities_count']}")
    print(f"Relationships: {result['relationships_count']}")
    assert response.status_code == 200

def main():
    print("=" * 60)
    print("PHASE 3 TEST: FastAPI Endpoints")
    print("=" * 60)
    
    try:
        test_health()
        test_stats()
        test_query()
        test_graph()
        test_upload()
        
        print("\n" + "=" * 60)
        print("✅ ALL PHASE 3 TESTS PASSED")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()