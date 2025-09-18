from google.adk.agents import Agent, LlmAgent, BaseAgent
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

from google.adk.tools import load_artifacts
from typing import AsyncGenerator, Dict,Any
from .prompts import return_instructions
from .utils import *
from typing_extensions import override
from google.adk.tools.agent_tool import AgentTool, BaseTool
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events.event import Event
from typing import Optional, Union
from datetime import datetime
from google.adk.events import Event, EventActions
import time
import asyncio
import sqlglot
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest


import logging
logger = logging.getLogger(__name__)


class OrchestratorAgent(Agent):
    db_agent_attr: LlmAgent
    summarizer_agent_attr: LlmAgent
    fs_agent_attr: LlmAgent
    analyst_agent_attr: Optional[LlmAgent] = None
    nl2sql_db_agent_attr: Optional[LlmAgent] = None
    mssql_db_attr:object = None
    # approver_agent_attr: LlmAgent = None

    def __init__(self, model_name: str,
            fs_agent_attr:LlmAgent,
            db_agent_attr:LlmAgent ,
            summarizer_agent_attr:LlmAgent ,
            analyst_agent_attr:LlmAgent,
            nl2sql_dg_agent_attr:LlmAgent,
            mssql_db_attr:object,
            # approver_agent_attr:LlmAgent,
            **kwargs
        ):

        kwargs['fs_agent_attr'] = fs_agent_attr
        kwargs['db_agent_attr'] = db_agent_attr
        kwargs['summarizer_agent_attr'] = summarizer_agent_attr
        kwargs['analyst_agent_attr'] = analyst_agent_attr
        kwargs['nl2sql_db_agent_attr'] = nl2sql_dg_agent_attr
        kwargs['mssql_db_attr'] = mssql_db_attr
        # kwargs['approver_agent_attr'] = approver_agent_attr

        super().__init__(
            name="orchestrator_agent",
            description="Orchestrates products details by delegating to specialized LLM agents for data fetching and formatting.",
            model=model_name,
            instruction=return_instructions(),
            sub_agents=[summarizer_agent_attr],
            # sub_agents=[summarizer_agent_attr,approver_agent_attr],
            tools=[   
                AgentTool(fs_agent_attr),
                AgentTool(db_agent_attr),
                AgentTool(analyst_agent_attr),
                AgentTool(nl2sql_dg_agent_attr),
                load_artifacts],
            **kwargs
        )

    
    def _setup_before_model_call(self,
        callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
        agent_name = callback_context.agent_name
        print(f"[Callback] Befor model call : {agent_name}")
        return None

    def _setup_before_tool_call(self, tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
    ) -> Optional[Dict]:
        """Inspects/modifies tool args or skips the tool call."""
        agent_name = tool_context.agent_name
        tool_name = tool.name
        print(f"[Callback] Before tool call for tool '{tool_name}' in agent '{agent_name}'")
        print(f"[Callback] Original args: {args}")

        # tool_context.actions.transfer_to_agent = "approver_agent"
        return None


    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        
        logger.info(f"{datetime.now()} :Orchestrator Agent: Implementation started ...")

        user_query = ctx.user_content.parts[0].text
        ctx.session.state["user_query"] = user_query
        
        user_query_lower = ctx.session.state["user_query"].lower()
        logger.info(f"user query lower : {user_query_lower}")

      
        # 1. filesystem agent WITHOUT APPROVAL
        if ("file" in user_query_lower or "folder" in user_query_lower or
           "director" in user_query_lower or "content" in user_query_lower):
                logger.info(f"Orchestrator Agent: User asked about {user_query}, delegating to file system agent...")
                
                async for event in self.fs_agent_attr.run_async(ctx):
                    yield event # Stream events from sub-agent up for visibility


        # 2. if user is asking other than file system then to nl2sql agent
        else:
            logger.info(f"Orchestrator Agent: User asked about {user_query}, delegating to nl2sql db agent...")

            async for event in self.nl2sql_db_agent_attr.run_async(ctx):
                # logger.debug(f"Event - {self.name} - {event}")
                yield event # Stream events from sub-agent up for visibility

            if("user:nl2sql_sql_query" in ctx.session.state and ctx.session.state["user:nl2sql_sql_query"]):
               
                sql_query = ctx.session.state["user:nl2sql_sql_query"]
                logger.info(f"Generated query is : {sql_query}")

                if not sql_query.strip().upper().startswith("SELECT"):
                    logger.error(f"NL2SQL Agent NOT generated a SELECT statment : {sql_query}. Aborting workflow.")
                    return # Stop processing if initial story failed
                else:
                    try:
                        # validate the sql statement for syntax error
                        try:
                            results = sqlglot.parse_one(sql=sql_query,dialect="tsql")
                        except Exception as e:
                            logger.error(f"NL2SQL Agent generated INVALID SQL statment {sql_query}. Aborting workflow.")
                            ctx.end_invocation = True # Signal framework to stop processing
                            yield Event(author=self.name, invocation_id=ctx.invocation_id, content="Stopping due to critical error.")
                            return # Stop this agent's execution

                        loop = asyncio.get_running_loop()

                        # Await the result of the synchronous function executed in the thread pool
                        # `None` uses the default thread pool executor
                        results = await loop.run_in_executor(None, self.mssql_db_attr.execute_query,sql_query)

                        # Below won't work
                        # ctx.session.state["nl2sql_db_output"] = results

                        # --- Define State Changes ONLY way to update session state ---
                        state_changes = {
                            "localdb_output": results   # Update session state, changed user:nl2sql_db_output
                        }
                        system_event = update_state(state_changes,ctx.invocation_id,"agent")
                        await ctx.session_service.append_event(ctx.session, system_event)
                        logger.info("'append_event' called with explicit state delta - nl2sql_output.")

                    except Exception as e:
                        logger.info(f"An error occurred during database operation: {e}")

                        ctx.end_invocation = True # Signal framework to stop processing
                        yield Event(author=self.name, invocation_id=ctx.invocation_id, content="Stopping due to critical error.")
                        raise
                        # return # raise Stop this agent's execution
                        


            # if nl2sql unable to generate SQL
            else:
                logger.error(f"NL2SQL Agent failed to generate SQL statement. Trying MCP Tool ...")
               
                logger.info(f"Orchestrator Agent: User asked about {user_query}, delegating to local db agent...")
                async for event in self.db_agent_attr.run_async(ctx):
                    # logger.debug(f"Event - {self.name} - {event}")
                    yield event # Stream events from sub-agent up for visibility
                
                # print(f"ctx session data : {ctx.session.model_dump_json()}")



        # 3. Conditional delegation to analytics agent
        if ("draw" in user_query_lower or "plot" in user_query_lower or
            "graph" in user_query_lower or "chart" in user_query_lower ):

            logger.info(f"Orchestrator Agent: User asked about {user_query}, delegating to analystics agent...")

            if ("localdb_output" not in ctx.session.state or not ctx.session.state["localdb_output"]):
                logger.error(f"Local db agent failed to generate data. Aborting workflow.")
                
                ctx.end_invocation = True # Signal framework to stop processing
                yield Event(author=self.name, invocation_id=ctx.invocation_id, content="Stopping due to non-availability of data")
                return 
            else:
                async for event in self.analyst_agent_attr.run_async(ctx):
                    # print(f"Event - {self.name} - {event}")
                    yield event # Stream events from sub-agent up for visibility


        # 4. Always delegate to FinalFormatterAgent
        logger.info("Orchestrator Agent: Delegating to Final Formatter Agent for final response generation...")
  
        if (("localdb_output" not in ctx.session.state or not ctx.session.state["localdb_output"])
            and ("filesystem_output" not in ctx.session.state or not ctx.session.state["filesystem_output"])
            and ("analytics_output" not in ctx.session.state or not ctx.session.state["analytics_output"])
            and ("approver_output" not in ctx.session.state or not ctx.session.state["approver_output"])):

            logger.error(f"Local db / file system / analystics/ approver agent failed to generate data. Aborting workflow.")
           
            ctx.end_invocation = True # Signal framework to stop processing
            yield Event(author=self.name, invocation_id=ctx.invocation_id, content="Stopping due to non-availability of data")
            return # Stop processing if initial story failed
        
        else:
            ai_output = ""
            
            if ("filesystem_output" in ctx.session.state and ctx.session.state["filesystem_output"]):
                ai_output = f"FileSystem output is \n {ctx.session.state["filesystem_output"]} \n\n"
        
            if ("localdb_output" in ctx.session.state and ctx.session.state["localdb_output"]):
                ai_output = f"{ai_output} Database output is : \n {ctx.session.state["localdb_output"]} \n\n"
                    
            if ("analytics_output" in ctx.session.state and ctx.session.state["analytics_output"]):
                ai_output = f"{ai_output} Analytics output is \n {ctx.session.state["analytics_output"]} \n\n"

            if ("approver_output" in ctx.session.state and ctx.session.state["approver_output"]):
                ai_output = f"{ai_output} Approver output is \n {ctx.session.state["approver_output"]} \n\n"
                   
            # --- Define State Changes ONLY way to update session state ---
            state_changes = {
                "ai_agent_output": ai_output   # Update session state
            }
            system_event = update_state(state_changes,ctx.invocation_id,"agent")
            await ctx.session_service.append_event(ctx.session, system_event)
            logger.info("'append_event' called with explicit state delta - ai_agent_output")


            async for event in self.summarizer_agent_attr.run_async(ctx):
                # print(f"Event - {self.name} - {event}")
                yield event # Stream events from sub-agent up for logging


        logger.info(f"{datetime.now()} :Orchestrator Agent: implementation completed...")

