import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

# Import the Flask app
from app_phantom import app

# This is the WSGI application that Vercel will use
def handler(request, response):
    return app(request, response)

# For Vercel, we need to export the app
app = app

# If running locally, start the development server
if __name__ == "__main__":
    app.run(debug=True)