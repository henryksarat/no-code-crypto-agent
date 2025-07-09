import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

# Import the Flask app with error handling
try:
    from app_phantom import app
except ImportError as e:
    # Fallback to basic app if phantom app fails
    print(f"Warning: Could not import app_phantom: {e}")
    try:
        from app import app
    except ImportError as e2:
        print(f"Critical: Could not import any app: {e2}")
        raise

# For Vercel compatibility
app.config['TEMPLATES_AUTO_RELOAD'] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 year cache

# Export the app for Vercel
application = app

# If running locally, start the development server
if __name__ == "__main__":
    app.run(debug=True)