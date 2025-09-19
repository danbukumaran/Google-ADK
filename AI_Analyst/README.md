
# Data Analyst Agent

It is a data analysis tool that generates graphical reports based on natural language requests, designed for management users.


## Features

- Host Agent
- Sub Agents
    - NL2SQL Agent
    - MCP toolbox for DB Agent
    - File System Agent
    - Graph generation Agent using Vertex code extender
    - Approver Agent using HITL (human in the loop)
    - Summarizer Agent using Local LLM



## Tech Stack

**API Interface:** FastAPI

**Agent Framework:** Google ADK v1.4

**MCP Tools:** MCP toolbox for database, @modelcontextprotocol/server-filesystem

**Local LLM:** Gemma3 on OLAMA

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

#### APP setting
APP_ENV = "production" # e.g., "development", "production"

#### APP authentication
API_KEY = ""

API_KEY_NAME = ""


#### Choose Model Backend: 0 -> ML Dev, 1 -> Vertex
GOOGLE_GENAI_USE_VERTEXAI=0

#### Vertex backend config
GOOGLE_CLOUD_PROJECT=""
GOOGLE_CLOUD_LOCATION=""

GOOGLE_APPLICATION_CREDENTIALS = ""

GOOGLE_API_KEY=""
ANTHROPIC_API_KEY =""

#### Set up Code Interpreter, if it exists. Else leave empty
CODE_INTERPRETER_EXTENSION_NAME='' 

#### Models used in Agents
ROOT_AGENT_MODEL=''  # anthropic/claude-3-7-sonnet-20250219

DB_AGENT_MODEL=''  # gemini-2.5-flash-preview-04-17

ANALYTICS_AGENT_MODEL=''

FILESYSTEM_AGENT_MODEL = ''

SUMMARIZER_AGENT_MODEL = ''

APPROVER_AGENT_MODEL=''

#### for Local LLM
USE_OLLAMA = False
OLLAMA_MODEL = "phi4-mini:latest"

#### for MCP toolbox for database tool
DATABASE_TOOL_URL = ""

DB_HOST = ""

DB_USER = ""

DB_PASSWORD = ""

DB_DATABASE = ""







## Deployment

To start MCP toolbox server


```bash
  toolbox.exe --tools-file "tools.yaml" --log-level "DEBUG"
```

To run the App 

```bash
uvicorn AI_Analyst.main:app --port=8123
```


## Documentation


These agents have been built and tested using Google models on Vertex AI. You can test these samples with other models as well. Please refer to ADK Tutorials to use other models 
