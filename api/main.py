"""
Credit Card Statement PDF Parser
Main entry point for parsing credit card statements
"""

import sys
import json
import logging
from pathlib import Path

from parser.utils import extract_text_from_pdf
from parser.detect_issuer import detect_issuer, UnsupportedIssuerError
from parser import (
    parse_hdfc,
    parse_icici,
    parse_axis,
    parse_chase,
    parse_idfc,
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('parser.log'),
        logging.StreamHandler()
    ]
)


def parse_statement(pdf_path):
    """
    Parse a credit card statement PDF.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        dict: Parsed statement data
        
    Raises:
        UnsupportedIssuerError: If issuer cannot be detected
        FileNotFoundError: If PDF file does not exist
    """
    # Validate file exists
    if not Path(pdf_path).exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    logging.info(f"Processing PDF: {pdf_path}")
    
    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path)
    
    if not text.strip():
        logging.error("No text extracted from PDF")
        raise ValueError("PDF appears to be empty or contains no extractable text")
    
    logging.info(f"Extracted {len(text)} characters from PDF")
    
    # Detect issuer
    issuer = detect_issuer(text)
    
    # Route to appropriate parser
    parsers = {
        "HDFC": parse_hdfc,
        "ICICI": parse_icici,
        "AXIS": parse_axis,
        "CHASE": parse_chase,
        "IDFC": parse_idfc,
    }
    
    parser_func = parsers.get(issuer)
    if not parser_func:
        raise UnsupportedIssuerError(f"No parser available for issuer: {issuer}")
    
    # Parse the statement
    logging.info(f"Parsing statement using {issuer} parser")
    result = parser_func(text)
    
    logging.info("Parsing completed successfully")
    return result


def main():
    """
    Main entry point for the parser.
    """
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_pdf>")
        print("\nExample:")
        print("  python main.py samples/hdfc_statement.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    try:
        # Parse the statement
        result = parse_statement(pdf_path)
        
        # Print result as formatted JSON
        print("\n" + "="*60)
        print("PARSED STATEMENT DATA")
        print("="*60)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("="*60 + "\n")
        
    except FileNotFoundError as e:
        logging.error(str(e))
        print(f"\nError: {e}")
        sys.exit(1)
        
    except UnsupportedIssuerError as e:
        logging.error(str(e))
        print(f"\nError: {e}")
        sys.exit(1)
        
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\nUnexpected error occurred: {e}")
        print("Check parser.log for more details")
        sys.exit(1)


if __name__ == "__main__":
    main()
