# run_backend.py - Production backend runner for Windows service
"""Production Flask backend runner optimized for Windows services."""

import os
import sys
from pathlib import Path

# Ensure we can find our modules
sys.path.insert(0, str(Path(__file__).parent))

# Set production environment
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'
os.environ['UPLOAD_FOLDER'] = r'C:\Verificator Preturi App\assets'

def main():
    """Run the Flask application in production mode."""
    try:
        from app import create_app
        from waitress import serve
        
        print("Starting Campaign Manager Backend Service")
        print(f"Assets folder: {os.environ['UPLOAD_FOLDER']}")
        print("Server will be available at: http://192.168.103.111:5000")
        
        # Create Flask app
        app = create_app()
        
        # Ensure assets folder exists
        assets_path = Path(os.environ['UPLOAD_FOLDER'])
        assets_path.mkdir(parents=True, exist_ok=True)
        
        print(f"Assets folder ready: {assets_path}")
        print("Starting Waitress WSGI server...")
        
        # Use Waitress for production WSGI server
        serve(
            app,
            host='0.0.0.0',  # Listen on all interfaces
            port=5000,
            threads=4,
            channel_timeout=300,
            cleanup_interval=30,
            log_socket_errors=True
        )
        
    except KeyboardInterrupt:
        print("Service stopped by user")
    except Exception as e:
        print(f"ERROR: Service failed to start: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()