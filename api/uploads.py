# api/uploads.py - Enhanced with comprehensive logging
from pathlib import Path
import json

from flask import Blueprint, jsonify, request, g

from auth.decorators import jwt_required, log_activity
from models import Campaign, CampaignImage, db
from .utils import allowed_file, save_image

uploads_bp = Blueprint("uploads", __name__)


def _get_image_filename(campaign_start_date, image_type: str) -> str:
    """Generate the correct filename based on date and image type."""
    date_str = campaign_start_date.isoformat()
    
    image_type_mapping = {
        "background": "bkg",
        "logo": "logo", 
        "screensaver": "screensaver_bkg"
    }
    
    suffix = image_type_mapping.get(image_type, image_type)
    return f"{date_str}{suffix}.png"


@uploads_bp.route("/<int:campaign_id>", methods=["POST"])
@jwt_required
@log_activity("upload_images", resource_type="campaign")
def upload_image(campaign_id: int):
    """Upload images to an existing campaign."""
    campaign = Campaign.query.get_or_404(campaign_id)
    folder = Path(campaign.folder_path)
    
    uploaded_files = []
    updated_images = []
    errors = []
    
    # Handle multiple image types
    for image_type in ["background", "logo", "screensaver"]:
        file = request.files.get(image_type)
        if file and allowed_file(file.filename):
            try:
                # Generate filename: YYYY-MM-DDsuffix.png
                filename = _get_image_filename(campaign.start_date, image_type)
                path = save_image(file, folder / filename)
                
                # Update or create image record
                img = CampaignImage.query.filter_by(
                    campaign_id=campaign.id, image_type=image_type
                ).first()
                
                old_path = None
                if img:
                    # Delete old image file if it exists and is different
                    old_path = Path(img.file_path)
                    if old_path.exists() and str(old_path) != str(path):
                        try:
                            old_path.unlink()
                        except Exception as e:
                            errors.append(f"Could not delete old {image_type} image: {e}")
                    
                    # Update existing image record
                    img.file_path = str(path)
                    updated_images.append({
                        "type": image_type,
                        "action": "updated",
                        "old_path": str(old_path) if old_path else None,
                        "new_path": str(path)
                    })
                else:
                    # Create new image record
                    img = CampaignImage(
                        campaign_id=campaign.id,
                        image_type=image_type,
                        file_path=str(path)
                    )
                    db.session.add(img)
                    updated_images.append({
                        "type": image_type,
                        "action": "created",
                        "new_path": str(path)
                    })
                
                uploaded_files.append({
                    "type": image_type,
                    "path": str(path),
                    "filename": filename,
                    "size": file.content_length or len(file.read())
                })
                
                # Reset file pointer after reading for size
                file.seek(0)
                
            except Exception as e:
                errors.append(f"Failed to upload {image_type} image: {e}")
    
    if not uploaded_files and not errors:
        return jsonify({"error": "No valid image files provided"}), 400
    
    db.session.commit()
    
    # Update log with detailed upload info
    from models import ActivityLog
    recent_log = ActivityLog.query.filter_by(
        user_id=g.current_user.id,
        action="upload_images"
    ).order_by(ActivityLog.created_at.desc()).first()
    
    if recent_log:
        details = {
            "campaign_id": campaign_id,
            "campaign_name": campaign.name,
            "uploaded_files": uploaded_files,
            "updated_images": updated_images,
            "errors": errors,
            "success_count": len(uploaded_files),
            "error_count": len(errors)
        }
        recent_log.details = json.dumps(details)
        recent_log.resource_id = str(campaign_id)
        recent_log.status = "success" if not errors else "warning"
        db.session.commit()
    
    response_data = {
        "message": "Images processed",
        "uploaded_files": uploaded_files
    }
    
    if errors:
        response_data["warnings"] = errors
    
    return jsonify(response_data)