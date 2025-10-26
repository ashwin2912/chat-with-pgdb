"""FastAPI application for text-to-SQL queries."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from ..config import Config
from ..core.db_client import DbClient
from ..agents.llm_client import LLMClient
from ..agents.text_to_sql_agent import TextToSQLAgent

# Initialize FastAPI app
app = FastAPI(
    title="Chat with PostgreSQL DB",
    description="Natural language to SQL query API",
    version="0.1.0",
)

# Global instances (initialized on startup)
db_client = None
agent = None


@app.on_event("startup")
async def startup_event():
    """Initialize database and agent on startup."""
    global db_client, agent

    config = Config()
    db_client = DbClient(config)
    llm_client = LLMClient(api_key=config.ANTHROPIC_API_KEY)
    agent = TextToSQLAgent(db_client=db_client, llm_client=llm_client)


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    if db_client:
        db_client.close()


# Request/Response models
class QuestionRequest(BaseModel):
    """Request model for asking questions."""

    question: str


class QuestionResponse(BaseModel):
    """Response model for question answers."""

    question: str
    sql_query: str
    results: List[Dict[str, Any]]
    row_count: int


# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "chat-with-pgdb"}


@app.post("/ask_question", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Generate SQL from natural language question and execute it.

    Args:
        request: QuestionRequest containing the natural language question

    Returns:
        QuestionResponse with SQL query and results
    """
    try:
        # Generate SQL
        sql_query = agent.generate_sql(request.question)

        # Execute query
        results = agent.execute_query(request.question)

        return QuestionResponse(
            question=request.question,
            sql_query=sql_query,
            results=results,
            row_count=len(results),
        )

    except ValueError as e:
        # Safety validation errors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # General errors
        raise HTTPException(
            status_code=500, detail=f"Error processing question: {str(e)}"
        )
