# Credit Card Statement PDF Parser

A production-ready Python-based system for extracting structured data from credit card statement PDFs across multiple issuers.

## Overview

This parser uses deterministic, rule-based text extraction to parse credit card statements from 5 major Indian credit card issuers. It extracts key fields using regex patterns and keyword anchors, providing consistent JSON-like output regardless of the issuer.

## Supported Issuers

- **HDFC Bank**
- **ICICI Bank**
- **Axis Bank**
- **Chase Bank**
- **IDFC First Bank**

Each supported issuer has its own dedicated parser module to handle layout-specific variations.

## Sample Statements

The `samples/` directory contains example credit card statements you can use for testing:

- **Axis Bank**: `samples/axisbank_statement.pdf`
- **Chase**: `samples/chase_statement.pdf`
- **HDFC Bank**: `samples/HDFC_statement.pdf`
- **ICICI Bank**: `samples/ICICI_statement.pdf`
- **IDFC First Bank**: `samples/IDFC_statement.pdf`

## Extracted Fields

For every supported statement the parser extracts:

1. **issuer** - Name of the credit card issuer (e.g., "HDFC", "ICICI", "AXIS", "CHASE", "IDFC")
2. **card_last_4_digits** - Last 4 digits of the card number
3. **billing_period** - Statement period/date range
4. **payment_due_date** - Payment due date
5. **total_amount_due** - Total amount payable
6. **transactions** - List of parsed transactions (date, description, amount)

### Output Format

```json
{
  "issuer": "HDFC",
  "card_last_4_digits": "4341",
  "billing_period": "23/10/2024",
  "payment_due_date": "12/11/2024",
  "total_amount_due": "₹83,794.00",
  "transactions": [
    {
      "date": "23/10/2024",
      "description": "AMAZON PURCHASE",
      "amount": "1,234.56"
    },
    {
      "date": "24/10/2024",
      "description": "REFUND SOME MERCHANT",
      "amount": "-500.00"
    }
  ]
}
```

If a field cannot be extracted, it returns `null` instead of crashing.

## Project Structure

```
credit_card_parser/
│
├── parser/
│   ├── __init__.py           # Package initialization
│   ├── detect_issuer.py      # Issuer detection logic
│   ├── hdfc.py               # HDFC Bank parser
│   ├── icici.py              # ICICI Bank parser
│   ├── axis.py               # Axis Bank parser
│   ├── chase.py              # Chase Bank parser
│   ├── idfc.py               # IDFC First Bank parser
│   └── utils.py              # Shared utility functions
│
├── samples/                   # Place sample PDFs here
│
├── main.py                    # Entry point
├── requirements.txt           # Python dependencies
├── parser.log                 # Generated log file
└── README.md                  # This file
```

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. **Clone or download this repository**

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

This will install:
- `pdfplumber` - For PDF text extraction

## Usage

### Basic Usage

```bash
python main.py <path_to_pdf>
```

### Example

```bash
python main.py samples/hdfc_statement.pdf
```

### Output

The parser will:
1. Extract text from the PDF
2. Detect the credit card issuer
3. Parse relevant fields
4. Print structured JSON output
5. Log all operations to `parser.log`

### Sample Output

**HDFC Bank Example:**
```
============================================================
PARSED STATEMENT DATA
============================================================
{
  "issuer": "HDFC",
  "card_last_4_digits": "4341",
  "billing_period": "23/10/2024",
  "payment_due_date": "12/11/2024",
  "total_amount_due": "₹83,794.00"
}
============================================================
```

**Axis Bank Example:**
```PDF Text Extraction

The parser uses `pdfplumber` library to extract text from PDF files:
- Reads all pages sequentially
- Extracts text content line by line
- Preserves text structure and spacing
- Works with text-based PDFs (no OCR for scanned documents)

### 2. Issuer Detection

The system identifies the issuer by searching for unique keywords in the extracted text:

- **HDFC Bank**: Pattern matches "HDFC BANK" (case-insensitive)
- **ICICI Bank**: Pattern matches "ICICI BANK"
- **Axis Bank**: Pattern matches "AXIS BANK"
- **Chase Bank**: Pattern matches "CHASE BANK" or "JPMORGAN CHASE"
- **IDFC First Bank**: Pattern matches "IDFC FIRST BANK" or "IDFC BANK"

If no issuer is detected, the system raises an `UnsupportedIssuerError` with a clear message listing supported issuers.

### 3. Field Extraction with Regex Patterns

Each issuer has a dedicated parser module with custom regex patterns tailored to their specific statement format:

#### HDFC Bank Patterns:
- **Card Number**: `Card No: 4341 55XX XXXX 3388` → Extracts first 4 digits
- **Billing Period**: `Statement Date:23/10/2024` → Extracts date
- **Payment Due Date**: Table format with "Payment Due Date Total Dues" header → Extracts date from next line
- **Total Amount**: Parses table row: `12/11/2024 83,794.00 4,240.00` → Second value is total dues

#### Axis Bank Patterns:
- **Card Number**: `Credit Card Number 53346700****1060` → Extracts last 4 digits after asterisks
- **Billing Period**: `Statement Period 16/04/2021 - 15/05/2021` → Extracts date range
- **Payment Due Date**: Extracts date after billing period in same line
- **Total Amount**: `Total Payment Due ... 1,289.00 Dr` → Extracts amount before "Dr"

### 4. Parsing Strategy

Each parser follows this approach:
- **Multiple Pattern Attempts**: Tries primary pattern, falls back to alternative patterns if first fails
- **Keyword Anchors**: Searches for field labels (e.g., "Payment Due Date", "Total Amount")
- **Flexible Matching**: Uses `.*?` to handle variable spacing and formatting
- **Graceful Degradation**: Returns `None` for missing fields, never crashes the program
- **Logging**: Records success/failure for each field extraction attempt

### 5. Output Normalization

The parser ensures consistent output format:
- All amounts prefixed with ₹ symbol
- Dates preserved in original format (normalized via `normalize_date()`)
- Missing fields returned as `null` in JSON output
- Clean formatting with indented JSON structure

### 6. Logging System

All operations are logged to `parser.log` with timestamps:
```
2025-12-17 14:27:50,960 - INFO - Processing PDF: samples/axisbank_statement.pdf
2025-12-17 14:27:50,959 - INFO - Extracted 2540 characters from PDF
2025-12-17 14:27:50,960 - INFO - Detected issuer: Axis Bank
2025-12-17 14:27:50,960 - INFO - Extracted card_last_4_digits: 1060
2025-12-17 14:27:50,961 - INFO - Extracted billing_period: 16/04/2021 - 15/05/2021
2025-12-17 14:27:50,961 - INFO - Extracted payment_due_date: 04/06/2021
2025-12-17 14:27:50,962 - INFO - Extracted total_amount_due: 1,289.00
2025-12-17 14:27:50,962 - INFO - Parsing completed successfully
```

Logs include:
- PDF processing start
- Character count extracted
- Axis Bank: "AXIS BANK"

If no issuer is detected, it raises a clear error message.

### 2. Parsing Strategy

Each issuer has a dedicated parser module that:
- Uses regex patterns with keyword anchors
- Searches for fields using common statement terminology
- Handles multiple format variations
- Returns `None` for missing fields instead of crashing

### 3. Logging

All operations are logged to `parser.log` with:
- Issuer detection results
- Field extraction successes/failures
- Warnings for missing data
- Error details for debugging

## Error Handling

The parser is designed for graceful failure:

- **Missing Fields**: Logs a warning and returns `None`
- **Unknown Issuer**: Raises `UnsupportedIssuerError` with clear message
- **File Not Found**: Raises `FileNotFoundError`
- **Empty PDF**: Raises `ValueError`

The program never crashes due to missing patterns - it continues extracting remaining fields.

## Known Limitations

1. **Text-based PDFs only**: Does not support image-based/scanned PDFs (OCR not implemented)
2. **Format-specific patterns**: Regex patterns are tailored to specific statement layouts. If bank changes format, patterns may need updates
3. **Date format variations**: Dates are preserved as-is from PDF (not converted to standard format)
4. **Multi-page statements**: Extracts from all pages sequentially but doesn't validate field consistency across pages
5. **Currency symbols**: Primarily designed for Indian rupee (₹) formatted statements
6. **Parser customization**: Each issuer requires custom regex patterns based on their specific statement format
7. **Statement variations**: Different card types from same issuer may have slightly different formats requiring pattern adjustments

## Future Improvements

### Short-term
- Add support for more credit card issuers (Kotak, Standard Chartered, etc.)
- Improve date normalization to handle more formats
- Add transaction-level parsing (individual purchase details)
- Support for EMI details extraction

### Medium-term
- OCR support for scanned/image-based PDFs using Tesseract
- Multi-statement batch processing
- Export to CSV/Excel formats
- REST API wrapper for integration

### Long-term
- Machine learning-based field detection for better accuracy
- Support for international card issuers
- Web interface for easier usage
- Database integration for storing parsed data

## Troubleshooting

### Parser doesn't detect issuer
- **Check PDF type**: Ensure the PDF is text-based (not scanned image)
- **Verify issuer name**: Look for issuer name prominently displayed in PDF
- **Check logs**: Review `parser.log` for detection attempts and failures
- **Manual verification**: Open PDF and confirm it contains text like "HDFC BANK" or "AXIS BANK"

### Fields returning null
- **Statement format changed**: Bank may have updated their statement layout
- **Non-standard terminology**: Statement uses different field labels than expected
- **Check logs**: Review `parser.log` to see which patterns were attempted
- **Debug approach**:
  1. Run `python -c "import pdfplumber; print(pdfplumber.open('your.pdf').pages[0].extract_text())"` to see raw text
  2. Identify the actual pattern in the text
  3. Update the regex pattern in the respective parser file (e.g., `parser/hdfc.py`)

### Import errors
- **Install dependencies**: Run `pip install -r requirements.txt`
- **Check Python version**: Run `python --version` (requires 3.7+)
- **Virtual environment**: Consider using `venv` to isolate dependencies

### Incorrect data extracted
- **Pattern mismatch**: The regex may be matching wrong section of text
- **Multiple matches**: Pattern may be finding first occurrence instead of correct one
- **Solution**: Adjust regex patterns in the issuer-specific parser file to be more precise

## Development

### Adding a New Issuer

Follow these steps to add support for a new credit card issuer:

1. **Create Parser File**: Create `parser/new_issuer.py`
   ```python
   def parse_new_issuer(text):
       result = {
           "issuer": "NEW_ISSUER",
           "card_last_4_digits": None,
           "billing_period": None,
           "payment_due_date": None,
           "total_amount_due": None
       }
       
       # Add regex patterns for each field
       # Example: pattern = r'Card\s+No:\s*(\d{4})'
       # Use utils.find_pattern() for extraction
       
       return result
   ```

2. **Add Issuer Detection**: Update `parser/detect_issuer.py`
   ```python
   if re.search(r'NEW\s+ISSUER', text_upper):
       logging.info("Detected issuer: New Issuer")
       return "NEW_ISSUER"
   ```

3. **Export Parser**: Update `parser/__init__.py`
   ```python
   from .new_issuer import parse_new_issuer
   __all__ = [..., 'parse_new_issuer']
   ```

4. **Add Routing**: Update `main.py` parsers dictionary
   ```python
   parsers = {
       ...,
       "NEW_ISSUER": parse_new_issuer
   }
   ```

5. **Test Thoroughly**: Run with sample PDF and check `parser.log` for any issues

### Debugging Regex Patterns

When creating patterns for a new issuer:

1. **Extract raw text first**:
   ```bash
   python -c "import pdfplumber; print(pdfplumber.open('statement.pdf').pages[0].extract_text())"
   ```

2. **Test patterns interactively**:
   ```python
   import re
   text = "your extracted text"
   pattern = r'Payment\s+Due\s+Date\s+(\d{1,2}/\d{1,2}/\d{4})'
   match = re.search(pattern, text, re.IGNORECASE)
   if match:
       print(match.group(1))
   ```

3. **Use multiple fallback patterns** for robust extraction

### Code Style

- Follow PEP 8 guidelines
- Add docstrings to all functions
- Use descriptive variable names
- Keep functions small and focused (one field per pattern group)
- Log all field extraction attempts (success and failure)
- Use raw strings (`r''`) for regex patterns
- Test with multiple statement samples from same issuer

## License

This is an educational/demonstration project. Use at your own discretion.

## Support

For issues or questions:
1. Check the `parser.log` file for detailed error information
2. Ensure your PDF matches the expected format for your issuer
3. Verify all dependencies are properly installed

---

**Note**: This parser is designed for educational and demonstration purposes. Always verify extracted data against original statements for critical financial operations.
