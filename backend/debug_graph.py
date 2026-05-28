"""
Debug: Check what's actually in Neo4j
"""
from neo4j_manager import Neo4jManager

def debug_graph():
    """Check all entities and relationships in graph"""
    
    neo4j = Neo4jManager()
    
    print("\n" + "=" * 60)
    print("CHECKING GRAPH CONTENTS")
    print("=" * 60)
    
    # Get all entities
    entities_query = "MATCH (e:ENTITY) RETURN e.name, e.type, e.confidence"
    entities = neo4j.query_graph(entities_query)
    
    print(f"\n📊 ENTITIES ({len(entities)} total):")
    for entity in entities:
        print(f"  - {entity['e.name']} ({entity['e.type']}) [confidence: {entity['e.confidence']}]")
    
    # Get all relationships
    rels_query = "MATCH (a:ENTITY)-[r]-(b:ENTITY) RETURN type(r) as rel_type, a.name as source, b.name as target"
    rels = neo4j.query_graph(rels_query)
    
    print(f"\n🔗 RELATIONSHIPS ({len(rels)} total):")
    for rel in rels:
        print(f"  - {rel['source']} -{rel['rel_type']}-> {rel['target']}")
    
    if not rels:
        print("  ⚠️  No relationships found!")
    
    neo4j.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    debug_graph()