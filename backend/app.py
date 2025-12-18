"""
Backend API server for the Credit Card Statement Parser.

Run with:
    python app.py

The frontend (HTML/JS) should live separately and call this API.
"""

import os
import tempfile

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

from main import parse_statement
from parser.detect_issuer import UnsupportedIssuerError


app = Flask(__name__)

ALLOWED_EXTENSIONS = {"pdf"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.after_request
def add_cors_headers(response):
    """
    Add very simple CORS headers so a separate frontend can call this API.
    Adjust origins for production deployments.
    """
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return response


@app.route("/api/parse", methods=["POST"])
def api_parse():
    """
    Parse an uploaded PDF and return JSON with statement + transactions.
    Expects form-data with a single field: "file" (PDF).
    """
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file part in the request."}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"success": False, "error": "No file selected."}), 400

    if not allowed_file(file.filename):
        return jsonify({"success": False, "error": "Unsupported file type. Please upload a PDF."}), 400

    filename = secure_filename(file.filename)

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name

        parsed = parse_statement(tmp_path)
        return jsonify({"success": True, "file": filename, "data": parsed})

    except UnsupportedIssuerError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to parse statement: {e}"}), 500
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


if __name__ == "__main__":
    # Simple development server; for production use a proper WSGI server
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)

