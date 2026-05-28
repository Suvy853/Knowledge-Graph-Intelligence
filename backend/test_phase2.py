"""
Test Phase 2: Query engine + answer generation
"""
from query_engine import QueryEngine

def test_phase2():
    """Test query engine"""
    
    print("=" * 60)
    print("PHASE 2 TEST: Query Engine + Answer Generation")
    print("=" * 60)
    
    engine = QueryEngine()
    
    # Test questions
    questions = [
        "What products does Apple manufacture?",
        "What operating systems does Apple design?",
        "What is iPhone based on?"
    ]
    
    for question in questions:
        result = engine.answer_question(question)
        
        print(f"\n{'=' * 60}")
        print(f"Question: {result['question']}")
        print(f"\nCypher: {result['cypher']}")
        print(f"\nResults: {result['results']}")
        print(f"\nAnswer: {result['answer']}")
        print(f"{'=' * 60}\n")
    
    engine.close()
    print("✅ PHASE 2 TEST COMPLETE")

if __name__ == "__main__":
    test_phase2()