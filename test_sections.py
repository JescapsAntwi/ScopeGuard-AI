"""
Test script to debug section extraction
"""

from extractor import extract_sow_content

def test_section_extraction():
    # Sample SOW text with clear section headers
    sample_sow = """
    PROJECT OVERVIEW
    This is a construction project for building a new office complex.
    
    SCOPE OF WORK
    The scope includes foundation work, structural framing, and interior finishing.
    Materials are to be determined based on availability.
    
    TIMELINE
    Project duration is 12 months with completion expected by December 2024.
    However, the phases spanning 18 months may overlap.
    
    MATERIALS
    Standard construction materials will be used as per standard specifications.
    
    COSTS
    Budget is TBD and subject to change.
    
    PAYMENT TERMS
    Payment will be made as required.
    
    DELIVERABLES
    The project will deliver a completed office building.
    
    QUALITY STANDARDS
    Quality will be maintained as per standard.
    
    LEGAL CLAUSES
    Force majeure clauses apply.
    """
    
    print("=== Testing Section Extraction ===\n")
    
    # Extract content
    result = extract_sow_content(text=sample_sow)
    
    print("Full text length:", len(result['full_text']))
    print("Full text preview:", result['full_text'][:200] + "...\n")
    
    print("Extracted sections:")
    for section, content in result['sections'].items():
        print(f"\n{section.upper()}:")
        if content:
            print(f"  Content: {content}")
            print(f"  Length: {len(content)} characters")
        else:
            print("  [EMPTY]")

if __name__ == "__main__":
    test_section_extraction() 