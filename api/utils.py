"""Utility functions for API modules."""

import os
from datetime import date
from typing import Iterable

from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def create_campaign_folder(start_date: date) -> str:
    """Return path for campaign assets based on start date."""
    folder_name = start_date.strftime("%Y-%m-%d")
    base_path = current_app.config["UPLOAD_FOLDER"]
    path = os.path.join(base_path, folder_name)
    os.makedirs(path, exist_ok=True)
    return path


def allowed_file(filename: str, allowed: Iterable[str] = ALLOWED_EXTENSIONS) -> bool:
    """Check if filename has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


def save_file(file_storage, folder: str, filename: str) -> str:
    """Save an uploaded file and return its path."""
    filename = secure_filename(filename)
    full_path = os.path.join(folder, filename)
    file_storage.save(full_path)
    return full_path
