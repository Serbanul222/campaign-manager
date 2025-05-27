"""Endpoints for uploading campaign images."""

from pathlib import Path

from flask import Blueprint, jsonify, request

from auth.decorators import jwt_required
from models import Campaign, CampaignImage, db
from .utils import allowed_file, save_image

uploads_bp = Blueprint("uploads", __name__)


@uploads_bp.post("/<int:campaign_id>")
@jwt_required
def upload_image(campaign_id: int):
    """Upload a single image to an existing campaign."""
    campaign = Campaign.query.get_or_404(campaign_id)
    image_type = request.args.get("type")
    file = request.files.get("file")
    if image_type not in {"background", "logo", "screensaver"}:
        return jsonify({"error": "Invalid type"}), 400
    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file"}), 400
    folder = Path(campaign.folder_path)
    filename = f"{campaign.start_date.isoformat()}{image_type[:3]}.png"
    path = save_image(file, folder / filename)
    img = CampaignImage.query.filter_by(
        campaign_id=campaign.id, image_type=image_type
    ).first()
    if img:
        img.file_path = path
    else:
        db.session.add(
            CampaignImage(
                campaign_id=campaign.id, image_type=image_type, file_path=path
            )
        )
    db.session.commit()
    return jsonify({"message": "Uploaded", "path": path})
