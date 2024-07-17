# main_app.py

import streamlit as st
import sqlite3
import pandas as pd
import sql_db
from prompts.prompts import SYSTEM_MESSAGE
from azure_openai import get_completion_from_messages
import json
import re


def append_group_by(query):
    # Regular expression to find column numbers in SELECT statement
    pattern = r'SELECT\s+(.*?)\s+FROM'

    select_match = re.search(pattern, query, re.IGNORECASE | re.DOTALL)
    if not select_match:
        raise ValueError("Invalid query format: SELECT statement not found.")

    select_clause = select_match.group(1)
    if(select_clause == '*'):
        return query
    # Splitting the select clause by comma and trimming spaces
    columns = [col.strip() for col in select_clause.split(',')]
    # Find indices of columns with aggregate functions
    aggregate_indices = [i + 1 for i, col in enumerate(columns) if re.search(r'\b(?:COUNT|SUM|AVG|MIN|MAX)\b', col, re.IGNORECASE)]

    # Constructing the group by clause
    group_by_indices = ','.join(str(idx) for idx in range(1, len(columns) + 1) if idx not in aggregate_indices)
    group_by_clause = ' GROUP BY ' + group_by_indices if group_by_indices else ''
    # print(f"Query ->{query} ->{query[:select_match.end()]} abc-> {group_by_clause}")
    # Append group by clause after the original query
    # modified_query = query[:select_match.end()] + group_by_clause + query[select_match.end():]
    modified_query = query + group_by_clause
    return modified_query


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
    formatted_system_message = SYSTEM_MESSAGE.format(schema=schemas['PurchaseOrders'])

    # Use GPT-4 to generate the SQL query
    response = get_completion_from_messages(formatted_system_message, user_message)
        # Find the start and end indexes of the JSON part
    start_index = response.find('{')
    end_index = response.rfind('}') + 1

    # Extract the JSON part from the string
    json_string = response[start_index:end_index]
   
    # Parse the extracted JSON string into a Python dictionary
    json_response = json.loads(json_string)
    query = json_response['query']


    # query1 = json_response.get('query')
    if '=' in query:
        query = query.replace('=', 'LIKE')
    # modified_query = append_group_by(str(query))
    modified_query = str(query)
    # Display the generated SQL query
    st.write("Generated SQL Query:")
    st.code(modified_query, language="sql")

    try:
        # Run the SQL query and display the results
        sql_results = query_database(modified_query, conn)
        # print(f"sql_results->{sql_results}")
        # exit()
        st.write("Query Results:")
        st.dataframe(sql_results)

    except Exception as e:
        st.write(f"An error occurred: {e}")
