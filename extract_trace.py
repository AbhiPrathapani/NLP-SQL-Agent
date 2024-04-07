import re

def extract_action_input_and_observation(trace_file):
    with open(trace_file, 'r') as file:
        content = file.read()
        sql_text="Action Input:"
    sql_index=content.rfind(sql_text)
    observation_text='Observation:'
    obs_index=content.rfind(observation_text)
    thought_text='Thought:'
    thought_index=content.rfind(thought_text)
    ans_text="Final Answer:"
    ans_index=content.rfind(ans_text)
    sqlquery,observation,Thought,Final_answer="","","",""
    
    for i in range(sql_index+len(sql_text),obs_index):
        sqlquery=sqlquery+content[i]
        
    for i in range(obs_index+len(observation_text),thought_index):
        observation=observation+content[i]
    
    for i in range(thought_index+len(thought_text),ans_index):
        Thought=Thought+content[i]    
    l=[]
    l=[i.replace('\n',' ') for i in [sqlquery,observation,Thought]]
    
    return l
                  


def get_final_trace(full_trace=False):
    
    trace_file_path = "fulltrace.txt"
    if full_trace:
        fulltrace=extract_action_input_and_observation(trace_file_path,full_trace=True)
        return fulltrace
    action_input, observation, thought = extract_action_input_and_observation(trace_file_path)
    
    return action_input,observation,thought

# print(get_final_trace())
