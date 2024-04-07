import streamlit as st
import time
import pandas as pd
from main import nl_response,execution_result,generate_sql,convert_csv_to_db,get_db_schema,get_table_dimensions

if "messages" not in st.session_state:
    st.session_state.messages = []
if "db_choice" not in st.session_state:
    st.session_state.db_choice = ''
if "input_mode" not in st.session_state:
    st.session_state.input_mode = ''
if "dbfile_name" not in st.session_state:
    st.session_state.dbfile_name = ''
if "filetype" not in st.session_state:
    st.session_state.filetype=0    
if "file_extension" not in st.session_state:
    st.session_state.file_extension=''    
if "csvfile_name" not in st.session_state:
    st.session_state.csvfile_name=''   
if "db_initialized" not in st.session_state:
    st.session_state.db_initialized=False
if "if_df" not in st.session_state:
    st.session_state.if_df=False    
if "generated_query" not in st.session_state:
    st.session_state.generated_query=''
if "generated_ans" not in st.session_state:
    st.session_state.generated_ans=''        

st.title("SQL Query Agent")
       
with open("styles.md", "r") as styles_file:
    styles_content = styles_file.read()
    
st.write(styles_content, unsafe_allow_html=True)

db_options={"***SQLite***":1, "***Postgresql***":2}
label_text='Select the database type:'
db_type = st.radio(label_text, options=list(db_options.keys()),captions=['Sqlite allows uploading custom db/csv files.','Postgresql mode accesses default databases.'],index=None,horizontal=True,)

st.markdown(
    """<style>
div[class*="stRadio"] > label > div[data-testid="stMarkdownContainer"] > p {
    font-size: 24px;
}
    </style>
    """, unsafe_allow_html=True)
    
if db_type:
    st.session_state.db_choice=db_options[db_type]
    
    if st.session_state.db_choice==1:
        file_options={"***Use default sales data.***":1, "***Upload a db/csv file.***":2}
        file_type=st.radio(label="Select file type:",options=list(file_options.keys()),index=None,horizontal=True)
        
        if file_type:
            st.session_state.filetype = file_options[file_type]
            
            if st.session_state.filetype==1:
                st.session_state.dbfile_name='sales.db'
                st.session_state.csvfile_name='sales-data-sample.csv'
                
            elif st.session_state.filetype==2:
                uploaded_file=''
                uploaded_file = st.file_uploader("Choose a file")
                
                if uploaded_file :
                    st.session_state.file_extension = str(uploaded_file.name).split(".")[-1]
                    
                    if st.session_state.file_extension not in ["db", "csv"]:
                        st.error("Please upload a file with .db or .csv extension.")
                        
                    elif st.session_state.file_extension=='csv':
                        st.session_state.csvfile_name=str(uploaded_file.name) 
                        st.session_state.dbfile_name=convert_csv_to_db(st.session_state.csvfile_name)
                        st.markdown(f"Database Selected : {st.session_state.dbfile_name}")
                        
                    elif st.session_state.file_extension=='db':
                        st.session_state.dbfile_name=str(uploaded_file.name)
                        
            if st.session_state.csvfile_name:
                with st.expander('View raw data'):
                    
                    dataframe = pd.read_csv(st.session_state.csvfile_name)
                    rows, cols = dataframe.shape
                    st.write(f'Table dimensions : {rows} rows X {cols} columns')
                    st.write(dataframe)
                    
            elif st.session_state.dbfile_name and not st.session_state.csvfile_name :
                with st.expander("View tables and sample rows"):
                    tables,results=get_db_schema(st.session_state.db_choice,st.session_state.dbfile_name)
                    shapes=get_table_dimensions(st.session_state.db_choice,st.session_state.dbfile_name)
                    for i in range(0,len(tables)):
                        st.write(f"**{tables[i].capitalize()+' table'}**  :  {shapes[tables[i]]}")
                        st.write(results[i])
            
            # if  st.session_state.dbfile_name:
            #     with st.expander("View data explanation:"):
            #         st.write('some response')
            #         # to be done here
            st.session_state.db_initialized=True            
    elif st.session_state.db_choice==2:
        st.write("*Employees database is selected*")
        with st.expander('See sample rows of database.'):
            tables,results=get_db_schema(st.session_state.db_choice,st.session_state.dbfile_name)
            shapes=get_table_dimensions(st.session_state.db_choice,st.session_state.dbfile_name)
            for i in range(0,len(tables)):
                st.write(f"**{tables[i].capitalize()+' table'}**  :  {shapes[tables[i]]}")
                st.write(results[i])
        st.session_state.db_initialized=True
    
    if st.session_state.db_initialized:
        usage_options={"***Response agent***":1, "***Query agent***":2}
        input_type=st.radio('Select the mode of use:',options=list(usage_options.keys()),index=None,horizontal=True)
        
        if input_type:
            st.session_state.input_mode=usage_options[input_type]
            # if len(st.session_state.messages)==0:
            #     initial_message="Hi im an sql agent designed to assist with databases."
            #     # st.session_state.messages.append({"role": "assistant", "content": initial_message})
            #     st.session_state.messages.append({"role": "user", "content": 'Okay lets start!'})
            #     st.session_state.messages.append({"role": "assistant", "content": initial_message})
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    if 'dframe' not in message:
                        continue
                    if message['role']=='assistant' and st.session_state.if_df:
                        if message['sql'].lower().find('select')!=-1:
                            with st.expander('See results'):
                                st.markdown('**SQL**:<br>',unsafe_allow_html=True)
                                st.code(message['sql'],language='sql')
                                if type(message['dframe'])==str:
                                    continue
                                st.dataframe(message['dframe'])
            if prompt := st.chat_input("What is up?"):
                with st.chat_message("user"):
                    st.markdown(prompt)
                st.session_state.messages.append({"role": "user", "content": prompt})
                full_response = ""
                
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    assistant_response=''
                    assistant_response2=''
                    full_response=''
                    if st.session_state.input_mode==1:
                        with st.spinner("Please wait while generating response..."):
                            assistant_response=nl_response(prompt,st.session_state.db_choice,st.session_state.dbfile_name)
                            # assistant_response2={'SQL':assistant_response['SQL'],'Answer':assistant_response['Answer']}
                            st.session_state.generated_query=assistant_response["SQL"]
                            st.session_state.generated_ans=assistant_response['Answer']
                        for chunk in st.session_state.generated_ans.split():
                            full_response += chunk + " "
                            time.sleep(0.10)        
                            message_placeholder.markdown(full_response,unsafe_allow_html=True)
                        if st.session_state.generated_query.lower().find('select')!=-1:
                            st.code(st.session_state.generated_query,language='sql')
                            
                    elif st.session_state.input_mode==2:
                        with st.spinner("Please wait query is being generated..."):
                            sqls,assistant_response=generate_sql(prompt,st.session_state.db_choice,st.session_state.dbfile_name)

                        if sqls:
                            if len(sqls)==0:
                                st.error("Error occured try again.")
                            elif len(sqls)>1:
                                st.session_state.generated_query = sqls[0]
                                other_sqls=sqls[1:]
                                for i in other_sqls:
                                    st.code(i,language='sql')
                            else:
                                st.session_state.generated_query = sqls[0]
                                
                        st.session_state.generated_ans=assistant_response
                        message_placeholder = st.empty()    
                        for chunk in assistant_response.split():
                            full_response += chunk + " "
                            time.sleep(0.10)
                            message_placeholder.markdown(full_response,unsafe_allow_html=True)
                    # st.code(full_response + "▌",language="sql")
                    # message_placeholder.markdown(assistant_response2,unsafe_allow_html=True)    
                    if assistant_response:
                        is_df=False
                        if st.session_state.generated_query.lower().find('select')!=-1:
                            try:
                                with st.spinner("Please wait while generating results."):
                                    time.sleep(1)
                                    if st.session_state.input_mode==1:
                                        
                                        df=execution_result(st.session_state.generated_query,st.session_state.db_choice,st.session_state.dbfile_name)
                                        is_df=True
                                    elif st.session_state.input_mode==2:
                                        try:
                                            df=execution_result(st.session_state.generated_query,st.session_state.db_choice,st.session_state.dbfile_name)
                                            is_df=True
                                        except Exception as e:
                                            is_df=False
                            except ValueError:
                                pass            
                            
                        if is_df:
                            st.session_state.if_df=is_df
                            if st.session_state.generated_query.lower().find('select')!=-1:
                                with st.expander('see results'):
                                    try:
                                        st.markdown('**SQL**:<br>',unsafe_allow_html=True)
                                        st.code(st.session_state.generated_query,language="sql")
                                        st.dataframe(df)
                                    except:
                                        pass    
                            
                if assistant_response:
                    if is_df:
                        st.session_state.messages.append({"role": "assistant", "content": full_response,'dframe':df,"sql":st.session_state.generated_query})
                    else:
                        st.session_state.messages.append({"role": "assistant", "content": full_response,"sql":st.session_state.generated_query})    
        