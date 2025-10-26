"""Prompt builder for text-to-SQL generation."""

from typing import Optional


class PromptBuilder:
    """Builds prompts for SQL generation from user questions and database schema."""

    def __init__(self):
        """Initialize prompt builder with default templates."""
        self.system_template = """You are an expert SQL query generator for PostgreSQL databases.

Your task is to convert natural language questions into valid PostgreSQL SQL queries.

Guidelines:
1. Generate ONLY the SQL query, no explanations or markdown formatting
2. Use proper PostgreSQL syntax
3. Generate only SELECT queries (read-only)
4. Use appropriate JOINs when querying multiple tables
5. Include WHERE clauses for filtering when relevant
6. Use LIMIT when appropriate to avoid returning too many rows
7. Return the raw SQL query without ```sql``` markers or additional text

Database Schema:
{schema}"""

    def build_system_message(self, schema: str) -> str:
        """Build system message with schema context.

        Args:
            schema: Formatted database schema string

        Returns:
            System message for LLM
        """
        return self.system_template.format(schema=schema)

    def build_user_message(self, question: str) -> str:
        """Build user message from question.

        Args:
            question: User's natural language question

        Returns:
            User message for LLM
        """
        return f"Generate a SQL query to answer: {question}"

    def build_full_prompt(self, schema: str, question: str) -> str:
        """Build complete prompt combining schema and question.

        Args:
            schema: Formatted database schema string
            question: User's natural language question

        Returns:
            Complete prompt string
        """
        system_msg = self.build_system_message(schema)
        user_msg = self.build_user_message(question)
        return f"{system_msg}\n\nUser Question:\n{user_msg}"
