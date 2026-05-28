"""
Query engine: Convert natural language to Cypher + generate answers
"""
from anthropic import Anthropic
from neo4j_manager import Neo4jManager
from typing import Dict
import json

CYPHER_GENERATION_PROMPT = """You are a Neo4j Cypher query generator for a knowledge graph about SEC 10-K filings.

The graph has:
- Node type: ENTITY with properties {name, type, confidence}
- Edge types: MANUFACTURES, DESIGNS, MARKETS, INCLUDES, BASED_ON, OFFERS
- Entity types: COMPANY, PRODUCT, PRODUCT_LINE, OPERATING_SYSTEM, PERSON, EXECUTIVE, DIVISION

Given a natural language question, generate a Cypher query to find the answer.

Return ONLY the Cypher query, no explanation.

Examples:
Q: What products does Apple manufacture?
A: MATCH (c:ENTITY {name: "Apple Inc."})-[:MANUFACTURES]->(p:ENTITY) RETURN p.name, p.type

Q: What is iPhone based on?
A: MATCH (p:ENTITY {name: "iPhone"})-[:BASED_ON]->(os:ENTITY) RETURN os.name, os.type

Question: %s
"""

ANSWER_GENERATION_PROMPT = """You are an AI assistant answering questions about companies based on their SEC 10-K filings.

Given a question and search results from a knowledge graph, generate a clear, concise answer grounded in the data.

Question: %s

Graph Results:
%s

Generate a natural answer based only on the results provided. If no results, say "I could not find information about that in the filings."
"""

class QueryEngine:
    """Generate and execute graph queries"""
    
    def __init__(self):
        self.client = Anthropic()
        self.neo4j = Neo4jManager()
    
    def generate_cypher(self, question: str) -> str:
        """
        Convert natural language question to Cypher query
        
        Args:
            question: User's natural language question
            
        Returns:
            Cypher query string
        """
        prompt = CYPHER_GENERATION_PROMPT % question
        
        message = self.client.messages.create(
            model="claude-opus-4-6",
            max_tokens=500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        block = message.content[0] if message.content else None
        cypher = ""
        if block and getattr(block, "type", None) == "text":
            cypher = getattr(block, "text", "").strip()
        else:
            print("No valid Cypher query returned by Claude.")
        return cypher
    
    def execute_query(self, cypher: str) -> list:
        """
        Execute Cypher query against Neo4j
        
        Args:
            cypher: Cypher query string
            
        Returns:
            Query results
        """
        try:
            results = self.neo4j.query_graph(cypher)
            return results
        except Exception as e:
            print(f"Query execution error: {str(e)}")
            return []
    
    def generate_answer(self, question: str, results: list) -> str:
        """
        Generate natural language answer from graph results
        
        Args:
            question: Original question
            results: Graph query results
            
        Returns:
            Natural language answer
        """
        # Format results for Claude
        results_text = json.dumps(results, indent=2) if results else "No results found"
        
        prompt = ANSWER_GENERATION_PROMPT % (question, results_text)
        
        message = self.client.messages.create(
            model="claude-opus-4-6",
            max_tokens=500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        block = message.content[0] if message.content else None
        answer = ""
        if block and getattr(block, "type", None) == "text":
            answer = getattr(block, "text", "").strip()
        else:
            print("No valid answer returned by Claude.")
        return answer
    
    def answer_question(self, question: str) -> Dict:
        """
        Complete pipeline: question → cypher → execute → answer
        
        Args:
            question: User's question
            
        Returns:
            Dict with question, cypher, results, answer
        """
        print(f"\n❓ Question: {question}")
        
        # Step 1: Generate Cypher
        print("🔄 Generating Cypher query...")
        cypher = self.generate_cypher(question)
        print(f"📝 Cypher: {cypher}")
        
        # Step 2: Execute query
        print("⚙️  Executing query...")
        results = self.execute_query(cypher)
        print(f"✅ Got {len(results)} results")
        
        # Step 3: Generate answer
        print("💭 Generating answer...")
        answer = self.generate_answer(question, results)
        
        return {
            "question": question,
            "cypher": cypher,
            "results": results,
            "answer": answer
        }
    
    def close(self):
        """Close connections"""
        self.neo4j.close()