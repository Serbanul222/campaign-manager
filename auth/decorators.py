# auth/decorators.py - Safe decorators with backward compatibility
from functools import wraps
from flask import request, jsonify, g
from datetime import datetime
import json

from models import User, ActivityLog, db
from .jwt_handler import decode_token


def jwt_required(func):
    """Ensure the request has a valid JWT token."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"message": "Missing token"}), 401
        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_token(token)
        except Exception:
            return jsonify({"message": "Invalid token"}), 401
        user = User.query.get(payload.get("sub"))
        if not user:
            return jsonify({"message": "Invalid user"}), 401
        g.current_user = user
        return func(*args, **kwargs)
    return wrapper


def admin_required(func):
    """Allow only admin users to access the route."""
    @wraps(func)
    @jwt_required
    def wrapper(*args, **kwargs):
        user = g.current_user
        if not user.is_admin:
            return jsonify({"message": "Forbidden"}), 403
        return func(*args, **kwargs)
    return wrapper


def log_activity(action: str, details: str = None, resource_type: str = None, resource_id: str = None):
    """Safe activity logging decorator with backward compatibility."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Execute the function first to get the response
            start_time = datetime.utcnow()
            
            try:
                response = func(*args, **kwargs)
                status = "success"
                
                # Extract status code from response tuple if present
                if isinstance(response, tuple) and len(response) >= 2:
                    status_code = response[1]
                    if status_code >= 400:
                        status = "error"
                else:
                    status_code = 200
                    
            except Exception as e:
                response = jsonify({"error": str(e)}), 500
                status = "error"
                status_code = 500
            
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Log the activity safely
            user = getattr(g, "current_user", None)
            if user:
                try:
                    # Create basic log entry
                    log_data = {
                        'user_id': user.id,
                        'action': action,
                        'ip_address': request.remote_addr,
                        'created_at': start_time
                    }
                    
                    # Add enhanced fields if the columns exist
                    try:
                        # Test if enhanced columns exist by trying to create a log with them
                        log_details = {
                            "method": request.method,
                            "endpoint": request.endpoint,
                            "url": request.url,
                            "status_code": status_code,
                            "duration_ms": duration_ms,
                            "user_agent": request.headers.get("User-Agent", "")[:255],
                        }
                        
                        if details:
                            log_details["details"] = details
                            
                        if resource_type and resource_id:
                            log_details["resource_type"] = resource_type
                            log_details["resource_id"] = str(resource_id)
                        
                        # Extract resource info from URL parameters if not provided
                        if not resource_id and 'id' in request.view_args:
                            log_details["resource_id"] = str(request.view_args['id'])
                        
                        # Try to add enhanced fields
                        log_data.update({
                            'status': status,
                            'details': json.dumps(log_details),
                            'resource_type': resource_type,
                            'resource_id': log_details.get("resource_id"),
                            'duration_ms': duration_ms
                        })
                        
                    except Exception:
                        # Enhanced columns don't exist, use basic logging
                        pass
                    
                    log = ActivityLog(**log_data)
                    db.session.add(log)
                    db.session.commit()
                    
                except Exception as log_error:
                    print(f"Failed to log activity: {log_error}")
                    # Don't fail the main request due to logging issues
                    try:
                        db.session.rollback()
                    except:
                        pass
            
            return response
        return wrapper
    return decorator