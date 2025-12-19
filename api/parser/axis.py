"""
Axis Bank credit card statement parser
"""

import re
import logging
from .utils import find_pattern, find_multiline_pattern, clean_amount, normalize_date


def parse_axis(text):
    """
    Parse Axis Bank credit card statement.
    
    Args:
        text: Extracted text from PDF
        
    Returns:
        dict: Parsed statement data
    """
    result = {
        "issuer": "AXIS",
        "card_last_4_digits": None,
        "billing_period": None,
        "payment_due_date": None,
        "total_amount_due": None,
        "transactions": [],
    }
    
    # Extract card last 4 digits
    # Pattern: Credit Card Number 53346700****1060
    pattern = r'(?:Credit\s+Card\s+Number|Card\s+No:)\s*\d+\*+(\d{4})'
    card_digits = find_pattern(text, pattern, 1)
    if card_digits:
        result["card_last_4_digits"] = card_digits
        logging.info(f"Extracted card_last_4_digits: {card_digits}")
    else:
        logging.warning("Could not extract card_last_4_digits for Axis")
    
    # Extract billing period
    # Pattern: Statement Period Payment Due Date ... 16/04/2021 - 15/05/2021 04/06/2021
    pattern = r'Statement\s+Period.*?(\d{1,2}/\d{1,2}/\d{4}\s*-\s*\d{1,2}/\d{1,2}/\d{4})'
    billing_period = find_pattern(text, pattern, 1)
    if billing_period:
        result["billing_period"] = normalize_date(billing_period)
        logging.info(f"Extracted billing_period: {billing_period}")
    else:
        logging.warning("Could not extract billing_period for Axis")
    
    # Extract payment due date
    # Pattern: Payment Due Date ... 04/06/2021 (after the billing period dates)
    pattern = r'Payment\s+Due\s+Date.*?\d{1,2}/\d{1,2}/\d{4}\s*-\s*\d{1,2}/\d{1,2}/\d{4}\s+(\d{1,2}/\d{1,2}/\d{4})'
    due_date = find_pattern(text, pattern, 1)
    if due_date:
        result["payment_due_date"] = normalize_date(due_date)
        logging.info(f"Extracted payment_due_date: {due_date}")
    else:
        logging.warning("Could not extract payment_due_date for Axis")
    
    # Extract total amount due
    # Pattern: Total Payment Due 1,289.00 Dr (in table header)
    pattern = r'Total\s+Payment\s+Due\s+Minimum\s+Payment\s+Due.*?\s+([\d,]+\.?\d*)\s+Dr'
    amount = find_pattern(text, pattern, 1)
    if amount:
        result["total_amount_due"] = f"₹{clean_amount(amount)}"
        logging.info(f"Extracted total_amount_due: {amount}")
    else:
        logging.warning("Could not extract total_amount_due for Axis")

    # Transactions (simplified heuristic)
    # Example line: "16/04/2021 POS PURCHASE SOME MERCHANT   1,289.00 Dr"
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

    logging.info(f"Extracted {len(result['transactions'])} transactions for Axis")

    return result
