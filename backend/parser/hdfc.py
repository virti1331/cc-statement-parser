"""
HDFC Bank credit card statement parser
"""

import re
import logging
from .utils import find_pattern, find_multiline_pattern, clean_amount, normalize_date


def parse_hdfc(text):
    """
    Parse HDFC Bank credit card statement.
    
    Args:
        text: Extracted text from PDF
        
    Returns:
        dict: Parsed statement data
    """
    result = {
        "issuer": "HDFC",
        "card_last_4_digits": None,
        "billing_period": None,
        "payment_due_date": None,
        "total_amount_due": None,
        "transactions": [],
    }
    
    # Extract card last 4 digits
    # Pattern: Card No: 4341 55XX XXXX 3388
    pattern = r'Card\s+No:\s*(\d{4})'
    card_digits = find_pattern(text, pattern, 1)
    if card_digits:
        result["card_last_4_digits"] = card_digits
        logging.info(f"Extracted card_last_4_digits: {card_digits}")
    else:
        logging.warning("Could not extract card_last_4_digits for HDFC")
    
    # Extract billing period
    # Pattern: Statement Date:23/10/2024
    pattern = r'Statement\s+Date:\s*(\d{1,2}/\d{1,2}/\d{4})'
    statement_date = find_pattern(text, pattern, 1)
    
    # Also try to extract the statement month/period info
    pattern_month = r'Statement\s+for\s+.*?(\d{2}/\d{4})'
    statement_month = find_pattern(text, pattern_month, 1)
    
    if statement_date:
        result["billing_period"] = normalize_date(statement_date)
        logging.info(f"Extracted billing_period: {statement_date}")
    elif statement_month:
        result["billing_period"] = statement_month
        logging.info(f"Extracted billing_period: {statement_month}")
    else:
        logging.warning("Could not extract billing_period for HDFC")
    
    # Extract payment due date
    # Pattern: Payment Due Date in table format
    # Line structure: "Payment Due Date Total Dues Minimum Amount Due"
    # Next line: "12/11/2024 83,794.00 4,240.00"
    pattern = r'Payment\s+Due\s+Date\s+Total\s+Dues\s+Minimum\s+Amount\s+Due.*?(\d{1,2}/\d{1,2}/\d{4})'
    due_date = find_pattern(text, pattern, 1)
    if due_date:
        result["payment_due_date"] = normalize_date(due_date)
        logging.info(f"Extracted payment_due_date: {due_date}")
    else:
        logging.warning("Could not extract payment_due_date for HDFC")
    
    # Extract total amount due
    # Pattern: Total Dues appears in table, followed by amount
    # Format: "12/11/2024 83,794.00 4,240.00" (due date, total dues, minimum due)
    pattern = r'Payment\s+Due\s+Date\s+Total\s+Dues\s+Minimum\s+Amount\s+Due.*?\d{1,2}/\d{1,2}/\d{4}\s+([\d,]+\.?\d*)'
    amount = find_pattern(text, pattern, 1)
    if amount:
        result["total_amount_due"] = f"₹{clean_amount(amount)}"
        logging.info(f"Extracted total_amount_due: {amount}")
    else:
        # Alternative: Look for "Total Dues" in Account Summary section
        pattern = r'Total\s+Dues[^\d]*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        amount = find_pattern(text, pattern, 1)
        if amount:
            result["total_amount_due"] = f"₹{clean_amount(amount)}"
            logging.info(f"Extracted total_amount_due (alternative): {amount}")
        else:
            logging.warning("Could not extract total_amount_due for HDFC")

    # Transactions (simplified heuristic)
    # Example line: "23/10/2024 SOME MERCHANT NAME  1,234.56 Cr"
    tx_pattern = r'(\d{1,2}/\d{1,2}/\d{4})\s+([A-Z0-9 ,.&\-\/]+?)\s+(-?\d{1,3}(?:,\d{3})*(?:\.\d{2}))\s*(Cr|Dr)?'
    for match in re.finditer(tx_pattern, text, re.IGNORECASE):
        date, description, amount_str, cr_dr = match.groups()
        amount_clean = clean_amount(amount_str)
        if cr_dr and cr_dr.lower() == "cr":
            amount_clean = f"-{amount_clean}"
        transaction = {
            "date": normalize_date(date),
            "description": description.strip(),
            "amount": amount_clean,
        }
        result["transactions"].append(transaction)

    logging.info(f"Extracted {len(result['transactions'])} transactions for HDFC")

    return result
