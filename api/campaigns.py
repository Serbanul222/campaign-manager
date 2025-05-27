"""Campaign management API routes."""

from datetime import date

from flask import Blueprint, jsonify, request, g

from auth.decorators import jwt_required, log_activity
from models import Campaign, db
from .utils import create_campaign_folder


campaign_bp = Blueprint("campaigns", __name__)


def _serialize_campaign(campaign: Campaign) -> dict:
    campaign.update_status(date.today())
    return {
        "id": campaign.id,
        "name": campaign.name,
        "start_date": campaign.start_date.isoformat(),
        "end_date": campaign.end_date.isoformat(),
        "status": campaign.status,
    }


@campaign_bp.route("/campaigns", methods=["GET"])
@jwt_required
def list_campaigns():
    """Return all campaigns for the current user."""
    user = g.current_user
    campaigns = Campaign.query.filter_by(user_id=user.id).all()
    return jsonify([_serialize_campaign(c) for c in campaigns])


@campaign_bp.route("/campaigns", methods=["POST"])
@jwt_required
@log_activity("create_campaign")
def create_campaign():
    """Create a new campaign."""
    data = request.get_json() or {}
    name = data.get("name")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    if not all([name, start_date, end_date]):
        return jsonify({"error": "Missing fields"}), 400
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    folder = create_campaign_folder(start)
    campaign = Campaign(
        name=name,
        start_date=start,
        end_date=end,
        folder_path=folder,
        user_id=g.current_user.id,
    )
    db.session.add(campaign)
    db.session.commit()
    return jsonify(_serialize_campaign(campaign)), 201


@campaign_bp.route("/campaigns/<int:campaign_id>", methods=["PUT"])
@jwt_required
@log_activity("update_campaign")
def update_campaign(campaign_id: int):
    """Update an existing campaign."""
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != g.current_user.id:
        return jsonify({"error": "Forbidden"}), 403
    data = request.get_json() or {}
    campaign.name = data.get("name", campaign.name)
    if "start_date" in data:
        campaign.start_date = date.fromisoformat(data["start_date"])
    if "end_date" in data:
        campaign.end_date = date.fromisoformat(data["end_date"])
    db.session.commit()
    return jsonify(_serialize_campaign(campaign))


@campaign_bp.route("/campaigns/<int:campaign_id>", methods=["DELETE"])
@jwt_required
@log_activity("delete_campaign")
def delete_campaign(campaign_id: int):
    """Delete a campaign and its files."""
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != g.current_user.id:
        return jsonify({"error": "Forbidden"}), 403
    db.session.delete(campaign)
    db.session.commit()
    return jsonify({"message": "Campaign deleted"})
