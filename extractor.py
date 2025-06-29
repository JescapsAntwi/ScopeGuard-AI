"""
PDF and Text Extraction Module for SOW Reviewer
Handles extraction and cleaning of text from PDF documents and direct text input.
"""

import pdfplumber
import re
from typing import Optional, List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextExtractor:
    """Handles extraction and cleaning of text from various sources."""
    
    def __init__(self):
        self.common_headers = [
            r'page \d+ of \d+',
            r'confidential',
            r'draft',
            r'version \d+\.\d+',
            r'© \d{4}',
            r'proprietary'
        ]
        
        self.common_footers = [
            r'page \d+',
            r'prepared by:',
            r'approved by:',
            r'date:',
            r'revision:'
        ]
    
    def extract_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted and cleaned text
        """
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            logger.info(f"Successfully extracted text from {pdf_path}")
            return self.clean_text(text)
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {str(e)}")
            raise
    
    def extract_from_text(self, text: str) -> str:
        """
        Process direct text input.
        
        Args:
            text: Raw text input
            
        Returns:
            Cleaned text
        """
        return self.clean_text(text)
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing headers, footers, and normalizing whitespace.
        Preserves document structure for section detection.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text with preserved structure
        """
        if not text:
            return ""
        
        # Remove common headers and footers
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip header/footer patterns
            if self._is_header_footer(line):
                continue
                
            cleaned_lines.append(line)
        
        # Join lines with newlines to preserve structure
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Normalize whitespace within lines but preserve line breaks
        cleaned_text = re.sub(r'[ \t]+', ' ', cleaned_text)
        
        # Remove special characters that might interfere with analysis
        cleaned_text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}\n]', '', cleaned_text)
        
        logger.info("Text cleaning completed")
        return cleaned_text.strip()
    
    def _is_header_footer(self, line: str) -> bool:
        """
        Check if a line matches common header/footer patterns.
        
        Args:
            line: Text line to check
            
        Returns:
            True if line matches header/footer pattern
        """
        line_lower = line.lower()
        
        # Check header patterns
        for pattern in self.common_headers:
            if re.search(pattern, line_lower):
                return True
        
        # Check footer patterns
        for pattern in self.common_footers:
            if re.search(pattern, line_lower):
                return True
        
        return False
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """
        Extract common SOW sections from the text using improved parsing.
        
        Args:
            text: Cleaned text content
            
        Returns:
            Dictionary of section names and their content
        """
        sections = {
            'project_overview': '',
            'scope': '',
            'timeline': '',
            'materials': '',
            'costs': '',
            'payment_terms': '',
            'deliverables': '',
            'quality_standards': '',
            'legal_clauses': ''
        }
        
        section_headers = {
            'project_overview': [
                r'project\s+overview', r'introduction', r'background', r'purpose', r'project\s+description'
            ],
            'scope': [
                r'scope\s+of\s+work', r'scope', r'work\s+scope', r'project\s+scope', r'statement\s+of\s+work'
            ],
            'timeline': [
                r'timeline', r'schedule', r'duration', r'deadline', r'milestone', r'project\s+schedule', r'time\s+frame'
            ],
            'materials': [
                r'materials', r'equipment', r'supplies', r'resources', r'material\s+requirements'
            ],
            'costs': [
                r'costs?', r'budget', r'pricing', r'estimate', r'financial', r'cost\s+breakdown', r'budgetary'
            ],
            'payment_terms': [
                r'payment\s+terms?', r'payment', r'invoice', r'billing', r'payment\s+schedule'
            ],
            'deliverables': [
                r'deliverables?', r'output', r'result', r'product', r'delivery'
            ],
            'quality_standards': [
                r'quality\s+standards?', r'quality', r'standard', r'specification', r'requirement', r'quality\s+assurance'
            ],
            'legal_clauses': [
                r'legal\s+clauses?', r'legal', r'clause', r'liability', r'warranty', r'indemnification', r'terms\s+and\s+conditions'
            ]
        }
        
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            found_section = None
            found_pattern = None
            for section_name, patterns in section_headers.items():
                for pattern in patterns:
                    match = re.match(pattern, line, re.IGNORECASE)
                    if match:
                        found_section = section_name
                        found_pattern = pattern
                        break
                if found_section:
                    break
            
            if found_section:
                # Save previous section content
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                # Start new section
                current_section = found_section
                current_content = []
                # If header and content are on the same line, extract the rest after the header
                header_match = None
                for pattern in section_headers[found_section]:
                    header_match = re.match(pattern, line, re.IGNORECASE)
                    if header_match:
                        break
                if header_match:
                    after_header = line[header_match.end():].strip()
                    if after_header:
                        current_content.append(after_header)
            elif current_section:
                current_content.append(line)
        # Save the last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        if not any(sections.values()):
            return self._fallback_section_extraction(text)
        return sections
    
    def _fallback_section_extraction(self, text: str) -> Dict[str, str]:
        """
        Fallback section extraction using keyword matching.
        
        Args:
            text: Cleaned text content
            
        Returns:
            Dictionary of section names and their content
        """
        sections = {
            'project_overview': '',
            'scope': '',
            'timeline': '',
            'materials': '',
            'costs': '',
            'payment_terms': '',
            'deliverables': '',
            'quality_standards': '',
            'legal_clauses': ''
        }
        
        # Split text into paragraphs
        paragraphs = text.split('\n\n')
        
        for paragraph in paragraphs:
            paragraph_lower = paragraph.lower()
            
            # Check which section this paragraph belongs to
            if any(keyword in paragraph_lower for keyword in ['project overview', 'introduction', 'background']):
                if sections['project_overview']:
                    sections['project_overview'] += '\n\n' + paragraph
                else:
                    sections['project_overview'] = paragraph
            elif any(keyword in paragraph_lower for keyword in ['scope of work', 'scope', 'work scope']):
                if sections['scope']:
                    sections['scope'] += '\n\n' + paragraph
                else:
                    sections['scope'] = paragraph
            elif any(keyword in paragraph_lower for keyword in ['timeline', 'schedule', 'duration', 'deadline']):
                if sections['timeline']:
                    sections['timeline'] += '\n\n' + paragraph
                else:
                    sections['timeline'] = paragraph
            elif any(keyword in paragraph_lower for keyword in ['materials', 'equipment', 'supplies']):
                if sections['materials']:
                    sections['materials'] += '\n\n' + paragraph
                else:
                    sections['materials'] = paragraph
            elif any(keyword in paragraph_lower for keyword in ['cost', 'budget', 'pricing', 'estimate']):
                if sections['costs']:
                    sections['costs'] += '\n\n' + paragraph
                else:
                    sections['costs'] = paragraph
            elif any(keyword in paragraph_lower for keyword in ['payment', 'invoice', 'billing']):
                if sections['payment_terms']:
                    sections['payment_terms'] += '\n\n' + paragraph
                else:
                    sections['payment_terms'] = paragraph
            elif any(keyword in paragraph_lower for keyword in ['deliverable', 'output', 'result']):
                if sections['deliverables']:
                    sections['deliverables'] += '\n\n' + paragraph
                else:
                    sections['deliverables'] = paragraph
            elif any(keyword in paragraph_lower for keyword in ['quality', 'standard', 'specification']):
                if sections['quality_standards']:
                    sections['quality_standards'] += '\n\n' + paragraph
                else:
                    sections['quality_standards'] = paragraph
            elif any(keyword in paragraph_lower for keyword in ['legal', 'clause', 'liability', 'warranty']):
                if sections['legal_clauses']:
                    sections['legal_clauses'] += '\n\n' + paragraph
                else:
                    sections['legal_clauses'] = paragraph
        
        return sections


def extract_sow_content(file_path: Optional[str] = None, text: Optional[str] = None) -> Dict[str, str]:
    """
    Main function to extract SOW content from file or text.
    
    Args:
        file_path: Path to PDF file (optional)
        text: Direct text input (optional)
        
    Returns:
        Dictionary containing cleaned text and extracted sections
    """
    extractor = TextExtractor()
    
    if file_path:
        if file_path.lower().endswith('.pdf'):
            cleaned_text = extractor.extract_from_pdf(file_path)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_text = f.read()
            cleaned_text = extractor.extract_from_text(raw_text)
    elif text:
        cleaned_text = extractor.extract_from_text(text)
    else:
        raise ValueError("Either file_path or text must be provided")
    
    sections = extractor.extract_sections(cleaned_text)
    
    return {
        'full_text': cleaned_text,
        'sections': sections
    }


if __name__ == "__main__":
    # Test the extractor
    test_text = """
    PROJECT OVERVIEW
    This is a construction project for building a new office complex.
    
    SCOPE OF WORK
    The scope includes foundation work, structural framing, and interior finishing.
    
    TIMELINE
    Project duration is 12 months with completion expected by December 2024.
    
    MATERIALS
    Standard construction materials will be used including concrete, steel, and drywall.
    """
    
    result = extract_sow_content(text=test_text)
    print("Extracted sections:")
    for section, content in result['sections'].items():
        if content:
            print(f"\n{section.upper()}:")
            print(content[:100] + "..." if len(content) > 100 else content) 