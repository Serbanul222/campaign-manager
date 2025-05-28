"""Endpoints for uploading campaign images with proper file naming."""

from pathlib import Path

from flask import Blueprint, jsonify, request

from auth.decorators import jwt_required
from models import Campaign, CampaignImage, db
from .utils import allowed_file, save_image

uploads_bp = Blueprint("uploads", __name__)


def _get_image_filename(campaign_start_date, image_type: str) -> str:
    """Generate the correct filename based on date and image type."""
    date_str = campaign_start_date.isoformat()  # e.g., "2025-05-29"
    
    # File naming mapping according to your requirements
    image_type_mapping = {
        "background": "bkg",
        "logo": "logo", 
        "screensaver": "screensaver_bkg"
    }
    
    suffix = image_type_mapping.get(image_type, image_type)
    return f"{date_str}{suffix}.png"


@uploads_bp.route("/<int:campaign_id>", methods=["POST"])
@jwt_required
def upload_image(campaign_id: int):
    """Upload images to an existing campaign."""
    campaign = Campaign.query.get_or_404(campaign_id)
    folder = Path(campaign.folder_path)
    
    uploaded_files = []
    
    # Handle multiple image types
    for image_type in ["background", "logo", "screensaver"]:
        file = request.files.get(image_type)
        if file and allowed_file(file.filename):
            # Generate filename: YYYY-MM-DDsuffix.png
            filename = _get_image_filename(campaign.start_date, image_type)
            path = save_image(file, folder / filename)
            
            # Update or create image record
            img = CampaignImage.query.filter_by(
                campaign_id=campaign.id, image_type=image_type
            ).first()
            
            if img:
                # Delete old image file if it exists and is different
                old_path = Path(img.file_path)
                if old_path.exists() and str(old_path) != str(path):
                    try:
                        old_path.unlink()
                    except Exception as e:
                        print(f"Warning: Could not delete old image {old_path}: {e}")
                
                # Update existing image record
                img.file_path = str(path)
            else:
                # Create new image record
                img = CampaignImage(
                    campaign_id=campaign.id,
                    image_type=image_type,
                    file_path=str(path)
                )
                db.session.add(img)
            
            uploaded_files.append({
                "type": image_type,
                "path": str(path),
                "filename": filename
            })
    
    if not uploaded_files:
        return jsonify({"error": "No valid image files provided"}), 400
    
    db.session.commit()
    return jsonify({
        "message": "Images uploaded successfully",
        "uploaded_files": uploaded_files
    })