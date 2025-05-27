"""Utility functions for campaign management."""

from pathlib import Path
from typing import Iterable

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS: Iterable[str] = {"png", "jpg", "jpeg"}


def allowed_file(filename: str) -> bool:
    """Return True if the filename has an allowed extension."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def create_campaign_folder(folder_name: str) -> Path:
    """Create a folder for campaign assets."""
    base = Path(current_app.config["UPLOAD_FOLDER"])
    path = base / folder_name
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_image(file: FileStorage, path: Path) -> str:
    """Save the uploaded file to the provided path."""
    path = path.with_name(secure_filename(path.name))
    file.save(path)
    return str(path)
