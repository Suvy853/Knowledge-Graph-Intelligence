"""
Neo4j graph database manager
"""
from neo4j import GraphDatabase, basic_auth
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class Neo4jManager:
    """Manage Neo4j connections and queries"""
    
    def __init__(self):
        """Initialize Neo4j connection"""
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER")
        self.password = os.getenv("NEO4J_PASSWORD")
        
        if not self.uri or not self.user or not self.password:
            raise ValueError("Missing Neo4j credentials in .env file")
        
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=basic_auth(self.user, self.password)
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            print("✅ Connected to Neo4j Aura")
        except Exception as e:
            print(f"❌ Failed to connect to Neo4j: {str(e)}")
            raise
    
    def close(self) -> None:
        """Close connection"""
        if self.driver:
            self.driver.close()
    
    def create_entity(self, name: str, entity_type: str, confidence: float) -> None:
        """
        Create entity node in graph
        
        Args:
            name: Entity name
            entity_type: Type (COMPANY, PRODUCT, etc.)
            confidence: Confidence score (0-1)
        """
        with self.driver.session() as session:
            query = """
            MERGE (e:ENTITY {name: $name})
            SET e.type = $type, e.confidence = $confidence
            RETURN e
            """
            session.run(query, name=name, type=entity_type, confidence=confidence)
    
    def create_relationship(self, source: str, rel_type: str, target: str, confidence: float, evidence: str) -> None:
        """
        Create relationship between entities
        
        Args:
            source: Source entity name
            rel_type: Relationship type
            target: Target entity name
            confidence: Confidence score
            evidence: Supporting text
        """
        with self.driver.session() as session:
            query = f"""
            MERGE (a:ENTITY {{name: $source}})
            MERGE (b:ENTITY {{name: $target}})
            MERGE (a)-[r:{rel_type} {{confidence: $confidence, evidence: $evidence}}]->(b)
            RETURN r
            """
            try:
                session.run(query, source=source, target=target, confidence=confidence, evidence=evidence) # pyright: ignore[reportArgumentType]
            except Exception as e:
                print(f"Warning creating relationship: {str(e)}")
    
    def ingest_extraction(self, extraction: Dict[str, Any], doc_name: str) -> None:
        """
        Ingest extracted entities and relationships
        
        Args:
            extraction: Extracted data from Claude
            doc_name: Source document name
        """
        try:
            # Create entities first
            for entity in extraction.get("entities", []):
                self.create_entity(
                    entity["name"],
                    entity["type"],
                    entity["confidence"]
                )
            
            # Create relationships
            for rel in extraction.get("relationships", []):
                self.create_relationship(
                    rel["source"],
                    rel["relationship_type"],
                    rel["target"],
                    rel["confidence"],
                    rel["evidence"]
                )
            
            print(f"✅ Ingested {len(extraction.get('entities', []))} entities and {len(extraction.get('relationships', []))} relationships")
            
        except Exception as e:
            print(f"❌ Error ingesting to Neo4j: {str(e)}")
    
    def query_graph(self, cypher: str) -> List[Dict[str, Any]]:
        """
        Run custom Cypher query
        
        Args:
            cypher: Cypher query string
            
        Returns:
            Query results
        """
        with self.driver.session() as session:
            result = session.run(cypher) # pyright: ignore[reportArgumentType]
            return result.data()