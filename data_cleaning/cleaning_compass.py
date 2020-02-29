import pandas as pd 
import re


#Getting user story data
df = pd.read_csv('C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/datasets/compass_issues_extracted.csv')

#Selecting project
df_project = df[df['project.name'] == 'Compass ']

#Filtering out only user stories that have been compleated
story_done = df_project[(df_project['issuetype.name'] == 'Story') & (df_project['status.statusCategory.name'] == 'Done')]

#Cleaning
#Taking only description (user story) and sprint key
project_save = story_done[['description',  'key']]

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

#Writing cleaned data to a csv
project_save.to_csv("C://Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/cleaned_input_data/jira-compass-allus.csv", sep=',', encoding='utf-8', doublequote = True, header=False, index=False, line_terminator=",\n")
