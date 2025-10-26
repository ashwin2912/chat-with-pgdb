"""Text-to-SQL agent orchestrator."""

from typing import Dict, List, Any
from .context_service import ContextService
from .llm_client import LLMClient
from .prompt_builder import PromptBuilder
from ..core.db_client import DbClient
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class TextToSQLAgent:
    """Orchestrates the text-to-SQL generation process."""

    def __init__(
        self,
        db_client: DbClient,
        llm_client: LLMClient,
        context_service: ContextService = None,
        prompt_builder: PromptBuilder = None,
    ):
        """Initialize the agent with required components.

        Args:
            db_client: Database client for query execution
            llm_client: LLM client for SQL generation
            context_service: Optional context service (created if not provided)
            prompt_builder: Optional prompt builder (created if not provided)
        """
        self.db_client = db_client
        self.llm_client = llm_client
        self.context_service = context_service or ContextService(db_client)
        self.prompt_builder = prompt_builder or PromptBuilder()
        logger.info("TextToSQLAgent initialized")

    def generate_sql(self, question: str) -> str:
        """Generate SQL query from natural language question.

        Args:
            question: User's natural language question

        Returns:
            Generated SQL query string
        """
        try:
            # Get schema context
            logger.info(f"Generating SQL for question: {question}")
            schema = self.context_service.format_schema_for_llm()

            # Build prompt
            system_message = self.prompt_builder.build_system_message(schema)
            user_message = self.prompt_builder.build_user_message(question)

            # Generate SQL
            sql_query = self.llm_client.generate_with_system_message(
                system_message, user_message
            )

            # Clean up the query (remove markdown formatting if present)
            sql_query = self._clean_sql_query(sql_query)

            logger.info(f"Successfully generated SQL: {sql_query}")
            return sql_query

        except Exception as e:
            logger.error(f"Failed to generate SQL: {e}")
            raise

    def execute_query(self, question: str) -> List[Dict[str, Any]]:
        """Generate SQL from question and execute it.

        Args:
            question: User's natural language question

        Returns:
            Query results as list of dictionaries
        """
        try:
            # Generate SQL
            sql_query = self.generate_sql(question)

            # Validate query is SELECT only (safety check)
            if not self._is_safe_query(sql_query):
                raise ValueError("Only SELECT queries are allowed")

            # Execute query
            logger.info("Executing generated SQL query")
            results = self.db_client.run_sql(sql_query)
            logger.info(f"Query returned {len(results)} rows")

            return results

        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            raise

    def _clean_sql_query(self, sql_query: str) -> str:
        """Clean SQL query by removing markdown formatting.

        Args:
            sql_query: Raw SQL query from LLM

        Returns:
            Cleaned SQL query
        """
        # Remove markdown code blocks
        sql_query = sql_query.strip()
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        elif sql_query.startswith("```"):
            sql_query = sql_query[3:]

        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]

        return sql_query.strip()

    def _is_safe_query(self, sql_query: str) -> bool:
        """Check if query is safe (SELECT only).

        Args:
            sql_query: SQL query to validate

        Returns:
            True if query is safe, False otherwise
        """
        sql_upper = sql_query.strip().upper()

        # Must start with SELECT
        if not sql_upper.startswith("SELECT"):
            logger.warning(f"Unsafe query detected: does not start with SELECT")
            return False

        # Check for dangerous keywords
        dangerous_keywords = [
            "DROP",
            "DELETE",
            "UPDATE",
            "INSERT",
            "ALTER",
            "CREATE",
            "TRUNCATE",
        ]
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                logger.warning(f"Unsafe query detected: contains {keyword}")
                return False

        return True
