import os, platform
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from .prompts import return_instructions
from google.adk.models import LlmResponse, LlmRequest
from typing import Optional
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import BaseTool, FunctionTool
from typing import List, Dict, Any
from google.adk.tools.tool_context import ToolContext

# for RAG based db schema 
# from .utils import get_dbschema_for_query, get_sample_sql_for_query

# for testing ....
# from .tools import execute_sql
# from google.genai import types
# from copy import copy
# from google.adk.tools.mcp_tool import conversion_utils
# from mcp.client.session import ClientSession
# from mcp.client.sse import sse_client


import logging
logger = logging.getLogger(__name__)

API_KEY = "ASDF"

usr_name:str = "sfg"


# Load environment variables from the project root .env file
# load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))

# import litellm
# litellm._turn_on_debug() 
# os.environ["LITELLM_DEBUG"] = "true" # Also set as environment variable for more verbose logging

async def get_mcp_tools() -> List:
    """
    Connects to an MCP server and loads its tools.

    Returns:
        A list of BaseTool instances loaded from the MCP server.
    """
    pass
    # conversion_utils.adk_to_mcp_tool_type

    # server_url = "http://localhost:9123/sse"
 
    # logger.info(f"Connecting to SSE server at {server_url}...")
    
    # the below doesn't convert mcp tool to ADK tool
    # # Create the connection via SSE transport
    # async with sse_client(url=server_url) as streams:
    #     # Create the client session with the streams
    #     async with ClientSession(*streams) as session:
    #         # Initialize the session
    #         await session.initialize()
            
    #         # List available tools
    #         response = await session.list_tools()
    #         logger.info("Available tools:", [tool.name for tool in response.tools])

    #         return [response.tools]

    # use below provided the mcp server SHOULD return ADK mcp tool type
    # remote_server_params = SseServerParams(url="http://localhost:9123/sse")
    # remote_toolset = MCPToolset(connection_params=remote_server_params)
    # # await exit_stack.enter_async_context(remote_toolset)
    # remote_tools = await remote_toolset.get_tools()
    # # all_tools.extend(remote_tools)
    # print(f"Loaded {len(remote_tools)} tools from remote SSE server.")

    # return remote_tools
  

def setup_after_model_call(callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """Inspects/modifies the LLM response after it's received."""
    agent_name = callback_context.agent_name
    logger.debug(f"[Callback] After model call for agent: {agent_name}")

    try:
        # --- Inspection ---
        original_text = ""
        if llm_response.content and llm_response.content.parts:
            # Assuming simple text response for this example
            if llm_response.content.parts[0].text:
                original_text = llm_response.content.parts[0].text
                logger.debug(f"[Callback] Inspected original response text: '{original_text[:300]}...'") # Log snippet
                
                sql_query = original_text.replace("```",'').replace('sql','').replace("\n",' ')
                callback_context.state["user:nl2sql_sql_query"] = sql_query

                #  below control not coming back here after the execute method ?
                # sql_query = original_text.replace("```",'').replace('sql','').replace("\n",'')
                # results = execute_sql(sql_query)
                # print("test msg")
                # logger.debug(results)
                # # Create a NEW LlmResponse with the modified content
                # # Deep copy parts to avoid modifying original if other callbacks exist
                # modified_parts = [copy.deepcopy(part) for part in llm_response.content.parts]
                # modified_parts[0].text = results # Update the text in the copied part

                # new_response = LlmResponse(
                # content= types.Content(role="model", parts=modified_parts),
                # # Copy other relevant fields if necessary, e.g., grounding_metadata
                # grounding_metadata=llm_response.grounding_metadata
                # )
                # return new_response # Return the modified response 

                logger.info(f"[Callback] Stored the query in state, returning unmodified response.")
                return None

            elif llm_response.content.parts[0].function_call:
                logger.debug(f"[Callback] Inspected response: Contains function call '{llm_response.content.parts[0].function_call.name}'. No text modification.")
                return None # Don't modify tool calls in this example
            else:
                logger.debug("[Callback] Inspected response: No text content found.")
                return None
        elif llm_response.error_message:
            logger.debug(f"[Callback] Inspected response: Contains error '{llm_response.error_message}'. No modification.")
            return None   # proceed further
        else:
            logger.debug("[Callback] Inspected response: Empty LlmResponse.")
            return None # Nothing to modify
        
    except Exception as e:
            logger.info(f"Error in setup after model call back : {e}")
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

    # tool_context.state['user:nl2sql_db_schema'] =  tool_response

    return None


async def create_nl2sql_db_agent_asyc() -> LlmAgent:
    """ nl2sql db manager agent"""

    # Get tools from MCP servers
    # mcp_tools = await get_mcp_tools()

    # llm_model = LiteLlm(model=os.getenv("DB_AGENT_MODEL"),mode="agentic")
    # llm_model = LiteLlm(model=f"ollama_chat/{os.getenv("OLLAMA_MODEL")}") if os.getenv("USE_OLLAMA") else os.getenv("FILESYSTEM_AGENT_MODEL")
    # llm_model = LiteLlm(model=f"openai/{os.getenv("OLLAMA_MODEL")}") if os.getenv("USE_OLLAMA") else os.getenv("FILESYSTEM_AGENT_MODEL")
    llm_model = os.getenv("DB_AGENT_MODEL")

    # Create the TTS Speaker agent
    agent_instance = LlmAgent(
        name='nl2sql_db_agent',
        description='A helpful AI assistant. use the given tool to get relevant data ',
        instruction=return_instructions(),
        model=llm_model,
        # output_key="nl2sql_db_output",
        # tools=[FunctionTool(get_dbschema_for_query)], for RAG based db schema ONLY
        after_tool_callback=setup_after_tool_call,
        after_model_callback=setup_after_model_call
    )

    logger.info('NL2SQL Database Agent Connected ...')    
    return agent_instance


# Expose agent for ADK
# fs_agent = create_filesystem_agent()

