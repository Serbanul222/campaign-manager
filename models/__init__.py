"""Database models package exports."""

from flask_sqlalchemy import SQLAlchemy

# Singleton database object
db = SQLAlchemy()

# Import all models
from .user import User
from .campaign import Campaign, CampaignImage, CampaignStatus
from .log import ActivityLog, JWTBlacklist

# Define what gets imported with "from models import *"
__all__ = [
    "db",
    "User",
    "Campaign",
    "CampaignImage",
    "CampaignStatus",
    "ActivityLog",
    "JWTBlacklist",
]
