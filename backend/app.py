"""
Simple Flask API server for Credit Card Statement Parser
"""

import os
import tempfile
from pathlib import Path

from flask import Flask, request, jsonify, send_from_directory

from backend.main import parse_statement
from parser.detect_issuer import UnsupportedIssuerError

app = Flask(__name__, static_folder=None)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_UPLOAD_SIZE', 16 * 1024 * 1024))  # 16MB

# Frontend directory - resolve to absolute path
FRONTEND_DIR = (Path(__file__).parent.parent / 'frontend').resolve()

# Verify frontend directory exists
if not FRONTEND_DIR.exists():
    raise FileNotFoundError(f"Frontend directory not found: {FRONTEND_DIR}")


@app.after_request
def add_cors_headers(response):
    """Add CORS headers"""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    return response


# API routes must be defined BEFORE catch-all routes
@app.route('/api/parse', methods=['POST', 'OPTIONS'])
def api_parse():
    """Parse uploaded PDF statement"""
    if request.method == 'OPTIONS':
        return '', 200
    
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file provided"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No file selected"}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"success": False, "error": "Only PDF files are supported"}), 400
    
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name
        
        parsed = parse_statement(tmp_path)
        return jsonify({"success": True, "file": file.filename, "data": parsed})
    
    except UnsupportedIssuerError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to parse: {str(e)}"}), 500
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except:
                pass


# Catch-all route for frontend (must be last)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve frontend files"""
    # Don't catch API routes
    if path and path.startswith('api/'):
        return jsonify({"success": False, "error": "API endpoint not found"}), 404
    
    # Serve index.html for root or empty path
    if not path or path == '/':
        return send_from_directory(str(FRONTEND_DIR), 'index.html')
    
    # Security: prevent directory traversal
    safe_path = os.path.normpath(path).lstrip('/')
    if '..' in safe_path or safe_path.startswith('/'):
        return jsonify({"success": False, "error": "Invalid path"}), 400
    
    # Try to serve the requested file
    file_path = FRONTEND_DIR / safe_path
    # Ensure file is within frontend directory (prevent directory traversal)
    try:
        file_path.resolve().relative_to(FRONTEND_DIR.resolve())
    except ValueError:
        return jsonify({"success": False, "error": "Invalid path"}), 400
    
    if file_path.exists() and file_path.is_file():
        return send_from_directory(str(FRONTEND_DIR), safe_path)
    
    # Fallback to index.html for SPA routing
    return send_from_directory(str(FRONTEND_DIR), 'index.html')


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
