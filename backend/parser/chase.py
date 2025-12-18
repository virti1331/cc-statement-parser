"""
Chase credit card statement parser
"""

import re
import logging
from .utils import find_pattern, clean_amount, normalize_date


def parse_chase(text):
    """
    Parse Chase credit card statement.

    Args:
        text: Extracted text from PDF

    Returns:
        dict: Parsed statement data including transactions
    """
    result = {
        "issuer": "CHASE",
        "card_last_4_digits": None,
        "billing_period": None,
        "payment_due_date": None,
        "total_amount_due": None,
        "transactions": [],
    }

    # Card last 4 digits (e.g., "Account Number: ************1234")
    pattern = r'Account\s+Number.*?(\d{4})'
    card_digits = find_pattern(text, pattern, 1)
    if card_digits:
        result["card_last_4_digits"] = card_digits
        logging.info(f"Extracted card_last_4_digits (CHASE): {card_digits}")
    else:
        logging.warning("Could not extract card_last_4_digits for Chase")

    # Billing period (e.g., "Opening/Closing Date 11/01/24 - 11/30/24")
    pattern = r'(?:Opening/Closing\s+Date|Statement\s+Period)\s+(\d{1,2}/\d{1,2}/\d{2,4}\s*-\s*\d{1,2}/\d{1,2}/\d{2,4})'
    billing_period = find_pattern(text, pattern, 1)
    if billing_period:
        result["billing_period"] = normalize_date(billing_period)
        logging.info(f"Extracted billing_period (CHASE): {billing_period}")
    else:
        logging.warning("Could not extract billing_period for Chase")

    # Payment due date (e.g., "Payment Due Date 12/25/24")
    pattern = r'Payment\s+Due\s+Date\s+(\d{1,2}/\d{1,2}/\d{2,4})'
    due_date = find_pattern(text, pattern, 1)
    if due_date:
        result["payment_due_date"] = normalize_date(due_date)
        logging.info(f"Extracted payment_due_date (CHASE): {due_date}")
    else:
        logging.warning("Could not extract payment_due_date for Chase")

    # Total amount due (e.g., "New Balance $1,234.56" or "Total Payment Due $1,234.56")
    pattern = r'(?:New\s+Balance|Total\s+Payment\s+Due)\s+\$?([\d,]+\.\d{2})'
    amount = find_pattern(text, pattern, 1)
    if amount:
        result["total_amount_due"] = clean_amount(amount)
        logging.info(f"Extracted total_amount_due (CHASE): {amount}")
    else:
        logging.warning("Could not extract total_amount_due for Chase")

    # Transactions section (simplified heuristic)
    # Typical line: "11/05 PURCHASE SOME MERCHANT      123.45"
    tx_pattern = r'(\d{1,2}/\d{1,2})\s+([A-Z0-9 ,.&\-\/]+?)\s+(-?\d{1,3}(?:,\d{3})*(?:\.\d{2}))'
    for match in re.finditer(tx_pattern, text, re.IGNORECASE):
        date, description, amount_str = match.groups()
        transaction = {
            "date": normalize_date(date),
            "description": description.strip(),
            "amount": clean_amount(amount_str),
        }
        result["transactions"].append(transaction)

    logging.info(f"Extracted {len(result['transactions'])} transactions for Chase")

    return result


