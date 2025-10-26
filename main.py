from app.config import Config
from app.core.db_client import DbClient
from app.core.database import DatabaseManager


def main():
    try:
        # Create Config instance
        config = Config()

        # Database configuration from Config instance
        db_config = {
            "host": config.DB_HOST,
            "port": config.DB_PORT,
            "database": config.DB_NAME,
            "user": config.DB_USER,
            "password": config.DB_PASSWORD,
        }

        # Create database client and connect
        db_client = DbClient(db_config)
        print("Successfully connected to the database!")

        # Create Database instance for schema operations
        database = DatabaseManager(db_client)

        # Get and print schema
        schema = database.get_schema(db_client=db_client)
        print(f"\nDatabase schema:\n{schema}")

        # Close connection
        db_client.close()

    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
