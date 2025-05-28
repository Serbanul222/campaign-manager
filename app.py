"""Flask application factory for the campaign manager."""

from flask import Flask, jsonify, send_from_directory, abort
from flask_cors import CORS
from pathlib import Path
import os

from config import Config
from database.db_setup import init_app


def register_blueprints(app: Flask) -> None:
    """Register available blueprints if their modules exist."""
    blueprints = [
        ("auth.routes", "bp", "/api/auth"),
        ("api.campaigns", "campaign_bp", "/api/campaigns"),
        ("api.users", "users_bp", "/api/users"),
        ("api.uploads", "uploads_bp", "/api/uploads"),
    ]
    
    registered_routes = []
    
    for module_name, blueprint_name, url_prefix in blueprints:
        try:
            module = __import__(module_name, fromlist=[blueprint_name])
            blueprint = getattr(module, blueprint_name)
            app.register_blueprint(blueprint, url_prefix=url_prefix)
            registered_routes.append(f"✅ {module_name} -> {url_prefix}")
            print(f"✅ Registered blueprint: {module_name} at {url_prefix}")
        except Exception as e:
            registered_routes.append(f"❌ {module_name} -> ERROR: {str(e)}")
            app.logger.warning(f"❌ Could not register blueprint from {module_name}: {str(e)}")
    
    return registered_routes


def create_app(config_class: type[Config] = Config) -> Flask:
    """Application factory used by Flask."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app, 
         origins=["http://localhost:5173", "http://127.0.0.1:5173"], 
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         supports_credentials=True)

    init_app(app)
    registration_status = register_blueprints(app)
    
    # Image serving endpoints
    @app.route("/api/images/<path:filepath>")
    def serve_image(filepath):
        """Serve images from the assets directory."""
        try:
            upload_folder = app.config.get('UPLOAD_FOLDER', 'assets')
            full_path = Path(upload_folder) / filepath
            
            # Security check
            if not str(full_path.resolve()).startswith(str(Path(upload_folder).resolve())):
                abort(403)
            
            if not full_path.exists():
                print(f"Image not found: {full_path}")
                abort(404)
            
            return send_from_directory(
                directory=str(full_path.parent),
                path=full_path.name,
                as_attachment=False
            )
            
        except Exception as e:
            print(f"Error serving image {filepath}: {e}")
            abort(404)
    
    @app.route("/api/campaigns/<int:campaign_id>/images")
    def get_campaign_images(campaign_id):
        """Get all images for a specific campaign."""
        from models import Campaign, CampaignImage
        
        campaign = Campaign.query.get_or_404(campaign_id)
        images = CampaignImage.query.filter_by(campaign_id=campaign_id).all()
        
        image_data = {}
        for img in images:
            try:
                # Convert absolute path to relative URL
                relative_path = Path(img.file_path).relative_to(Path(app.config.get('UPLOAD_FOLDER', 'assets')))
                image_url = f"/api/images/{relative_path}".replace("\\", "/")
                
                image_data[img.image_type] = {
                    "url": image_url,
                    "path": img.file_path,
                    "uploaded_at": img.uploaded_at.isoformat() if img.uploaded_at else None
                }
            except Exception as e:
                print(f"Error processing image {img.file_path}: {e}")
        
        return jsonify({
            "campaign_id": campaign_id,
            "images": image_data
        })
    
    # Test routes
    @app.route("/api/health")
    def health_check():
        return jsonify({
            "status": "ok", 
            "message": "Campaign Manager API is running",
            "registered_blueprints": registration_status,
            "upload_folder": app.config.get('UPLOAD_FOLDER', 'assets')
        })
    
    @app.route("/api/routes")
    def list_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                "endpoint": rule.endpoint,
                "methods": [m for m in rule.methods if m not in ['HEAD', 'OPTIONS']],
                "url": str(rule)
            })
        return jsonify({"routes": sorted(routes, key=lambda x: x['url'])})
    
    @app.before_request
    def handle_preflight():
        from flask import request
        if request.method == "OPTIONS":
            response = jsonify({'status': 'ok'})
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add('Access-Control-Allow-Headers', "*")
            response.headers.add('Access-Control-Allow-Methods', "*")
            return response
    
    return app


if __name__ == "__main__":
    flask_app = create_app()
    print("\n" + "="*50)
    print("🚀 Starting Campaign Manager API")
    print("="*50)
    print("📍 Backend: http://localhost:5000")
    print("🔗 API Base: http://localhost:5000/api")
    print("🖼️ Images: http://localhost:5000/api/images/")
    print("🧪 Test endpoints:")
    print("   - http://localhost:5000/api/health")
    print("   - http://localhost:5000/api/routes")
    print("="*50)
    flask_app.run(host="0.0.0.0", port=5000, debug=True)