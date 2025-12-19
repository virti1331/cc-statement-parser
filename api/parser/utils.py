"""
Utility functions for credit card statement parsing
"""

import re
import logging


def extract_text_from_pdf(pdf_path):
    """
    Extract text from all pages of a PDF.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        str: Extracted text from all pages
    """
    import pdfplumber
    
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
        raise


def find_pattern(text, pattern, group=1):
    """
    Find a pattern in text using regex.
    
    Args:
        text: Text to search
        pattern: Regex pattern
        group: Regex group to return (default: 1)
        
    Returns:
        str or None: Matched text or None if not found
    """
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(group).strip()
    return None


def find_multiline_pattern(text, pattern, group=1):
    """
    Find a pattern that spans multiple lines.
    
    Args:
        text: Text to search
        pattern: Regex pattern
        group: Regex group to return (default: 1)
        
    Returns:
        str or None: Matched text or None if not found
    """
    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
    if match:
        return match.group(group).strip()
    return None


def clean_amount(amount_str):
    """
    Clean and normalize amount strings.
    
    Args:
        amount_str: Amount string (e.g., "₹12,450.00")
        
    Returns:
        str: Cleaned amount
    """
    if not amount_str:
        return None
    return amount_str.strip()


def normalize_date(date_str):
    """
    Normalize date strings.
    
    Args:
        date_str: Date string
        
    Returns:
        str: Normalized date
    """
    if not date_str:
        return None
    return date_str.strip()
