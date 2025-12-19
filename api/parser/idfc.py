"""
IDFC First Bank credit card statement parser
"""

import re
import logging
from .utils import find_pattern, clean_amount, normalize_date


def parse_idfc(text):
    """
    Parse IDFC First Bank credit card statement.

    Args:
        text: Extracted text from PDF

    Returns:
        dict: Parsed statement data including transactions
    """
    result = {
        "issuer": "IDFC",
        "card_last_4_digits": None,
        "billing_period": None,
        "payment_due_date": None,
        "total_amount_due": None,
        "transactions": [],
    }

    # Card last 4 digits (e.g., "Card Number XXXX XXXX XXXX 1234")
    pattern = r'Card\s+Number.*?(\d{4})'
    card_digits = find_pattern(text, pattern, 1)
    if card_digits:
        result["card_last_4_digits"] = card_digits
        logging.info(f"Extracted card_last_4_digits (IDFC): {card_digits}")
    else:
        logging.warning("Could not extract card_last_4_digits for IDFC")

    # Billing period (e.g., "Statement Period 01/11/2024 - 30/11/2024")
    pattern = r'Statement\s+Period\s+(\d{1,2}/\d{1,2}/\d{4}\s*-\s*\d{1,2}/\d{1,2}/\d{4})'
    billing_period = find_pattern(text, pattern, 1)
    if billing_period:
        result["billing_period"] = normalize_date(billing_period)
        logging.info(f"Extracted billing_period (IDFC): {billing_period}")
    else:
        logging.warning("Could not extract billing_period for IDFC")

    # Payment due date (e.g., "Payment Due Date 12/12/2024")
    pattern = r'Payment\s+Due\s+Date\s+(\d{1,2}/\d{1,2}/\d{4})'
    due_date = find_pattern(text, pattern, 1)
    if due_date:
        result["payment_due_date"] = normalize_date(due_date)
        logging.info(f"Extracted payment_due_date (IDFC): {due_date}")
    else:
        logging.warning("Could not extract payment_due_date for IDFC")

    # Total amount due (e.g., "Total Amount Due ₹ 12,345.67")
    pattern = r'Total\s+Amount\s+Due\s*(?:₹|Rs\.?)?\s*([\d,]+\.?\d*)'
    amount = find_pattern(text, pattern, 1)
    if amount:
        result["total_amount_due"] = f"₹{clean_amount(amount)}"
        logging.info(f"Extracted total_amount_due (IDFC): {amount}")
    else:
        logging.warning("Could not extract total_amount_due for IDFC")

    # Transactions section (simplified heuristic)
    # Typical line: "01/11/2024 POS PURCHASE SOME MERCHANT     1,234.56"
    tx_pattern = r'(\d{1,2}/\d{1,2}/\d{4})\s+([A-Z0-9 ,.&\-\/]+?)\s+(-?\d{1,3}(?:,\d{3})*(?:\.\d{2}))'
    for match in re.finditer(tx_pattern, text, re.IGNORECASE):
        date, description, amount_str = match.groups()
        transaction = {
            "date": normalize_date(date),
            "description": description.strip(),
            "amount": clean_amount(amount_str),
        }
        result["transactions"].append(transaction)

    logging.info(f"Extracted {len(result['transactions'])} transactions for IDFC")

    return result


