#sql_db.py

import pyodbc
import pandas as pd

# Replace these with your actual Azure SQL Database credentials
server = 'sqldemoserver-poc.database.windows.net'
database = 'pocdata'
username = 'sqldemoserver-poc'
password = 'Appmocx@ai'

def create_connection():
    """Create or connect to an Azure SQL Database"""
    conn = None
    try:
        conn = pyodbc.connect(
            f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}')
        print("Connection established successfully.")
    except pyodbc.Error as e:
        print(f"Error while connecting to SQL Server: {e}")
    return conn

def query_database(query, conn):
    """Run SQL query and return results in a dataframe"""
    try:
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        print(f"Error while querying database: {e}")
        return None


def get_schema_representation():
    """Get the database schema in a JSON-like format"""
    conn = create_connection()
    
           
    if conn is not None:
        try:
            cursor = conn.cursor()
            
            # Query to get all table names
            cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
            # cursor.execute("SELECT SCHEMA_NAME(o.schema_id) + '.' + o.Name AS 'TableName', c.Name as 'ColumName' \
            #     FROM     sys.columns c \
            #              JOIN sys.objects o ON o.object_id = c.object_id \
            #     WHERE    o.type = 'U' \
            #     ORDER BY o.Name")
            tables = cursor.fetchall()
            # print(f"tables",tables)
            # exit()

            db_schema = []
    
            for table in tables:
                table_name = table[0]
                
                # Query to get column details for each table
                cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'")
                columns = cursor.fetchall()
                
                for column in columns:
                    column_name = column[0]
                    db_schema.append((table_name, column_name))
            
            conn.close()
            # print(f"db_schema->",db_schema)
            # exit()
            return db_schema


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



def get_schema_representation1():
    """Get the database schema in a JSON-like format"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            
            # Query to get all table names
            cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
            # cursor.execute("SELECT SCHEMA_NAME(o.schema_id) + '.' + o.Name AS 'TableName', c.Name as 'ColumName' \
            #     FROM     sys.columns c \
            #              JOIN sys.objects o ON o.object_id = c.object_id \
            #     WHERE    o.type = 'U' \
            #     ORDER BY o.Name")
            tables = cursor.fetchall()
            # print(f"tables",tables)
            # exit()
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

def find_common_columns(schema):
    """Find common columns across all tables"""
    column_tables = {}
    for table, columns in schema.items():
        for column in columns:
            if column in column_tables:
                column_tables[column].add(table)
            else:
                column_tables[column] = {table}

    common_columns = {column: tables for column, tables in column_tables.items() if len(tables) > 1}
    return common_columns

def generate_join_query(table1, table2, common_column):
    """Generate SQL join query for two tables on a common column"""
    query = (f"SELECT * "
             f"FROM [{table1}] AS t1 "
             f"JOIN [{table2}] AS t2 "
             f"ON t1.[{common_column}] = t2.[{common_column}]")
    return query

def query_tables_with_join(schema, common_columns):
    """Query data from tables that share common columns"""
    result = {}
    conn = create_connection()
    if conn:
        for column, tables in common_columns.items():
            if len(tables) >= 2:
                table_list = list(tables)
                table1 = table_list[0]
                table2 = table_list[1]
                
                query = generate_join_query(table1, table2, column)
                result_df = query_database(query, conn)
                if result_df is not None:
                    result[f"{table1} JOIN {table2} ON {column}"] = result_df
                else:
                    print(f"Failed to query tables: {table1} and {table2} for column: {column}")
        conn.close()
    else:
        print("Failed to establish database connection.")
    return result

if __name__ == "__main__":
    # Getting the schema representation
    schema = get_schema_representation()
    if schema is not None:
        print("Database schema:")
        print(schema)

        # # Find common columns
        # common_columns = find_common_columns(schema)
        # print("Common columns across tables:")
        # print(common_columns)

        # # Query tables with common columns
        # results = query_tables_with_join(schema, common_columns)
        # for key, df in results.items():
        #     print(f"\nData from {key}:")
            #print(df)
    else:
        print("Failed to retrieve schema representation.")