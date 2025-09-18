
import os
from google.adk.code_executors import VertexAiCodeExecutor
from google.adk.agents import Agent
from .prompts import return_instructions
import vertexai
# from google.adk.code_executors import UnsafeLocalCodeExecutor
# from google.adk.tools.built_in_code_execution_tool import built_in_code_execution
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents.callback_context import CallbackContext

import logging
logger = logging.getLogger(__name__)

# load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))


def setup_afer_agent_call(callback_context: CallbackContext) -> None:
    agent_name = callback_context.agent_name
    logger.info(f"[Callback]: After agent call - {agent_name} is executed")
    return None


def create_analytics_agent():
    """ anaytics agent """
   
    llm_model = LiteLlm(model=os.getenv("ANALYTICS_AGENT_MODEL"))
    # llm_model = LiteLlm(model=f"openai/{os.getenv("OLLAMA_MODEL")}") if os.getenv("USE_OLLAMA") else os.getenv("DB_AGENT_MODEL")

    # Initialize Vertex AI API once per session
    vertexai.init(project="genai-431416", location="us-central1")

    # to execute given python code like calculation etc
    # root_agent = Agent(
    #     model=os.getenv("ANALYTICS_AGENT_MODEL"),
    #     name="data_science_agent",
    #     instruction=return_instructions_ds(),
    #     description="Executes Python code to perform various tasks.",
    #     tools=[built_in_code_execution]
    # )

    analytics_agent = Agent(
        model=llm_model,
        name="analytics_agent",
        description="AI analytics agent for grouping, filtering, sorting, ploting graph and any data science work",
        instruction=return_instructions(),
        code_executor=VertexAiCodeExecutor(
            optimize_data_file=True,
            stateful=True,
        ),
        output_key="analytics_output"
        # after_agent_callback=setup_afer_agent_call,
    )

    logger.info("Analystics Agent using Vertex AI platform Connected ...")
    return analytics_agent

# analyst_agent = create_analytics_agent()