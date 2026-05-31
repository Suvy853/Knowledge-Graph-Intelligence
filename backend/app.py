"""
FastAPI app: Knowledge Graph Intelligence System
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import tempfile
from pathlib import Path
from pdf_processor import process_filing
from entity_extractor import extract_from_sections
from neo4j_manager import Neo4jManager
from query_engine import QueryEngine

# Global Neo4j connection (reused across requests)
_neo4j_instance: Neo4jManager = None  # pyright: ignore[reportAssignmentType]

def get_neo4j() -> Neo4jManager:
    """Get or create Neo4j connection (singleton)"""
    global _neo4j_instance
    if _neo4j_instance is None:
        _neo4j_instance = Neo4jManager()
    return _neo4j_instance

app = FastAPI(
    title="Knowledge Graph Intelligence",
    description="Extract entities from SEC filings and answer questions",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    answer: str
    results: List[Dict[str, Any]]
    cypher: str

class UploadResponse(BaseModel):
    message: str
    entities_count: int
    relationships_count: int

class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    confidence: float

class GraphEdge(BaseModel):
    source: str
    target: str
    type: str

class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

# Routes
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Knowledge Graph Intelligence"
    }

@app.post("/clear")
async def clear_database():
    """Clear all data from Neo4j database"""
    try:
        neo4j = get_neo4j()
        
        # Delete all entities and relationships
        neo4j.query_graph("MATCH (n) DETACH DELETE n")
        
        return {
            "message": "Database cleared successfully",
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload", response_model=UploadResponse)
async def upload_filing(file: UploadFile = File(...)):
    """
    Upload and process SEC filing
    
    Args:
        file: SEC filing HTML file
        
    Returns:
        Upload status with entity/relationship counts
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        print(f"Processing file: {file.filename}")
        
        # Process filing
        sections = process_filing(tmp_path)
        print(f"✅ Got {len(sections)} sections")
        
        # Extract entities
        extractions = extract_from_sections(sections)
        
        total_entities = sum(r["entities_count"] for r in extractions)
        total_rels = sum(r["relationships_count"] for r in extractions)
        print(f"✅ Extracted {total_entities} entities, {total_rels} relationships")
        
        # Store in Neo4j
        neo4j = get_neo4j()
        for extraction_result in extractions:
            extraction = extraction_result["extraction"]
            if extraction.get("entities") or extraction.get("relationships"):
                neo4j.ingest_extraction(extraction, file.filename)  # pyright: ignore[reportArgumentType]
        
        # Clean up
        os.remove(tmp_path)
        
        return UploadResponse(
            message=f"Successfully processed {file.filename}",
            entities_count=total_entities,
            relationships_count=total_rels
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query_graph(request: QueryRequest):
    """
    Query the knowledge graph with natural language
    
    Args:
        request: QueryRequest with question
        
    Returns:
        Answer with supporting graph results
    """
    try:
        engine = QueryEngine()
        result = engine.answer_question(request.question)
        engine.close()
        
        return QueryResponse(
            question=result["question"],
            answer=result["answer"],
            results=result["results"],
            cypher=result["cypher"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/graph", response_model=GraphResponse)
async def get_graph():
    """
    Get graph visualization data
    
    Returns:
        Nodes and edges for visualization
    """
    try:
        neo4j = get_neo4j()
        
        # Get all nodes
        nodes_query = "MATCH (e:ENTITY) RETURN e.name as name, e.type as type, e.confidence as confidence"
        nodes_data = neo4j.query_graph(nodes_query)
        
        nodes = [
            GraphNode(
                id=n["name"],
                label=n["name"],
                type=n["type"] or "UNKNOWN",
                confidence=n["confidence"] or 0.5
            )
            for n in nodes_data
        ]
        
        # Get all edges
        edges_query = "MATCH (a:ENTITY)-[r]->(b:ENTITY) RETURN a.name as source, b.name as target, type(r) as rel_type"
        edges_data = neo4j.query_graph(edges_query)
        
        edges = [
            GraphEdge(
                source=e["source"],
                target=e["target"],
                type=e["rel_type"]
            )
            for e in edges_data
        ]
        
        return GraphResponse(nodes=nodes, edges=edges)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get database statistics"""
    try:
        neo4j = get_neo4j()
        
        entities_query = "MATCH (e:ENTITY) RETURN COUNT(e) as count"
        entities_count = neo4j.query_graph(entities_query)[0]["count"]
        
        rels_query = "MATCH (a:ENTITY)-[r]-(b:ENTITY) RETURN COUNT(r) as count"
        rels_count = neo4j.query_graph(rels_query)[0]["count"]
        
        return {
            "entities": entities_count,
            "relationships": rels_count,
            "status": "healthy"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def serve_frontend():
    """Serve frontend index.html"""
    try:
        frontend_path = Path(__file__).parent.parent / "frontend" / "index.html"
        with open(frontend_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Frontend not found: {str(e)}")

@app.get("/static/{filename}")
async def serve_static(filename: str):
    """Serve static files (JS, CSS)"""
    try:
        frontend_path = Path(__file__).parent.parent / "frontend" / filename
        
        if filename.endswith(".js"):
            return FileResponse(frontend_path, media_type="application/javascript")
        elif filename.endswith(".css"):
            return FileResponse(frontend_path, media_type="text/css")
        else:
            with open(frontend_path, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)