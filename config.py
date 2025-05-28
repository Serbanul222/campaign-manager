"""Application configuration with enhanced logging support."""

import os


class Config:
    """Base configuration with default settings."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///campaigns.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "assets")
    
    # Enhanced logging configuration
    ACTIVITY_LOGGING_ENABLED = True
    LOG_FAILED_REQUESTS = True
    LOG_REQUEST_DETAILS = True
    MAX_LOG_RETENTION_DAYS = int(os.getenv("MAX_LOG_RETENTION_DAYS", "90"))
    LOG_EXPORT_MAX_RECORDS = int(os.getenv("LOG_EXPORT_MAX_RECORDS", "10000"))


class DevelopmentConfig(Config):
    """Development configuration with verbose logging."""
    DEBUG = True
    ACTIVITY_LOGGING_ENABLED = True
    LOG_REQUEST_DETAILS = True


class ProductionConfig(Config):
    """Production configuration with optimized logging."""
    DEBUG = False
    ACTIVITY_LOGGING_ENABLED = True
    LOG_REQUEST_DETAILS = False  # Reduce log verbosity in production
    MAX_LOG_RETENTION_DAYS = 365  # Keep logs longer in production


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
