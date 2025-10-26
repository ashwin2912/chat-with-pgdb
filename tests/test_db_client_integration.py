"""Integration tests for DbClient.

These tests require a running PostgreSQL database.
They test actual database connections and queries.
"""

import pytest
from app.config import Config
from app.core.db_client import DbClient


@pytest.mark.integration
class TestDbClientIntegration:
    """Integration tests for DbClient with real database."""

    @pytest.fixture
    def config(self):
        """Load configuration from .env file."""
        return Config()

    @pytest.fixture
    def db_client(self, config):
        """Create a DbClient instance with real database connection."""
        client = DbClient(config)
        yield client
        # Cleanup: close connection after test
        client.close()

    def test_connection_is_established(self, db_client):
        """Test that database connection is successfully established."""
        assert db_client.connection is not None
        assert db_client.connection.closed == 0  # 0 means connection is open

    def test_run_simple_query(self, db_client):
        """Test running a simple SELECT query."""
        result = db_client.run_sql("SELECT 1 as test_value;")

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["test_value"] == 1

    def test_run_query_with_schema(self, db_client):
        """Test querying information schema."""
        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            LIMIT 1;
        """
        result = db_client.run_sql(query)

        assert isinstance(result, list)
        assert len(result) > 0
        assert "table_name" in result[0]

    def test_run_query_returns_empty_list(self, db_client):
        """Test query that returns no rows."""
        result = db_client.run_sql("SELECT 1 WHERE 1=0;")

        assert isinstance(result, list)
        assert len(result) == 0

    def test_invalid_query_raises_exception(self, db_client):
        """Test that invalid SQL raises an exception."""
        with pytest.raises(Exception, match="Query execution failed"):
            db_client.run_sql("SELECT * FROM nonexistent_table_xyz;")

    def test_connection_close(self, config):
        """Test that connection can be closed properly."""
        client = DbClient(config)
        assert client.connection is not None

        client.close()
        assert client.connection.closed == 1  # 1 means connection is closed

    def test_query_after_close_raises_exception(self, config):
        """Test that querying after close raises an exception."""
        client = DbClient(config)
        client.close()

        with pytest.raises(Exception):
            client.run_sql("SELECT 1;")

    def test_config_initialization(self, config):
        """Test that Config object is properly initialized."""
        assert hasattr(config, "DB_HOST")
        assert hasattr(config, "DB_PORT")
        assert hasattr(config, "DB_NAME")
        assert hasattr(config, "DB_USER")
        assert hasattr(config, "DB_PASSWORD")

    def test_db_client_with_invalid_config(self):
        """Test that DbClient fails gracefully with invalid config."""
        # Create a Config with invalid credentials
        import os

        os.environ["DB_HOST"] = "invalid_host"
        os.environ["DB_NAME"] = "invalid_db"
        os.environ["DB_USER"] = "invalid_user"
        os.environ["DB_PASSWORD"] = "invalid_pass"
        os.environ["DB_PORT"] = "5432"

        config = Config()
        client = DbClient(config)

        # Connection should fail, so connection should be None
        assert client.connection is None


# Instructions for running these tests:
#
# Run all tests including integration tests:
#   pytest tests/ -v
#
# Run only unit tests (skip integration tests):
#   pytest tests/ -v -m "not integration"
#
# Run only integration tests:
#   pytest tests/ -v -m integration
