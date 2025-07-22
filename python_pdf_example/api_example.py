#!/usr/bin/env python3
"""
Simple Flask API example for Python PDF generation.

This demonstrates how the Python PDF generator could be deployed
as a microservice that the main C# application could call.

Usage:
    pip install flask
    python api_example.py
    
    # Test with:
    curl -X POST http://localhost:5001/generate-pdf \
      -H "Content-Type: application/json" \
      -H "X-Submission-ID: 12345" \
      -d @sample_data.json \
      --output test_output.pdf
"""

import os
import json
from flask import Flask, request, send_file, jsonify
from tempfile import NamedTemporaryFile
from pdf_generator import AccommodationFormPDFGenerator

app = Flask(__name__)

# Configure for production
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "accommodation-form-pdf-generator",
        "version": "1.0.0"
    })


@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    """
    Generate PDF from form data.
    
    Expects JSON form data in request body matching C# FormData structure.
    Returns PDF file as attachment.
    """
    try:
        # Get form data from request
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        form_data = request.get_json()
        if not form_data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Get optional parameters
        submission_id = request.headers.get('X-Submission-ID')
        backend = request.args.get('backend', 'reportlab')  # Default to reportlab
        
        if backend not in ['reportlab', 'fpdf']:
            return jsonify({"error": "Backend must be 'reportlab' or 'fpdf'"}), 400
        
        # Validate required fields
        if 'TenantDetails' not in form_data:
            return jsonify({"error": "TenantDetails section is required"}), 400
        
        if 'FullName' not in form_data['TenantDetails']:
            return jsonify({"error": "FullName is required in TenantDetails"}), 400
        
        # Generate PDF
        generator = AccommodationFormPDFGenerator(backend=backend)
        filename = generator.generate_filename(form_data)
        
        # Use temporary file that gets cleaned up automatically
        with NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            generator.generate_pdf_from_json(form_data, temp_file.name, submission_id)
            
            # Send file and clean up
            def cleanup():
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
            
            return send_file(
                temp_file.name,
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf'
            )
    
    except ImportError as e:
        return jsonify({
            "error": f"PDF backend not available: {str(e)}",
            "suggestion": "Install required dependencies: pip install reportlab fpdf2"
        }), 500
    
    except Exception as e:
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500


@app.route('/generate-pdf-info', methods=['POST'])
def generate_pdf_info():
    """
    Get PDF generation info without actually generating the PDF.
    Useful for filename preview, validation, etc.
    """
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        form_data = request.get_json()
        if not form_data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        generator = AccommodationFormPDFGenerator()
        filename = generator.generate_filename(form_data)
        
        return jsonify({
            "filename": filename,
            "available_backends": ["reportlab", "fpdf"],
            "form_sections_detected": list(form_data.keys()),
            "tenant_name": form_data.get('TenantDetails', {}).get('FullName', 'Unknown')
        })
    
    except Exception as e:
        return jsonify({"error": f"Info generation failed: {str(e)}"}), 500


@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File too large. Maximum size is 16MB"}), 413


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404


if __name__ == '__main__':
    print("Starting Flask PDF Generation API...")
    print("Available endpoints:")
    print("  GET  /health              - Health check")
    print("  POST /generate-pdf        - Generate PDF from form data")
    print("  POST /generate-pdf-info   - Get PDF info without generating")
    print("")
    print("Example usage:")
    print("  curl -X POST http://localhost:5001/generate-pdf \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -H 'X-Submission-ID: 12345' \\")
    print("    -d '{\"TenantDetails\":{\"FullName\":\"John Doe\"}}' \\")
    print("    --output output.pdf")
    
    app.run(host='0.0.0.0', port=5001, debug=True)