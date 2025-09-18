"""Database Agent: get data from database using MCP."""

import os
from typing import Optional
from google.genai import types
from google.adk.agents import Agent, LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext

# from toolbox_langchain import ToolboxClient
from google.adk.models import LlmResponse, LlmRequest
from google.adk.tools.base_tool import BaseTool
from typing import Dict, Any, List
from google.adk.models.lite_llm import LiteLlm
from .prompts import return_instructions

# from google.adk.tools.toolbox_toolset import ToolboxToolset 
from toolbox_core import ToolboxSyncClient, ToolboxClient
from typing import AsyncGenerator

import logging
logger = logging.getLogger(__name__)


# load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))

# run the below to start the mcp toolbox server
# toolbox.exe --tools-file "tools.yaml" --log-level "DEBUG"

# import litellm
# litellm._turn_on_debug() 
# os.environ["LITELLM_DEBUG"] = "true" # Also set as environment variable for more verbose logging


def get_db_tools():
    """Gets tools from the Local database MCP Server."""
    # print("Attempting to connect to Local database server...")

    toolbox_client = ToolboxSyncClient(os.getenv("DATABASE_TOOL_URL"))
    return toolbox_client.load_toolset("my-toolset")

# pending - getting error while reading tool_response in after_tool_call
async def get_db_tools_asyc() -> List[BaseTool]:
    """Gets tools from the Local database MCP Server."""
    # print("Attempting to connect to Local database server...")

    toolbox_client = ToolboxClient(os.getenv("DATABASE_TOOL_URL"))
    return await toolbox_client.load_toolset("my-toolset")


def setup_before_agent_call(callback_context: CallbackContext) -> None:
    """Setup the agent."""
    agent_name = callback_context.agent_name
    logger.debug(f"[Callback] Before agent call : {agent_name}")
    return None

def setup_afer_agent_call(callback_context: CallbackContext) -> None:
    agent_name = callback_context.agent_name
    print(f"[Callback] After agetn call - {agent_name} is executed")

    return None

def setup_before_model_call(
    callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
    agent_name = callback_context.agent_name
    print(f"[Callback] Befor model call : {agent_name}")
    return None

def setup_after_model_call(callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """Inspects/modifies the LLM response after it's received."""
    agent_name = callback_context.agent_name
    print(f"[Callback] After model call for agent: {agent_name}")

    # --- Inspection ---
    original_text = ""
    if llm_response.content and llm_response.content.parts:
        # Assuming simple text response for this example
        if llm_response.content.parts[0].text:
            original_text = llm_response.content.parts[0].text
            print(f"[Callback] Inspected original response text: '{original_text[:100]}...'") # Log snippet
            None
        elif llm_response.content.parts[0].function_call:
            print(f"[Callback] Inspected response: Contains function call '{llm_response.content.parts[0].function_call.name}'. No text modification.")
            return None # Don't modify tool calls in this example
        else:
            print("[Callback] Inspected response: No text content found.")
            return None
    elif llm_response.error_message:
        print(f"[Callback] Inspected response: Contains error '{llm_response.error_message}'. No modification.")
        # error_msg = llm_response.error_message
        # new_response = LlmResponse(
        #      content=types.Content(role="model", parts=[types.Part(text=error_msg)]),
        #      grounding_metadata=llm_response.grounding_metadata
        #      )
        # return new_response # Return the modified response and no proceed further
        return None   # proceed further
    else:
        print("[Callback] Inspected response: Empty LlmResponse.")
        return None # Nothing to modify
    

def setup_before_tool_call(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """Inspects/modifies tool args or skips the tool call."""
    agent_name = tool_context.agent_name
    tool_name = tool.name
    print(f"[Callback] Before tool call for tool '{tool_name}' in agent '{agent_name}'")
    print(f"[Callback] Original args: {args}")
    return None

def setup_after_tool_call(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict
) -> Optional[Dict]:
    """Inspects/modifies the tool result after execution."""
    # agent_name = tool_context.agent_name
    # tool_name = tool.name
    # print(f"[Callback] After tool call for tool '{tool_name}' in agent '{agent_name}'")
    # print(f"[Callback] Args used: {args}")
    # print(f"[Callback] Original tool_response: {tool_response}")

    # pending - streaming tools - getting error
    # print(f"[Callback] Original tool_response: {await tool_response}")

    tool_context.state['localdb_output'] =  tool_response
    # print(f"localdb_output text =  {tool_context.state.get('localdb_output')}")

    return None

#  pending - streaming tools - getting error
async def create_local_db_agent_async() -> LlmAgent:

    llm_model = LiteLlm(model=os.getenv("DB_AGENT_MODEL"))
    # llm_model = LiteLlm(model=f"ollama_chat/{os.getenv("OLLAMA_MODEL")}") if os.getenv("USE_OLLAMA") else os.getenv("DB_AGENT_MODEL")
    # llm_model = LiteLlm(model=f"openai/{os.getenv("OLLAMA_MODEL")}") if os.getenv("USE_OLLAMA") else os.getenv("DB_AGENT_MODEL")
  
    # db_tools = get_db_tools()
    db_tools = await get_db_tools_asyc()

    database_agent = LlmAgent(
        model=llm_model,
        name='db_agent',
        description='A helpful AI assistant. use the given tool to get relevant data ',
        instruction=return_instructions(),
        tools=db_tools,
        generate_content_config=types.GenerateContentConfig(temperature=0.01),
        output_key="localdb_output",
        # before_agent_callback=setup_before_agent_call,
        # after_agent_callback=setup_afer_agent_call,
        # before_model_callback=setup_before_model_call,
        # after_model_callback=setup_after_model_call,
        # before_tool_callback=setup_before_tool_call,
        after_tool_callback=setup_after_tool_call
    )

    logger.info('Local DB Agent Connected .....')
    return database_agent


def create_local_db_agent() -> LlmAgent:

    llm_model = LiteLlm(model=os.getenv("DB_AGENT_MODEL"))
    # llm_model = LiteLlm(model=f"ollama_chat/{os.getenv("OLLAMA_MODEL")}") if os.getenv("USE_OLLAMA") else os.getenv("DB_AGENT_MODEL")
    # llm_model = LiteLlm(model=f"openai/{os.getenv("OLLAMA_MODEL")}") if os.getenv("USE_OLLAMA") else os.getenv("DB_AGENT_MODEL")
  
    # db_tools = get_db_tools()
    db_tools = get_db_tools()

    database_agent = LlmAgent(
        model=llm_model,
        name='db_agent',
        description='A helpful AI assistant. use the given tool to get relevant data ',
        instruction=return_instructions(),
        tools=db_tools,
        generate_content_config=types.GenerateContentConfig(temperature=0.01),
        # output_key="localdb_output",
        # before_agent_callback=setup_before_agent_call,
        # after_agent_callback=setup_afer_agent_call,
        # before_model_callback=setup_before_model_call,
        # after_model_callback=setup_after_model_call,
        # before_tool_callback=setup_before_tool_call,
        after_tool_callback=setup_after_tool_call
    )

    logger.info('Local DB Agent Connected .....')
    return database_agent


# for adk web
# db_agent = create_local_db_agent()