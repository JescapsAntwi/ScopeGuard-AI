"""
Reporting Module for SOW Reviewer
Generates structured JSON and PDF reports from analysis results.
"""

import json
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def save_json_report(issues: List[Dict[str, Any]], output_path: str) -> None:
    """
    Save the analysis issues as a JSON report.
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(issues, f, indent=2, ensure_ascii=False)


def save_pdf_report(issues: List[Dict[str, Any]], output_path: str, title: str = "SOW Review Report") -> None:
    """
    Save the analysis issues as a PDF report.
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 12))

    if not issues:
        elements.append(Paragraph("No issues found.", styles['Normal']))
    else:
        # Table header
        data = [["#", "Severity", "Issue", "Suggestion"]]
        for idx, issue in enumerate(issues, 1):
            data.append([
                str(idx),
                issue.get('severity', ''),
                issue.get('issue', issue.get('message', '')),
                issue.get('suggestion', '')
            ])
        table = Table(data, colWidths=[30, 80, 250, 180])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)

    doc.build(elements)


def summarize_issues(issues: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Summarize the number of issues by severity.
    """
    summary = {"Critical": 0, "Warning": 0, "Info": 0}
    for issue in issues:
        sev = issue.get('severity', 'Info')
        if sev in summary:
            summary[sev] += 1
        else:
            summary['Info'] += 1
    return summary


def assign_risk_score(issues: List[Dict[str, Any]], weights: Dict[str, int] = None) -> int:
    """
    Assign a risk score to the SOW based on issue severity.
    """
    if weights is None:
        weights = {"Critical": 10, "Warning": 5, "Info": 1}
    score = 0
    for issue in issues:
        sev = issue.get('severity', 'Info')
        score += weights.get(sev, 1)
    return score


if __name__ == "__main__":
    # Example usage
    example_issues = [
        {"issue": "Missing timeline section.", "severity": "Critical", "suggestion": "Add a timeline."},
        {"issue": "Ambiguous term: 'as per standard'", "severity": "Warning", "suggestion": "Specify the standard."},
        {"issue": "No legal clauses found.", "severity": "Critical", "suggestion": "Add legal clauses."}
    ]
    save_json_report(example_issues, "example_report.json")
    save_pdf_report(example_issues, "example_report.pdf")
    print("Summary:", summarize_issues(example_issues))
    print("Risk Score:", assign_risk_score(example_issues)) 