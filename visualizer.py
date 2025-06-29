"""
Streamlit Dashboard for Automated Scope of Work Reviewer
"""

import streamlit as st
from extractor import extract_sow_content
from nlp_rules import analyze_sow_nlp
from llm_review import review_sow_with_llm
from reporter import summarize_issues, assign_risk_score
import os

st.set_page_config(page_title="SOW Reviewer Dashboard", layout="wide")
st.title("Automated Scope of Work Reviewer 🏗️")

st.sidebar.header("Upload SOW Document")
file = st.sidebar.file_uploader("Choose a PDF or text file", type=["pdf", "txt"]) 
use_llm = st.sidebar.checkbox("Include LLM (GPT) Review", value=False)
show_risk = st.sidebar.checkbox("Show Risk Score", value=True)

if file:
    # Save uploaded file temporarily
    temp_path = f"temp_{file.name}"
    with open(temp_path, "wb") as f:
        f.write(file.read())
    
    # Extract and analyze
    sow_data = extract_sow_content(file_path=temp_path)
    full_text = sow_data['full_text']
    sections = sow_data['sections']
    nlp_issues = analyze_sow_nlp(full_text, sections)
    llm_issues = review_sow_with_llm(full_text) if use_llm else []
    all_issues = nlp_issues + llm_issues
    summary = summarize_issues(all_issues)
    risk_score = assign_risk_score(all_issues) if show_risk else None
    
    # Display results
    st.subheader("Extracted Sections")
    for section, content in sections.items():
        if content:
            with st.expander(section.replace('_', ' ').title()):
                st.write(content)
    
    st.subheader("Detected Issues")
    if all_issues:
        for idx, issue in enumerate(all_issues, 1):
            st.markdown(f"**{idx}. [{issue.get('severity', 'Info')}]** {issue.get('issue', issue.get('message', ''))}")
            st.markdown(f"_Suggestion:_ {issue.get('suggestion', '')}")
            st.markdown("---")
    else:
        st.success("No issues found!")
    
    st.subheader("Summary")
    st.json(summary)
    if show_risk:
        st.metric("Risk Score", risk_score)
    
    # Clean up temp file
    os.remove(temp_path)
else:
    st.info("Upload a SOW PDF or text file to begin analysis.") 