"""
Entity extraction using Claude API - CORRECTED MODEL
"""
import json
from typing import Dict, List
from anthropic import Anthropic, APIError
import os

# Locked extraction prompt - using %s instead of .format()
ENTITY_EXTRACTION_PROMPT = """You are an entity and relationship extractor for SEC 10-K filings.

Extract ALL entities and relationships from the following text section.

Return ONLY valid JSON (no preamble, no markdown).

Entity types: COMPANY, PRODUCT, PRODUCT_LINE, OPERATING_SYSTEM, PERSON, EXECUTIVE, DIVISION

Relationship types (REQUIRED - use these EXACTLY):
- MANUFACTURES: When a company/division manufactures a product (e.g., "Apple manufactures iPhone")
- DESIGNS: When a company/division designs something (e.g., "Apple designs Mac")
- MARKETS: When a company/division markets something (e.g., "Company markets product")
- INCLUDES: When a product line includes specific models (e.g., "iPhone line includes iPhone 16")
- BASED_ON: When something is based on technology (e.g., "iPhone based on iOS")
- OFFERS: When a company offers services or features

Confidence scoring:
- 0.95: Explicitly stated (e.g., "Apple manufactures iPhone")
- 0.85: Clearly implied (e.g., listed as a product line)
- 0.75: Contextually inferred
- Discard if < 0.70

Return this JSON structure EXACTLY:
{
  "entities": [
    {"name": "string", "type": "string", "confidence": float}
  ],
  "relationships": [
    {"source": "string", "relationship_type": "string", "target": "string", "confidence": float, "evidence": "string"}
  ]
}

TEXT:
%s
"""

def extract_entities(text: str) -> Dict:
    """
    Extract entities and relationships from text using Claude
    
    Args:
        text: Text section from SEC filing
        
    Returns:
        Parsed JSON with entities and relationships
    """
    try:
        client = Anthropic()
        
        # Fill prompt with text using % formatting instead of .format()
        prompt = ENTITY_EXTRACTION_PROMPT % text
        
        # Call Claude
        message = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract response
        response_text = message.content[0].text # pyright: ignore[reportAttributeAccessIssue]
        
        # Clean response (remove markdown code blocks if present)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        response_text = response_text.strip()
        
        # Parse JSON
        try:
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError as e:
            # A bad JSON response is a per-section content issue, not a fatal
            # error - skip this section but keep processing the rest.
            print(f"JSON Parse Error: {str(e)}")
            return {"entities": [], "relationships": []}

    except APIError as e:
        # API-level failures (no credits, bad key, rate limit, etc.) affect
        # EVERY section. Re-raise so the caller surfaces a real error instead
        # of silently returning 0 entities and reporting "success".
        print(f"Anthropic API error during extraction: {str(e)}")
        raise

def extract_from_sections(sections: List[Dict]) -> List[Dict]:
    """
    Extract entities from all sections
    
    Args:
        sections: List of text sections
        
    Returns:
        List of extraction results per section
    """
    results = []
    
    # OPTIMIZATION: Only process first 10 sections for speed
    sections_to_process = sections[:10]
    total_sections = len(sections_to_process)
    
    for i, section in enumerate(sections_to_process):
        print(f"Extracting from section {i+1}/{total_sections}...")
        
        extraction = extract_entities(section["text"])
        
        results.append({
            "section_num": section["section_num"],
            "extraction": extraction,
            "entities_count": len(extraction.get("entities", [])),
            "relationships_count": len(extraction.get("relationships", []))
        })
    
    return results