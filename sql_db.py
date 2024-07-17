import pyodbc
import pandas as pd

# Replace these with your actual Azure SQL Database credentials
server = 'sqldemoserver-poc.database.windows.net'
database = 'pocdata'
username = 'sqldemoserver-poc'
password = 'Appmocx@ai'

def create_connection():
    """ Create or connect to an Azure SQL Database """
    conn = None
    try:
        conn = pyodbc.connect(
            f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}')
        print("Connection established successfully.")
    except pyodbc.Error as e:
        print(f"Error while connecting to SQL Server: {e}")
    return conn

def query_database(query):
    """ Run SQL query and return results in a dataframe """
    conn = create_connection()
    if conn is not None:
        try:
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error while querying database: {e}")
            return None
    else:
        print("Failed to establish connection to the database.")
        return None

def get_schema_representation():
    """ Get the database schema in a JSON-like format """
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            
            # Query to get all table names
            cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
            tables = cursor.fetchall()
            
            db_schema = {}
            
            for table in tables:
                table_name = table[0]
                
                # Query to get column details for each table
                cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'")
                columns = cursor.fetchall()
                
                column_details = {}
                for column in columns:
                    column_name = column[0]
                    column_type = column[1]
                    column_details[column_name] = column_type
                
                db_schema[table_name] = column_details
            
            conn.close()
            return db_schema
        except Exception as e:
            print(f"Error while fetching schema: {e}")
            return None
    else:
        print("Failed to establish connection to the database.")
        return None

if __name__ == "__main__":
    # Example query to fetch data from your table
    result_df = query_database("SELECT TOP 50 * FROM PurchaseOrders")
    if result_df is not None:
        print(result_df)

    # Getting the schema representation
    schema = get_schema_representation()
    if schema is not None:
        print(schema)
