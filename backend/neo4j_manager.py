"""
Neo4j graph database manager
"""
from neo4j import GraphDatabase
from typing import List, Dict
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
        
        try:
            self.driver = GraphDatabase.driver(
                self.uri, # type: ignore
                auth=(self.user, self.password) # type: ignore
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            print("✅ Connected to Neo4j Aura")
        except Exception as e:
            print(f"❌ Failed to connect to Neo4j: {str(e)}")
            raise
    
    def close(self):
        """Close connection"""
        if self.driver:
            self.driver.close()
    
    def create_entity(self, name: str, entity_type: str, confidence: float):
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
    
    def create_relationship(self, source: str, rel_type: str, target: str, confidence: float, evidence: str):
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
            CREATE (a)-[r:{rel_type} {{confidence: $confidence, evidence: $evidence}}]->(b)
            RETURN r
            """
            session.run(query, source=source, target=target, confidence=confidence, evidence=evidence) # type: ignore
    
    def ingest_extraction(self, extraction: Dict, doc_name: str):
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
    
    def query_graph(self, cypher: str):
        """
        Run custom Cypher query
        
        Args:
            cypher: Cypher query string
            
        Returns:
            Query results
        """
        with self.driver.session() as session:
            result = session.run(cypher) # type: ignore
            return result.data()