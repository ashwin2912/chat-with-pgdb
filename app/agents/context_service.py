"""Context service for retrieving database schema and metadata."""

from typing import Dict, List
from ..core.db_client import DbClient
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class ContextService:
    """Retrieves and formats database context for SQL generation."""

    def __init__(self, db_client: DbClient):
        """Initialize with a database client.

        Args:
            db_client: Database client for executing queries
        """
        self.db_client = db_client

    def get_schema_info(self) -> List[Dict]:
        """Get database schema information.

        Returns:
            List of dictionaries containing table and column information
        """
        query = """
            SELECT
                table_name,
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position;
        """
        try:
            result = self.db_client.run_sql(query)
            logger.info(
                f"Retrieved schema for {len(set(r['table_name'] for r in result))} tables"
            )
            return result
        except Exception as e:
            logger.error(f"Failed to retrieve schema: {e}")
            raise

    def format_schema_for_llm(self) -> str:
        """Format schema information as a readable string for LLM context.

        Returns:
            Formatted schema string
        """
        schema_info = self.get_schema_info()

        # Group columns by table
        tables = {}
        for row in schema_info:
            table = row["table_name"]
            if table not in tables:
                tables[table] = []

            nullable = "NULL" if row["is_nullable"] == "YES" else "NOT NULL"
            tables[table].append(
                f"  - {row['column_name']} ({row['data_type']}) {nullable}"
            )

        # Format as readable text
        formatted = "Database Schema:\n\n"
        for table, columns in sorted(tables.items()):
            formatted += f"Table: {table}\n"
            formatted += "\n".join(columns)
            formatted += "\n\n"

        return formatted.strip()

    def get_sample_data(self, table_name: str, limit: int = 3) -> List[Dict]:
        """Get sample rows from a table.

        Args:
            table_name: Name of the table
            limit: Number of rows to retrieve

        Returns:
            List of sample rows
        """
        query = f"SELECT * FROM {table_name} LIMIT {limit};"
        try:
            result = self.db_client.run_sql(query)
            logger.info(f"Retrieved {len(result)} sample rows from {table_name}")
            return result
        except Exception as e:
            logger.error(f"Failed to retrieve sample data from {table_name}: {e}")
            raise
