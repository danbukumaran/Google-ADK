import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Response
from .coordinator.main import execute_agent_async, initialize_global_agents_and_service, unload_global_agents_and_service
from pydantic import BaseModel
import json
import base64
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, Security, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

from .config.logger_config import setup_logger
setup_logger()

import logging
logger = logging.getLogger(__name__)


# --- FastAPI Startup Event ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initializes ADK agents and the session service once when the FastAPI app starts.
    """

    try:
        logger.info("API startup event: Calling initialize_global_agents_and_service()...")
        await initialize_global_agents_and_service()
        logger.info("API startup event: ADK agents and services ready.")

        yield

        unload_global_agents_and_service()
        logger.info("API shutdown event: ADK agents and services removed.")
    except Exception as e:
        logger.error(f"An Error occured during API setup : {e}")

app = FastAPI(lifespan=lifespan)


# --- Request Payload Model ---
class Payload(BaseModel):
    user_query: str
    user_id: str # Required: Unique identifier for the user
    session_id: Optional[str] = None # Optional: Unique identifier for the conversation session


# Create a FastAPI security dependency
api_key_header = APIKeyHeader(name=os.getenv("API_KEY_NAME"), auto_error=False)

# Dependency to validate API key
async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key == os.getenv("API_KEY"):
        return api_key
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN,
        detail="Could not validate API key"
    )


# --- API Endpoint ---
@app.post("/run", dependencies=[Depends(get_api_key)])
async def execute(query: Payload):
    """
    FastAPI endpoint to run the agent.
    It reuses the globally initialized agent and session service.
    """
    app_name = "ai_analyst_app" 

    # Determine the session_id to use. If not provided by the client,
    # generate a default based on user_id. For production, consider using UUIDs.
    current_session_id = query.session_id if query.session_id else f"{query.user_id}_default_session"

    logger.info(f"--- API Call Begin: User '{query.user_id}', Session '{current_session_id}' ---")
    
    # Call the execute_agent function, which now uses the globally initialized instances.
    txt_response, binary_response = await execute_agent_async(
        user_query=query.user_query,
        app_name=app_name,
        user_id=query.user_id,
        session_id=current_session_id
    )

    base64_encoded = ""

    # Encode binary data to base64
    if binary_response:
        base64_encoded = base64.b64encode(binary_response).decode('utf-8')

    # Create JSON object
    json_data = {
        "txt_data": txt_response,
        "binary_data": base64_encoded
    }

    # Convert to JSON string
    json_string = json.dumps(json_data)

    logger.info(f"---- API Call End ----")
    return json_string


# --- Health Check Endpoint (Unprotected) ---
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "FastAPI app is running."}