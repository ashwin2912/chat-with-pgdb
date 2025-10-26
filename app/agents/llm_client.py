"""LLM client wrapper for text-to-SQL generation."""

from typing import Optional
from langchain_anthropic import ChatAnthropic
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class LLMClient:
    """Wrapper for LLM API calls, making it easier to test and swap providers."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-5-20250929",
        temperature: float = 0.0,
    ):
        """Initialize LLM client.

        Args:
            api_key: Anthropic API key
            model: Model name to use
            temperature: Temperature for generation (0.0 = deterministic)
        """
        self.model = model
        self.temperature = temperature
        self.llm = ChatAnthropic(api_key=api_key, model=model, temperature=temperature)
        logger.info(f"Initialized LLM client with model: {model}")

    def generate_sql(self, prompt: str) -> str:
        """Generate SQL query from prompt.

        Args:
            prompt: Full prompt including schema and user question

        Returns:
            Generated SQL query string
        """
        try:
            logger.info("Sending request to LLM for SQL generation")
            response = self.llm.invoke(prompt)
            sql_query = response.content.strip()
            logger.info(f"Generated SQL query: {sql_query[:100]}...")
            return sql_query
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise

    def generate_with_system_message(
        self, system_message: str, user_message: str
    ) -> str:
        """Generate SQL with separate system and user messages.

        Args:
            system_message: System instructions
            user_message: User question

        Returns:
            Generated SQL query string
        """
        try:
            logger.info("Sending request to LLM with system message")
            messages = [("system", system_message), ("user", user_message)]
            response = self.llm.invoke(messages)
            sql_query = response.content.strip()
            logger.info(f"Generated SQL query: {sql_query[:100]}...")
            return sql_query
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise
