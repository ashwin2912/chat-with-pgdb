"""Unit tests for PromptBuilder."""

import pytest
from app.agents.prompt_builder import PromptBuilder


class TestPromptBuilder:
    """Test suite for PromptBuilder."""

    @pytest.fixture
    def prompt_builder(self):
        """Create a PromptBuilder instance."""
        return PromptBuilder()

    @pytest.fixture
    def sample_schema(self):
        """Sample database schema for testing."""
        return """Table: users
  - id (integer) NOT NULL
  - name (varchar) NULL
  - email (varchar) NULL

Table: posts
  - id (integer) NOT NULL
  - user_id (integer) NOT NULL
  - title (varchar) NULL"""

    def test_build_system_message(self, prompt_builder, sample_schema):
        """Test building system message with schema."""
        result = prompt_builder.build_system_message(sample_schema)

        assert sample_schema in result
        assert "SQL query generator" in result
        assert "PostgreSQL" in result
        assert "SELECT queries" in result
        assert "read-only" in result

    def test_build_user_message(self, prompt_builder):
        """Test building user message from question."""
        question = "Show me all users"
        result = prompt_builder.build_user_message(question)

        assert question in result
        assert "SQL query" in result

    def test_build_full_prompt(self, prompt_builder, sample_schema):
        """Test building complete prompt."""
        question = "How many posts are there?"
        result = prompt_builder.build_full_prompt(sample_schema, question)

        assert sample_schema in result
        assert question in result
        assert "SQL query generator" in result
        assert "User Question:" in result

    def test_system_message_contains_guidelines(self, prompt_builder, sample_schema):
        """Test that system message contains important guidelines."""
        result = prompt_builder.build_system_message(sample_schema)

        guidelines = ["SELECT", "read-only", "PostgreSQL", "JOINs", "WHERE", "LIMIT"]
        for guideline in guidelines:
            assert guideline in result
