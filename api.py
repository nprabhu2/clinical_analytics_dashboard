"""
Clinical Trials Analytics REST API

A simple Flask-based REST API for clinical trial data analysis.
Provides basic capabilities for CSV upload and summary statistics generation.

Available Endpoints:
- POST /api/upload - Upload CSV file and get summary statistics
- GET /api/summary - Get summary statistics from default data file

All endpoints return JSON responses with proper error handling.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import traceback
import logging
import os
import tempfile
from werkzeug.utils import secure_filename
from analytics import (
    load_data, 
    calculate_summary_statistics
)

# Initialize Flask application
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enable CORS (Cross-Origin Resource Sharing) for all routes
# This allows the API to be accessed from web browsers and other domains
CORS(app)

# Configuration for file uploads
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def not_found(error):
    """
    Handle 404 errors when endpoints are not found.
    
    Args:
        error: The 404 error object
        
    Returns:
        JSON response with error message and 404 status code
    """
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """
    Handle 500 errors for internal server issues.
    
    Args:
        error: The 500 error object
        
    Returns:
        JSON response with error message and 500 status code
    """
    return jsonify({'error': 'Internal server error', 'details': str(error)}), 500


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.route('/api/upload', methods=['POST'])
def upload_csv():
    """
    Upload a CSV file and return summary statistics.
    
    Expected CSV format:
    - Columns: patient_id, trial_site, enrollment_date, age, adverse_event, completed_trial
    - File size limit: 16MB
    - File type: CSV only
    
    Returns:
        JSON response with summary statistics and validation results
    """
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only CSV files are allowed.'}), 400
        
        # Secure the filename and save temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)
        
        logger.info(f"Processing uploaded file: {filename}")
        
        try:
            # Load and validate the uploaded CSV data
            df = load_data(temp_path)
            
            # Calculate summary statistics
            stats = calculate_summary_statistics(df)
            
            # Add file processing info to response
            stats['file_info'] = {
                'filename': filename,
                'total_records': len(df),
                'status': 'success'
            }
            
            logger.info(f"Successfully processed {filename} with {len(df)} records")
            
            return jsonify(stats)
            
        except Exception as e:
            logger.error(f"Error processing file {filename}: {str(e)}")
            return jsonify({
                'error': f'Error processing CSV file: {str(e)}',
                'file_info': {
                    'filename': filename,
                    'status': 'error'
                }
            }), 400
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                logger.info(f"Cleaned up temporary file: {temp_path}")
    
    except Exception as e:
        logger.error(f"Unexpected error in upload endpoint: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/summary', methods=['GET'])
def get_summary_statistics():
    """
    Get summary statistics from the default clinical trial data file.
    
    Returns key metrics including:
    - Total patient count
    - Patient distribution by site
    - Average age
    - Completion and adverse event rates
    
    Returns:
        JSON response with summary statistics
    """
    try:
        logger.info("Generating summary statistics from default data file")
        df = load_data()
        stats = calculate_summary_statistics(df)
        
        # Add data source info
        stats['data_source'] = 'default_file'
        stats['total_records'] = len(df)
        
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error generating summary statistics: {str(e)}")
        return jsonify({'error': str(e)}), 500



# =============================================================================
# APPLICATION STARTUP
# =============================================================================

if __name__ == '__main__':
    """
    Start the Flask development server.
    
    The server will run on:
    - Host: 0.0.0.0 (accessible from all network interfaces)
    - Port: 8000
    - Debug mode: enabled (for development)
    
    To run the API:
    flask run --host=0.0.0.0 --port=8000
    
    Then visit:
    - http://localhost:8000/api/summary for default data summary
    """
    logger.info("Starting Clinical Trials Analytics API on port 8000")
    app.run(debug=True, host='0.0.0.0', port=8000)
