from langchain import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.chat_models import ChatOpenAI  # Use the recommended version of the OpenAI chat model
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Get the OpenAI API key and the PostgreSQL database URL
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
PG_DB_URL = os.environ.get('PG_DB_URL')

# Set the API key in the environment
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Create the database connection
db = SQLDatabase.from_uri(PG_DB_URL)

# Create the LLM model using the recommended version
llm = ChatOpenAI(temperature=0)

# Create the database chain using the correct method
db_chain = SQLDatabaseChain.from_llm(llm=llm, db=db, verbose=False)

def generate_query(natural_query):
    """
    Generates an SQL query from a natural language query and adjusts the syntax if necessary.
    """
    try:
        # Retrieve the table information from the database
        table_info = db.get_table_info()
        
        # Create the necessary parameters to generate the SQL query
        inputs = {
            'input': natural_query,
            'table_info': table_info,
            'top_k': 1  # Limit the options to keep the most relevant ones
        }
        
        # Use the model to translate the natural language query to SQL
        sql_query = db_chain.llm_chain.predict(**inputs)
        
        # Adjust the query to ensure compatibility with SQL Server
        sql_query = adjust_syntax(sql_query)
        return sql_query
    except Exception as e:
        print("Error generating the SQL query:", e)
        return None

def adjust_syntax(sql_query):
    """
    Adjusts the SQL query syntax to ensure compatibility with SQL Server.
    """
    # Replace double quotes with brackets if necessary
    sql_query = sql_query.replace("\"", "[")
    sql_query = sql_query.replace("[[", "[")  # Ensure no duplicate brackets
    sql_query = sql_query.replace("]", "]")  # Maintain correct closing brackets

    # Adjust other potential syntax issues if necessary
    if "SELECT TOP 1" in sql_query:
        sql_query = sql_query.replace("SELECT TOP 1", "SELECT TOP 1")

    return sql_query

def execute_query(sql_query):
    """
    Executes the SQL query in the database.
    """
    try:
        # Execute the SQL query using the database
        result = db.run(sql_query)
        return result
    except Exception as e:
        print("Error executing the SQL query:", e)
        return None

def display_result(result):
    """
    Displays only the result of the SQL query.
    """
    if result is not None and len(result) > 0:
        # Assuming the result is a list of rows (tuples)
        print(result[0][0])

# Example usage
natural_query = "tell me the type of holiday that is most common in the holiday table"
sql_query = generate_query(natural_query)

if sql_query:
    result = execute_query(sql_query)
    display_result(result)
