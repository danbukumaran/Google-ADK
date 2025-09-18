
import warnings
warnings.filterwarnings("ignore")

import os, platform
from datetime import datetime
import asyncio
import json
from typing import Dict, Any, Optional

from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv
from contextlib import AsyncExitStack
from google.adk.runners import Runner
from google.adk.agents import RunConfig
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.genai import types

from google.adk.sessions import DatabaseSessionService
from .custom_agent import OrchestratorAgent
from ..sub_agents.data_sources.files_source.agent import create_filesystem_agent_asyc
from ..sub_agents.data_sources.db_source.agent import create_local_db_agent
from ..sub_agents.summarizer.agent import create_summarizer_agent
from ..sub_agents.data_sources.db_nl2sql_source.agent import create_nl2sql_db_agent_asyc
from ..sub_agents.data_sources.db_nl2sql_source.db_servers.mssqlserver import MSSQlServer
from ..sub_agents.analytics.agent import create_analytics_agent

from .utils import *

import logging
logger = logging.getLogger(__name__)


# --- Global Agent/Service Instances ---
# These will be initialized once and then reused.
_orchestrator_agent_instance: Optional[OrchestratorAgent] = None
_session_service_instance: Optional[DatabaseSessionService] = None



# --- Initialization Function ---
async def initialize_global_agents_and_service():
    """
    Initializes all agents and the session service once globally.
    This function should be called at application startup.
    """
    global _orchestrator_agent_instance, _session_service_instance

    if _orchestrator_agent_instance is not None and _session_service_instance is not None:
        logger.info("Agents and Session Service already initialized. Skipping re-initialization.")
        return

    logger.info("Initializing ADK Agents and Session Service globally...")
    
    try:

        llm_model = LiteLlm(model=os.getenv("ROOT_AGENT_MODEL"))

        # Ensure the directory for the DB file exists
        db_dir = os.path.join(os.path.dirname(__file__),"..", "data/session_data")
        os.makedirs(db_dir, exist_ok=True)
 
        # _session_service_instance = InMemorySessionService()
        _session_service_instance = DatabaseSessionService(db_url=f"sqlite:///{db_dir}/aia_sessions.db")

        filesystem_agent = await create_filesystem_agent_asyc()
        db_agent = create_local_db_agent()
        summarizer_agent = create_summarizer_agent()
        nl2sql_db_agent = await create_nl2sql_db_agent_asyc()
        approver_agent = None #create_approver_agent()
        analyst_agent = create_analytics_agent()

        # for nl2sql DB
        mssql_db = MSSQlServer(host=os.getenv("DB_HOST"), 
                            user=os.getenv("DB_USER"), 
                            password=os.getenv("DB_PASSWORD"), 
                            database=os.getenv("DB_DATABASE"))

        # call root agent
        _orchestrator_agent_instance = OrchestratorAgent(model_name=llm_model
                                               ,fs_agent_attr=filesystem_agent
                                               ,db_agent_attr=db_agent
                                               ,summarizer_agent_attr=summarizer_agent
                                               ,analyst_agent_attr=analyst_agent
                                               ,nl2sql_dg_agent_attr=nl2sql_db_agent
                                               ,mssql_db_attr=mssql_db )
                                            #  ,approver_agent_attr=approver_agent)
    
        logger.info("ADK Agents and Session Service initialized globally.")

    except Exception as e:
        err = f"An unexpected error occurred during agent initialization : {e}"
        logger.error(err)
        # final_response_text = err
        raise 


def unload_global_agents_and_service():
    global _orchestrator_agent_instance, _session_service_instance
    del _orchestrator_agent_instance
    del _session_service_instance


# --- Execution Function (now uses global instances) ---
async def execute_agent_async(
        user_query: str,
        app_name: str,
        user_id: str,
        session_id: str
    ) -> tuple[str, Optional[bytes]]:
    """
    Executes the orchestrator agent with the given query.
    Reuses globally initialized agent and session service instances.

    Args:
        user_query (str): The user's input query.
        app_name (str): The name of your ADK application.
        user_id (str): A unique identifier for the user.
        session_id (str): A unique identifier for the conversation session.

    Returns:
        tuple[str, Optional[bytes]]: The text response from the agent and
                                     an optional binary response (e.g., image).
    """

    if _orchestrator_agent_instance is None or _session_service_instance is None:
        raise RuntimeError("ADK agents and session service are not initialized. Call initialize_global_agents_and_service() first.")

    # Get or create session based on session_id
    initial_states = {
        "user_query": "",
        "user:user_query_pending" : "",
        "user:approval_status": "",
        "filesystem_output" : "",
        "localdb_output": "",
        "analytics_output": "",
        "approver_output": "",
        "ai_agent_output": ""
    }

    try:
        session = await _session_service_instance.get_session(app_name=app_name, 
                                                              user_id=user_id, 
                                                              session_id=session_id,
                                                              )
       
        if session is None:
            session = await _session_service_instance.create_session(app_name=app_name, 
                                                                     user_id=user_id, 
                                                                     session_id=session_id,
                                                                     state=initial_states
                                                                    )
            logger.info(f"Created new session: {session.id} ---")
        else:
            logger.info(f"Reusing existing session: {session_id} ---")
    except Exception as e: 
        # session = await _session_service_instance.create_session(app_name=app_name, user_id=user_id, session_id=session_id)
        logger.info(f"Error while handling session object {e} ---")


    try:

        logger.info(f"{datetime.now()} : AI Agent workflow Started .....")

        # Default response
        final_response_text = "Awaiting Agent's final response." 
        binary_bytes = None

        # artifacts for bytes
        artifacts_service = InMemoryArtifactService()

        # reset state values
        reset_state = {
            "user_query": "",
            "filesystem_output" : "",
            "localdb_output": "",
            "analytics_output": "",
            "approver_output": "",
            "ai_agent_output": ""
        }
        system_event = update_state(reset_state,"reset_state","main")
        await _session_service_instance.append_event(session, system_event)
        logger.info("'append_event' called with explicit state delta - reset state values")

        # Create a RunConfig instance to customize agent behavior
        my_run_config = RunConfig(
            max_llm_calls=20   # Limit LLM calls
        )

        # Initialize the Runner with the global orchestrator agent and session service
        runner = Runner(agent=_orchestrator_agent_instance
                        ,app_name=app_name
                        ,session_service=_session_service_instance
                        ,artifact_service=artifacts_service)

        content = types.Content(role='user', parts=[types.Part(text=user_query)])

        logger.info(f"{datetime.now()} : AI Agent Running .....")
        events_async = runner.run_async(
            session_id=session.id, 
            user_id=user_id, 
            new_message=content,
            run_config=my_run_config
        )

        async for event in events_async:
            # You can uncomment the line below to see *all* events during execution
            # logger.debug(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

            # for testing
            # if event.content and event.content.parts:
            #     calls = event.get_function_calls()
            #     if calls:
            #         for call in calls:
            #             tool_name = call.name
            #             print(f" Type: Tool Call Request : {tool_name}")
            # elif event.get_function_responses():
            #     print("  Type: Tool Result")

            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response_text = event.content.parts[0].text
                elif event.actions and event.actions.escalate: # Handle potential errors/escalations
                    final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                
                # below break stop processing events once the final response is found from the first sub agent
                # break 
        
        # print(f"AI Response: {final_response_text}")
        logger.info(f"{datetime.now()} : AI Agent workflow completed successfully ...")
    
        try:
            # return binary data
            lst_filenames = await artifacts_service.list_artifact_keys(app_name=app_name,
                                                                       user_id=user_id,
                                                                       session_id=session.id)
            for filename in lst_filenames:
                logger.info(f"getting artifact work : {datetime.now()}")
                report_artifact = await artifacts_service.load_artifact(
                            app_name=app_name, 
                            user_id=user_id, 
                            session_id=session.id, 
                            filename=filename
                )
        
                if report_artifact and report_artifact.inline_data:
                    logger.info(f"Successfully loaded latest artifact '{filename}'.")
                    logger.info(f"MIME Type: {report_artifact.inline_data.mime_type}")
                    # Process the report_artifact.inline_data.data (bytes)
                    binary_bytes = report_artifact.inline_data.data
                    # print(f"Report size: {len(binary_bytes)} bytes.")
                else:
                    logger.warning(f"Artifact '{filename}' not found.")

        except ValueError as e:
            logger.error(f"Error loading artifact: {e}. Is ArtifactService configured?")
        except Exception as e:
            logger.error(f"An unexpected error occurred during artifact load: {e}")

        # for debugging
        # logger.info("Final Session State:")
        # final_session = await _session_service_instance.get_session(app_name=app_name, 
        #                                         user_id=user_id, 
        #                                         session_id=session.id)
        # logger.info(final_session.events)
        # logger.info(json.dumps(final_session.state, indent=2))

 
    except Exception as e:
        err = f"An unexpected error occurred during agent execution: {e}"
        logger.error(err)
        raise 

    # return final response to API
    if final_response_text:
        final_response_text = final_response_text.replace("```","").replace("html","")

    return final_response_text, binary_bytes

  
async def async_main():
      
    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("👋 Goodbye!")
            break
        
        ai_response = await execute_agent(user_input)
        print(f"ai response:  {ai_response}")
       

if __name__ == '__main__':
    try:
        asyncio.run(async_main())
    except Exception as e:
        print(f"An error occurred: {e}")