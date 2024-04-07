import sqlite3
import csv
import re 
import pandas as pd
import sqlite3

def get_names(csv_filename):
    
    database_filename = csv_filename.split('.')[0]
    db_tablename= re.sub(r'[^a-zA-Z0-9]', '', database_filename)
    database_filename=db_tablename+'.db'
    db_tablename=db_tablename+'_table'
    
    return database_filename,db_tablename


def get_sqlitedb(csv_filename):
    
    database_filename,db_tablename=get_names(csv_filename)
    df=pd.read_csv(csv_filename)
    conn=sqlite3.connect(database_filename) 
    df.to_sql(db_tablename,conn,if_exists='replace')
    
    return database_filename  

# def get_db(db_filename):
#     csv_filename = db_filename
#     db_filename = csv_filename.split('.')[0]
#     db_name= re.sub(r'[^a-zA-Z0-9]', '', db_filename)
#     db_filename=db_name+'.db'
#     connection = sqlite3.connect(db_filename)
#     db_name=db_name+'_table'
#     cursor = connection.cursor()
#     # print(db_name,db_filename)
    
#     # Read the CSV file and create a table in the SQLite database
#     with open(csv_filename, 'r') as csv_file:
#         csv_reader = csv.reader(csv_file)
#         headers = next(csv_reader)
        
#         # Creating a table with columns based on CSV headers
#         create_table_query = f"CREATE TABLE IF NOT EXISTS {db_name} ({', '.join(headers)});"
#         cursor.execute(create_table_query)

#         # Inserting data into the table
#         for row in csv_reader:
#             insert_data_query = f"INSERT INTO {db_name} VALUES ({', '.join(['?' for _ in row])});"
#             cursor.execute(insert_data_query, row)
            
#     connection.commit()
#     connection.close()
#     return db_filename 

   
# get_sqlitedb('sales-data-sample.csv')    
    
