# Automated Scope of Work Reviewer

An AI-powered Python tool that analyzes construction project Scope of Work (SOW) documents to flag inconsistencies, missing details, and potential issues.

## Features

- **PDF/Text Extraction**: Extract and clean text from PDF SOW documents
- **NLP Rules Engine**: Detect missing sections, contradictions, and ambiguous terms
- **LLM Enhancement**: Use OpenAI GPT-3.5-turbo for advanced analysis
- **Structured Reports**: Generate JSON and PDF reports with severity levels
- **Interactive Dashboard**: Streamlit-based visualization (optional)
- **Risk Scoring**: Assign risk scores based on issue severity
- **Comparative Analysis**: Compare against reference templates

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Download spaCy model:
   ```bash
   python -m spacy download en_core_web_sm
   ```
4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Add your OpenAI API key to .env
   ```

## Usage

### Command Line Interface

```bash
python main.py --input sow_document.pdf --output report.json
```

### Streamlit Dashboard

```bash
streamlit run visualizer.py
```

## Project Structure

- `main.py` - CLI entry point
- `extractor.py` - PDF/text extraction and cleaning
- `nlp_rules.py` - Rule-based NLP checks
- `llm_review.py` - OpenAI API integration
- `reporter.py` - Report generation
- `visualizer.py` - Streamlit dashboard
- `tests/` - Test cases and synthetic SOWs
- `reference.json` - SOW template for comparison

## Testing

Run tests with:

```bash
pytest tests/
```
