"""File upload endpoints."""

import os
from datetime import datetime

from flask import Blueprint, jsonify, request

from auth.decorators import jwt_required, log_activity
from models import Campaign, CampaignImage, db
from .utils import allowed_file, save_file


upload_bp = Blueprint("uploads", __name__)

IMAGE_TYPES = {
    "background": "bkg.png",
    "logo": "logo.png",
    "screensaver": "screensaver_bkg.png",
}


@upload_bp.route("/campaigns/<int:campaign_id>/images", methods=["POST"])
@jwt_required
@log_activity("upload_images")
def upload_images(campaign_id: int):
    """Upload images for a campaign."""
    campaign = Campaign.query.get_or_404(campaign_id)
    uploaded = {}
    for image_type, suffix in IMAGE_TYPES.items():
        file = request.files.get(image_type)
        if not file:
            continue
        if not allowed_file(file.filename):
            return jsonify({"error": f"Invalid file for {image_type}"}), 400
        filename = campaign.start_date.strftime("%Y-%m-%d") + suffix
        path = save_file(file, campaign.folder_path, filename)
        db.session.add(
            CampaignImage(
                campaign_id=campaign.id,
                image_type=image_type,
                file_path=path,
            )
        )
        uploaded[image_type] = path
    db.session.commit()
    return jsonify({"uploaded": uploaded})
