import streamlit as st
import sqlite3
import pandas as pd
import sql_db
from prompts.prompts import SYSTEM_MESSAGE
from azure_openai import get_completion_from_messages
import json

def query_database(query, conn):
    """ Run SQL query and return results in a dataframe """
    return pd.read_sql_query(query, conn)

# Create or connect to SQLite database
conn = sql_db.create_connection()

# Schema Representation for finances table
schemas = sql_db.get_schema_representation()

st.title("SQL Query Generator with GPT-4")
st.write("Enter your message to generate SQL and view results.")

# Input field for the user to type a message
user_message = st.text_input("Enter your message:")

if user_message:
    # Format the system message with the schema
    formatted_system_message = SYSTEM_MESSAGE.format(schema=schemas['data-poc'])

    # Use GPT-4 to generate the SQL query
    response = get_completion_from_messages(formatted_system_message, user_message)
    print(f"response{response}")

        # Find the start and end indexes of the JSON part
    start_index = response.find('{')
    end_index = response.rfind('}') + 1

    # Extract the JSON part from the string
    json_string = response[start_index:end_index]
   
    # Parse the extracted JSON string into a Python dictionary
    json_response = json.loads(json_string)
    query = json_response['query']
    query_like = query.replace('=', 'LIKE')

    # Display the generated SQL query
    st.write("Generated SQL Query:")
    st.code(query_like, language="sql")

    try:
        # Run the SQL query and display the results
        sql_results = query_database(query_like, conn)
        st.write("Query Results:")
        st.dataframe(sql_results)

    except Exception as e:
        st.write(f"An error occurred: {e}")
