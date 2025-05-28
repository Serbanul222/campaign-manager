# api/campaigns.py - Enhanced with comprehensive activity logging
from datetime import date
from pathlib import Path
from typing import Dict
import json

from flask import Blueprint, jsonify, request, g

from auth.decorators import jwt_required, log_activity
from models import Campaign, CampaignImage, db
from .utils import allowed_file, create_campaign_folder, save_image

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
    updated_campaigns = []
    
    for campaign in campaigns:
        old_status = campaign.status
        campaign.update_status(today)
        
        if old_status != campaign.status:
            updated_count += 1
            updated_campaigns.append({
                "id": campaign.id,
                "name": campaign.name,
                "old_status": old_status,
                "new_status": campaign.status
            })
            print(f"Campaign '{campaign.name}' status changed: {old_status} -> {campaign.status}")
    
    if updated_count > 0:
        db.session.commit()
        print(f"Updated {updated_count} campaign statuses")
        
        # Log the bulk status update
        user = getattr(g, "current_user", None)
        if user:
            from models import ActivityLog
            log = ActivityLog(
                user_id=user.id,
                action="bulk_update_campaign_status",
                status="success",
                ip_address=request.remote_addr if request else None,
                details=json.dumps({
                    "updated_count": updated_count,
                    "campaigns": updated_campaigns
                }),
                resource_type="campaign"
            )
            db.session.add(log)
            db.session.commit()
    
    return updated_count


def _check_date_conflicts(start_date: date, end_date: date, exclude_campaign_id: int = None) -> str:
    """Check if the date range conflicts with existing active campaigns."""
    _update_all_campaign_statuses()
    
    query = Campaign.query.filter(
        Campaign.status == "active"
    ).filter(
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
    date_str = campaign_start_date.isoformat()
    
    image_type_mapping = {
        "background": "bkg",
        "logo": "logo", 
        "screensaver": "screensaver_bkg"
    }
    
    suffix = image_type_mapping.get(image_type, image_type)
    return f"{date_str}{suffix}.png"


@campaign_bp.route("/", methods=["GET"])
@jwt_required
@log_activity("list_campaigns", "Retrieved campaign list")
def list_campaigns():
    """Return all campaigns with updated statuses."""
    _update_all_campaign_statuses()
    
    campaigns = Campaign.query.all()
    campaign_data = [_serialize_campaign(c) for c in campaigns]
    
    return jsonify(campaign_data)


@campaign_bp.route("/", methods=["POST"])
@jwt_required
@log_activity("create_campaign", resource_type="campaign")
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
    
    # Track uploaded images for logging
    uploaded_images = []
    
    # Handle file uploads with proper naming convention
    for image_type in ["background", "logo", "screensaver"]:
        file = request.files.get(image_type)
        if file and allowed_file(file.filename):
            filename = _get_image_filename(campaign.start_date, image_type)
            path = save_image(file, folder / filename)
            
            db.session.add(
                CampaignImage(
                    campaign_id=campaign.id, 
                    image_type=image_type, 
                    file_path=str(path)
                )
            )
            uploaded_images.append(image_type)
    
    db.session.commit()
    
    # Update the decorator with detailed information
    from models import ActivityLog
    # Find the most recent log for this user and update it with details
    recent_log = ActivityLog.query.filter_by(
        user_id=g.current_user.id,
        action="create_campaign"
    ).order_by(ActivityLog.created_at.desc()).first()
    
    if recent_log:
        details = {
            "campaign_id": campaign.id,
            "campaign_name": name,
            "start_date": start_date,
            "end_date": end_date,
            "status": campaign.status,
            "uploaded_images": uploaded_images,
            "folder_path": str(folder)
        }
        recent_log.details = json.dumps(details)
        recent_log.resource_id = str(campaign.id)
        db.session.commit()
    
    _update_all_campaign_statuses()
    
    return jsonify(_serialize_campaign(campaign)), 201


@campaign_bp.route("/<int:campaign_id>", methods=["PUT"])
@jwt_required
@log_activity("update_campaign", resource_type="campaign")
def update_campaign(campaign_id: int):
    """Update campaign details."""
    campaign = Campaign.query.get_or_404(campaign_id)
    data = request.get_json() or {}
    
    # Track what's being changed for logging
    changes = {}
    original_data = {
        "name": campaign.name,
        "start_date": campaign.start_date.isoformat(),
        "end_date": campaign.end_date.isoformat(),
        "status": campaign.status
    }
    
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
        
        # Track date changes
        if new_start != campaign.start_date:
            changes["start_date"] = {
                "old": campaign.start_date.isoformat(),
                "new": new_start.isoformat()
            }
            
        if new_end != campaign.end_date:
            changes["end_date"] = {
                "old": campaign.end_date.isoformat(),
                "new": new_end.isoformat()
            }
        
        # If dates changed, handle file renaming
        if new_start != campaign.start_date:
            old_folder = Path(campaign.folder_path)
            new_folder_name = new_start.isoformat()
            new_folder = old_folder.parent / new_folder_name
            
            new_folder.mkdir(parents=True, exist_ok=True)
            
            renamed_files = []
            for image in campaign.images:
                old_path = Path(image.file_path)
                if old_path.exists():
                    new_filename = _get_image_filename(new_start, image.image_type)
                    new_path = new_folder / new_filename
                    
                    old_path.rename(new_path)
                    image.file_path = str(new_path)
                    renamed_files.append({
                        "type": image.image_type,
                        "old_path": str(old_path),
                        "new_path": str(new_path)
                    })
            
            campaign.folder_path = str(new_folder)
            changes["folder_path"] = {
                "old": str(old_folder),
                "new": str(new_folder)
            }
            changes["renamed_files"] = renamed_files
            
            # Remove old folder if empty
            try:
                if old_folder.exists() and not any(old_folder.iterdir()):
                    old_folder.rmdir()
            except OSError:
                pass
        
        campaign.start_date = new_start
        campaign.end_date = new_end
    
    # Handle name changes
    new_name = data.get("name")
    if new_name and new_name != campaign.name:
        changes["name"] = {
            "old": campaign.name,
            "new": new_name
        }
        campaign.name = new_name
    
    old_status = campaign.status
    campaign.update_status(date.today())
    
    if campaign.status != old_status:
        changes["status"] = {
            "old": old_status,
            "new": campaign.status
        }
    
    db.session.commit()
    
    # Update log with detailed changes
    from models import ActivityLog
    recent_log = ActivityLog.query.filter_by(
        user_id=g.current_user.id,
        action="update_campaign"
    ).order_by(ActivityLog.created_at.desc()).first()
    
    if recent_log:
        details = {
            "campaign_id": campaign_id,
            "campaign_name": campaign.name,
            "changes": changes,
            "original_data": original_data
        }
        recent_log.details = json.dumps(details)
        recent_log.resource_id = str(campaign_id)
        db.session.commit()
    
    _update_all_campaign_statuses()
    
    return jsonify(_serialize_campaign(campaign))


@campaign_bp.route("/<int:campaign_id>", methods=["DELETE"])
@jwt_required
@log_activity("delete_campaign", resource_type="campaign")
def delete_campaign(campaign_id: int):
    """Delete campaign and associated images."""
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Collect information for logging before deletion
    campaign_info = {
        "id": campaign.id,
        "name": campaign.name,
        "start_date": campaign.start_date.isoformat(),
        "end_date": campaign.end_date.isoformat(),
        "status": campaign.status,
        "folder_path": campaign.folder_path
    }
    
    deleted_images = []
    # Delete associated image files
    for image in campaign.images:
        path = Path(image.file_path)
        if path.exists():
            try:
                path.unlink()
                deleted_images.append({
                    "type": image.image_type,
                    "path": str(path),
                    "deleted": True
                })
            except Exception as e:
                deleted_images.append({
                    "type": image.image_type,
                    "path": str(path),
                    "deleted": False,
                    "error": str(e)
                })
    
    # Try to remove the campaign folder if it's empty
    folder_removed = False
    folder_path = Path(campaign.folder_path)
    try:
        if folder_path.exists() and not any(folder_path.iterdir()):
            folder_path.rmdir()
            folder_removed = True
    except OSError:
        pass
    
    db.session.delete(campaign)
    db.session.commit()
    
    # Update log with detailed deletion info
    from models import ActivityLog
    recent_log = ActivityLog.query.filter_by(
        user_id=g.current_user.id,
        action="delete_campaign"
    ).order_by(ActivityLog.created_at.desc()).first()
    
    if recent_log:
        details = {
            "deleted_campaign": campaign_info,
            "deleted_images": deleted_images,
            "folder_removed": folder_removed
        }
        recent_log.details = json.dumps(details)
        recent_log.resource_id = str(campaign_id)
        db.session.commit()
    
    _update_all_campaign_statuses()
    
    return jsonify({"message": "Campaign deleted successfully"})


@campaign_bp.route("/active", methods=["GET"])  
@jwt_required
@log_activity("get_active_campaign", "Retrieved active campaign")
def get_active_campaign():
    """Get the currently active campaign."""
    _update_all_campaign_statuses()
    
    active_campaign = Campaign.query.filter_by(status="active").first()
    
    if not active_campaign:
        return jsonify({"message": "No active campaign"}), 404
    
    return jsonify({
        "campaign": _serialize_campaign(active_campaign),
        "folder_path": active_campaign.folder_path
    })


@campaign_bp.route("/update-statuses", methods=["POST"])
@jwt_required
@log_activity("manual_update_statuses", "Manually triggered campaign status update")
def update_campaign_statuses():
    """Manual endpoint to update all campaign statuses."""
    updated_count = _update_all_campaign_statuses()
    
    return jsonify({
        "message": f"Updated {updated_count} campaign statuses",
        "updated_count": updated_count
    })