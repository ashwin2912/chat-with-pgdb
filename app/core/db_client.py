from ..config import Config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class DbClient:
    def __init__(self, config: Config):
        self.config = config
        self.connection = None

        try:
            logger.info("Initializing db_client")
            self.connection = self._connect_database()

        except Exception as e:
            logger.error(f"Failed to initialize client: {e}")

    def _connect_database(self) -> None:
        """Connect to PostgreSQL database."""
        try:
            logger.info(f"Connecting to db with {self.config}")
            connection = self.connect_to_postgres()
            logger.info("Database connection established")
            return connection
        except Exception as e:
            logger.error(f"Database connection failed: {e}")

    def ensure_db_connection(self) -> None:
        """Ensure database connection is active, reconnect if needed."""
        try:
            self.run_sql("SELECT 1")
        except Exception as e:
            logger.warning(f"Database connection lost: {e}. Reconnecting...")
        try:
            self._connect_database()
        except Exception as reconnect_error:
            logger.error(f"Reconnection failed: {reconnect_error}")

    def connect_to_postgres(self):
        """Connect to a PostgreSQL database and return the connection object."""
        import psycopg2

        logger.info(f"Entered connect_to_postgres with :{self.config}")
        try:
            logger.info("Entered try block in connect_to_postgres")
            db_config = self.config
            self.connection = psycopg2.connect(**db_config)
            return self.connection
        except Exception as e:
            raise Exception(f"Failed to connect to PostgreSQL: {str(e)}")

    def run_sql(self, query):
        """Execute a SQL query and return the results as a list of dictionaries."""
        import psycopg2.extras

        try:
            cursor = self.connection.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            cursor.execute(query)

            # If it's a SELECT query, fetch results
            if query.strip().upper().startswith("SELECT"):
                results = cursor.fetchall()
                return [dict(row) for row in results]
            else:
                # For INSERT, UPDATE, DELETE, etc.
                self.connection.commit()
                return {"affected_rows": cursor.rowcount}
        except Exception as e:
            self.connection.rollback()
            raise Exception(f"Query execution failed: {str(e)}")
        finally:
            cursor.close()
