
import json
import mssql_python

class MSSQlServer:
    """
    A read-only server for interacting with a MySQL database.

    This class provides methods to execute SELECT queries and retrieve schema information.
    """

    def __init__(self, host: str, user: str, password: str, database: str):
        """
        Initializes the SqlReadOnlyServer with database connection details.

        Args:
            host (str): The database host address.
            user (str): The database username.
            password (str): The database password.
            database (str): The name of the database.
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def get_sql_schema(self) -> json:
        """
        Retrieves the schema information for the database in a format suitable for LLMs.

        Returns:
            json: A JSON string representing the database schema.
        """
        # Connect to the database
        connection_string = f"Server={self.host};Database={self.database};UID={self.user};PWD={self.password};Encrypt=no;"
        connection = mssql_python.connect(connection_string)
       
        schema = {}
        tables = ['TA_Candidate_Info','TA_Employment_History', 'CRM_Candidate_Intro_History']

        try:
            cursor = connection.cursor()
            query = """
                SELECT 
                    TABLE_NAME, 
                    COLUMN_NAME, 
                    DATA_TYPE, 
                    IS_NULLABLE, 
                    COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME IN ({tables})
                ORDER BY TABLE_NAME, ORDINAL_POSITION;
                """

            cursor.execute(query)
            results = cursor.fetchall()

            for row in results:
                table_name = row[0]
                column_info = {
                    "name": row[1],
                    "data_type": row[2],
                    "is_nullable": row[3],
                    "default": row[4]
                }

                if table_name not in schema:
                    schema[table_name] = []

                schema[table_name].append(column_info)

        except Exception as e:
            raise ValueError(f"Error while getting schema details: {str(e)}")
        finally:
            connection.close()

        return json.dumps(schema, indent=2)


    def execute_query(self, query: str) -> str:
        """
        Executes a SQL query and returns the results as a list of dictionaries.

        Args:
            query (str): The SQL query to execute.

        Returns:
            str: A string contains list of dictionaries, where each dictionary represents a row.

        Raises:
            ValueError: If there is an error executing the query.
        """

         # Connect to the database
        connection_string = f"Server={self.host};Database={self.database};UID={self.user};PWD={self.password};Encrypt=no;"
        try:
            # json_result = ""

            connection = mssql_python.connect(connection_string)

            cursor = connection.cursor()

            cursor.execute(query)
            # results = cursor.fetchall()

            columns = [desc[0] for desc in cursor.description]
            result = []
            rows = cursor.fetchall()
            for row in rows:
                row = dict(zip(columns, row))
                result.append(row)

            json_result = json.dumps(result,indent=2,default=str)
            # print("Data received")

            return json_result
        
        except Exception as e:
            raise ValueError(f"Error executing query: {str(e)}")
            # return f"Error while executing query {e}"
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

