# app.py - Updated Flask application with enhanced activity logging
"""Flask application factory for the campaign manager with enhanced activity logging."""

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
        ("api.logs", "bp", "/api/logs"),  # Enhanced logs blueprint
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
    
    # Enhanced CORS configuration
    CORS(app, 
         origins=["http://localhost:5173", 
         "http://127.0.0.1:5173" ,
         "http://localhost:3000",
         "http://127.0.0.1:3000",
         "http://192.168.103.111:3000",     # Add VM IP access
         "http://192.168.103.111:5173"], 
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         supports_credentials=True,
         expose_headers=["Content-Type", "Authorization"])

    init_app(app)
    registration_status = register_blueprints(app)
    
    # Add explicit OPTIONS handler for preflight requests
    @app.before_request
    def handle_preflight():
        from flask import request, make_response
        if request.method == "OPTIONS":
            response = make_response()
            response.headers.add("Access-Control-Allow-Origin", request.headers.get('Origin', '*'))
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
            response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response
    
    # Enhanced image serving endpoints
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
    
    # Activity logging middleware
    @app.before_request
    def log_request_start():
        """Log request start time for duration calculation."""
        from flask import g
        from datetime import datetime
        g.request_start_time = datetime.utcnow()
    
    @app.after_request
    def log_request_completion(response):
        """Log completed requests with performance metrics."""
        if not app.config.get('ACTIVITY_LOGGING_ENABLED', True):
            return response
        
        try:
            from flask import request, g
            from datetime import datetime
            from models import ActivityLog, db
            
            # Skip logging for static files and health checks
            if (request.endpoint in ['static', 'health_check', 'list_routes'] or 
                request.path.startswith('/api/images/')):
                return response
            
            # Calculate request duration
            end_time = datetime.utcnow()
            start_time = getattr(g, 'request_start_time', end_time)
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Only log if user is authenticated or it's an auth endpoint
            user = getattr(g, 'current_user', None)
            is_auth_endpoint = request.endpoint and 'auth' in request.endpoint
            
            if user or is_auth_endpoint:
                # Determine action based on endpoint and method
                action = f"api_request_{request.method.lower()}"
                if request.endpoint:
                    action = f"{request.endpoint}_{request.method.lower()}"
                
                # Determine status
                status = "success" if response.status_code < 400 else "error"
                
                # Build request details
                details = {
                    "method": request.method,
                    "endpoint": request.endpoint,
                    "path": request.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "content_length": response.content_length
                }
                
                # Add query parameters (filtered)
                if request.args:
                    safe_args = {k: v for k, v in request.args.items() 
                               if k.lower() not in ['password', 'token', 'secret']}
                    if safe_args:
                        details["query_params"] = safe_args
                
            if user or is_auth_endpoint:
                log = ActivityLog(
                    user_id=user.id if user else None,
                    action=action,
                    status=status,
                    ip_address=request.remote_addr,
                    details=str(details) if app.config.get('LOG_REQUEST_DETAILS', True) else None,
                    duration_ms=duration_ms,
                    created_at=start_time
                )
                
                db.session.add(log)
                db.session.commit()
                
        except Exception as e:
            # Don't fail the request due to logging issues
            print(f"Request logging error: {e}")
            try:
                db.session.rollback()
            except:
                pass
        
        return response
    
    # Enhanced test routes
    @app.route("/api/health")
    def health_check():
        """Health check endpoint with system info."""
        from models import ActivityLog, User, Campaign
        
        try:
            # Test database connectivity
            user_count = User.query.count()
            campaign_count = Campaign.query.count()
            log_count = ActivityLog.query.count()
            
            return jsonify({
                "status": "ok", 
                "message": "Campaign Manager API is running",
                "registered_blueprints": registration_status,
                "upload_folder": app.config.get('UPLOAD_FOLDER', 'assets'),
                "system_info": {
                    "users": user_count,
                    "campaigns": campaign_count,
                    "activity_logs": log_count,
                    "logging_enabled": app.config.get('ACTIVITY_LOGGING_ENABLED', True)
                },
                "features": {
                    "enhanced_logging": True,
                    "log_filtering": True,
                    "log_export": True,
                    "activity_stats": True
                }
            })
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Database connectivity issue: {str(e)}",
                "registered_blueprints": registration_status
            }), 500
    
    @app.route("/api/routes")
    def list_routes():
        """List all available API routes with enhanced information."""
        routes = []
        for rule in app.url_map.iter_rules():
            route_info = {
                "endpoint": rule.endpoint,
                "methods": [m for m in rule.methods if m not in ['HEAD', 'OPTIONS']],
                "url": str(rule),
                "description": ""
            }
            
            # Add descriptions for known endpoints
            descriptions = {
                "auth.login": "User authentication",
                "auth.logout": "User logout",
                "auth.set_password": "Set user password",
                "auth.get_current_user": "Get current user info",
                "campaigns.list_campaigns": "List all campaigns",
                "campaigns.create_campaign": "Create new campaign",
                "campaigns.update_campaign": "Update campaign",
                "campaigns.delete_campaign": "Delete campaign",
                "campaigns.get_active_campaign": "Get active campaign",
                "users.list_users": "List all users (admin only)",
                "users.create_user": "Create new user (admin only)",
                "users.delete_user": "Delete user (admin only)",
                "uploads.upload_image": "Upload campaign images",
                "logs.list_logs": "List activity logs with filtering (admin only)",
                "logs.export_logs": "Export activity logs as CSV (admin only)",
                "logs.log_stats": "Get activity log statistics (admin only)",
                "health_check": "API health check",
                "list_routes": "List all API routes"
            }
            
            route_info["description"] = descriptions.get(rule.endpoint, "")
            routes.append(route_info)
        
        return jsonify({
            "routes": sorted(routes, key=lambda x: x['url']),
            "total_routes": len(routes),
            "api_version": "1.0",
            "features": {
                "authentication": "JWT-based",
                "activity_logging": "Enhanced with filtering",
                "file_upload": "Campaign images",
                "admin_features": "User management, activity logs"
            }
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Enhanced 404 handler."""
        return jsonify({
            "error": "Not Found",
            "message": "The requested resource was not found.",
            "status_code": 404
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Enhanced 500 handler with logging."""
        try:
            from models import db
            db.session.rollback()
        except:
            pass
        
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred.",
            "status_code": 500
        }), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        """Enhanced 403 handler."""
        return jsonify({
            "error": "Forbidden",
            "message": "You don't have permission to access this resource.",
            "status_code": 403
        }), 403
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Enhanced 401 handler."""
        return jsonify({
            "error": "Unauthorized",
            "message": "Authentication required to access this resource.",
            "status_code": 401
        }), 401
    
    return app


if __name__ == "__main__":
    flask_app = create_app()
    print("\n" + "="*60)
    print("🚀 Starting Campaign Manager API with Enhanced Logging")
    print("="*60)
    print("📍 Backend: http://localhost:5000")
    print("🔗 API Base: http://localhost:5000/api")
    print("🖼️ Images: http://localhost:5000/api/images/")
    print("📊 Activity Logs: http://localhost:5000/api/logs")
    print("🧪 Test endpoints:")
    print("   - http://localhost:5000/api/health")
    print("   - http://localhost:5000/api/routes")
    print("\n🎯 Enhanced Features:")
    print("   ✅ Comprehensive activity logging")
    print("   ✅ Advanced log filtering and search")
    print("   ✅ CSV export functionality")
    print("   ✅ Real-time activity statistics")
    print("   ✅ User attribution for all actions")
    print("   ✅ Performance monitoring")
    print("="*60)
    flask_app.run(host="0.0.0.0", port=5000, debug=True)