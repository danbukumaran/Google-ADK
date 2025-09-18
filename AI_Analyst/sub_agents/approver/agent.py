import os
from typing import Any
from google.adk.tools.long_running_tool import LongRunningFunctionTool
from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.tool_context import ToolContext
from .prompt import return_instructions

import logging
logger = logging.getLogger(__name__)


# 1. Define the long running function
def ask_for_approval(tool_context: ToolContext):
    """Ask for approval to proceed further."""

    # send email & update DB the status is pending
    tool_context.state["user:approval_status"] = "pending"

    # IMPORTANT - Otherwise it's become empty after the agent run, 
    tool_context.state["user:user_query_pending"] = tool_context.state["user:user_query_pending"]

    status_desc = "Awaiting Manager's approval"
    logger.info(status_desc)
    # tool_context.actions.transfer_to_agent = "orchestrator_agent"

    return status_desc


def check_approval_status(tool_context: ToolContext):
    """check for approval status """
    req_status = "approved"
    status_desc = ""
    
    if(req_status == "approved"):
        status_desc = "Request is approved by the manager"
        tool_context.state["user:approval_status"] = "approved"
        tool_context.state["user:user_query_pending"] = ""   #it's persistent across invocation as using toolcontext

        tool_context.actions.transfer_to_agent = "orchestrator_agent"
    
    elif(req_status == "rejected"):
        status_desc = "Request is rejected by the manager"
        tool_context.state["user:approval_status"] = "rejected"
        tool_context.state["user:user_query_pending"] = "" #it's persistent across invocation as using toolcontext
    
    elif(req_status == "pending"):
        status_desc = "Request is still pending with the manager"
        tool_context.state["user:approval_status"] = "pending"

    logger.info(status_desc)
    return status_desc


def proceed_further(tool_context: ToolContext):
    """Agree to proceed further"""

    logger.info('Approved by the user\n\n')
    tool_context.state["user:approval_status"] = "approved"

    tool_context.actions.transfer_to_agent = "orchestrator_agent"

    return "approved"

def stop_processing(tool_context: ToolContext):
    """Stop further processing """

    logger.info('Rejected by the user\n\n')
    tool_context.state["user:approval_status"] = "rejected"
    return "rejected"


def create_approver_agent() -> LlmAgent:

    # 2. Wrap the function with LongRunningFunctionTool
    approval_tool = LongRunningFunctionTool(func=ask_for_approval)

    llm_model = LiteLlm(model=os.getenv("APPROVER_AGENT_MODEL"))

    agent_instance = LlmAgent(
        model=llm_model,
        name='approver_agent',
        instruction=return_instructions(),
        tools=[check_approval_status, approval_tool],
        output_key="approver_output"
    )

    logger.info('Approver Agent Connected ...')    
    return agent_instance



