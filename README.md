# Knowledge Graph Intelligence System

## Live Demo
🔗 [knowledge-graph-intelligence-production.up.railway.app](https://knowledge-graph-intelligence-production.up.railway.app/)

## Overview
An AI-powered SEC filing analysis system that extracts entities and relationships from 10-K documents, stores them in a Neo4j graph database, and enables natural language querying.

## Features
- **Document Processing**: Parse SEC 10-K filings (HTML format)
- **Entity Extraction**: Claude AI extracts companies, products, relationships with confidence scoring
- **Knowledge Graph**: Neo4j stores and visualizes entity relationships
- **Natural Language Query**: Ask questions about the filing in plain English
- **Interactive Visualization**: D3.js graph shows entity relationships and connections
- **Professional UI**: Corporate design with sidebar controls and full-screen graph

## Tech Stack
- **Backend**: FastAPI, Python 3.14
- **Database**: Neo4j Aura (cloud)
- **LLM**: Claude Opus 4.8 (Anthropic API)
- **Frontend**: D3.js, HTML5, CSS3, JavaScript
- **Deployment**: Railway

## Installation

### Prerequisites
- Python 3.14+
- Neo4j Aura account (free tier available)
- Anthropic API key

### Setup
1. Clone the repository
2. Create virtual environment:
```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1
```

3. Install dependencies:
```bash
   pip install -r requirements.txt
```

4. Create `.env` file with:
```bash
ANTHROPIC_API_KEY=your_key_here
NEO4J_URI=your_uri
NEO4J_USER=your_user
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=your_db
ENVIRONMENT=development
```
5. Run server:
```bash
   cd backend
   python -m uvicorn app:app --reload
```

6. Visit: `http://localhost:8000/`

## Usage

### Upload a Filing
1. Click "Upload Filing" section
2. Drag & drop or click to browse for HTML SEC filing
3. Wait for processing (extracts entities from all sections)
4. Graph auto-updates with entities and relationships

### Search the Graph
1. Type a question in the "Search Knowledge Graph" box
2. Examples:
   - "What products does Microsoft manufacture?"
   - "What operating systems does Apple offer?"
   - "What are the main business segments?"
3. Claude analyzes the graph and returns grounded answers

### Clear Data
- **Clear DB**: Removes all entities and relationships
- **Clear**: Clears search results but keeps query input

## Architecture

### Backend Components
- `app.py`: FastAPI server with REST endpoints
- `pdf_processor.py`: HTML parsing and section extraction
- `entity_extractor.py`: Claude API integration for entity extraction
- `neo4j_manager.py`: Graph database operations (CRUD)
- `query_engine.py`: Natural language to Cypher translation

### Frontend Components
- `index.html`: Responsive layout (sidebar + full-screen graph)
- `app.js`: D3.js visualization, API calls, user interactions

### API Endpoints
- `GET /health` - Health check
- `GET /stats` - Entity/relationship counts
- `POST /upload` - Upload and process SEC filing
- `POST /query` - Natural language query
- `GET /graph` - Graph visualization data
- `POST /clear` - Clear database

## Key Decisions
- **Entity Extraction**: Claude Opus 4.8 with confidence scoring (0.7-0.95)
- **Relationship Types**: MANUFACTURES, DESIGNS, MARKETS, INCLUDES, BASED_ON, OFFERS
- **Processing**: All sections processed for complete entity coverage
- **Graph Database**: Neo4j for scalability and relationship queries
- **Frontend**: D3.js force-directed graph with interactive nodes

## Future Enhancements
- Add more relationship types
- Custom entity type detection
- Graph export (JSON, GraphML)
- Advanced filtering and drill-down
- Multi-filing comparison

## License
MIT

## Author
Suveera Pratapa
