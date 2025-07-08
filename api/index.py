import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

# Import the Flask app
from app_phantom import app

# For Vercel, we need to export the app
# This is the WSGI application that Vercel will use
def handler(request):
    return app(request.environ, lambda status, headers: None)

# Export the app for Vercel
application = app

# If running locally, start the development server
if __name__ == "__main__":
    app.run(debug=True)