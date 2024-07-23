import streamlit as st
import sqlite3
import pandas as pd
import sql_db
from prompts.prompts import SYSTEM_MESSAGE
from azure_openai import get_completion_from_messages
import json
import matplotlib.pyplot as plt


def query_database(query, conn):
    """ Run SQL query and return results in a dataframe """
    return pd.read_sql_query(query, conn)
def plot_data(df, plot_type):
    if df.empty:
        raise ValueError("The DataFrame is empty. Please provide a valid DataFrame.")

    if len(df.columns) < 2:
        raise ValueError("The DataFrame must contain at least two columns for plotting.")

    if plot_type == "bar":
        plt.figure(figsize=(10, 6))
        plt.bar(df.iloc[:, 0], df.iloc[:, 1])
        plt.xlabel(df.columns[0])
        plt.ylabel(df.columns[1])
        plt.title("Bar Plot")
        plt.xticks(rotation=45)
        plt.tight_layout()

    elif plot_type == "line":
        plt.figure(figsize=(10, 6))
        plt.plot(df.iloc[:, 0], df.iloc[:, 1], marker='o')
        plt.xlabel(df.columns[0])
        plt.ylabel(df.columns[1])
        plt.title("Line Plot")
        plt.xticks(rotation=45)
        plt.tight_layout()

    elif plot_type == "scatter":
        plt.figure(figsize=(10, 6))
        plt.scatter(df.iloc[:, 0], df.iloc[:, 1])
        plt.xlabel(df.columns[0])
        plt.ylabel(df.columns[1])
        plt.title("Scatter Plot")
        plt.tight_layout()

    elif plot_type == "pie":
            plt.figure(figsize=(10, 6))
            plt.pie(df.iloc[:, 1], labels=df.iloc[:, 0], autopct='%1.1f%%')
            plt.title("Pie Chart")
            plt.tight_layout()

    elif plot_type == "box":
        plt.figure(figsize=(10, 6))
        plt.boxplot(df.iloc[:, 1])
        plt.xlabel(df.columns[0])
        plt.ylabel(df.columns[1])
        plt.title("Box Plot")
        plt.tight_layout()


    else:
        raise ValueError("Invalid plot type. Please choose from 'bar', 'line', 'scatter', 'pie', or 'box'.")

    # Save the plot
    plot_filename = f"{plot_type}_plot.png"
    plt.savefig(plot_filename)
    return plot_filename

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
        st.write("Results:")
        st.dataframe(sql_results)


        # Save the DataFrame to a CSV file
        sql_results.to_csv('query_results.csv', index=False)
        # st.write("Query results saved to 'query_results.csv'.")

        # Choose the plot type
        plot_type = st.selectbox("Select Graph Type", ["bar", "line", "scatter", "pie"]) #, "box"])
        
        if st.button("Generate Plot"):
            # Plot the data
            plot_filename = plot_data(sql_results, plot_type)
            st.image(plot_filename)
    except Exception as e:
        st.write(f"An error occurred: {e}")
