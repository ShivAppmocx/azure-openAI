# main_app.py

import streamlit as st
import sqlite3
import pandas as pd
import sql_db
from prompts.reference_prompt import SYSTEM_MESSAGE
from azure_openai import get_completion_from_messages
import json

def query_database(query):
    """ Run SQL query and return results in a dataframe """
    return pd.read_sql_query(query, conn)

# Create or connect to SQLite database
conn = sql_db.create_connection()

# Schema Representation for finances table
schemas = sql_db.get_schema_representation()
print(f'schemas',schemas)

# Format the system message with the schema
# formatted_system_message = SYSTEM_MESSAGE.format(schema=schemas['data-poc'])
formatted_system_message = SYSTEM_MESSAGE.format(schema=schemas)
# print(f"formatted_system_message",SYSTEM_MESSAGE)
# Generate the SQL query from the user message
user_message = "Show me all expenses greater than 1000"
# user_message = "give me all details for top 10 material by quantity"
# user_message = "give me all detail for purchase order no 4500000000 "
# user_message = "retrieve total quatity for purchase order 4500000007 from all tables"
#&nbsp;Use GPT-4 to generate the SQL query
response = get_completion_from_messages(formatted_system_message, user_message)
print(f"response",response)
exit()
json_response = json.loads(response)
query = json_response['query']
print(query)

# Run the SQL query
sql_results = query_database(query)
print(sql_results)
