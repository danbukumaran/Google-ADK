import os
from dotenv import load_dotenv
load_dotenv()

from .db_servers.mssqlserver import MSSQlServer
# from .db_servers.mysqlserver import MySqlServer

import logging
logger = logging.getLogger(__name__)

# Load environment variables from the project root .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))

def get_db_schema():
    """
        Retrieves the schema information for the database in a format suitable for LLMs.

        Returns:
            json: A JSON string representing the database schema.
    """
    try:
        db = MSSQlServer(host=os.getenv("DB_HOST"), 
                    user=os.getenv("DB_USER"), 
                    password=os.getenv("DB_PASSWORD"), 
                    database=os.getenv("DB_DATABASE"))

        results = db.get_sql_schema()

        logger.info(f'schema details : {results} ')    
        return results
    except Exception as e:
        logger.error(f"Error retrieving schema details : {e}")
        raise 


def execute_sql(query : str):
    """
        Executes a SQL query and returns the results as a list of dictionaries.

        Args:
            query (str): The SQL query to execute.

        Returns:
            list[dict]: A list of dictionaries, where each dictionary represents a row.

        Raises:
            ValueError: If there is an error executing the query.
    """
    try:
        if not query.strip().upper().startswith("SELECT"):
            raise ValueError("Only SELECT queries are allowed for read_query")
        
        db = MSSQlServer(host=os.getenv("DB_HOST"), 
                    user=os.getenv("DB_USER"), 
                    password=os.getenv("DB_PASSWORD"), 
                    database=os.getenv("DB_DATABASE"))
        
        logger.info(f'generated query : {query} ')  
        results = db.execute_query(query)
        return results
    
    except Exception as e:
        logger.error(f"Error while executing the tool : {e}")
        raise 

