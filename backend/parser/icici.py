"""
ICICI Bank credit card statement parser
"""

import re
import logging
from .utils import find_pattern, find_multiline_pattern, clean_amount, normalize_date


def parse_icici(text):
    """
    Parse ICICI Bank credit card statement.
    
    Args:
        text: Extracted text from PDF
        
    Returns:
        dict: Parsed statement data
    """
    result = {
        "issuer": "ICICI",
        "card_last_4_digits": None,
        "billing_period": None,
        "payment_due_date": None,
        "total_amount_due": None,
        "transactions": [],
    }
    
    # Extract card last 4 digits
    # Pattern: Card Number: XXXX XXXX XXXX 1234
    pattern = r'(?:card\s+(?:number|no\.?):?.*?)(\d{4})(?:\s|$|\.)'
    card_digits = find_pattern(text, pattern, 1)
    if card_digits:
        result["card_last_4_digits"] = card_digits
        logging.info(f"Extracted card_last_4_digits: {card_digits}")
    else:
        logging.warning("Could not extract card_last_4_digits for ICICI")
    
    # Extract billing period
    # Pattern: Statement Period: 01-Nov-2025 to 30-Nov-2025
    pattern = r'(?:statement\s+period:?\s*)(\d{1,2}[-/]\w+[-/]\d{4}\s+(?:to|-)\s+\d{1,2}[-/]\w+[-/]\d{4})'
    billing_period = find_pattern(text, pattern, 1)
    if billing_period:
        result["billing_period"] = normalize_date(billing_period)
        logging.info(f"Extracted billing_period: {billing_period}")
    else:
        logging.warning("Could not extract billing_period for ICICI")
    
    # Extract payment due date
    # Pattern: Due Date: 15-Dec-2025
    pattern = r'(?:due\s+date:?\s*)(\d{1,2}[-/]\w+[-/]\d{4})'
    due_date = find_pattern(text, pattern, 1)
    if due_date:
        result["payment_due_date"] = normalize_date(due_date)
        logging.info(f"Extracted payment_due_date: {due_date}")
    else:
        logging.warning("Could not extract payment_due_date for ICICI")
    
    # Extract total amount due
    # Pattern: Total Amount Due: Rs. 12,450.00
    pattern = r'(?:total\s+amount\s+due:?\s*)((?:₹|Rs\.?)\s*[\d,]+\.?\d*)'
    amount = find_pattern(text, pattern, 1)
    if amount:
        result["total_amount_due"] = clean_amount(amount)
        logging.info(f"Extracted total_amount_due: {amount}")
    else:
        logging.warning("Could not extract total_amount_due for ICICI")

    # Transactions (simplified heuristic)
    # Example line: "01-Nov-2025 AMAZON PURCHASE      1,234.56"
    tx_pattern = r'(\d{1,2}[-/]\w+[-/]\d{4})\s+([A-Z0-9 ,.&\-\/]+?)\s+(-?\d{1,3}(?:,\d{3})*(?:\.\d{2}))'
    for match in re.finditer(tx_pattern, text, re.IGNORECASE):
        date, description, amount_str = match.groups()
        transaction = {
            "date": normalize_date(date),
            "description": description.strip(),
            "amount": clean_amount(amount_str),
        }
        result["transactions"].append(transaction)

    logging.info(f"Extracted {len(result['transactions'])} transactions for ICICI")

    return result
