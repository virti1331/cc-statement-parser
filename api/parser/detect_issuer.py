"""
Issuer detection module
Detects credit card issuer from PDF text
"""

import re
import logging


class UnsupportedIssuerError(Exception):
    """Raised when the issuer cannot be detected or is not supported"""
    pass


def detect_issuer(text):
    """
    Detect credit card issuer from PDF text.
    
    Args:
        text: Extracted text from PDF
        
    Returns:
        str: Issuer name ('HDFC', 'ICICI', 'AXIS', 'CHASE', 'IDFC')
        
    Raises:
        UnsupportedIssuerError: If issuer cannot be detected
    """
    text_upper = text.upper()
    
    # HDFC Bank detection
    if re.search(r'HDFC\s+BANK', text_upper):
        logging.info("Detected issuer: HDFC Bank")
        return "HDFC"
    
    # ICICI Bank detection
    if re.search(r'ICICI\s+BANK', text_upper):
        logging.info("Detected issuer: ICICI Bank")
        return "ICICI"
    
    # Axis Bank detection
    if re.search(r'AXIS\s+BANK', text_upper):
        logging.info("Detected issuer: Axis Bank")
        return "AXIS"

    # Chase Bank detection
    if re.search(r'CHASE\s+BANK', text_upper) or re.search(r'JPMORGAN\s+CHASE', text_upper):
        logging.info("Detected issuer: Chase")
        return "CHASE"

    # IDFC First Bank detection
    if re.search(r'IDFC\s+FIRST\s+BANK', text_upper) or re.search(r'IDFC\s+BANK', text_upper):
        logging.info("Detected issuer: IDFC First Bank")
        return "IDFC"
    
    # If no issuer detected
    logging.error("Unable to detect credit card issuer from PDF")
    raise UnsupportedIssuerError(
        "Unable to detect credit card issuer. "
        "Supported issuers: HDFC Bank, ICICI Bank, Axis Bank, Chase, IDFC First Bank"
    )
