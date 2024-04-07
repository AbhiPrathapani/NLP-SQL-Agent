import os
import pandas as pd
from decimal import Decimal
from sqlalchemy import create_engine, inspect,text,MetaData
from langchain.sql_database import SQLDatabase
from csvtodb import get_sqlitedb


def create_dbengine(database_choice,db_filename=''):
    
    try:  
          
        db_uri=""   
        current_dir = os.getcwd()
        
        if database_choice==1:
            # if db_filename==None:
            #     db_filename='salesdatasample.db'
            db_filename=db_filename or 'salesdatasample.db'    
            db_path = os.path.join(current_dir, db_filename)
            db_uri="sqlite:///"+db_path
             
            # db_uri="sqlite:////home/Sravan/Desktop/d/prjcode/chinook.db"
           
        elif database_choice==2:
            db_uri= "postgresql://postgres:pavan@localhost:5432/hrdata"
            # db_uri= "postgresql://postgres:3033@localhost:5432/hrdata"
            
        engine= create_engine(db_uri)
        
        return engine
    
    except Exception as e:
        print("sqlalchemy engine error: ",e)
        

def get_relations(engine):
    
    metadata = MetaData()
    metadata.reflect(bind=engine)
    relations= ""
    
    for table_name, table in metadata.tables.items():
        for fk in table.foreign_key_constraints:
            local_columns = ", ".join(str(column) for column in fk.columns)
            referenced_table = fk.elements[0].column.table
            referenced_columns = ", ".join(str(column) for column in referenced_table.primary_key)
            relations=relations+"# "+f"{local_columns} --> {referenced_columns}"+'\n'
            # print(f"{table_name}.{local_columns} = {referenced_table.name}.{referenced_columns}")
            # print(f"{local_columns} = {referenced_columns}")
            
    return relations       
        
def get_table_info(database_choice,db_filename=''):
    
    try:
        if db_filename:
            if db_filename.endswith('csv'):
                db_filename=get_sqlitedb(db_filename)
        # if database_choice==1:
        #     engine=create_dbengine(database_choice,db_filename)
        # elif database_choice==2:
        #     engine=create_dbengine(database_choice)   
        engine=create_dbengine(database_choice,db_filename) 
        inspector = inspect(engine)
        relations=get_relations(engine)
        connection=engine.connect()
        table_names = [i for i in inspector.get_table_names() if not i.startswith('sql')]
        table_info,table_shape = {},{}

        for table_name in table_names:
            column_details = inspector.get_columns(table_name)
            columns = [column['name'] for column in column_details]
            if table_name not in table_info:
                table_info[table_name]=columns
                
            count_query = f'SELECT COUNT(*) FROM {table_name}'
            num_rows = connection.execute(text(count_query)).scalar()
            
            if table_name not in table_shape:
                table_shape[table_name]=f"{num_rows} rows x {len(columns)} columns"   
        # print(table_shape)
        connection.close()       
        engine.dispose()
        return table_names,table_info,relations


    except Exception as e:
        print(f"table info Error: {e}")
        return None


# print(table_names,table_info)
def get_formatted_schema(database_choice=1,db_filename=''):
    
    table_names,table_info,relations=get_table_info(database_choice,db_filename)
    formatted_schema=""
    start_string=""
    
    for table_name in table_names:
        start_string="# "+table_name+" ( "
        for column in table_info[table_name]:    
            start_string=start_string+column+", "    
        start_string=start_string[:-2]+" )"
        # sample rows add here
        formatted_schema=formatted_schema+ start_string+"\n"
        
    formatted_schema=formatted_schema+relations   
    return formatted_schema

def get_db_uri(database_choice,db_filename=''):
    
    if db_filename.endswith('csv'):
        db_filename=get_sqlitedb(db_filename)
        
    db_uri=''
    if database_choice==1:
        
        start_str='sqlite:///'
        current_dir = os.getcwd()
        db_filename=db_filename or 'sales.db'    
        db_path = os.path.join(current_dir, db_filename)
        # default_db_uri = "sqlite:////home/Sravan/Desktop/d/prjcode/demo.db"
        db_uri=start_str+db_path
        
    elif database_choice==2:
        
        db_username='postgres'
        password='pavan'
        host='localhost'
        port=5432
        db='hrdata'
        
        # db_username='postgres'
        # password='3033'
        # db='Employees'
        start_str='postgresql+psycopg2://'
        db_uri=f'{start_str}{db_username}:{password}@{host}:{port}/{db}'
        # default_db_uri="postgresql+psycopg2://tempuser:password@localhost:5432/hrdata"
        
    return db_uri

def get_SQLdb(database_choice,db_filename):
    db_uri=get_db_uri(database_choice,db_filename)
    db = SQLDatabase.from_uri(db_uri)
    return db

def get_execution_result(sql_query='',database_choice=1,db_filename='',shape=False):
    
    db=get_SQLdb(database_choice,db_filename)
    if sql_query.lower().find('select')!=-1:
        col_list,rows=db.run_no_throw(sql_query,columns=True)
        if shape==True:
            return f'{len(rows)} rows X {len(col_list)} columns'
        df = pd.DataFrame(rows, columns=col_list) 
        
    return df

def get_schema_and_sample_rows(database_choice,db_filename=''):
    
    db=get_SQLdb(database_choice,db_filename)
    tables=db.get_usable_table_names()
    df_list=[]
    
    for table_name in tables:
        df=get_execution_result(sql_query=f'SELECT * FROM {table_name} LIMIT 5',database_choice=database_choice,db_filename=db_filename)
        df_list.append(df)
    # schema_sample_rows=db.get_table_info_no_throw()

    return tables,df_list

def get_tablenames(database_choice,db_filename=''):
    
    db=get_SQLdb(database_choice,db_filename)
    tables=db.get_usable_table_names()
    return tables

def get_table_shape(database_choice,db_filename=''):
    
    tables=get_tablenames(database_choice,db_filename)
    shapes={}
    for table_name in tables:
        shapes[f'{table_name}']=get_execution_result(f'SELECT * FROM {table_name}',database_choice,db_filename,shape=True)
    
    return shapes

def get_3_rows(database_choice,db_filename=''):
    db=get_SQLdb(database_choice,db_filename)
    tables=get_tablenames(database_choice,db_filename)
    table_rows=""
    for table_name in tables:
        full_desc=db.get_table_info_no_throw(table_names=[table_name])
        # print(full_desc)
        row_start=full_desc.rfind('/*')
        rows_end=len(full_desc)
        table_rows+=full_desc[row_start:rows_end]+'\n'
    return table_rows.replace('/*','#').replace('*/','#')
print(get_3_rows(1,'sales.db'))
# print(get_execution_result("SELECT COUNT(*)  FROM employees  JOIN countries ON employees.country_id = countries.country_id  WHERE countries.country_name IN ('Canada', 'Australia');",2))
# print(get_table_shape(1,'chinook.db'))