"""Campaign-related database models."""

from datetime import date, datetime
from enum import Enum

from sqlalchemy.orm import relationship

from . import db


class CampaignStatus(str, Enum):
    """Enumeration of campaign statuses."""

    SCHEDULED = "scheduled"
    ACTIVE = "active"
    EXPIRED = "expired"


class Campaign(db.Model):
    """Represents a promotional campaign."""

    __tablename__ = "campaigns"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default=CampaignStatus.SCHEDULED.value)
    folder_path = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = relationship("User", backref="campaigns", lazy=True)
    images = relationship(
        "CampaignImage",
        back_populates="campaign",
        cascade="all, delete-orphan",
    )

    def update_status(self, current_date: date) -> None:
        """Update campaign status based on the given date."""
        if self.start_date > current_date:
            self.status = CampaignStatus.SCHEDULED.value
        elif self.end_date < current_date:
            self.status = CampaignStatus.EXPIRED.value
        else:
            self.status = CampaignStatus.ACTIVE.value

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Campaign {self.name}>"


class CampaignImage(db.Model):
    """Image associated with a campaign."""

    __tablename__ = "campaign_images"

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaigns.id"), nullable=False)
    image_type = db.Column(db.String(20), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="images")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<CampaignImage {self.image_type}>"
