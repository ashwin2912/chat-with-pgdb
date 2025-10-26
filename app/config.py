"""Configuration management for Vanna Server."""

import os
from dotenv import load_dotenv


class Config:
    """Application configuration."""

    def __init__(self, env_file: str = ".env"):
        load_dotenv(env_file)

        # Database Configuration
        self.DB_HOST: str = self._get_required("DB_HOST")
        self.DB_NAME: str = self._get_required("DB_NAME")
        self.DB_USER: str = self._get_required("DB_USER")
        self.DB_PASSWORD: str = os.getenv(
            "DB_PASSWORD", ""
        )  # Allow empty password for local dev
        self.DB_PORT: int = int(os.getenv("DB_PORT", "5432"))

    def _get_required(self, key: str) -> str:
        """Get required environment variable or raise error."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable '{key}' is not set")
        return value
