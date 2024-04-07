from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.callbacks import get_openai_callback
from langchain.sql_database import SQLDatabase
from langchain.chat_models import ChatOpenAI

from dotenv import load_dotenv 
load_dotenv()


from extract_trace import get_final_trace
from db_info import get_db_uri

def initialize_agent(database_choice,db_filename,db_uri):
    
    db = SQLDatabase.from_uri(db_uri)
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-0125",temperature=0,openai_api_key="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")
    toolkit = SQLDatabaseToolkit(db=db,llm=llm)
    agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True
) 
    return agent_executor


def get_nl_response(input_query,database_choice,db_filename=''):
   
    #change for contents not there in database ,i dont knw
    db_uri=get_db_uri(database_choice,db_filename)
    agent_executor=initialize_agent(database_choice,db_filename,db_uri)
    try:
        with get_openai_callback() as cost:
            final_answer=agent_executor.run(input=input_query,handle_parsing_errors=True)
            print(final_answer)
        if final_answer==" I don't know.":
            return {'Answer':"Relevant information can't be extracted from the database.",'SQL':'','Result':'','Thought':'','Cost':str(cost)}
    except ValueError:
        return {'Answer':"Relevant information is not contained in the database.",'SQL':'','Result':'','Thought':'','Cost':str(cost)}
        
        
    sql_query,db_result,thought=get_final_trace()
    if sql_query.find(';')==-1:
        final_trace={'SQL':sql_query+';','Result':db_result,'Thought':thought,'Answer':final_answer,'Cost':str(cost)}
    else:
        final_trace={'SQL':sql_query,'Result':db_result,'Thought':thought,'Answer':final_answer,'Cost':str(cost)}
    return final_trace

#query="what type of information is present in the database?"    
# query='Tell me the number of employees from each country.Make sure to include those countries which doesnt have any employees as well.'
# query='What are job roles of the employees and also their names, who has the top 4 salaries?'
# query='Which customer ordered the most and how many orders by that customer?'
# query='which city received the highest individual average discount having negative profit ratio '
# query="Name any 3 employees from Australia"
# query='how many employees in total are Japan,Germany,Canada and China ?'
# query='tell me the count of employees from the countries Japan ,Germany,Canada and China ?'
# query='tell me any two employees having equal salary'
# how many employees earn close to average salary without having difference greater than 1500
# which employee recevied the highest salary and which employee received the lowest salary
# for key,value in get_nl_response(query,1,"sales.db").items():
#     print(f"{key}: {value}")
    