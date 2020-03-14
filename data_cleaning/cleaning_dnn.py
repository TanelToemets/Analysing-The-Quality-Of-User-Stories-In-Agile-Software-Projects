import pandas as pd 
import re
import numpy as np


#Getting user story data
df = pd.read_csv('C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/datasets/jiradataset_issues.csv')

#Selecting project
df_project = df[df['project'] == 'dnn']

#Filtering out only user stories that have been compleated
story_done = df_project[(df_project['fields.issuetype.name'] == 'Story') & (df_project['fields.status.statusCategory.name'] == 'Done')]


#Cleaning
#Taking summary (heading of issue) and description of the issue
project_description = story_done[['fields.description',  'key']]
project_summary = story_done[['fields.summary', 'key']]
project_summary = project_summary.rename(columns={'fields.summary': 'fields.description'})
#Adding row with indentifier for indentifyng summary and description
project_description['identif'] = 0
project_summary['identif'] = 1
#Mergeing summary and description together
project_save = pd.merge(project_description, project_summary, how='outer')
print('Description and summary merged: ' + str(len(project_save)))

#Removing duplicates with same descriptions and keys
project_save = project_save.drop_duplicates(subset=['fields.description', 'key'])
print('Duplicates removed: ' + str(len(project_save)))

#Removing empty descriptions
project_save = project_save[ project_save['fields.description'].notnull() ]
print('Empty rows removed: ' + str(len(project_save)))

#Remove descriptions 
project_save['nr_of_words'] = project_save['fields.description'].str.split().str.len()
project_save = project_save[project_save['nr_of_words'] >= 3] 
#project_save = project_save[(project_save['nr_of_words'] >= 3) & (project_save['identif'] == 1 )]
#project_save.query('nr_of_words >= 3 & 1 == identif')
print('Three or less word stories removed: ' + str(len(project_save)))
 
#Removing unneeded headings from beginning of the description
project_save['fields.description'] = project_save['fields.description'].str.replace('h3. Card', '')
project_save['fields.description'] = project_save['fields.description'].str.replace('h3. CARD', '')
project_save['fields.description'] = project_save['fields.description'].str.replace('h2. Card', '')

#Removing everything that follows special headings
project_save['fields.description'] = project_save['fields.description'].str.split('h2. Conversation').str[0] 
project_save['fields.description'] = project_save['fields.description'].str.split('h3. Conversation').str[0]
project_save['fields.description'] = project_save['fields.description'].str.split('h2. Expected Result').str[0]
project_save['fields.description'] = project_save['fields.description'].str.split('h3. CONVERSATION').str[0]
project_save['fields.description'] = project_save['fields.description'].str.split('h3. CONFIRMATION').str[0]
project_save['fields.description'] = project_save['fields.description'].str.split('h2.').str[0]
project_save['fields.description'] = project_save['fields.description'].str.split('h3.').str[0]
project_save['fields.description'] = project_save['fields.description'].str.split('Confirmation').str[0]

#Removing whitespaces
project_save['fields.description'] = project_save['fields.description'].str.replace('\n', ' ')
project_save['fields.description'] = project_save['fields.description'].str.replace('\r', ' ')
project_save['fields.description'] = project_save['fields.description'].str.replace('\t', ' ')
project_save['fields.description'] = project_save['fields.description'].str.replace('\s', ' ')
project_save['fields.description'] = project_save['fields.description'].str.replace(' +', ' ')
project_save['fields.description'] = project_save['fields.description'].str.replace('&nbsp', ' ')
project_save['fields.description'] = project_save['fields.description'].str.lstrip()

#Remove links to web
project_save['fields.description'] = project_save['fields.description'].apply(lambda x: re.sub('http[s]?://\S+', ' ', str(x)))
#Remove curly brackets and everitying in them
project_save['fields.description'] = project_save['fields.description'].apply(lambda x: re.sub('\s*{.*}\s*', ' ', str(x)))
#Remove exclamation marks and everything between them (used for image files, for example !GettingStarted.png! )
project_save['fields.description'] = project_save['fields.description'].apply(lambda x: re.sub('\s*!.*!\s*', ' ', str(x)))
#Remove square braces and everything between them
project_save['fields.description'] = project_save['fields.description'].apply(lambda x: re.sub('\[([^[\].*()]+?)\]', ' ', str(x)))
#Cleaning nin-ascii characters
project_save['fields.description'] = project_save['fields.description'].apply(lambda x: re.sub(r'[^\x00-\x7F]+',' ', x))

#Removing duplicate stories
project_save = project_save.drop_duplicates(subset='fields.description', keep="first")
print(len(project_save))

#Replacing special characters
xlist = ['\\n', '\\r', '<', '>', '`', ':', '\\', '_', '{', '}', '@', '-', '$', '[', ']', '#', '/', '(', ')', '*', '+', '%', '~', '|', '=', '&', "'", '"', '\t']
for x in xlist:
    project_save['fields.description'] = project_save['fields.description'].str.replace(x, ' ')

#Removing upper outliers using standard deviation
project_save['description_length'] = project_save['fields.description'].str.len()
mean_story_length = np.mean(project_save['description_length'])
standart_deviation_story_length = np.std(project_save['description_length'])
project_save['suitable_title_length'] = project_save['description_length'].apply(lambda x: x if x < mean_story_length + 2 * standart_deviation_story_length else 0)
project_save = project_save[project_save.suitable_title_length != 0]

#Selecting rows for output
project_output = project_save[['fields.description',  'key', 'identif']]
print('Nr of rows after cleaning: ' + str(len(project_save)))

#Writing cleaned data to a csv
project_output.to_csv("C://Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/cleaned_input_data/jira-dnn-allus.csv", sep=',', encoding='utf-8', doublequote = True, header=False, index=False, line_terminator=",\n")
