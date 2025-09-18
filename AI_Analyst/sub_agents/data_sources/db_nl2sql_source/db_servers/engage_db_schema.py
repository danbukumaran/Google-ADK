
import json

def return_engage_db_schema() -> str:
    schema = f"""
     
    -- Table: CRM_Candidate_Intro_History
    -- Stores information about candidate introduction history.
    CREATE TABLE [dbo].[CRM_Candidate_Intro_History](
        [CIH_Code] [int] IDENTITY(1,1) NOT NULL PRIMARY KEY,
        [Profile_Id] [nvarchar](10) NULL,
        [Lead_Code] [nvarchar](10) NOT NULL,
        [Company_Name_English] [nvarchar](150) NULL,
        [Company_Name_Japanese] [nvarchar](150) NULL,
        [Lead_Contracts_ID] [nvarchar](10) NULL,
        [Client_Name_JPY] [nvarchar](50) NULL,
        [Client_Name_ENG] [nvarchar](50) NULL,
        [Candidate_Name] [nvarchar](50) NULL,
        [Age] [int] NULL,
        [Gender] [nvarchar](10) NULL,
        [Candidate_Status] [nvarchar](50) NULL,
        [Employment_Type] [nvarchar](50) NULL,
        [Domain_ID] [nvarchar](20) NULL,
        [Domain] [nvarchar](max) NULL,
        [SubDomain_ID] [nvarchar](20) NULL,
        [SubDomain] [nvarchar](max) NULL,
        [Software_Skills] [nvarchar](100) NULL,
        [Additional_Skills] [nvarchar](100) NULL,
        [Search_Tags] [nvarchar](200) NULL,
        [Visa_Type] [nvarchar](25) NULL,
        [Sourced_By] [nvarchar](250) NULL,
        [Updated_Date] [datetime] NULL,
        [Residing_Country] [nvarchar](50) NULL,
        [Nationality] [nvarchar](50) NULL,
        [Present_Salary] [nvarchar](50) NULL,
        [Expected_Salary] [nvarchar](50) NULL,
        [JLPT_Level] [nvarchar](50) NULL,
        [English_Level] [nvarchar](25) NULL,
        [Offer_Date] [datetime] NULL,
        [Offer_status] [nvarchar](3) NULL,
        [Interview_Date_Time] [datetime] NULL,
        [Schedule_Interview_Status] [nvarchar](3) NULL,
        [TA_Status] [nvarchar](50) NULL,
        [TA_Comments] [nvarchar](max) NULL,
        [Sales_Status] [nvarchar](50) NULL,
        [Sales_Comments] [nvarchar](max) NULL,
        [Scheduled_Status] [nvarchar](max) NULL,
        [Recommend_by] [nvarchar](50) NULL,
        [Recommender_Comments] [nvarchar](max) NULL,
        [Converted_Candidate_Status] [nvarchar](50) NULL,
        [Converted_Comments] [nvarchar](max) NULL,
        [User_Type] [nvarchar](20) NULL,
        [User_Code] [nvarchar](10) NULL,
        [REF_User_Code] [nvarchar](10) NULL,
        [Comp_Code] [nvarchar](7) NOT NULL,
        [Jd_Code] [nvarchar](10) NULL,
        [Client_Code] [nvarchar](50) NULL,
        [Current_JD_Position_Status] [nvarchar](50) NULL,
        [Emp_Code] [nvarchar](10) NULL,
        [Created_By] [nvarchar](250) NULL,
        [Created_Date] [datetime] NULL,
        [Modified_By] [nvarchar](20) NULL,
        [Modified_Date] [datetime] NULL
    )

    -- Table: TA_Employment_History
    -- Stores information about candidate once he/she becomes employee.
    CREATE TABLE [dbo].[TA_Employment_History](
        [Emp_History_Code] [nvarchar](10) NOT NULL PRIMARY KEY,
        [Employee_Code] [nvarchar](10) NULL,
        [Profile_Id] [nvarchar](10) NULL,
        [Lead_Code] [nvarchar](10) NOT NULL,
        [Lead_Contracts_ID] [nvarchar](10) NULL,
        [Salutation] [nvarchar](3) NULL,
        [First_Name] [nvarchar](50) NULL,
        [Middle_Name] [nvarchar](50) NULL,
        [Last_Name] [nvarchar](50) NULL,
        [Display_Name] [nvarchar](160) NULL,
        [Display_Name_Japanese] [nvarchar](160) NULL,
        [Company_Name_English] [nvarchar](150) NULL,
        [Company_Name_Japanese] [nvarchar](150) NULL,
        [Client_Name_JPY] [nvarchar](50) NULL,
        [Client_Name_ENG] [nvarchar](50) NULL,
        [Candidate_Name] [nvarchar](50) NULL,
        [Candidate_Status] [nvarchar](50) NULL,
        [Employment_Type] [nvarchar](50) NULL,
        [Domain_ID] [nvarchar](20) NULL,
        [Domain] [nvarchar](max) NULL,
        [SubDomain_ID] [nvarchar](20) NULL,
        [SubDomain] [nvarchar](max) NULL,
        [Sourced_By] [nvarchar](250) NULL,
        [Updated_Date] [datetime] NULL,
        [Offer_Date] [datetime] NULL,
        [Offer_status] [nvarchar](3) NULL,
        [Interview_Date_Time] [datetime] NULL,
        [TA_Status] [nvarchar](50) NULL,
        [TA_Comments] [nvarchar](max) NULL,
        [Sales_Status] [nvarchar](50) NULL,
        [Sales_Comments] [nvarchar](max) NULL,
        [Recommend_by] [nvarchar](50) NULL,
        [Recommender_Comments] [nvarchar](max) NULL,
        [Converted_Candidate_Status] [nvarchar](50) NULL,
        [Converted_Comments] [nvarchar](max) NULL,
        [User_Type] [nvarchar](20) NULL,
        [User_Code] [nvarchar](10) NULL,
        [REF_User_Code] [nvarchar](10) NULL,
        [Comp_Code] [nvarchar](7) NOT NULL PRIMARY KEY,
        [Jd_Code] [nvarchar](10) NULL,
        [Client_Code] [nvarchar](50) NULL,
        [Emp_Code] [nvarchar](10) NULL,
        [Created_By] [nvarchar](250) NULL,
        [Created_Date] [datetime] NULL,
        [Modified_By] [nvarchar](20) NULL,
        [Modified_Date] [datetime] NULL
    )

    -- Table: TA_Candidate_Info
    -- Stores information about candidate's basic information.
    CREATE TABLE [dbo].[TA_Candidate_Info](
        [Profile_Code] [nvarchar](10) NOT NULL PRIMARY KEY,
        [Registration_Date] [datetime] NULL,
        [Candidate_Img] [nvarchar](50) NULL,
        [First_Name_Kanji] [nvarchar](50) NULL,
        [Last_Name_Kanji] [nvarchar](50) NULL,
        [First_Name_Kana] [nvarchar](50) NULL,
        [Last_Name_Kana] [nvarchar](50) NULL,
        [Salutation] [nvarchar](3) NULL,
        [First_Name] [nvarchar](50) NULL,
        [Middle_Name] [nvarchar](50) NULL,
        [Last_Name] [nvarchar](50) NULL,
        [Japanese_First_Name] [nvarchar](50) NULL,
        [Japanese_Middle_Name] [nvarchar](50) NULL,
        [Japanese_Last_Name] [nvarchar](50) NULL,
        [Display_Name] [nvarchar](160) NULL,
        [Display_Name_Japanese] [nvarchar](160) NULL,
        [Province_ID] [int] NULL,
        [Province] [nvarchar](50) NULL,
        [State_ID] [int] NULL,
        [State] [nvarchar](50) NULL,
        [Country_ID] [int] NULL,
        [Country] [nvarchar](50) NULL,
        [Nationality_ID] [int] NULL,
        [Nationality] [nvarchar](50) NULL,
        [Gender] [nvarchar](10) NULL,
        [DOB] [datetime] NULL,
        [Age] [int] NULL,
        [Email_ID] [nvarchar](50) NULL,
        [Alternate_Email_ID] [nvarchar](50) NULL,
        [Mobile_No] [nvarchar](15) NULL,
        [Mobile_CountryCode] [nvarchar](5) NULL,
        [AL_Mobile_No] [nvarchar](15) NULL,
        [AL_Mobile_CountryCode] [nvarchar](5) NULL,
        [Martial_Status] [nvarchar](15) NULL,
        [Number_Of_Kids] [nvarchar](max) NULL,
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
        [Comments] [nvarchar](max) NULL,
        [DOJ] [nvarchar](10) NULL,
        [CU_Currency] [nvarchar](5) NULL,
        [CU_Period] [nvarchar](15) NULL,
        [CU_Salary] [nvarchar](50) NULL,
        [EX_Currency] [nvarchar](5) NULL,
        [EX_Period] [nvarchar](15) NULL,
        [EX_Salary] [nvarchar](50) NULL,
        [Reason_For_Change] [nvarchar](max) NULL,
        [Desired_Job_Location_Country_ID] [nvarchar](10) NULL,
        [Desired_Job_Location_ID] [nvarchar](max) NULL,
        [Desired_Job_Location] [nvarchar](max) NULL,
        [Visa_Type] [nvarchar](25) NULL,
        [Visa_Validity] [nvarchar](10) NULL,
        [Others_Visa_Type] [nvarchar](100) NULL,
        [Employment_History] [nvarchar](max) NULL,
        [Domain_ID] [nvarchar](20) NULL,
        [Domain] [nvarchar](max) NULL,
        [SubDomain_ID] [nvarchar](20) NULL,
        [SubDomain] [nvarchar](max) NULL,
        [Division] [nvarchar](max) NULL,
        [Software_Skills] [nvarchar](max) NULL,
        [Additional_Skills] [nvarchar](max) NULL,
        [Search_Tags] [nvarchar](200) NULL,
        [Certification] [nvarchar](max) NULL,
        [CV_Upload_English] [nvarchar](100) NULL,
        [CV_Upload_Others] [nvarchar](100) NULL,
        [File_Jap_Curriculum] [nvarchar](100) NULL,
        [Skill_Sheet_Upload] [nvarchar](100) NULL,
        [CV_Upload_Res_English_Others] [nvarchar](100) NULL,
        [CV_Upload_Japanese_Others] [nvarchar](100) NULL,
        [Upload_Japanese_Curriculum_Others] [nvarchar](100) NULL,
        [skill_sheet_Upload_Others] [nvarchar](100) NULL,
        [Reg_Status] [nvarchar](10) NULL,
        [Mode_Of_Registration] [nvarchar](max) NULL,
        [Status] [nvarchar](5) NULL,
        [Page_Status] [nvarchar](10) NULL,
        [Assessment_DML_Status] [nvarchar](10) NULL,
        [User_Type] [nvarchar](20) NULL,
        [User_Code] [nvarchar](10) NULL,
        [Favorites_User_Code] [nvarchar](max) NULL,
        [Favorites_User_Name] [nvarchar](max) NULL,
        [REF_User_Code] [nvarchar](10) NULL,
        [Comp_Code] [nvarchar](7) NOT NULL PRIMARY KEY,
        [Approved_Emp_Code] [nvarchar](10) NULL,
        [Rejected_Emp_Code] [nvarchar](10) NULL,
        [Rejected_Comments] [nvarchar](max) NULL,
        [Converted_Code] [nvarchar](10) NULL,
        [Converted_Status] [nchar](3) NULL,
        [Converted_Emp_Code] [nvarchar](10) NULL,
        [Created_By] [nvarchar](250) NULL,
        [Created_Date] [datetime] NULL,
        [Modified_By] [nvarchar](20) NULL,
        [Modified_Date] [datetime] NULL,
        [Approved_By] [nvarchar](20) NULL,
        [Approved_Date] [datetime] NULL,
        [Rejected_By] [nvarchar](20) NULL,
        [Rejected_Date] [datetime] NULL
    )

    """

    return schema


def return_engage_db_schema_1() -> str:

    schema = f"""
    -- Table: Products
    -- Description: Stores information about products
    -- Columns:
    --   product_id (INTEGER, PRIMARY KEY) - Unique ID for the product
    --   product_name (TEXT) - Name of the product
    --   category (TEXT) - Category of the product (e.g., 'Electronics', 'Clothing')
    --   price (REAL) - Price of the product

    -- Table: Customers
    -- Description: Stores information about customers
    -- Columns:
    --   customer_id (INTEGER, PRIMARY KEY) - Unique ID for the customer
    --   customer_name (TEXT) - Name of the customer
    --   city (TEXT) - City where the customer lives

    -- Table: Orders
    -- Description: Stores order details
    -- Columns:
    --   order_id (INTEGER, PRIMARY KEY) - Unique ID for the order
    --   customer_id (INTEGER, FOREIGN KEY to Customers.customer_id) - ID of the customer who placed the order
    --   order_date (DATE) - Date the order was placed
    --   total_amount (REAL) - Total amount of the order

    """

    return schema