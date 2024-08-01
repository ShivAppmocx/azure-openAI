
import streamlit as st
import sqlite3
import pandas as pd
import sql_db
from prompts.reference_prompt import SYSTEM_MESSAGE
from azure_openai import get_completion_from_messages
import json

from st_aggrid import AgGrid, GridOptionsBuilder



def query_database(query, conn):
    """ Run SQL query and return results in a dataframe """
    return pd.read_sql_query(query, conn)

# Create or connect to SQLite database
conn = sql_db.create_connection()

# Schema Representation for finances table
schemas = sql_db.get_schema_representation()

st.title("Data Analytics Assistant")
# st.write("Enter your message to generate SQL and view results.")

# Input field for the user to type a message
user_message = st.text_input("How may i help you!")

if user_message:
    # Format the system message with the schema
    # formatted_system_message = SYSTEM_MESSAGE.format(schema=schemas['data-poc'])
    formatted_system_message = SYSTEM_MESSAGE.format(schema=schemas)

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
        # st.write("Results:")
        # st.dataframe(sql_results)

        df = pd.DataFrame(sql_results)
        #  # Configure AgGrid options
        gb = GridOptionsBuilder.from_dataframe(df)
        is_fit_column = True
        if "PURCHASE ORDER NUMBER" in sql_results.columns:
            is_fit_column = False
            gb.configure_column("PURCHASE ORDER NUMBER", pinned="left")  # Freeze this column
        
        cell_style = {'textAlign': 'center'}
        # header_style = {'textAlign': 'left'}
        # gb.configure_default_column(resizable=True, wrapText=True, autoHeight=True,  cellStyle=cell_style, headerStyle=header_style)
        gb.configure_default_column(resizable=True, wrapText=True, autoHeight=True,  cellStyle=cell_style)

        # Add custom CSS for header alignment
       
        gb.configure_grid_options(domLayout='autoHeight')

        gridOptions = gb.build()

        # Display the DataFrame with AgGrid
        st.write("Results:")
        AgGrid(df, gridOptions=gridOptions, fit_columns_on_grid_load=is_fit_column, enable_enterprise_modules=True)


    except Exception as e:
        st.write(f"An error occurred: {e}")
