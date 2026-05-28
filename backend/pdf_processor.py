"""
SEC filing text extraction and chunking (HTML parser)
"""
from typing import List, Dict
from bs4 import BeautifulSoup 

def extract_text_from_html(file_path: str) -> str:
    """
    Extract text from HTML SEC filing (handles multiple encodings)
    
    Args:
        file_path: Path to HTML file
        
    Returns:
        Full text content
    """
    text = ""
    
    # Try multiple encodings
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                soup = BeautifulSoup(f, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text
                text = soup.get_text()
                
                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                print(f"✅ Successfully parsed with {encoding} encoding")
                return text
                
        except (UnicodeDecodeError, Exception) as e:
            continue
    
    raise Exception(f"Could not decode HTML file with any encoding")

def split_into_sections(text: str, max_chars: int = 2000) -> List[Dict[str, str]]:
    """
    Split text into sections (rough by length)
    
    Args:
        text: Full text from filing
        max_chars: Maximum characters per section
        
    Returns:
        List of sections with metadata
    """
    sections = []
    current_pos = 0
    section_num = 0
    
    while current_pos < len(text):
        # Find next section break or max_chars
        end_pos = min(current_pos + max_chars, len(text))
        
        # Try to break at newline
        if end_pos < len(text):
            last_newline = text.rfind('\n', current_pos, end_pos)
            if last_newline > current_pos:
                end_pos = last_newline
        
        section_text = text[current_pos:end_pos].strip()
        
        if section_text and len(section_text) > 100:  # Only add substantial sections
            sections.append({
                "section_num": section_num,
                "text": section_text,
                "start_char": current_pos,
                "end_char": end_pos
            })
            section_num += 1
        
        current_pos = end_pos + 1
    
    return sections

def process_filing(file_path: str) -> List[Dict[str, str]]:
    """
    Complete pipeline: extract text + split into sections
    
    Args:
        file_path: Path to HTML filing file
        
    Returns:
        List of text sections ready for entity extraction
    """
    print(f"Processing filing: {file_path}")
    
    # Extract text
    full_text = extract_text_from_html(file_path)
    print(f"Extracted {len(full_text)} characters")
    
    # Split into sections
    sections = split_into_sections(full_text, max_chars=2000)
    print(f"Split into {len(sections)} sections")
    
    return sections