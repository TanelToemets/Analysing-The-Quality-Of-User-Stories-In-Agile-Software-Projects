import pandas as pd 
import re
import numpy as np


#Getting user story data
df = pd.read_csv('C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/datasets/compass_issues_extracted.csv')

#Selecting project
df_project = df[df['project.key'] == 'COMPASS']

#Filtering out only user stories that have been compleated
story_done = df_project[(df_project['issuetype.name'] == 'Story') & (df_project['status.statusCategory.name'] == 'Done')]

#Cleaning
#Taking only description (user story) and sprint key
project_save = story_done[['description',  'key']]
print(len(project_save))

#Removing empty descriptions
project_save = project_save[ project_save['description'].notnull() ]

#Replacing special characters
xlist = ['\\n', '\\r', '<', '>', '`', ':', '\\', '_', '{', '}', '@', '-', '$', '[', ']', '#', '/', '(', ')', '*', '+', '%', '~', '|', '=', '&', '"', '\t']
for x in xlist:
    project_save['description'] = project_save['description'].str.replace(x, ' ')

#Cleaning nin-ascii characters
project_save['description'] = project_save['description'].apply(lambda x: re.sub(r'[^\x00-\x7F]+',' ', x))

#Removing unneeded headings and spaces from the beginning of the description
project_save['description'] = project_save['description'].str.replace('h3.', '')
project_save['description'] = project_save['description'].str.replace('h5.', '')
project_save['description'] = project_save['description'].str.replace('User story ', '')
project_save['description'] = project_save['description'].str.replace('User Story', '')
project_save['description'] = project_save['description'].str.replace('Story', '')
project_save['description'] = project_save['description'].str.replace('quote Split from COMPASS 3826 quote', '')
project_save['description'] = project_save['description'].str.lstrip()

#Removing everything that follows to unneeded headings (not part of user storie)
project_save['description'] = project_save['description'].str.split('h3. Acceptance Criteria').str[0] 
project_save['description'] = project_save['description'].str.split('h3. Notes').str[0]
project_save['description'] = project_save['description'].str.split('h2.').str[0]
project_save['description'] = project_save['description'].str.split('Acceptance Criteria').str[0]
project_save['description'] = project_save['description'].str.split('Acceptance criteria').str[0]
project_save['description'] = project_save['description'].str.split('Notes').str[0]
project_save['description'] = project_save['description'].str.rstrip()

#Replacing multiple spaces with one
project_save['description'] = project_save['description'].str.replace(' +', ' ')

#Removing duplicates
project_save = project_save.drop_duplicates()

#Removing duplicate stories
project_save = project_save.drop_duplicates(subset='description', keep="first")
print(len(project_save))


#Removing upper outliers using standard deviation
project_save['description_length'] = project_save['description'].str.len()
mean_story_length = np.mean(project_save['description_length'])
standart_deviation_story_length = np.std(project_save['description_length'])
project_save['suitable_title_length'] = project_save['description_length'].apply(lambda x: x if x < mean_story_length + 3 * standart_deviation_story_length else 0)
project_save = project_save[project_save.suitable_title_length != 0]

project_output = project_save[['description',  'key']]
print(len(project_output))

#Writing 93 rows of cleaned data to a csv
project_output.to_csv("C://Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/cleaned_input_data/jira-compass-allus.csv", sep=',', encoding='utf-8', doublequote = True, header=False, index=False, line_terminator=",\n")
