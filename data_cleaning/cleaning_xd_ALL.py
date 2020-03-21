
import pandas as pd 
import re
import numpy as np


#Getting user story data
df = pd.read_csv('C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/datasets/jiradataset_issues.csv')

#Selecting project
df_project = df[df['project'] == 'xd']

#Filtering out only user stories that have been compleated
DONE = ['Closed', 'Done', 'Resolved']
story_done = df_project[(df_project['fields.issuetype.name'] == 'Story') & (df_project['fields.status.name'].isin(DONE))]

#Cleaning
#Taking summary (heading of issue) and description of the issue
project_description = story_done[['fields.description',  'key']]
project_summary = story_done[['fields.summary', 'key']]
#Renaming summary to description
project_summary = project_summary.rename(columns={'fields.summary': 'fields.description'})

# #Mergeing summary and description together
project_save = pd.merge(project_summary, project_description, how='outer')
print('Description and summary merged: ' + str(len(project_save)))

#Preparation for groupby
project_save['fields.description'] = project_save['fields.description'].fillna('').astype(str)
#Concatenateing summary and description fields: summary + ' ' + description
project_save = project_save.groupby(['key'])['fields.description'].apply(lambda x: ' '.join(x)).reset_index()

#Removing empty descriptions
project_save = project_save[ project_save['fields.description'].notnull() ]
print('Empty descriptions removed: ' + str(len(project_save)))

#Removing unneeded headings from beginning of the description
project_save['fields.description'] = project_save['fields.description'].str.replace('h2. Narrative', '')
project_save['fields.description'] = project_save['fields.description'].str.lstrip()

#Removing everything that follows special headings
project_save['fields.description'] = project_save['fields.description'].str.split('h2. Back story   ').str[0]
project_save['fields.description'] = project_save['fields.description'].str.split('h2.  Back story').str[0]
project_save['fields.description'] = project_save['fields.description'].str.split('h2.').str[0]
project_save['fields.description'] = project_save['fields.description'].str.split('Back story').str[0]
project_save['fields.description'] = project_save['fields.description'].str.split('\*Example:\*').str[0]

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

#Keeping the "I'd like" part in a correct way
project_save['fields.description'] = project_save['fields.description'].str.replace('I d like', "I'd like")
project_save['fields.description'] = project_save['fields.description'].str.replace('I d want', "I'd want")

#Removing duplicates with same descriptions
project_save = project_save.drop_duplicates(subset=['fields.description'])
print('Duplicates removed: ' + str(len(project_save)))

#Removing upper outliers using standard deviation
project_save['description_length'] = project_save['fields.description'].str.len()
mean_story_length = np.mean(project_save['description_length'])
standart_deviation_story_length = np.std(project_save['description_length'])
project_save['suitable_title_length'] = project_save['description_length'].apply(lambda x: x if x < mean_story_length + 0.7 * standart_deviation_story_length else 0)
project_save = project_save[project_save.suitable_title_length != 0]

# Removing summaries with less than 3 words (lower outliers) - these are not real stories, often afected by data cleaning and connot be analyesd. For example only web link in description instead of user story
project_save['nr_of_words'] = project_save['fields.description'].str.split().str.len()
project_save = project_save[project_save['nr_of_words'] > 3]

project_output = project_save[['fields.description',  'key']]
print('Nr of rows after cleaning: ' + str(len(project_save)))

#Writing cleaned data to a csv
project_output.to_csv("C://Users/Tanel/Documents/Ylikool/Magister/Master Thesis//Analysing ASP Repo/data/cleaned_input_data/jira-xd-allus-ALL.csv", sep=',', encoding='utf-8', doublequote = True, header=False, index=False, line_terminator=",\n")
