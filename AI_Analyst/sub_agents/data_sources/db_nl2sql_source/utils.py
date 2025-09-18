import chromadb
from chromadb.utils import embedding_functions
import os

import logging
logger = logging.getLogger(__name__)

DB_DIR = os.path.join(os.path.dirname(__file__), "..", "..","..", "data/rag_data/")
os.makedirs(DB_DIR, exist_ok=True)

SCHEMA_COLLECTION_NAME = "schema_collection"
SQL_COLLECTION_NAME = "sql_collection"
TOP_K = 2

# create client
chroma_client = chromadb.PersistentClient(
    path=DB_DIR,
)

# get or load collections   
try:
    schema_collection = chroma_client.get_or_create_collection(
        name=SCHEMA_COLLECTION_NAME,
        embedding_function=embedding_functions.GoogleGenerativeAiEmbeddingFunction(
            api_key=os.getenv("GOOGLE_API_KEY")
        ),
        metadata={"hnsw:space": "cosine"}
    )
    logger.info(f"Chroma_DB collection '{SCHEMA_COLLECTION_NAME}' loaded or created.")

    sql_collection = chroma_client.get_or_create_collection(
        name=SQL_COLLECTION_NAME,
        embedding_function=embedding_functions.GoogleGenerativeAiEmbeddingFunction(
             api_key=os.getenv("GOOGLE_API_KEY")
        ),
        metadata={"hnsw:space": "cosine"}
    )
    logger.info(f"Chroma_DB collection '{SQL_COLLECTION_NAME}' loaded or created.")
except Exception as e:
    logger.error(f"Error accessing ChromaDB collection(s): {e}")
    exit(1)



# for testing
def _add_schema_documents():
    # Add documents (embeddings auto-generated)
    documents = [
        "show me recruitment teams performance",
        "get me candidates who are all converted in this month",
        "get me count of candidates by state "
    ]
    ids = ["doc1", "doc2", "doc3"]
    metadatas = [{"table1": """
        -- Table: TA_Candidate_Info
        -- Stores information about candidate's basic information.
        CREATE TABLE [dbo].[TA_Candidate_Info](
            [Profile_Code] [nvarchar](10) NOT NULL PRIMARY KEY,
            [Comp_Code] [nvarchar](7) NOT NULL PRIMARY KEY,
            [Registration_Date] [datetime] NULL,
            [Salutation] [nvarchar](3) NULL,
            [First_Name] [nvarchar](50) NULL,
            [Middle_Name] [nvarchar](50) NULL,
            [Last_Name] [nvarchar](50) NULL,
            [Display_Name] [nvarchar](160) NULL,
            [Province] [nvarchar](50) NULL,
            [State] [nvarchar](50) NULL,
            [Country] [nvarchar](50) NULL,
            [Nationality] [nvarchar](50) NULL,
            [Gender] [nvarchar](10) NULL,
            [Age] [int] NULL,
            [Martial_Status] [nvarchar](15) NULL,
            [Sourced_By] [nvarchar](250) NULL,
            [Linkedin_Url] [nvarchar](50) NULL,
            [Facebook_Link] [nvarchar](50) NULL,
            [Qualification] [nvarchar](max) NULL,
            [Experience_In_Years] [nvarchar](50) NULL,
            [Employment_Type] [nvarchar](50) NULL,
            [Notice_Period] [nvarchar](20) NULL,
            [Candidate_Status] [nvarchar](50) NULL,
            [English_Level] [nvarchar](25) NULL,
            [Japanese_Level] [nvarchar](25) NULL,
            [Actual_Level] [nvarchar](50) NULL,
            [Other_Language_Known] [nvarchar](max) NULL,
            [Candidate_Profile_Status] [nvarchar](25) NULL,
            [DOJ] [nvarchar](10) NULL,
            [CU_Currency] [nvarchar](5) NULL,
            [CU_Period] [nvarchar](15) NULL,
            [CU_Salary] [nvarchar](50) NULL,
            [EX_Currency] [nvarchar](5) NULL,
            [EX_Period] [nvarchar](15) NULL,
            [EX_Salary] [nvarchar](50) NULL,
            [Reason_For_Change] [nvarchar](max) NULL,
            [Desired_Job_Location] [nvarchar](max) NULL,
            [Visa_Type] [nvarchar](25) NULL,
            [Visa_Validity] [nvarchar](10) NULL,
            [Others_Visa_Type] [nvarchar](100) NULL,
            [Employment_History] [nvarchar](max) NULL,
            [Domain] [nvarchar](max) NULL,
            [SubDomain] [nvarchar](max) NULL,
            [Division] [nvarchar](max) NULL,
            [Software_Skills] [nvarchar](max) NULL,
            [Additional_Skills] [nvarchar](max) NULL,
        )""", 

        "table2":"""
        -- Table: TA_Employment_History
        -- Stores information about candidate once he/she becomes employee.
        CREATE TABLE [dbo].[TA_Employment_History](
            [Emp_History_Code] [nvarchar](10) NOT NULL PRIMARY KEY,
            [Comp_Code] [nvarchar](7) NOT NULL PRIMARY KEY,
            [Employee_Code] [nvarchar](10) NULL,
            [Profile_Id] [nvarchar](10) NULL,
            [Lead_Code] [nvarchar](10) NOT NULL,
            [Lead_Contracts_ID] [nvarchar](10) NULL,
            [Salutation] [nvarchar](3) NULL,
            [First_Name] [nvarchar](50) NULL,
            [Middle_Name] [nvarchar](50) NULL,
            [Last_Name] [nvarchar](50) NULL,
            [Display_Name] [nvarchar](160) NULL,
            [Company_Name_English] [nvarchar](150) NULL,
            [Client_Name_ENG] [nvarchar](50) NULL,
            [Candidate_Name] [nvarchar](50) NULL,
            [Candidate_Status] [nvarchar](50) NULL,
            [Employment_Type] [nvarchar](50) NULL,
            [Domain] [nvarchar](max) NULL,
            [SubDomain] [nvarchar](max) NULL,
            [Sourced_By] [nvarchar](250) NULL,
            [Offer_Date] [datetime] NULL,
            [Offer_status] [nvarchar](3) NULL,
            [Interview_Date_Time] [datetime] NULL,
            [TA_Status] [nvarchar](50) NULL,
            [Sales_Status] [nvarchar](50) NULL,
            [Recommend_by] [nvarchar](50) NULL,
            [Converted_Candidate_Status] [nvarchar](50) NULL,
            [User_Type] [nvarchar](20) NULL,
            [User_Code] [nvarchar](10) NULL,
            [REF_User_Code] [nvarchar](10) NULL,
            [Jd_Code] [nvarchar](10) NULL,
            [Client_Code] [nvarchar](50) NULL,
            [Emp_Code] [nvarchar](10) NULL
        )
        """
        },
    {"table1": "client_info", "table2":"sales_info"},
    {"table1" :"sales_info"}] 

    schema_collection.add(
        documents=documents,
        ids=ids,
        metadatas=metadatas,
    )

    print('added schema documents')

# for testing
def _add_sql_documents():
    # Add documents (embeddings auto-generated)
    documents = [
        "show me recruitment teams performance",
        "get me candidates who are all converted in this month",
        "get me count of candidates by state "
    ]
    ids = ["doc1", "doc2", "doc3"]
    metadatas = [{"sql1": "select count(0) from cand_info", 
                "sql2":"select avg(0) from cand_info inner join sales on a.id = b.id"},
                {"sql1": "select sum(salary) from emp_info inner join cand_into on a.id = b.id"},
                {"sql1": "select state, count(0) from sales group by state"}] 

    sql_collection.add(
        documents=documents,
        ids=ids,
        metadatas=metadatas
    )
    print('added documents')


def get_dbschema_for_query(user_query: str) -> str:
    """Return top_k similar document texts for the query."""
    result = schema_collection.query(
        query_texts=[user_query],
        n_results=TOP_K,
        include=['metadatas','distances']
    )
    # metadatas = result["metadatas"][0]
    # similarity_score = result["distances"][0]

    metas = result['metadatas'][0]
    all_unique_values = set(val for d in metas for val in d.values())

    res_str = "\n".join(map(str, all_unique_values)) 
    return res_str


def get_sample_sql_for_query(user_query: str) -> str:

    """query metadata only"""
    # result = collection.get(
    #     where={"author": "anbu"},
    #     include=['documents', 'metadatas','distances']
    # )
    # If you want to limit top_k results manually
    # top_k = 5
    # limited_result = {
    #     key: value[:top_k]
    #     for key, value in result.items()
    # }

    result = sql_collection.query(
        query_texts=[user_query],
        n_results=TOP_K,
        include=['metadatas','distances']
    )
    
    metas = result['metadatas'][0]
    all_unique_values = set(val for d in metas for val in d.values())
   
    res_str = "\n".join(map(str, all_unique_values)) 
    return res_str

# for testing
_add_schema_documents()


# if __name__ == "__main__":
# #    _add_schema_documents()
# #    _add_sql_documents()
#     qry = "help to get statewise candidate details"
#     result = get_sample_sql_for_query(qry)
    
#     print(result)


