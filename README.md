## Credit Card Statement PDF Parser

A Python-based backend + simple HTML frontend for extracting structured data from credit card statement PDFs across multiple issuers.

### Overview

- **Backend**: Flask API + CLI parser in `backend/`  
- **Frontend**: Lightweight HTML/JS UI in `frontend/` that calls the backend API  
- **Parsing**: Deterministic, rule‑based text extraction with issuer‑specific parsers

### Supported Issuers

- **HDFC Bank**
- **ICICI Bank**
- **Axis Bank**
- **Chase Bank**
- **IDFC First Bank**

Each supported issuer has its own dedicated parser module under `backend/parser/`.

### Project Structure

```
CC Statement Parser/
│
├── backend/
│   ├── app.py              # Flask API server
│   ├── main.py             # CLI entry point
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── detect_issuer.py
│   │   ├── hdfc.py
│   │   ├── icici.py
│   │   ├── axis.py
│   │   ├── chase.py
│   │   ├── idfc.py
│   │   └── utils.py
│   ├── samples/            # Sample PDF statements
│   │   ├── axisbank_statement.pdf
│   │   ├── chase_statement.pdf
│   │   ├── HDFC_statement.pdf
│   │   ├── ICICI_statement.pdf
│   │   └── IDFC_statement.pdf
│   ├── requirements.txt    # Backend dependencies
│   └── parser.log          # Generated log file
│
└── frontend/
    └── index.html          # Simple web UI
```

### Sample Statements

Sample PDFs for quick testing live in `backend/samples/`:

- **Axis Bank**: `backend/samples/axisbank_statement.pdf`
- **Chase**: `backend/samples/chase_statement.pdf`
- **HDFC Bank**: `backend/samples/HDFC_statement.pdf`
- **ICICI Bank**: `backend/samples/ICICI_statement.pdf`
- **IDFC First Bank**: `backend/samples/IDFC_statement.pdf`

### Extracted Fields

For every supported statement the parser extracts at least:

1. **issuer** – Name of the issuer (`HDFC`, `ICICI`, `AXIS`, `CHASE`, `IDFC`)
2. **card_last_4_digits** – Last 4 digits of the card number
3. **billing_period** – Statement period / date range
4. **payment_due_date** – Payment due date
5. **total_amount_due** – Total amount payable
6. **transactions** – List of parsed transactions (date, description, amount) when available

If a field cannot be extracted, it is returned as `null` instead of crashing.

### Example JSON Output

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
    }
  ]
}
```

---

## Backend (CLI + API)

### 1. Setup

- **Prerequisites**
  - **Python 3.8+**
  - **pip**

- **Install dependencies**

From the project root:

```bash
cd backend
pip install -r requirements.txt
```

This installs `Flask`, `pdfplumber` and other parsing dependencies.

### 2. CLI Usage

From inside `backend/`:

```bash
python main.py <path_to_pdf>
```

**Example:**

```bash
python main.py samples/HDFC_statement.pdf
```

The CLI will:

1. Extract text from the PDF
2. Detect the credit card issuer
3. Route to the appropriate issuer parser
4. Print structured JSON to stdout
5. Log details to `parser.log`

### 3. API Server

From inside `backend/`:

```bash
python app.py
```

By default this starts a development server at `http://127.0.0.1:5000`.

- **Endpoint**: `POST /api/parse`
- **Body**: `multipart/form-data` with a single field `file` containing the PDF
- **Response**:
  - On success: `{"success": true, "file": "<uploaded_name>", "data": { ...parsed JSON... }}`
  - On error: `{"success": false, "error": "<reason>" }`

Example `curl`:

```bash
curl -X POST http://127.0.0.1:5000/api/parse \
  -F "file=@backend/samples/HDFC_statement.pdf"
```

---

## Frontend

- Located at `frontend/index.html`
- Simple single‑page UI that:
  - Lets you pick a PDF file
  - Sends it to the backend `POST /api/parse` endpoint
  - Shows the parsed JSON result or error message

### Running the Frontend

For **deployment**, the frontend is designed to work best when served from the **same origin** as the backend:

- Serve `index.html` and other static assets from the same host/port as the Flask app.
- Proxy `/api/parse` to the Flask backend (for example, via Nginx or any reverse proxy).
- The frontend uses a relative API URL (`/api/parse` by default) so everything lives under a single origin.

For **local development** you can still point it directly at a running backend on `http://127.0.0.1:5000` by opening the browser console and setting:

```js
window.API_URL_OVERRIDE = "http://127.0.0.1:5000/api/parse";
```

Then reload the page.

---

## How Parsing Works (Backend)

- **PDF Text Extraction**: Uses `pdfplumber` to extract text from all pages (text‑based PDFs only, no OCR).
- **Issuer Detection**: `parser/detect_issuer.py` looks for issuer‑specific keywords (e.g., `HDFC BANK`, `AXIS BANK`, `JPMORGAN CHASE`).
- **Issuer Parsers**: Each file in `parser/` (`hdfc.py`, `axis.py`, etc.) contains regex‑based logic tailored to that bank’s statement layout.
- **Graceful Failure**: Missing fields are logged and returned as `null`; unknown issuers raise `UnsupportedIssuerError`.

Key operations and errors are written to `backend/parser.log` for debugging.

---

## Limitations

- Works only with **text‑based PDFs** (no OCR for scanned/image PDFs).
- Parsers are **layout‑specific** – if a bank substantially changes its statement format, the corresponding parser may need updates.
- Primarily tuned for **Indian Rupee (₹)** style amounts and the bundled sample statements.

---

## Development Notes

- To add a new issuer, create a parser module in `backend/parser/`, wire it into `detect_issuer.py` and the parser mapping in `backend/main.py`, and add at least one sample PDF under `backend/samples/`.
- Follow basic PEP 8 style and log both successes and failures when extracting fields to keep `parser.log` useful.

---

## License & Usage

This is an **educational/demo** project.  
Always verify parsed results against the original statements before using them for any financial decisions.
