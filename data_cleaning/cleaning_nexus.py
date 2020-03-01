import pandas as pd 
import re
import numpy as np


#Getting user story data
df = pd.read_csv('C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/datasets/jiradataset_issues.csv')

#Selecting project
df_project = df[df['project'] == 'nexus']

#Filtering out only user stories that have been compleated
story_done = df_project[(df_project['fields.issuetype.name'] == 'Story') & (df_project['fields.status.name'] == 'Done')]


#Cleaning
#Taking only description (user story) and indentification key
project_save = story_done[['fields.description',  'key']]
print(len(project_save))

#Removing empty descriptions
project_save = project_save[ project_save['fields.description'].notnull() ]

#Replacing special characters
xlist = ['\\n', '\\r', '<', '>', '`', ':', '\\', '_', '{', '}', '@', '-', '$', '[', ']', '#', '/', '(', ')', '*', '+', '%', '~', '|', '=', '&', "'", '"', '\t']
for x in xlist:
    project_save['fields.description'] = project_save['fields.description'].str.replace(x, ' ')

#Keeping the "I'd like" part in a correct way
project_save['fields.description'] = project_save['fields.description'].str.replace('I d', "I'd")

#Cleaning nin-ascii characters
project_save['fields.description'] = project_save['fields.description'].apply(lambda x: re.sub(r'[^\x00-\x7F]+',' ', x))

#Removing spaces form the end of description
project_save['fields.description'] = project_save['fields.description'].str.lstrip()

#Replacing multiple spaces with one
project_save['fields.description'] = project_save['fields.description'].str.replace(' +', ' ')

#Removing duplicates
project_save = project_save.drop_duplicates()

#Removing duplicate stories
project_save = project_save.drop_duplicates(subset='fields.description', keep="first")
print(len(project_save))


#Removing upper outliers using standard deviation
project_save['description_length'] = project_save['fields.description'].str.len()
mean_story_length = np.mean(project_save['description_length'])
standart_deviation_story_length = np.std(project_save['description_length'])
project_save['suitable_title_length'] = project_save['description_length'].apply(lambda x: x if x < mean_story_length + 2 * standart_deviation_story_length else 0)
project_save = project_save[project_save.suitable_title_length != 0]

project_output = project_save[['fields.description',  'key']]
print(len(project_output))

#Writing 26 rows of cleaned data to a csv
project_output.to_csv("C://Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/cleaned_input_data/jira-nexus-allus.csv", sep=',', encoding='utf-8', doublequote = True, header=False, index=False, line_terminator=",\n")
