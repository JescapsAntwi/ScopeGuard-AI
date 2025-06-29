import os
import pytest
from extractor import extract_sow_content
from nlp_rules import analyze_sow_nlp
from reporter import summarize_issues, assign_risk_score

SYNTHETIC_SOWS = [
    {
        'desc': 'Missing timeline and ambiguous term',
        'text': '''
        PROJECT OVERVIEW
        This project is for a new school building.
        SCOPE OF WORK
        Includes foundation, structure, and finishing.
        MATERIALS
        As per standard.
        COSTS
        Estimated at $1,000,000.
        PAYMENT TERMS
        50% upfront, 50% on completion.
        DELIVERABLES
        Complete building.
        QUALITY STANDARDS
        High quality.
        ''',
        'expected_missing': ['timeline'],
        'expected_ambiguous': ['as per standard']
    },
    {
        'desc': 'Contradictory timeline',
        'text': '''
        PROJECT OVERVIEW
        New hospital construction.
        SCOPE OF WORK
        All civil and MEP works.
        TIMELINE
        Completion in 6 months.
        The phases spanning 12 months may overlap.
        MATERIALS
        Concrete, steel, glass.
        COSTS
        $5,000,000.
        PAYMENT TERMS
        Monthly billing.
        DELIVERABLES
        Hospital building.
        QUALITY STANDARDS
        As required.
        LEGAL CLAUSES
        Standard contract terms.
        ''',
        'expected_contradiction': True
    }
]

def test_missing_sections_and_ambiguous_terms():
    sow = SYNTHETIC_SOWS[0]
    result = extract_sow_content(text=sow['text'])
    issues = analyze_sow_nlp(result['full_text'], result['sections'])
    missing = [i['section'] for i in issues if i['type'] == 'missing_section']
    ambiguous = [i['term'] for i in issues if i['type'] == 'ambiguous_term']
    assert 'timeline' in missing
    assert any('as per standard' in a for a in ambiguous)

def test_contradiction_detection():
    sow = SYNTHETIC_SOWS[1]
    result = extract_sow_content(text=sow['text'])
    issues = analyze_sow_nlp(result['full_text'], result['sections'])
    contradiction = any(i['type'] == 'contradiction' for i in issues)
    assert contradiction

def test_risk_score():
    sow = SYNTHETIC_SOWS[0]
    result = extract_sow_content(text=sow['text'])
    issues = analyze_sow_nlp(result['full_text'], result['sections'])
    score = assign_risk_score(issues)
    assert score >= 10  # At least one critical issue 