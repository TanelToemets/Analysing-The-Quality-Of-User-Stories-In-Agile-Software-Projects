def get_sprint_dict(linex):
    line = linex.split(',')
    sprint_id, sprint_state, sprint_name, sprint_startDate, sprint_endDate, sprint_completeDate = '','','','','',''
    # for each element in the string list
    for l in line:
        if "id=" in l:
            sprint_id = re.sub('id=', '', l)
        elif "state=" in l:
            sprint_state = re.sub('state=', '', l)
        elif "name=" in l:
            sprint_name = re.sub('name=', '', l)
        elif "startDate=" in l:
            sprint_startDate = re.sub('startDate=', '', l)
        elif "endDate=" in l:
            sprint_endDate = re.sub('endDate=', '', l)
        elif "completeDate=" in l:
            sprint_completeDate = re.sub('completeDate=', '', l)

    # append (key, project, sprint name) to the final df
    d = {#'key': key, 
        #'project': p, 
        'sprint.id': sprint_id,
        'sprint.state': sprint_state,
        'sprint.name': sprint_name,
        'sprint.startDate': sprint_startDate,
        'sprint.endDate': sprint_endDate,
        'sprint.completeDate': sprint_completeDate
       }
    return d
	
import ast
import numpy as np
import re
import pandas as pd 
import json
import csv

#Getting user story data
df = pd.read_csv('C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/datasets/compass_issues_extracted.csv')

# df is the issue dataframe
df.loc[:,'sprint'] = df['customfield_10557'].apply(lambda x : np.nan if x is np.nan else ast.literal_eval(x))

# each issue has a list of sprints 
df['sprint'] = df['sprint'].apply(lambda x : np.nan if x is np.nan else [ get_sprint_dict(e) for e in x] )

df.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")

