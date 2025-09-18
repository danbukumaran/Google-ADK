import os
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from .prompts import return_instructions


import logging
logger = logging.getLogger(__name__)


def create_summarizer_agent():

    # for local LLM
    # os.environ["OPENAI_API_BASE"] = "http://localhost:11434/"
    # os.environ["OPENAI_API_KEY"] = "unused" # Can be anything, Ollama doesn't use it
    # ollama_url = "http://localhost:11434/v1"

    # llm_model = LiteLlm(model=f"openai/{os.getenv("OLLAMA_MODEL")}", stream=True, api_base=ollama_url, temperature=0.01)
    # llm_model = LiteLlm(model=f"ollama_chat/{os.getenv("OLLAMA_MODEL")}" stream=True, api_base=ollama_url, temperature=0.01)
    llm_model = LiteLlm(model=os.getenv("SUMMARIZER_AGENT_MODEL"))

    agent_instance = Agent(
        name="summarizer_agent",
        description="Summarizes the given data to a readable format.",
        model=llm_model,
        instruction=return_instructions()
    )

    logger.info('Summarizer Agent Connected ...')    
    return agent_instance

# Expose agent for ADK
# summarizer_agent = create_summarizer_agent() 
