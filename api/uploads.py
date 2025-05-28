"""Endpoints for uploading campaign images."""

from pathlib import Path

from flask import Blueprint, jsonify, request

from auth.decorators import jwt_required
from models import Campaign, CampaignImage, db
from .utils import allowed_file, save_image

uploads_bp = Blueprint("uploads", __name__)


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
            # Generate filename based on campaign date and image type
            filename = f"{campaign.start_date.isoformat()}{image_type[:3]}.png"
            path = save_image(file, folder / filename)
            
            # Update or create image record
            img = CampaignImage.query.filter_by(
                campaign_id=campaign.id, image_type=image_type
            ).first()
            
            if img:
                # Update existing image
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