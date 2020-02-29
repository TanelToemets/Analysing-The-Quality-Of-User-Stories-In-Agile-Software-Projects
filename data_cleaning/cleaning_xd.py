import pandas as pd 
import re


#Getting user story data
df = pd.read_csv('C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/datasets/jiradataset_issues.csv')

#Selecting project
df_project = df[df['project'] == 'xd']

#Filtering out only user stories that have been compleated
story_done = df_project[(df_project['fields.issuetype.name'] == 'Story') & (df_project['fields.status.name'] == 'Done')]


#Cleaning
#Taking only description (user story) and indentification key
project_save = story_done[['fields.description',  'key']]

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

#Removing unneeded headings and spaces from the beginning of the description
project_save['fields.description'] = project_save['fields.description'].str.replace('h2. Narrative', '')
project_save['fields.description'] = project_save['fields.description'].str.lstrip()

#Removing everything that follows "h2. Back story" (not part of user story)
project_save['fields.description'] = project_save['fields.description'].str.split('h2. Back story   ').str[0]
project_save['fields.description'] = project_save['fields.description'].str.split('h2.  Back story').str[0]

#Removing spaces form the end of description
project_save['fields.description'] = project_save['fields.description'].str.lstrip()

#Replacing multiple spaces with one
project_save['fields.description'] = project_save['fields.description'].str.replace(' +', ' ')

#Removing duplicates
project_save = project_save.drop_duplicates()

#Removing duplicate stories
project_save = project_save.drop_duplicates(subset='fields.description', keep="first")

#Writing cleaned data to a csv
project_save.to_csv("C://Users/Tanel/Documents/Ylikool/Magister/Master Thesis//Analysing ASP Repo/data/cleaned_input_data/jira-xd-allus.csv", sep=',', encoding='utf-8', doublequote = True, header=False, index=False, line_terminator=",\n")
