"""Unit tests for TextToSQLAgent."""

import pytest
from unittest.mock import Mock, MagicMock
from app.agents.text_to_sql_agent import TextToSQLAgent


class TestTextToSQLAgent:
    """Test suite for TextToSQLAgent."""

    @pytest.fixture
    def mock_db_client(self):
        """Create a mock database client."""
        return Mock()

    @pytest.fixture
    def mock_llm_client(self):
        """Create a mock LLM client."""
        return Mock()

    @pytest.fixture
    def mock_context_service(self):
        """Create a mock context service."""
        mock = Mock()
        mock.format_schema_for_llm.return_value = "Table: users\n  - id (integer)"
        return mock

    @pytest.fixture
    def mock_prompt_builder(self):
        """Create a mock prompt builder."""
        mock = Mock()
        mock.build_system_message.return_value = "System message"
        mock.build_user_message.return_value = "User question"
        return mock

    @pytest.fixture
    def agent(
        self, mock_db_client, mock_llm_client, mock_context_service, mock_prompt_builder
    ):
        """Create a TextToSQLAgent instance with mocks."""
        return TextToSQLAgent(
            db_client=mock_db_client,
            llm_client=mock_llm_client,
            context_service=mock_context_service,
            prompt_builder=mock_prompt_builder,
        )

    def test_generate_sql(
        self, agent, mock_llm_client, mock_context_service, mock_prompt_builder
    ):
        """Test SQL generation from question."""
        # Arrange
        question = "Show me all users"
        expected_sql = "SELECT * FROM users;"
        mock_llm_client.generate_with_system_message.return_value = expected_sql

        # Act
        result = agent.generate_sql(question)

        # Assert
        assert result == expected_sql
        mock_context_service.format_schema_for_llm.assert_called_once()
        mock_prompt_builder.build_system_message.assert_called_once()
        mock_prompt_builder.build_user_message.assert_called_once_with(question)
        mock_llm_client.generate_with_system_message.assert_called_once()

    def test_generate_sql_cleans_markdown(self, agent, mock_llm_client):
        """Test that SQL generation removes markdown formatting."""
        # Arrange
        question = "Count users"
        sql_with_markdown = "```sql\nSELECT COUNT(*) FROM users;\n```"
        expected_sql = "SELECT COUNT(*) FROM users;"
        mock_llm_client.generate_with_system_message.return_value = sql_with_markdown

        # Act
        result = agent.generate_sql(question)

        # Assert
        assert result == expected_sql
        assert "```" not in result

    def test_execute_query(self, agent, mock_db_client, mock_llm_client):
        """Test query execution."""
        # Arrange
        question = "Show me all users"
        sql_query = "SELECT * FROM users LIMIT 5;"
        expected_results = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

        mock_llm_client.generate_with_system_message.return_value = sql_query
        mock_db_client.run_sql.return_value = expected_results

        # Act
        results = agent.execute_query(question)

        # Assert
        assert results == expected_results
        mock_db_client.run_sql.assert_called_once_with(sql_query)

    def test_execute_query_rejects_unsafe_queries(self, agent, mock_llm_client):
        """Test that unsafe queries are rejected."""
        # Arrange
        question = "Delete all users"
        unsafe_sql = "DELETE FROM users;"
        mock_llm_client.generate_with_system_message.return_value = unsafe_sql

        # Act & Assert
        with pytest.raises(ValueError, match="Only SELECT queries are allowed"):
            agent.execute_query(question)

    def test_is_safe_query_accepts_select(self, agent):
        """Test that SELECT queries are considered safe."""
        assert agent._is_safe_query("SELECT * FROM users;")
        assert agent._is_safe_query("select id, name from posts;")

    def test_is_safe_query_rejects_dangerous_keywords(self, agent):
        """Test that dangerous SQL keywords are rejected."""
        dangerous_queries = [
            "DROP TABLE users;",
            "DELETE FROM users WHERE id = 1;",
            "UPDATE users SET name = 'test';",
            "INSERT INTO users VALUES (1, 'test');",
            "ALTER TABLE users ADD COLUMN test VARCHAR;",
            "CREATE TABLE test (id INT);",
            "TRUNCATE TABLE users;",
        ]

        for query in dangerous_queries:
            assert not agent._is_safe_query(query)

    def test_clean_sql_query_removes_markdown(self, agent):
        """Test SQL query cleaning."""
        test_cases = [
            ("```sql\nSELECT * FROM users;\n```", "SELECT * FROM users;"),
            ("```\nSELECT * FROM users;\n```", "SELECT * FROM users;"),
            ("SELECT * FROM users;", "SELECT * FROM users;"),
            ("  SELECT * FROM users;  ", "SELECT * FROM users;"),
        ]

        for input_sql, expected_output in test_cases:
            assert agent._clean_sql_query(input_sql) == expected_output

    def test_agent_initialization_with_defaults(self, mock_db_client, mock_llm_client):
        """Test that agent can be initialized with default context service and prompt builder."""
        # Act
        agent = TextToSQLAgent(db_client=mock_db_client, llm_client=mock_llm_client)

        # Assert
        assert agent.context_service is not None
        assert agent.prompt_builder is not None
