import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import datetime

DATABASE_NAME = "PurchaseOrdersDB"

def create_connection():
    """ Create or connect to a MySQL database """
    conn = None
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='shivam@123',
            database=DATABASE_NAME
        )
    except Error as e:
        print(e)
    return conn

def create_database():
    """ Create a database if it does not exist """
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='shivam@123'
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")
    conn.close()

def create_table(conn, create_table_sql):
    """ Create a table with the specified SQL command """
    try:
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
    except Error as e:
        print(e)

def insert_data(conn, table_name, data_dict):
    """ Insert new data into a table """
    columns = ', '.join(data_dict.keys())
    placeholders = ', '.join(['%s'] * len(data_dict))
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    
    # Convert date strings to datetime objects
    for key, value in data_dict.items():
        if isinstance(value, str) and key.endswith("_DATE"):
            try:
                data_dict[key] = datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                data_dict[key] = None  # Handle invalid date format
    
    # Insert data into the database
    cursor = conn.cursor()
    try:
        cursor.execute(sql, list(data_dict.values()))
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error inserting data: {e}")
        return None

def setup_purchase_orders_table():
    conn = create_connection()
    sql_create_purchase_orders_table = """
    CREATE TABLE IF NOT EXISTS PurchaseOrders (
        CLIENT INT,
        PURCHASE_ORDER_NUMBER BIGINT,
        COMPANY_CODE INT,
        PURCHASING_ORGANIZATION VARCHAR(255),
        PURCHASING_GROUP VARCHAR(255),
        PURCHASING_DOCUMENT_TYPE VARCHAR(255),
        PURCHASE_ORDER_DATE DATE,
        CONDITION_RECORD_NUMBER BIGINT,
        VENDOR_ACCOUNT_NUMBER BIGINT,
        TERMS_OF_PAYMENT_KEY VARCHAR(255),
        CURRENCY VARCHAR(10),
        EXCHANGE_RATE DOUBLE,
        GOODS_RECEIPT_DATE DATE,
        RELEASE_GROUP VARCHAR(255),
        RELEASE_CODE VARCHAR(255),
        RELEASE_STATUS VARCHAR(255),
        RELEASE_INDICATOR VARCHAR(255),
        CHANGE_DATE DATE,
        PURCHASE_ORDER_LINE_ITEM VARCHAR(255),
        PURCHASE_REQUISITION_ITEM_NUMBER INT,
        DELETION_INDICATOR VARCHAR(10),
        STATUS VARCHAR(255),
        SERVICE_BASED_INVOICE_VERIFICATION_INDICATOR VARCHAR(10),
        GOODS_RECEIPT_INDICATOR VARCHAR(10),
        MATERIAL_NUMBER BIGINT,
        VENDOR_MATERIAL_NUMBER VARCHAR(255),
        PLANT VARCHAR(255),
        STORAGE_LOCATION VARCHAR(255),
        MATERIAL_GROUP VARCHAR(255),
        PURCHASING_INFO_RECORD_NUMBER BIGINT,
        GL_ACCOUNT_NUMBER BIGINT,
        ACCOUNT_ASSIGNMENT_CATEGORY VARCHAR(255),
        ITEM_NUMBER_RESERVATION INT,
        VALUATION_TYPE_COMPANY_CODE VARCHAR(255),
        VALUATION_TYPE VARCHAR(255),
        GR_REVERSAL_INDICATOR VARCHAR(10),
        LINE_NUMBER_ACCOUNT_ASSIGNMENT INT,
        OVERDELIVERY_TOLERANCE DOUBLE,
        RETURNS_ITEM VARCHAR(10),
        SPECIAL_STOCK_INDICATOR VARCHAR(10),
        CONTRACT_NUMBER BIGINT,
        AGREEMENT_ITEM_NUMBER INT,
        ITEM_CATEGORY VARCHAR(255),
        TAX_JURISDICTION_CODE VARCHAR(255),
        DELIVERY_COSTS DOUBLE,
        ORDER_UNIT VARCHAR(255),
        QUANTITY DOUBLE,
        NET_PRICE DOUBLE,
        NET_ORDER_VALUE DOUBLE,
        TAX_CODE VARCHAR(10),
        PRIMARY KEY (PURCHASE_ORDER_NUMBER)
    );
    """
    create_table(conn, sql_create_purchase_orders_table)

    # Load the data from the Excel file
    excel_file_path = "Purchase Document.xlsx"
    df = pd.read_excel(excel_file_path, engine='openpyxl')

    # Insert data into the table
    for _, row in df.iterrows():
        data = {
            "CLIENT": row['CLIENT'],
            "PURCHASE_ORDER_NUMBER": row['PURCHASE ORDER NUMBER'],
            "COMPANY_CODE": row['COMPANY CODE'],
            "PURCHASING_ORGANIZATION": row['PURCHASING ORGANIZATION'],
            "PURCHASING_GROUP": row['PURCHASING GROUP'],
            "PURCHASING_DOCUMENT_TYPE": row['PURCHASING DOCUMENT TYPE'],
            "PURCHASE_ORDER_DATE": row['PURCHASE ORDER DATE'],
            "CONDITION_RECORD_NUMBER": row['CONDITION RECORD NUMBER'],
            "VENDOR_ACCOUNT_NUMBER": row['VENDOR ACCOUNT NUMBER'],
            "TERMS_OF_PAYMENT_KEY": row['TERMS OF PAYMENT KEY'],
            "CURRENCY": row['CURRENCY'],
            "EXCHANGE_RATE": row['EXCHANGE RATE'],
            "GOODS_RECEIPT_DATE": row['GOODS RECEIPT DATE'],
            "RELEASE_GROUP": row['RELEASE GROUP'],
            "RELEASE_CODE": row['RELEASE CODE'],
            "RELEASE_STATUS": row['RELEASE STATUS'],
            "RELEASE_INDICATOR": row['RELEASE INDICATOR'],
            "CHANGE_DATE": row['CHANGE DATE'],
            "PURCHASE_ORDER_LINE_ITEM": row['PURCHASE ORDER LINE ITEM'],
            "PURCHASE_REQUISITION_ITEM_NUMBER": row['PURCHASE REQUISITION ITEM NUMBER'],
            "DELETION_INDICATOR": row['DELETION INDICATOR'],
            "STATUS": row['STATUS'],
            "SERVICE_BASED_INVOICE_VERIFICATION_INDICATOR": row['SERVICE BASED INVOICE VERIFICATION INDICATOR'],
            "GOODS_RECEIPT_INDICATOR": row['GOODS RECEIPT INDICATOR'],
            "MATERIAL_NUMBER": row['MATERIAL NUMBER'],
            "VENDOR_MATERIAL_NUMBER": row['VENDOR MATERIAL NUMBER'],
            "PLANT": row['PLANT'],
            "STORAGE_LOCATION": row['STORAGE LOCATION'],
            "MATERIAL_GROUP": row['MATERIAL GROUP'],
            "PURCHASING_INFO_RECORD_NUMBER": row['PURCHASING INFO RECORD NUMBER'],
            "GL_ACCOUNT_NUMBER": row['GL ACCOUNT NUMBER'],
            "ACCOUNT_ASSIGNMENT_CATEGORY": row['ACCOUNT ASSIGNMENT CATEGORY'],
            "ITEM_NUMBER_RESERVATION": row['ITEM NUMBER RESERVATION'],
            "VALUATION_TYPE_COMPANY_CODE": row['VALUATION TYPE COMPANY CODE'],
            "VALUATION_TYPE": row['VALUATION TYPE'],
            "GR_REVERSAL_INDICATOR": row['GR REVERSAL INDICATOR'],
            "LINE_NUMBER_ACCOUNT_ASSIGNMENT": row['LINE NUMBER ACCOUNT ASSIGNMENT'],
            "OVERDELIVERY_TOLERANCE": row['OVERDELIVERY TOLERANCE'],
            "RETURNS_ITEM": row['RETURNS ITEM'],
            "SPECIAL_STOCK_INDICATOR": row['SPECIAL STOCK INDICATOR'],
            "CONTRACT_NUMBER": row['CONTRACT NUMBER'],
            "AGREEMENT_ITEM_NUMBER": row['AGREEMENT ITEM NUMBER'],
            "ITEM_CATEGORY": row['ITEM CATEGORY'],
            "TAX_JURISDICTION_CODE": row['TAX JURISDICTION CODE'],
            "DELIVERY_COSTS": row['DELIVERY COSTS'],
            "ORDER_UNIT": row['ORDER UNIT'],
            "QUANTITY": row['QUANTITY'],
            "NET_PRICE": row['NET PRICE'],
            "NET_ORDER_VALUE": row['NET ORDER VALUE'],
            "TAX_CODE": row['TAX CODE']
        }
        insert_data(conn, "PurchaseOrders", data)

    conn.close()


def get_schema_representation():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="shivam@123",
        database=DATABASE_NAME
    )
    cursor = conn.cursor()
 
    # Fetch all tables
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
 
    schema = {}
    for table in tables:
        table_name = table[0]
        cursor.execute(f"DESCRIBE {table_name};")
        columns = cursor.fetchall()
        table_schema = [{"name": col[0], "type": col[1]} for col in columns]
        schema[table_name] = table_schema
 
    conn.close()
    return schema

if __name__ == "__main__":
    create_database()
    setup_purchase_orders_table()
    # print(query_database("SELECT * FROM PurchaseOrders LIMIT 50"))

    print(get_schema_representation())