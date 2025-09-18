
import json
import pymysql

class MySqlServer:
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

    def _get_mysql_schema_for_llm(self) -> json:
        """
        Retrieves the schema information for the database in a format suitable for LLMs.

        Returns:
            json: A JSON string representing the database schema.
        """
        # Connect to the database
        connection = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

        schema = {}

        try:
            with connection.cursor() as cursor:
                query = """
                SELECT 
                    TABLE_NAME, 
                    COLUMN_NAME, 
                    DATA_TYPE, 
                    COLUMN_TYPE,
                    IS_NULLABLE, 
                    COLUMN_DEFAULT, 
                    COLUMN_KEY, 
                    EXTRA
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s
                ORDER BY TABLE_NAME, ORDINAL_POSITION;
                """

                cursor.execute(query, (self.database,))
                results = cursor.fetchall()

                for row in results:
                    table_name = row[0]
                    column_info = {
                        "name": row[1],
                        "data_type": row[2],
                        "column_type": row[3],
                        "is_nullable": row[4],
                        "default": row[5],
                        "key": row[6],
                        "extra": row[7]
                    }

                    if table_name not in schema:
                        schema[table_name] = []

                    schema[table_name].append(column_info)

        finally:
            connection.close()

        return json.dumps(schema, indent=2)


    def _execute_query(self, query: str) -> list[dict]:
        """
        Executes a SQL query and returns the results as a list of dictionaries.

        Args:
            query (str): The SQL query to execute.

        Returns:
            list[dict]: A list of dictionaries, where each dictionary represents a row.

        Raises:
            ValueError: If there is an error executing the query.
        """
        connection = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                return results
        except Exception as e:
            raise ValueError(f"Error executing query: {str(e)}")
        finally:
            connection.close()
