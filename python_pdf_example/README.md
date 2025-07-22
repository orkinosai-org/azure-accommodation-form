# Python PDF Generation Example

This directory contains a Python implementation for generating PDFs from Azure Accommodation Form data, demonstrating how the PDF generation could be implemented using Python libraries as an alternative to the existing C# solution.

## Overview

The main application uses a comprehensive C# implementation with iTextSharp for PDF generation (`BlazorApp/Services/PdfGenerationService.cs`). This Python example provides an alternative approach using popular Python PDF libraries.

## Features

- **Multiple backends**: Supports both ReportLab (advanced) and FPDF (simple)
- **Compatible data format**: Accepts the same JSON structure as the C# implementation
- **Filename generation**: Matches the C# naming convention (`FirstName_LastName_Application_Form_DDMMYYYYHHMM.pdf`)
- **Complete form coverage**: Handles all 12 form sections like the C# version

## Libraries Used

### ReportLab (Recommended)
- More advanced PDF features
- Better formatting and styling options
- Professional document layout
- Industry standard for Python PDF generation

### FPDF (Alternative)
- Simpler implementation
- Smaller dependency footprint
- Good for basic PDF needs
- Easier to understand for beginners

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install individually
pip install reportlab fpdf2
```

## Usage

### Basic Usage

```python
from pdf_generator import AccommodationFormPDFGenerator

# Sample form data (matches C# FormData structure)
form_data = {
    "TenantDetails": {
        "FullName": "John Doe",
        "Email": "john@example.com",
        # ... other fields
    },
    "BankDetails": {
        "BankName": "Example Bank",
        # ... other fields
    }
    # ... other sections
}

# Generate PDF with ReportLab
generator = AccommodationFormPDFGenerator(backend="reportlab")
filename = generator.generate_filename(form_data)
output_path = f"/path/to/output/{filename}"
generator.generate_pdf_from_json(form_data, output_path, "SUBMISSION-ID")
```

### Testing

Run the test script to see both backends in action:

```bash
python test_pdf.py
```

This will:
- Generate sample PDFs using both ReportLab and FPDF
- Save them to `/tmp/python_pdf_test/`
- Show file sizes and success status

## Integration with Main Application

While the C# implementation is the primary production solution, this Python code could be integrated as:

1. **Microservice**: Separate Python service for PDF generation
2. **Alternative backend**: Replace C# service with Python equivalent
3. **Backup solution**: Fallback PDF generation method
4. **Development reference**: Example for Python developers

## API Integration Example

```python
# Example Flask API endpoint
from flask import Flask, request, send_file
from pdf_generator import AccommodationFormPDFGenerator

app = Flask(__name__)

@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    form_data = request.get_json()
    submission_id = request.headers.get('X-Submission-ID')
    
    generator = AccommodationFormPDFGenerator()
    filename = generator.generate_filename(form_data)
    output_path = f"/tmp/{filename}"
    
    generator.generate_pdf_from_json(form_data, output_path, submission_id)
    
    return send_file(output_path, 
                    as_attachment=True, 
                    download_name=filename,
                    mimetype='application/pdf')
```

## File Structure

```
python_pdf_example/
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── pdf_generator.py       # Main PDF generation class
└── test_pdf.py           # Test script with sample data
```

## Comparison with C# Implementation

| Feature | C# (iTextSharp) | Python (ReportLab) | Python (FPDF) |
|---------|-----------------|-------------------|---------------|
| Advanced formatting | ✅ | ✅ | ⚠️ Basic |
| Professional layout | ✅ | ✅ | ⚠️ Simple |
| Integration | ✅ Native | 🔧 Requires setup | 🔧 Requires setup |
| Performance | ✅ Fast | ✅ Good | ✅ Fast |
| Maintenance | ✅ In use | ⚠️ Additional | ⚠️ Additional |

## Production Considerations

**Current Status**: The C# implementation is production-ready and actively used.

**If using Python in production**:
- Set up proper error handling and logging
- Add input validation and sanitization  
- Configure proper file storage and cleanup
- Implement rate limiting and security measures
- Add monitoring and health checks
- Consider containerization for deployment

## Notes

- This is a **reference implementation** to demonstrate Python PDF capabilities
- The **production application uses the C# implementation** which is fully integrated
- Both approaches generate equivalent PDF outputs with the same data structure
- Choose the approach that best fits your technology stack and requirements

## Dependencies

See `requirements.txt` for exact versions:
- `reportlab>=4.0.4` - Advanced PDF generation
- `fpdf2>=2.7.6` - Simple PDF generation  
- `requests>=2.31.0` - HTTP client (for API integration)