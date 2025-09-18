import asyncio
import os, platform
from google.adk.agents import Agent, LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.adk.models.lite_llm import LiteLlm
from .prompts import return_instructions
from google.adk.models import LlmResponse, LlmRequest
from typing import Optional
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import BaseTool
from typing import List, Dict, Any
from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams, StdioServerParameters
from google.adk.tools.tool_context import ToolContext

import logging
logger = logging.getLogger(__name__)

# Load environment variables from the project root .env file
# load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))

# import litellm
# litellm._turn_on_debug() 
# os.environ["LITELLM_DEBUG"] = "true" # Also set as environment variable for more verbose logging

async def get_mcp_tools() -> List[BaseTool]:
    """
    Connects to an MCP server and loads its tools.

    Returns:
        A list of BaseTool instances loaded from the MCP server.
    """
    all_tools = []

    # --- Option 1: Connecting to a local MCP server via StdioServerParameters ---
    # This is typically used when you have a local MCP server process
    # that communicates over standard input/output.
    try:
        # local_server_params = StdioServerParameters(
        #     command="npx.cmd",
        #     args=["-y", "@modelcontextprotocol/server-filesystem",
        #        "C:\\AnbuKumaran\\Projects\\AI\\Testing\\Input",
        #        "C:\\AnbuKumaran\\Projects\\AI\\Testing\\Output"
        #     ],
        #     env={"NPXPATH": "C:\\Program Files\\nodejs\\"},
        # )
        # local_toolset = MCPToolset(connection_params=local_server_params)
        connection_param=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command='npx.cmd',
                         args=["-y", "@modelcontextprotocol/server-filesystem",
                            "C:\\AnbuKumaran\\Projects\\AI\\Testing\\Input",
                            "C:\\AnbuKumaran\\Projects\\AI\\Testing\\Output"
                            ],
                            env={"NPXPATH": "C:\\Program Files\\nodejs\\"}
                    ),
                    timeout=20
                )
        local_toolset = MCPToolset(connection_params=connection_param)
        if local_toolset:
            # await exit_stack.enter_async_context(remote_toolset)
            local_tools = await local_toolset.get_tools()
            all_tools.extend(local_tools)

        logger.info(f"Loaded {len(local_tools)} tools from local Stdio server.")
       
    except Exception as e:
       logger.error(f"Failed to load tools from local Stdio server: {e}")
       raise

    # --- Option 2: Connecting to a remote MCP server via SseServerParams ---
    # This is used when your MCP server exposes its tools over an HTTP endpoint
    # using Server-Sent Events (SSE).
    # Replace 'http://localhost:5000/api/toolset' with the actual URL of your MCP server.
    # try:
    #     remote_server_params = SseServerParams(url="http://localhost:5000/api/toolset")
    #     remote_toolset = MCPToolset(connection_params=remote_server_params, exit_stack=exit_stack)
    #     await exit_stack.enter_async_context(remote_toolset)
    #     remote_tools = await remote_toolset.load_tools()
    #     all_tools.extend(remote_tools)
    #     logger.info(f"Loaded {len(remote_tools)} tools from remote SSE server.")
    # except Exception as e:
    #     logger.warning(f"Failed to load tools from remote SSE server: {e}")

    return all_tools


def setup_after_model_call(callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """Inspects/modifies the LLM response after it's received."""
    agent_name = callback_context.agent_name
    logger.debug(f"[Callback] After model call for agent: {agent_name}")

    # --- Inspection ---
    original_text = ""
    if llm_response.content and llm_response.content.parts:
        # Assuming simple text response for this example
        if llm_response.content.parts[0].text:
            original_text = llm_response.content.parts[0].text
            logger.debug(f"[Callback] Inspected original response text: '{original_text[:100]}...'") # Log snippet
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
    

def setup_after_tool_call(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict
) -> Optional[Dict]:
    """Inspects/modifies the tool result after execution."""
    # agent_name = tool_context.agent_name
    # tool_name = tool.name
    # print(f"[Callback] After tool call for tool '{tool_name}' in agent '{agent_name}'")
    # print(f"[Callback] Args used: {args}")
    # print(f"[Callback] Original tool_response: {tool_response}")

    if tool_response:
        extracted_text = ""
        # Check if tool_response has a 'content' attribute and it's iterable
        if hasattr(tool_response, 'content') and isinstance(tool_response.content, list):
            for part in tool_response.content:
                if hasattr(part, 'text') and part.text:
                    extracted_text += part.text + "\n" # Concatenate text parts
            # extracted_text = extracted_text.strip() # Remove trailing newline

        # user can ask files in multiple folders, so this after tool call will 
        # be called for each folder so appending below the output
        tool_context.state['filesystem_output'] = tool_context.state.get('filesystem_output', '') + extracted_text
        # print(f"extracted text =  {tool_context.state.get('filesystem_output')}")

    return None


async def create_filesystem_agent_asyc() -> LlmAgent:
    """ File system manager agent"""

    # Get tools from MCP servers
    mcp_tools = await get_mcp_tools()

    llm_model = LiteLlm(model=os.getenv("FILESYSTEM_AGENT_MODEL"))
    # llm_model = LiteLlm(model=f"ollama_chat/{os.getenv("OLLAMA_MODEL")}") if os.getenv("USE_OLLAMA") else os.getenv("FILESYSTEM_AGENT_MODEL")
    # llm_model = LiteLlm(model=f"openai/{os.getenv("OLLAMA_MODEL")}") if os.getenv("USE_OLLAMA") else os.getenv("FILESYSTEM_AGENT_MODEL")
  

    # Create the TTS Speaker agent
    agent_instance = LlmAgent(
        name="file_system_agent",
        description="Am a file system manager agent",
        instruction=return_instructions(),
        model=llm_model,
        tools=mcp_tools,
        # output_key="filesystem_output",
        # output_key="raw_fs_result"
        # tools = [ MCPToolset(
        # connection_params=StdioServerParameters(
        #     command='npx',
        #     args=["-y",
        #         "@modelcontextprotocol/server-filesystem",
        #         "D:\\Anbu\\Projects\\AI_Agents\\Testing\\Output",
        #         "D:\\Anbu\\Projects\\AI_Agents\\Testing\\Input"]
        #         )
        #     )],
        after_tool_callback=setup_after_tool_call
    )

    logger.info('File System Agent Connected ...')    
    return agent_instance


# Expose agent for ADK
# fs_agent = create_filesystem_agent()

