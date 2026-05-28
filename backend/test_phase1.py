"""
Test Phase 1: SEC filing extraction + entity extraction + Neo4j storage
"""
from pdf_processor import process_filing
from entity_extractor import extract_from_sections
from neo4j_manager import Neo4jManager
import os

def test_phase1():
    """Test complete Phase 1 pipeline"""
    
    # 1. Test with one SEC filing
    test_filing = "C:\\Users\\suvee\\Downloads\\SEC_fillings\\Apple SEC_filings.html"
    
    if not os.path.exists(test_filing):
        print(f"❌ Filing not found: {test_filing}")
        print("Make sure you have downloaded the Apple 10-K filing")
        return
    
    print("=" * 50)
    print("PHASE 1 TEST: Filing → Extract → Neo4j")
    print("=" * 50)
    
    # Step 1: Process filing
    print("\n[1/3] Processing SEC filing...")
    sections = process_filing(test_filing)
    print(f"✅ Got {len(sections)} sections")
    
    # Step 2: Extract entities
    print("\n[2/3] Extracting entities from first 2 sections...")
    extractions = extract_from_sections(sections[:2])  # Test with first 2 sections
    
    total_entities = sum(r["entities_count"] for r in extractions)
    total_rels = sum(r["relationships_count"] for r in extractions)
    print(f"✅ Extracted {total_entities} entities, {total_rels} relationships")
    
    if total_entities == 0:
        print("⚠️  No entities extracted. Check Claude API responses.")
        return
    
    # Step 3: Store in Neo4j
    print("\n[3/3] Storing in Neo4j...")
    try:
        neo4j = Neo4jManager()
        
        for extraction_result in extractions:
            extraction = extraction_result["extraction"]
            if extraction.get("entities") or extraction.get("relationships"):
                neo4j.ingest_extraction(extraction, "apple-10k-test")
        
        print("✅ Stored in Neo4j")
        
        # Query to verify
        results = neo4j.query_graph("MATCH (e:ENTITY) RETURN COUNT(e) as count")
        entity_count = results[0]["count"] if results else 0
        print(f"✅ Total entities in graph: {entity_count}")
        
        neo4j.close()
        
    except Exception as e:
        print(f"❌ Neo4j error: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 50)
    print("✅ PHASE 1 TEST COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    test_phase1()