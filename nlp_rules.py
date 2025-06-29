"""
NLP Rules Engine for SOW Reviewer
Detects missing sections, contradictions, and ambiguous terms in SOW documents.
"""

import nltk
import re
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Define critical SOW sections
CRITICAL_SECTIONS = [
    'project_overview',
    'scope',
    'timeline',
    'materials',
    'costs',
    'payment_terms',
    'deliverables',
    'quality_standards',
    'legal_clauses'
]

# Ambiguous terms to flag
AMBIGUOUS_TERMS = [
    r"as per standard",
    r"TBD",
    r"to be determined",
    r"as required",
    r"if necessary",
    r"subject to change",
    r"etc\.",
    r"or equivalent",
    r"as needed",
    r"unless otherwise specified"
]

# Contradiction patterns (simple examples)
CONTRADICTION_PATTERNS = [
    (r"completion in (\d+) months", r"phases? spanning (\d+) months"),
    (r"start date:? (\w+ \d{4})", r"completion date:? (\w+ \d{4})")
]


def check_missing_sections(sections: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Check for missing critical sections in the SOW.
    Returns a list of issues found.
    """
    issues = []
    for section in CRITICAL_SECTIONS:
        if not sections.get(section):
            issues.append({
                'type': 'missing_section',
                'section': section,
                'severity': 'Critical',
                'message': f'Missing critical section: {section.replace("_", " ").title()}',
                'suggestion': f'Add a section for {section.replace("_", " ").title()}.'
            })
    return issues


def check_ambiguous_terms(text: str) -> List[Dict[str, Any]]:
    """
    Check for ambiguous terms in the SOW text.
    Returns a list of issues found.
    """
    issues = []
    for term in AMBIGUOUS_TERMS:
        if re.search(term, text, re.IGNORECASE):
            issues.append({
                'type': 'ambiguous_term',
                'term': term,
                'severity': 'Warning',
                'message': f'Ambiguous term found: "{term}"',
                'suggestion': 'Replace with specific details.'
            })
    return issues


def check_contradictions(text: str) -> List[Dict[str, Any]]:
    """
    Check for simple contradictions in the SOW text.
    Returns a list of issues found.
    """
    issues = []
    for pattern1, pattern2 in CONTRADICTION_PATTERNS:
        match1 = re.search(pattern1, text, re.IGNORECASE)
        match2 = re.search(pattern2, text, re.IGNORECASE)
        if match1 and match2:
            # Example: flag if months are different
            if match1.group(1) != match2.group(1):
                issues.append({
                    'type': 'contradiction',
                    'patterns': [pattern1, pattern2],
                    'severity': 'Critical',
                    'message': f'Potential contradiction: "{match1.group(0)}" vs. "{match2.group(0)}"',
                    'suggestion': 'Clarify the timeline and ensure consistency.'
                })
    return issues


def analyze_sow_nlp(full_text: str, sections: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Run all NLP rule-based checks on the SOW.
    Returns a list of detected issues.
    """
    issues = []
    issues.extend(check_missing_sections(sections))
    issues.extend(check_ambiguous_terms(full_text))
    issues.extend(check_contradictions(full_text))
    return issues


if __name__ == "__main__":
    # Example usage
    example_sections = {
        'project_overview': 'This project is for... ',
        'scope': 'The scope includes...',
        'timeline': '',  # Missing
        'materials': 'Standard materials...',
        'costs': '',  # Missing
        'payment_terms': 'Payment will be...',
        'deliverables': 'Deliverables include...',
        'quality_standards': 'As per standard.',  # Ambiguous
        'legal_clauses': ''  # Missing
    }
    example_text = """
    The project will be completed in 3 months. However, the phases spanning 6 months may overlap.
    Payment will be made as per standard. Materials are to be determined.
    """
    issues = analyze_sow_nlp(example_text, example_sections)
    for issue in issues:
        print(issue) 