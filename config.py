import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base config."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-for-interview-app")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost/stasher_interview"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Database connection pool configuration for 8 workers
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 16,  # 2x number of Gunicorn workers (8 * 2)
        "max_overflow": 8,  # 50% of pool_size
        "pool_pre_ping": True,  # Health checks
        "pool_recycle": 3600,  # Recycle connections hourly
        "pool_timeout": 30,  # Connection timeout
    }


class DevConfig(Config):
    """Development config."""

    DEBUG = True


class ProdConfig(Config):
    """Production config."""

    DEBUG = False


class TestConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'postgresql://postgres:postgres@localhost/stasher_interview_test'
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 5,           # Smaller pool for tests
        'max_overflow': 2,
        'pool_pre_ping': True,
        'pool_recycle': 300,      # Recycle every 5 minutes
        'echo': False,
    }


def get_config():
    env = os.environ.get("FLASK_ENV", "development")
    if env == "production":
        return ProdConfig
    elif env == "testing":
        return TestConfig
    return DevConfig
