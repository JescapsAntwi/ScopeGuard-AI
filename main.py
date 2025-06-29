"""
Main CLI entry point for Automated Scope of Work Reviewer
"""

import argparse
import os
from extractor import extract_sow_content
from nlp_rules import analyze_sow_nlp
from llm_review import review_sow_with_llm
from reporter import save_json_report, save_pdf_report, summarize_issues, assign_risk_score


def main():
    parser = argparse.ArgumentParser(description="Automated Scope of Work Reviewer")
    parser.add_argument('--input', '-i', required=True, help='Path to SOW PDF or text file')
    parser.add_argument('--output', '-o', required=True, help='Output report file (JSON or PDF)')
    parser.add_argument('--llm', action='store_true', help='Include LLM (GPT) review')
    parser.add_argument('--risk', action='store_true', help='Show risk score in output')
    args = parser.parse_args()

    # Extract and clean SOW content
    sow_data = extract_sow_content(file_path=args.input)
    full_text = sow_data['full_text']
    sections = sow_data['sections']

    # Run NLP rules engine
    nlp_issues = analyze_sow_nlp(full_text, sections)

    # Optionally run LLM review
    llm_issues = []
    if args.llm:
        print("Running LLM review (this may take a few seconds)...")
        llm_issues = review_sow_with_llm(full_text)

    # Combine issues
    all_issues = nlp_issues + llm_issues

    # Optionally add risk score
    if args.risk:
        risk_score = assign_risk_score(all_issues)
        print(f"Risk Score: {risk_score}")

    # Output report
    if args.output.lower().endswith('.json'):
        save_json_report(all_issues, args.output)
        print(f"JSON report saved to {args.output}")
    elif args.output.lower().endswith('.pdf'):
        save_pdf_report(all_issues, args.output)
        print(f"PDF report saved to {args.output}")
    else:
        print("Unsupported output format. Please use .json or .pdf")

    # Print summary
    summary = summarize_issues(all_issues)
    print("Summary of issues:", summary)


if __name__ == "__main__":
    main() 