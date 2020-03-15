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
#Taking summary (heading of issue) and description of the issue
project_description = story_done[['description',  'key']]
project_summary = story_done[['summary', 'key']]
#Renaming description to fields.description to match with other projects
project_description = project_description.rename(columns={'description': 'fields.description'})
#Renaming summary to description
project_summary = project_summary.rename(columns={'summary': 'fields.description'})
#Adding row with indentifier for indentifyng summary and description
project_description['identif'] = 0
project_summary['identif'] = 1

# Removing summaries with less than 3 words
project_summary['nr_of_words'] = project_summary['fields.description'].str.split().str.len()
project_summary = project_summary[project_summary['nr_of_words'] > 3]

#Mergeing summary and description together
project_save = pd.merge(project_description, project_summary, how='outer')
print('Description and summary merged: ' + str(len(project_save)))

#Removing empty descriptions
project_save = project_save[ project_save['fields.description'].notnull() ]
print('Empty descriptions removed: ' + str(len(project_save)))

#Removing unneeded headings from beginning of the description
project_save['fields.description'] = project_save['fields.description'].str.replace('h3.', '')
project_save['fields.description'] = project_save['fields.description'].str.replace('h5.', '')
project_save['fields.description'] = project_save['fields.description'].str.replace('User story', '')
project_save['fields.description'] = project_save['fields.description'].str.replace('User Story', '')
project_save['fields.description'] = project_save['fields.description'].str.replace('Story', '')
project_save['fields.description'] = project_save['fields.description'].str.replace('quote Split from COMPASS 3826 quote', '')

#Removing everything that follows special headings
project_save['fields.description'] = project_save['fields.description'].str.split('h3. Acceptance Criteria').str[0] 
project_save['fields.description'] = project_save['fields.description'].str.split('h3. Notes').str[0]
project_save['fields.description'] = project_save['fields.description'].str.split('h2.').str[0]
project_save['fields.description'] = project_save['fields.description'].str.split('Product Acceptance Criteria').str[0]
project_save['fields.description'] = project_save['fields.description'].str.split('User anecdote').str[0]
project_save['fields.description'] = project_save['fields.description'].str.split('Acceptance Criteria').str[0]
project_save['fields.description'] = project_save['fields.description'].str.split('Acceptance criteria').str[0]
project_save['fields.description'] = project_save['fields.description'].str.split('Notes').str[0]
project_save['fields.description'] = project_save['fields.description'].str.rstrip()

#Remove links to web
project_save['fields.description'] = project_save['fields.description'].apply(lambda x: re.sub('http[s]?://\S+', ' ', str(x)))
#Remove jar file extensions
project_save['fields.description'] = project_save['fields.description'].apply(lambda x: re.sub('\s+.*.jar\s*', ' ', str(x)))
#Remove code examples
project_save['fields.description'] = project_save['fields.description'].apply(lambda x: re.sub('"{code(.*){code}"', ' ', str(x)))
#Remove curly bracets
project_save['fields.description'] = project_save['fields.description'].apply(lambda x: re.sub('{{(.*)}}', ' ', str(x)))
#Remove another type of curly bracets
project_save['fields.description'] = project_save['fields.description'].apply(lambda x: re.sub('{(.*)}', ' ', str(x)))
#Remove paths
project_save['fields.description'] = project_save['fields.description'].apply(lambda x: re.sub('\S+?(?=\/)\/\S*\/\S*', ' ', str(x)))
#Remove word longer than 19 characters
project_save['fields.description'] = project_save['fields.description'].apply(lambda x: re.sub('.\S{19,}.', ' ', str(x)))
#Remove curly brackets and everything in them
project_save['fields.description'] = project_save['fields.description'].apply(lambda x: re.sub('\s*{.*}\s*', ' ', str(x)))
#Remove exclamation marks and everything between them (used for image files, for example !GettingStarted.png! )
project_save['fields.description'] = project_save['fields.description'].apply(lambda x: re.sub('\s*!.*!\s*', ' ', str(x)))
#Remove square braces and everything between them
project_save['fields.description'] = project_save['fields.description'].apply(lambda x: re.sub('\[([^[\].*()]+?)\]', ' ', str(x)))
#Cleaning nin-ascii characters
project_save['fields.description'] = project_save['fields.description'].apply(lambda x: re.sub(r'[^\x00-\x7F]+',' ', x))

#Replacing special characters
xlist = ['\\n', '\\r', '<', '>', '`', ':', '\\', '_', '{', '}', '@', '-', '$', '[', ']', '#', '/', '(', ')', '*', '+', '%', '~', '|', '=', '&', "'", '"', '\t']
for x in xlist:
    project_save['fields.description'] = project_save['fields.description'].str.replace(x, ' ')

#Removing whitespaces
project_save['fields.description'] = project_save['fields.description'].str.replace('\n', ' ')
project_save['fields.description'] = project_save['fields.description'].str.replace('\r', ' ')
project_save['fields.description'] = project_save['fields.description'].str.replace('\t', ' ')
project_save['fields.description'] = project_save['fields.description'].str.replace('\s', ' ')
project_save['fields.description'] = project_save['fields.description'].str.replace(' +', ' ')
project_save['fields.description'] = project_save['fields.description'].str.replace('&nbsp', ' ')
project_save['fields.description'] = project_save['fields.description'].str.lstrip()

#Removing duplicates with same descriptions and keys
project_save = project_save.drop_duplicates(subset=['fields.description', 'key'])
print('Duplicates removed: ' + str(len(project_save)))

#Removing upper outliers using standard deviation
project_save['description_length'] = project_save['fields.description'].str.len()
mean_story_length = np.mean(project_save['description_length'])
standart_deviation_story_length = np.std(project_save['description_length'])
project_save['suitable_title_length'] = project_save['description_length'].apply(lambda x: x if x < mean_story_length + 3 * standart_deviation_story_length else 0)
project_save = project_save[project_save.suitable_title_length != 0]

project_output = project_save[['fields.description',  'key']]
print(len(project_output))

#Writing 93 rows of cleaned data to a csv
project_output.to_csv("C://Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/cleaned_input_data/jira-compass-allus.csv", sep=',', encoding='utf-8', doublequote = True, header=False, index=False, line_terminator=",\n")
