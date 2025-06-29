"""
LLM Review Module for SOW Reviewer
Uses OpenAI GPT-3.5-turbo to analyze SOW text and flag issues.
"""

import os
import openai
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 2000))
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.3))

openai.api_key = OPENAI_API_KEY

LLM_PROMPT = (
    "Review this construction SOW and list inconsistencies, missing details, or vague language. "
    "Focus on: timelines, deliverables, materials, costs, and legal clauses. Return a numbered list. "
    "For each issue, suggest a fix and assign a severity (Critical/Warning/Info). "
    "Respond in JSON array format: [{'issue': ..., 'severity': ..., 'suggestion': ...}]"
)

def review_sow_with_llm(sow_text: str) -> List[Dict[str, Any]]:
    """
    Use OpenAI GPT-3.5-turbo to review the SOW text and return a list of issues.
    """
    try:
        response = openai.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert construction contract reviewer."},
                {"role": "user", "content": f"{LLM_PROMPT}\n\nSOW:\n{sow_text}"}
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE
        )
        content = response.choices[0].message.content.strip()
        # Try to parse the JSON array from the response
        import json
        try:
            # Find the first and last brackets to extract the JSON array
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end != -1:
                json_str = content[start:end]
                issues = json.loads(json_str)
                return issues
            else:
                return [{
                    'issue': 'LLM response could not be parsed as JSON.',
                    'severity': 'Info',
                    'suggestion': content
                }]
        except Exception as e:
            return [{
                'issue': 'Error parsing LLM response.',
                'severity': 'Info',
                'suggestion': f'{content}\nError: {str(e)}'
            }]
    except Exception as e:
        return [{
            'issue': 'Error communicating with OpenAI API.',
            'severity': 'Critical',
            'suggestion': str(e)
        }]


if __name__ == "__main__":
    # Example usage
    test_sow = """
    The project will be completed in 3 months. However, the phases spanning 6 months may overlap.
    Payment will be made as per standard. Materials are to be determined.
    """
    issues = review_sow_with_llm(test_sow)
    for issue in issues:
        print(issue) 