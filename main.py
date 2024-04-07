from gptsql import get_nl_response
from sqlgen import get_sql_response
from extract_trace import get_final_trace
from db_info import get_execution_result,get_tablenames,get_schema_and_sample_rows,get_table_shape
from csvtodb import get_sqlitedb
def nl_response(query,db_choice=1,db_file=''):
    
    try:
        llm_answer=get_nl_response(input_query=query,database_choice=db_choice,db_filename=db_file)
        return llm_answer
    
    except Exception as e:
        print('Response generation error : ',e)
        return {'Answer':"Sorry. Cannot fulfill this request.",'SQL':'','Result':'','Thought':'','Cost':llm_answer['Cost']}

def get_full_trace():
    
    try:
        fulltrace=get_final_trace(full_trace=True)
        return fulltrace
    
    except Exception as e:
        print("Error occured in trace extraction : ",e)
        return 'Error occured in trace extraction.'
    
def generate_sql(user_input,db_choice=1,db_file=''):
    
    try:
        sql_list,llm_response=get_sql_response(user_query=user_input,database_choice=db_choice,db_filename=db_file)
        print(sql_list)
        return sql_list,llm_response
    
    except Exception as e:
        print("Error occured in SQL generation : " ,e)
        return [],'Error occured in SQL generation.'
    
def execution_result(gen_sql_query,db_choice=1,db_file=''):
    
    try:
        df=get_execution_result(sql_query=gen_sql_query,database_choice=db_choice,db_filename=db_file) 
        return df
    
    except Exception as e:
        print("Error occured in executing sql statement : ",e)
        return  "" 
    
def get_table_list(db_choice,db_file=''):
    
    try:
        tables =get_tablenames (database_choice=db_choice,db_filename=db_file)     
        return tables
    
    except Exception as e:
        print("Error occured retrieving table names : ",e)
        return ""
    
def get_db_schema(db_choice,db_file=''):
    
    try:
        tables,sql_schema =get_schema_and_sample_rows(database_choice=db_choice,db_filename=db_file)     
        return tables,sql_schema
    
    except Exception as e:
        print("Error occured retrieving schema : ",e)
        return ""    
    
def get_table_dimensions(database_choice,db_filename=''):
    try:
        shapes=get_table_shape(database_choice,db_filename)
        return shapes
    except Exception as e:
        print("Error occured retrieving table shape : ",e)    
        return '0x0'

def convert_csv_to_db(csvfilename):
    try:
        database_file=get_sqlitedb(csvfilename)
        return database_file
    except Exception as e:
        print("Error occured converting csv to db : ",e)        