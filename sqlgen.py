import re
from langchain.chat_models import ChatOpenAI
from db_info import get_formatted_schema,get_3_rows
from dotenv import load_dotenv 
load_dotenv()


def get_formatted_llmresponse(llmresponse):
    
    matches = re.finditer(r'SELECT.*?;', llmresponse, re.DOTALL)
    sql_queries = [match.group(0).replace('\n',' ') for match in matches]
    
    return sql_queries
    
    
def get_sql_response(user_query,database_choice,db_filename=''):
    
    chat_prompt= [
    {
        "role": "system",
        "content": "You are now an excellent SQL writer, first I'll give you some tips and examples, and I need you to remember the tips, and do not make same mistakes."
    },
    {
        "role": "user",
        "content": """Tips 1: 
Question: Which A has most number of B?
Gold SQL: select A from B group by A order by count ( * ) desc limit 1;
Notice that the Gold SQL doesn't select COUNT(*) because the question only wants to know the A and the number should be only used in ORDER BY clause, there are many questions asks in this way, and I need you to remember this in the the following questions."""
    },
    {
        "role": "assistant",
        "content": "Thank you for the tip! I'll keep in mind that when the question only asks for a certain field, I should not include the COUNT(*) in the SELECT statement, but instead use it in the ORDER BY clause to sort the results based on the count of that field."
    },
    {
        "role": "user",
        "content": """Tips 2: 
Don't use "IN", "OR", "LEFT JOIN" as it might cause extra results, use "INTERSECT" or "EXCEPT" instead, and remember to use "DISTINCT" or "LIMIT" when necessary.
For example, 
Question: Who are the A who have been nominated for both B award and C award?
Gold SQL should be: select A from X where award = 'B' intersect select A from X where award = 'C';"""
    },
    {
        "role": "assistant",
        "content": "Thank you for the tip! I'll remember to use \"INTERSECT\" or \"EXCEPT\" instead of \"IN\", \"OR\", or \"LEFT JOIN\" when I want to find records that match or don't match across two tables. Additionally, I'll make sure to use \"DISTINCT\" or \"LIMIT\" when necessary to avoid repetitive results or limit the number of results returned."
    },
    
    {
        "role": "user",
        "content": """Tips 3: 
Don't provide explanation as a replacement for providing 2 similar yet different SQL queries.For use cases that require 'highest and least' in one query follow this example below.When you need to use UNION and ORDER BY ,make sure to definitely use SUB-Queries.
Question: Which two cities has received the highest and least number of orders respectively?"
Gold SQL : SELECT City, num_orders
FROM (
    SELECT City, COUNT(*) AS num_orders
    FROM salesdatasample_table
    GROUP BY City
    ORDER BY num_orders DESC
    LIMIT 1
) AS highest_orders

UNION

SELECT City, num_orders
FROM (
    SELECT City, COUNT(*) AS num_orders
    FROM salesdatasample_table
    GROUP BY City
    ORDER BY num_orders ASC
    LIMIT 1
) AS least_orders;
 Notice that the Gold SQL doesn't provide 2 separate queries, instead provides a single query using subqueries and union clause ,also order by clause always comes after union clause in Gold SQL unless especially sub-queries are used.Also notice that Gold SQL doesnt return 2 cities from descending clause ,it returns one city each from asc and desc clause."""
    },
    {
        "role": "assistant",
        "content": "Thank you for the tip! I'll remember to use \"UNION\" and/or Sub-Queries instead of two different queries or single query that doesn't fulfill task requirements. Additionally, I'll  remember to use sub-queries when i need to use \"UNION\" and \"ORDER BY\" clauses , I'll also be cautious and double-check the number of opening and closing parenthesis always when using Sub-Queries."
    },
    {
        "role": "user",
        "content": """Tips 4: 
    Address the requirements provided in the question such as when using aggregate operations ,analyze on what portion of data is the aggregate operator to be applied, and that portion can be obtained by subqueries to prioritize elimination of irrelevant data ,which indirectly leads to selection of relevant data.
Question: What is the average life expectancy in the countries where English is not the official language? 
Gold SQL should be: SELECT AVG(life_expectancy) FROM country WHERE name NOT IN (SELECT T1.name FROM country WHERE T1.language='English');
    Observe that the Gold SQL is not 'select avg(life_expectancy) from country where language <> 'English';'
        Instead it made correct usage of subquery for better elimination.This is especially useful when dealing with multiple tables in database."""
    
    },
    {
        "role": "assistant",
        "content": "Sure! I'll remember to use subqueries and NOT IN operator as required to better eliminate irrelevant data and I'll verify that i retrieve only those rows after correct elimination and perform aggregation appropriately."
    }, 
    
]
    db_schema=get_formatted_schema(database_choice,db_filename)
    three_rows=get_3_rows(database_choice,db_filename)
    chat_prompt=[{
        "role": "system",
        "content": "You are now an SQL Agent that generates SQL query from user query"
    },
    {
        "role": "user",
        "content": '''Given the following database schema and a user query, generate a syntactically and semantically valid SQL query that selects relevant information from the database as required by user query. Ensure that the generated SQL query meets the user's intent and complies with the specified task requirements.'''
    },
    {
        "role": "assistant",
        "content": "Thank you for the tip! I'll keep in mind that when the question only asks for a certain field, I should not include the COUNT(*) in the SELECT statement, but instead use it in the ORDER BY clause to sort the results based on the count of that field."
    },
    ]
    user_prompt=f'''role": "user",
    "content":"""### Complete sqlite SQL query only without explanation ,by verifying presence of every column used in the sql query with provided schema information ,this helps to verify if a column is present in a particular table or not, and do not select extra columns that are not
explicitly requested in the query.An SQL query must have a semicolon in the end of query.
### Sqlite SQL tables, with their properties:
#
{db_schema}
#
### {user_query}
#

'''
    chat_prompt.append({user_prompt})
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-0125",temperature=0,openai_api_key="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")
    # llm = ChatOpenAI(model_name='gpt-3.5-turbo')
    # print(chat_prompt)
    llm_response=llm.predict(str(chat_prompt))
    print(llm_response)
    
    sql_list=get_formatted_llmresponse(llm_response)
    
    return sql_list,llm_response.replace('Gold SQL: ',"")


# #Sample rows from all tables,use this to verify existence of columns in tables.
# {three_rows}
#

# code from below to be moved to frontend
# user_inp='How many categories exist?'
# user_inp='What is the  average discount of specific cities individually, whose profit ratio is negative?'
#user_inp='which city received the highest individual average discount having negative profit ratio '
# all_sqls,llmresponse=get_sql_response(user_inp,1,'demo.db')
# user_inp='Display the average  salary  of all departments and their names from employees of  United States of America.'
# user_inp='Display the department wise  highest salary of all countries'
# all_sqls,llmresponse=get_sql_response(user_inp,1,"salesdatasample.db")
# num_queries=len(all_sqls)
# # print(llmresponse)
# if num_queries==0:
#     print("error")
    
# elif num_queries==1:
#     print(all_sqls[0])
#     pass    
# elif num_queries>1:
#     for i in all_sqls:
#         print(i)
