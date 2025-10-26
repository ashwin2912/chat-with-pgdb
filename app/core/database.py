"""Database connection management with SSH tunnel support."""

from ..config import Config
from ..utils.logger import setup_logger
from .db_client import DbClient

logger = setup_logger(__name__)


class DatabaseManager:
    """Manages database connections and SSH tunnels."""

    def __init__(self, config: Config):
        self.config = config

    def get_connection_params(self) -> dict:
        """Get database connection parameters.

        Returns:
            Dictionary with connection parameters
        """
        return {
            "host": self.config.DB_HOST,
            "port": self.config.DB_PORT,
            "dbname": self.config.DB_NAME,
            "user": self.config.DB_USER,
            "password": self.config.DB_PASSWORD,
        }

    def get_schema(self, db_client: DbClient) -> str:
        """Get database schema information."""
        query = """
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position;
        """
        return db_client.run_sql(query)
