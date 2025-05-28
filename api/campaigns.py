"""Campaign management endpoints with proper file naming and automatic status updates."""

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


def _update_all_campaign_statuses():
    """Update all campaign statuses based on current date."""
    today = date.today()
    campaigns = Campaign.query.all()
    
    updated_count = 0
    for campaign in campaigns:
        old_status = campaign.status
        campaign.update_status(today)
        
        if old_status != campaign.status:
            updated_count += 1
            print(f"Campaign '{campaign.name}' status changed: {old_status} -> {campaign.status}")
    
    if updated_count > 0:
        db.session.commit()
        print(f"Updated {updated_count} campaign statuses")
    
    return updated_count


def _check_date_conflicts(start_date: date, end_date: date, exclude_campaign_id: int = None) -> str:
    """Check if the date range conflicts with existing active campaigns."""
    # First update all statuses to get current active campaigns
    _update_all_campaign_statuses()
    
    query = Campaign.query.filter(
        Campaign.status == "active"
    ).filter(
        # Check for date overlap: new campaign overlaps if:
        # start_date <= existing.end_date AND end_date >= existing.start_date
        Campaign.start_date <= end_date,
        Campaign.end_date >= start_date
    )
    
    if exclude_campaign_id:
        query = query.filter(Campaign.id != exclude_campaign_id)
    
    conflicting_campaign = query.first()
    
    if conflicting_campaign:
        return f"Date range conflicts with existing active campaign '{conflicting_campaign.name}' ({conflicting_campaign.start_date} to {conflicting_campaign.end_date})"
    
    return None


def _get_image_filename(campaign_start_date: date, image_type: str) -> str:
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


@campaign_bp.route("/", methods=["GET"])
@jwt_required
def list_campaigns():
    """Return all campaigns with updated statuses."""
    # Update all campaign statuses before returning the list
    _update_all_campaign_statuses()
    
    campaigns = Campaign.query.all()
    return jsonify([_serialize_campaign(c) for c in campaigns])


@campaign_bp.route("/", methods=["POST"])
@jwt_required
def create_campaign():
    """Create a new campaign with uploaded images."""
    # Handle both form data and JSON data
    if request.content_type and 'multipart/form-data' in request.content_type:
        form = request.form
        name = form.get("name")
        start_date = form.get("start_date")
        end_date = form.get("end_date")
    else:
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
    
    if start >= end:
        return jsonify({"error": "End date must be after start date"}), 400
    
    # Check for date conflicts with active campaigns
    conflict_error = _check_date_conflicts(start, end)
    if conflict_error:
        return jsonify({"error": conflict_error}), 409
    
    # Create folder for campaign assets
    folder = create_campaign_folder(start.isoformat())
    
    # Create campaign record FIRST to get the ID
    campaign = Campaign(
        name=name,
        start_date=start,
        end_date=end,
        folder_path=str(folder),
        user_id=g.current_user.id,
    )
    campaign.update_status(date.today())
    db.session.add(campaign)
    db.session.flush()  # This assigns the ID without committing
    
    # Handle file uploads with proper naming convention
    for image_type in ["background", "logo", "screensaver"]:
        file = request.files.get(image_type)
        if file and allowed_file(file.filename):
            # Generate filename: YYYY-MM-DDsuffix.png
            filename = _get_image_filename(campaign.start_date, image_type)
            path = save_image(file, folder / filename)
            
            db.session.add(
                CampaignImage(
                    campaign_id=campaign.id, 
                    image_type=image_type, 
                    file_path=str(path)
                )
            )
    
    db.session.commit()
    
    # Update all statuses again after committing the new campaign
    _update_all_campaign_statuses()
    
    return jsonify(_serialize_campaign(campaign)), 201


@campaign_bp.route("/<int:campaign_id>", methods=["PUT"])
@jwt_required
def update_campaign(campaign_id: int):
    """Update campaign details."""
    campaign = Campaign.query.get_or_404(campaign_id)
    data = request.get_json() or {}
    
    # Handle date updates
    start_date_str = data.get("start_date")
    end_date_str = data.get("end_date")
    
    if start_date_str or end_date_str:
        try:
            new_start = date.fromisoformat(start_date_str) if start_date_str else campaign.start_date
            new_end = date.fromisoformat(end_date_str) if end_date_str else campaign.end_date
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        if new_start >= new_end:
            return jsonify({"error": "End date must be after start date"}), 400
        
        # Check for date conflicts (excluding current campaign)
        conflict_error = _check_date_conflicts(new_start, new_end, campaign_id)
        if conflict_error:
            return jsonify({"error": conflict_error}), 409
        
        # If dates changed, we need to rename image files
        if new_start != campaign.start_date:
            old_folder = Path(campaign.folder_path)
            new_folder_name = new_start.isoformat()
            new_folder = old_folder.parent / new_folder_name
            
            # Create new folder if it doesn't exist
            new_folder.mkdir(parents=True, exist_ok=True)
            
            # Rename and move image files
            for image in campaign.images:
                old_path = Path(image.file_path)
                if old_path.exists():
                    # Generate new filename with new date
                    new_filename = _get_image_filename(new_start, image.image_type)
                    new_path = new_folder / new_filename
                    
                    # Move file to new location
                    old_path.rename(new_path)
                    
                    # Update database record
                    image.file_path = str(new_path)
            
            # Update campaign folder path
            campaign.folder_path = str(new_folder)
            
            # Remove old folder if it's empty
            try:
                if old_folder.exists() and not any(old_folder.iterdir()):
                    old_folder.rmdir()
            except OSError:
                pass  # Folder not empty or other issue, ignore
        
        campaign.start_date = new_start
        campaign.end_date = new_end
    
    campaign.name = data.get("name", campaign.name)
    campaign.update_status(date.today())
    db.session.commit()
    
    # Update all campaign statuses after the change
    _update_all_campaign_statuses()
    
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
    
    # Try to remove the campaign folder if it's empty
    folder_path = Path(campaign.folder_path)
    try:
        if folder_path.exists() and not any(folder_path.iterdir()):
            folder_path.rmdir()
    except OSError:
        pass  # Folder not empty or other issue, ignore
    
    db.session.delete(campaign)
    db.session.commit()
    
    # Update remaining campaign statuses
    _update_all_campaign_statuses()
    
    return jsonify({"message": "Campaign deleted successfully"})


@campaign_bp.route("/active", methods=["GET"])  
@jwt_required
def get_active_campaign():
    """Get the currently active campaign."""
    # Update all statuses first
    _update_all_campaign_statuses()
    
    # Get active campaign
    active_campaign = Campaign.query.filter_by(status="active").first()
    
    if not active_campaign:
        return jsonify({"message": "No active campaign"}), 404
    
    return jsonify({
        "campaign": _serialize_campaign(active_campaign),
        "folder_path": active_campaign.folder_path
    })


@campaign_bp.route("/update-statuses", methods=["POST"])
@jwt_required
def update_campaign_statuses():
    """Manual endpoint to update all campaign statuses."""
    updated_count = _update_all_campaign_statuses()
    
    return jsonify({
        "message": f"Updated {updated_count} campaign statuses",
        "updated_count": updated_count
    })
    
_test_date_override = None

def _get_current_date():
    """Get current date, or test override date if set."""
    if _test_date_override:
        return _test_date_override
    return date.today()

# Modify your existing _update_all_campaign_statuses function
def _update_all_campaign_statuses():
    """Update all campaign statuses based on current date."""
    today = _get_current_date()  # Use test date if set
    campaigns = Campaign.query.all()
    
    updated_count = 0
    for campaign in campaigns:
        old_status = campaign.status
        campaign.update_status(today)
        
        if old_status != campaign.status:
            updated_count += 1
            print(f"Campaign '{campaign.name}' status changed: {old_status} -> {campaign.status} (using date: {today})")
    
    if updated_count > 0:
        db.session.commit()
        print(f"Updated {updated_count} campaign statuses")
    
    return updated_count