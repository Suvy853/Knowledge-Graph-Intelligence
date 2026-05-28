"""
Entity extraction using Claude API
"""
import json
from typing import Dict, List
from anthropic import Anthropic
import os

# Locked extraction prompt - using %s instead of .format()
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
            model="claude-opus-4-6",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract response
        response_text = message.content[0].text # type: ignore
        
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
            print(f"JSON Parse Error: {str(e)}")
            return {"entities": [], "relationships": []}
            
    except Exception as e:
        print(f"Error in extraction: {str(e)}")
        return {"entities": [], "relationships": []}

def extract_from_sections(sections: List[Dict]) -> List[Dict]:
    """
    Extract entities from all sections
    
    Args:
        sections: List of text sections
        
    Returns:
        List of extraction results per section
    """
    results = []
    
    for i, section in enumerate(sections):
        print(f"Extracting from section {i+1}/{len(sections)}...")
        
        extraction = extract_entities(section["text"])
        
        results.append({
            "section_num": section["section_num"],
            "extraction": extraction,
            "entities_count": len(extraction.get("entities", [])),
            "relationships_count": len(extraction.get("relationships", []))
        })
    
    return results