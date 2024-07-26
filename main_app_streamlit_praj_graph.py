import streamlit as st
import sqlite3
import pandas as pd
import sql_db
from prompts.prompts import SYSTEM_MESSAGE
from azure_openai import get_completion_from_messages
import json
import matplotlib.pyplot as plt
import openai
import subprocess
import re

# Set your OpenAI API key and Azure endpoint
openai.api_type = "azure"
openai.api_base = "https://fabric-poc.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = "5a3e842aa1b14dc7b092553422349c8d"



def query_database(query, conn):
    """Run SQL query and return results in a dataframe"""
    return pd.read_sql_query(query, conn)

# Function to get completion from Azure OpenAI
def get_completion_from_messages(system_message, user_message, model="gpt-4", temperature=0.7, max_tokens=1000) -> str:
    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': user_message}
    ]
    response = openai.ChatCompletion.create(
        engine=model,  # This should be the name of the deployed model in Azure OpenAI
        messages=messages,
        temperature=temperature, 
        max_tokens=max_tokens
    )
    return response['choices'][0]['message']['content']

# Function to get Python code for visualizations from GPT-4
def generate_python_code(csv_file):
    system_message = "You are a helpful assistant."
    user_message = f"""
    I have a CSV file with data, and I need a Python script that generates visualizations from this data.
    The CSV file is named '{csv_file}'. Please provide the Python code to read this CSV file and generate visualizations based on the column data present in the csv file generate visuals of all possible types.
    The visualizations should include appropriate plots try to stick with the plots which are most commonly used. Ensure that the code analyzes the columns to determine the types of plots.
    The visualizations should be saved as images with Static names for each type of plot.
    Strictly you are supposed to save the images with Static names like 'plot1', 'plot2', etc. Do not use any other names.
    And Strictly you are not supposed to generate anything apart from the code, NO COMMENTS, SENTENCES OR STUFF IS ALLOWED TO GENERATE, not even allowed to print the script type as python.
    """
    return get_completion_from_messages(system_message, user_message, model="gpt-4")

# Function to save Python code to a file
def save_python_code(code, file_name):
    with open(file_name, 'w') as file:
        file.write(code)

# Function to execute the Python code
def execute_python_code(file_name):
    subprocess.run(['python', file_name])

# Function to generate and save visualizations
def generate_visualizations(csv_file):
    # Generate Python code
    python_code = generate_python_code(csv_file)
    cleaned_code = re.sub(r"```[ \t]*python[ \t]*|```", "", python_code)
    
    # Save Python code to a file
    script_file = 'visualization_script.py'
    save_python_code(cleaned_code, script_file)
    
    # Execute the Python script
    execute_python_code(script_file)

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
    query_like = query

    # Display the generated SQL query
    st.write("Generated SQL Query:")
    st.code(query_like, language="sql")

    try:
        # Run the SQL query and display the results
        sql_results = query_database(query_like, conn)
        st.write("Query Results:")
        st.dataframe(sql_results)

        # Save the DataFrame to a CSV file
        sql_results.to_csv('query_results.csv', index=False)
        st.write("Query results saved to 'query_results.csv'.")

        # Generate and display visualizations using GPT-4
        generate_visualizations('query_results.csv')
        st.write("Visualizations generated and saved.")

        # Display the generated plots
        for i in range(1, 10):  # Assuming we generate 3 plots
            plot_filename = f'plot{i}.png'
            st.image(plot_filename)

    except Exception as e:
        st.write(f"An error occurred: {e}")