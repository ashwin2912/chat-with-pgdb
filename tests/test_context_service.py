"""Unit tests for ContextService."""

import pytest
from unittest.mock import Mock, MagicMock
from app.agents.context_service import ContextService


class TestContextService:
    """Test suite for ContextService."""

    @pytest.fixture
    def mock_db_client(self):
        """Create a mock database client."""
        mock = Mock()
        return mock

    @pytest.fixture
    def context_service(self, mock_db_client):
        """Create a ContextService instance with mock db client."""
        return ContextService(mock_db_client)

    def test_get_schema_info(self, context_service, mock_db_client):
        """Test getting schema information."""
        # Arrange
        mock_schema = [
            {
                "table_name": "users",
                "column_name": "id",
                "data_type": "integer",
                "is_nullable": "NO",
            },
            {
                "table_name": "users",
                "column_name": "name",
                "data_type": "varchar",
                "is_nullable": "YES",
            },
        ]
        mock_db_client.run_sql.return_value = mock_schema

        # Act
        result = context_service.get_schema_info()

        # Assert
        assert result == mock_schema
        mock_db_client.run_sql.assert_called_once()
        call_args = mock_db_client.run_sql.call_args[0][0]
        assert "information_schema.columns" in call_args

    def test_format_schema_for_llm(self, context_service, mock_db_client):
        """Test formatting schema for LLM."""
        # Arrange
        mock_schema = [
            {
                "table_name": "users",
                "column_name": "id",
                "data_type": "integer",
                "is_nullable": "NO",
            },
            {
                "table_name": "users",
                "column_name": "email",
                "data_type": "varchar",
                "is_nullable": "YES",
            },
            {
                "table_name": "posts",
                "column_name": "id",
                "data_type": "integer",
                "is_nullable": "NO",
            },
        ]
        mock_db_client.run_sql.return_value = mock_schema

        # Act
        result = context_service.format_schema_for_llm()

        # Assert
        assert "Database Schema:" in result
        assert "Table: users" in result
        assert "Table: posts" in result
        assert "id (integer) NOT NULL" in result
        assert "email (varchar) NULL" in result

    def test_get_sample_data(self, context_service, mock_db_client):
        """Test getting sample data from a table."""
        # Arrange
        table_name = "users"
        mock_data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        mock_db_client.run_sql.return_value = mock_data

        # Act
        result = context_service.get_sample_data(table_name, limit=2)

        # Assert
        assert result == mock_data
        mock_db_client.run_sql.assert_called_once()
        call_args = mock_db_client.run_sql.call_args[0][0]
        assert f"SELECT * FROM {table_name}" in call_args
        assert "LIMIT 2" in call_args

    def test_get_schema_info_error_handling(self, context_service, mock_db_client):
        """Test error handling when schema retrieval fails."""
        # Arrange
        mock_db_client.run_sql.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            context_service.get_schema_info()

    def test_get_sample_data_error_handling(self, context_service, mock_db_client):
        """Test error handling when sample data retrieval fails."""
        # Arrange
        mock_db_client.run_sql.side_effect = Exception("Table not found")

        # Act & Assert
        with pytest.raises(Exception, match="Table not found"):
            context_service.get_sample_data("nonexistent_table")
