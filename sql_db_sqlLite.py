# sql_db.py

import sqlite3
from sqlite3 import Error
import pandas as pd

DATABASE_NAME = "PurchaseOrders.db"

def create_connection():
    """ Create or connect to an SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
    except Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    """ Create a table with the specified SQL command """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def insert_data(conn, table_name, data_dict):
    """ Insert a new data into a table """
    columns = ', '.join(data_dict.keys())
    placeholders = ', '.join('?' * len(data_dict))
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    cur = conn.cursor()
    cur.execute(sql, list(data_dict.values()))
    conn.commit()
    return cur.lastrowid

def query_database(query):
    """ Run SQL query and return results in a dataframe """
    conn = create_connection()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def setup_purchase_orders_table():
    conn = create_connection()
    sql_create_purchase_orders_table = """
    CREATE TABLE IF NOT EXISTS PurchaseOrders (
        PO_Number INTEGER,
        Date DATE,
        Vendor_Name TEXT,
        Company_Code INTEGER,
        Plant INTEGER,
        Purchase_Org TEXT,
        Purchase_Group TEXT,
        Item_Number INTEGER,
        Material_Description TEXT,
        Quantity REAL,
        Unit_Price REAL,
        Total_Price REAL
    );
    """
    create_table(conn, sql_create_purchase_orders_table)

    # Load the data from the CSV file
    csv_file_path = "D:/Appmocx/Fabric POC setup/new_sap_purchase_orders(sample).csv"
    df = pd.read_csv(csv_file_path)

    # Insert data into the table
    for _, row in df.iterrows():
        data = {
            "PO_Number": row['PO_Number'],
            "Date": row['Date'],
            "Vendor_Name": row['Vendor_Name'],
            "Company_Code": row['Company_Code'],
            "Plant": row['Plant'],
            "Purchase_Org": row['Purchase_Org'],
            "Purchase_Group": row['Purchase_Group'],
            "Item_Number": row['Item_Number'],
            "Material_Description": row['Material_Description'],
            "Quantity": row['Quantity'],
            "Unit_Price": row['Unit_Price'],
            "Total_Price": row['Total_Price']
        }
        insert_data(conn, "PurchaseOrders", data)

    conn.close()

def get_schema_representation():
    """ Get the database schema in a JSON-like format """
    conn = create_connection()
    cursor = conn.cursor()
    
    # Query to get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    db_schema = {}
    
    for table in tables:
        table_name = table[0]
        
        # Query to get column details for each table
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        column_details = {}
        for column in columns:
            column_name = column[1]
            column_type = column[2]
            column_details[column_name] = column_type
        
        db_schema[table_name] = column_details
    
    conn.close()
    return db_schema

if __name__ == "__main__":

    # Setting up the purchase orders table and inserting data from CSV
    setup_purchase_orders_table()

    # Querying the database
    print(query_database("SELECT * FROM PurchaseOrders LIMIT 50"))
    
    # Getting the schema representation
    print(get_schema_representation())