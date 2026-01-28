"""
WSGI entry point for Flask application
Used by production servers like Gunicorn
"""
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app
from app import app

if __name__ == "__main__":
    # Get port from environment or use 5000 as default
    port = int(os.environ.get('PORT', 5000))
    
    # Get debug mode from environment (should be False in production)
    debug = os.environ.get('DEBUG', 'False') == 'True'
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=debug)
