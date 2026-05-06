ENTITY_EXTRACTION_PROMPT = """You are an entity and relationship extractor for SEC 10-K filings.

Extract ALL entities and relationships from the following text section.

Return ONLY valid JSON (no preamble, no markdown).

Entity types: COMPANY, PRODUCT, PRODUCT_LINE, OPERATING_SYSTEM, PERSON, EXECUTIVE, DIVISION

Relationship types: MANUFACTURES, DESIGNS, MARKETS, INCLUDES, BASED_ON, OFFERS

Confidence scoring:
- 0.95: Explicitly stated (e.g., "Apple manufactures iPhone")
- 0.85: Clearly implied (e.g., listed as a product line)
- 0.75: Contextually inferred
- Discard if < 0.70

Return this JSON structure exactly:
{
  "entities": [
    {"name": "string", "type": "string", "confidence": float}
  ],
  "relationships": [
    {"source": "string", "relationship_type": "string", "target": "string", "confidence": float, "evidence": "string"}
  ]
}

TEXT:
{text}
"""

def extract_entities_and_relationships(text: str):
    """Extract entities and relationships from SEC filing text"""
    # TODO: Implement Claude API call in Phase 1
    pass