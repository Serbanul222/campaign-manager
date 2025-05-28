"""Campaign management endpoints."""

from datetime import date
from pathlib import Path
from typing import Dict

from flask import Blueprint, jsonify, request, g

from auth.decorators import jwt_required
from models import Campaign, CampaignImage, db
from .utils import allowed_file, create_campaign_folder, save_image

# Create blueprint without URL prefix - it will be added during registration
campaign_bp = Blueprint("campaigns", __name__)


def _serialize_campaign(campaign: Campaign) -> Dict[str, str]:
    """Convert campaign to dictionary for JSON responses."""
    return {
        "id": campaign.id,
        "name": campaign.name,
        "start_date": campaign.start_date.isoformat(),
        "end_date": campaign.end_date.isoformat(),
        "status": campaign.status,
        "folder": campaign.folder_path,
    }


@campaign_bp.route("/", methods=["GET"])
@jwt_required
def list_campaigns():
    """Return all campaigns."""
    campaigns = Campaign.query.all()
    return jsonify([_serialize_campaign(c) for c in campaigns])


@campaign_bp.route("/", methods=["POST"])
@jwt_required
def create_campaign():
    """Create a new campaign with uploaded images."""
    # Handle both form data and JSON data
    if request.content_type and 'multipart/form-data' in request.content_type:
        # Form data with files
        form = request.form
        name = form.get("name")
        start_date = form.get("start_date")
        end_date = form.get("end_date")
    else:
        # JSON data
        data = request.get_json() or {}
        name = data.get("name")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
    
    if not all([name, start_date, end_date]):
        return jsonify({"error": "Missing required fields: name, start_date, end_date"}), 400
    
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Create folder for campaign assets
    folder = create_campaign_folder(start.isoformat())
    
    # Create campaign record
    campaign = Campaign(
        name=name,
        start_date=start,
        end_date=end,
        folder_path=str(folder),
        user_id=g.current_user.id,
    )
    campaign.update_status(date.today())
    db.session.add(campaign)
    db.session.commit()
    
    # Handle file uploads if present
    for image_type in ["background", "logo", "screensaver"]:
        file = request.files.get(image_type)
        if file and allowed_file(file.filename):
            filename = f"{campaign.start_date.isoformat()}{image_type[:3]}.png"
            path = save_image(file, folder / filename)
            db.session.add(
                CampaignImage(
                    campaign_id=campaign.id, 
                    image_type=image_type, 
                    file_path=str(path)
                )
            )
    
    db.session.commit()
    return jsonify(_serialize_campaign(campaign)), 201


@campaign_bp.route("/<int:campaign_id>", methods=["PUT"])
@jwt_required
def update_campaign(campaign_id: int):
    """Update campaign details."""
    campaign = Campaign.query.get_or_404(campaign_id)
    data = request.get_json() or {}
    
    campaign.name = data.get("name", campaign.name)
    if "start_date" in data:
        campaign.start_date = date.fromisoformat(data["start_date"])
    if "end_date" in data:
        campaign.end_date = date.fromisoformat(data["end_date"])
    
    campaign.update_status(date.today())
    db.session.commit()
    return jsonify(_serialize_campaign(campaign))


@campaign_bp.route("/<int:campaign_id>", methods=["DELETE"])
@jwt_required
def delete_campaign(campaign_id: int):
    """Delete campaign and associated images."""
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Delete associated image files
    for image in campaign.images:
        path = Path(image.file_path)
        if path.exists():
            path.unlink()
    
    db.session.delete(campaign)
    db.session.commit()
    return jsonify({"message": "Campaign deleted successfully"})