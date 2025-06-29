"""
Test script to run the SOW Reviewer tool
"""

from extractor import extract_sow_content
from nlp_rules import analyze_sow_nlp
from llm_review import review_sow_with_llm
from reporter import save_json_report, save_pdf_report, summarize_issues, assign_risk_score

def main():
    # Sample SOW text with intentional issues
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
    
    print("=== SOW Reviewer Tool Test ===\n")
    
    # Extract content
    print("1. Extracting content...")
    content = extract_sow_content(text=sample_sow)
    print(f"   Extracted {len(content['full_text'])} characters")
    
    # Run NLP analysis
    print("\n2. Running NLP analysis...")
    nlp_issues = analyze_sow_nlp(content['full_text'], content['sections'])
    print(f"   Found {len(nlp_issues)} NLP issues")
    
    # Run LLM analysis (if API key is available)
    print("\n3. Running LLM analysis...")
    try:
        llm_issues = review_sow_with_llm(content['full_text'])
        print(f"   Found {len(llm_issues)} LLM issues")
    except Exception as e:
        print(f"   LLM analysis failed: {e}")
        llm_issues = []
    
    # Combine all issues
    all_issues = nlp_issues + llm_issues
    
    # Generate summary
    print("\n4. Generating summary...")
    summary = summarize_issues(all_issues)
    risk_score = assign_risk_score(all_issues)
    
    print(f"   Summary: {summary}")
    print(f"   Risk Score: {risk_score}")
    
    # Save reports
    print("\n5. Saving reports...")
    save_json_report(all_issues, "sow_review_report.json")
    save_pdf_report(all_issues, "sow_review_report.pdf")
    print("   Reports saved as sow_review_report.json and sow_review_report.pdf")
    
    # Display issues
    print("\n=== Issues Found ===")
    for i, issue in enumerate(all_issues, 1):
        print(f"\n{i}. {issue.get('message', issue.get('issue', 'Unknown issue'))}")
        print(f"   Severity: {issue.get('severity', 'Unknown')}")
        print(f"   Suggestion: {issue.get('suggestion', 'No suggestion provided')}")

if __name__ == "__main__":
    main() 