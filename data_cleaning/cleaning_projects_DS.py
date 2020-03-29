import pandas as pd 
import re
import numpy as np

#Possible projects
#xd       +
#dnn      +
#COMPASS  +
#apstud   +
#mesos    +
#mule     +
#nexus    +
#timob    +
#tistud   +

project = 'SLICE'

projects = {
    "xd":      ("fields.issuetype.name",  "fields.status.name",                 "jiradataset_issues.csv",       0.7  ),
	"dnn":     ("fields.issuetype.name",  "fields.status.statusCategory.name",  "jiradataset_issues.csv",       2    ),
    "COMPASS": ("issuetype.name",         "status.statusCategory.name",         "compass_issues_extracted.csv", 3    ),
	"apstud":  ("fields.issuetype.name",  "fields.status.statusCategory.name",  "jiradataset_issues.csv",       2    ),
    "mesos":   ("fields.issuetype.name",  "fields.status.statusCategory.name",  "jiradataset_issues.csv",       2    ),
    "mule":    ("fields.issuetype.name",  "fields.status.statusCategory.name",  "jiradataset_issues.csv",       2    ),
    "nexus":   ("fields.issuetype.name",  "fields.status.statusCategory.name",  "jiradataset_issues.csv",       2    ),
    "timob":   ("fields.issuetype.name",  "fields.status.statusCategory.name",  "jiradataset_issues.csv",       2    ),
    "tistud":  ("fields.issuetype.name",  "fields.status.statusCategory.name",  "jiradataset_issues.csv",       2    ),
    "SLICE":   ("issuetype.name",         "status.name",                        "slice_issues_extracted.csv", 2      ),
}

#Getting user story data
df = pd.read_csv('C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/datasets/'+projects['{0}'.format(project)][2])

#Manage field names in order to use one file and improve readabiliy
def manage_field_names(project, initial_data):
    if project == 'COMPASS' or project == 'SLICE':
        initial_data = initial_data.rename(columns={'description': 'fields.description'})
        initial_data = initial_data.rename(columns={'project.key': 'project'})
        initial_data = initial_data.rename(columns={'issuetype.name': 'fields.issuetype.name'})
        initial_data = initial_data.rename(columns={'summary': 'fields.summary'})
        print('field names fixed')
    return initial_data

df = manage_field_names(project, df)
#df.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")

#Selecting project
df_project = df[df['project'] == '{0}'.format(project)]

#Filtering out only user stories that have been compleated
DONE = ['Closed', 'Done', 'Resolved', 'Complete']
story_done = df_project[(df_project['fields.issuetype.name'] == 'Story') & (df_project[projects['{0}'.format(project)][1]].isin(DONE))]

#Cleaning
#Taking summary (heading of issue) and description of the issue
project_description = story_done[['fields.description',  'key']]
project_summary = story_done[['fields.summary', 'key']]
#Renaming summary to description
project_summary = project_summary.rename(columns={'fields.summary': 'fields.description'})
#Adding row with indentifier for indentifyng summary and description
project_description['identif'] = 0
project_summary['identif'] = 1

#Mergeing summary and description together
project_save = pd.merge(project_description, project_summary, how='outer')
print('Description and summary merged: ' + str(len(project_save)))

#Removing empty descriptions
project_save = project_save[ project_save['fields.description'].notnull() ]
print('Empty descriptions removed: ' + str(len(project_save)))

def project_specific_cleaning(project):
    if project == 'xd':
        #Removing unneeded headings from beginning of the description
        project_save['fields.description'] = project_save['fields.description'].str.replace('h2. Narrative', '')
        project_save['fields.description'] = project_save['fields.description'].str.lstrip()

        #Removing everything that follows special headings
        project_save['fields.description'] = project_save['fields.description'].str.split('h2. Back story   ').str[0]
        project_save['fields.description'] = project_save['fields.description'].str.split('h2.  Back story').str[0]
        project_save['fields.description'] = project_save['fields.description'].str.split('h2.').str[0]
        project_save['fields.description'] = project_save['fields.description'].str.split('Back story').str[0]
        project_save['fields.description'] = project_save['fields.description'].str.split('\*Example:\*').str[0]
        print('xd special headings removed')
    elif project == 'dnn':
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
        print('dnn special headings removed')
    elif project == 'COMPASS':
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
        print('compass special headings removed')
    elif project == 'apstud':
        #Removing everything that follows special headings
        project_save['fields.description'] = project_save['fields.description'].str.split('h3. Steps to Reproduce').str[0] 
        project_save['fields.description'] = project_save['fields.description'].str.split('h3. Steps to Reproduce').str[0] 
        project_save['fields.description'] = project_save['fields.description'].str.split('Steps to reproduce').str[0] 
        project_save['fields.description'] = project_save['fields.description'].str.split('h3. Actual Result').str[0] 
        print('apstud special headings removed')    
    elif project == 'timob':
        #Removing unneeded headings from beginning of the description
        project_save['fields.description'] = project_save['fields.description'].str.replace('h3. Feature', '')

        #Removing everything that follows special headings
        project_save['fields.description'] = project_save['fields.description'].str.split('h3. Acceptance Test').str[0] 
        print('timob special headings removed')
    elif project == 'tistud':
        #Removing unneeded headings from beginning of the description
        project_save['fields.description'] = project_save['fields.description'].str.replace('h3. Feature', '')
        project_save['fields.description'] = project_save['fields.description'].str.replace('h3.Description', '')

        #Removing everything that follows special headings
        project_save['fields.description'] = project_save['fields.description'].str.split('h3. Debug iOS').str[0] 
        project_save['fields.description'] = project_save['fields.description'].str.split('h3. Notes').str[0]
        project_save['fields.description'] = project_save['fields.description'].str.split('h3. Run Android').str[0] 
        project_save['fields.description'] = project_save['fields.description'].str.split('h3. Steps to Reproduce').str[0]
        project_save['fields.description'] = project_save['fields.description'].str.split('h3. Actual Result').str[0]
        project_save['fields.description'] = project_save['fields.description'].str.split('h3. Expected Result').str[0]
        project_save['fields.description'] = project_save['fields.description'].str.split('h3. Problem').str[0]
        project_save['fields.description'] = project_save['fields.description'].str.split('h3. Expected behavior').str[0]
        project_save['fields.description'] = project_save['fields.description'].str.split('h3. Additional Information').str[0]
        project_save['fields.description'] = project_save['fields.description'].str.split('h3. Associated HD Ticket').str[0]
        project_save['fields.description'] = project_save['fields.description'].str.split('h3. Run MobileWeb').str[0]
        project_save['fields.description'] = project_save['fields.description'].str.split('h3. Debug iOS').str[0]
        project_save['fields.description'] = project_save['fields.description'].str.split('h3. Notes').str[0]

        project_save['fields.description'] = project_save['fields.description'].str.split('h2. Project Creation').str[0]
        project_save['fields.description'] = project_save['fields.description'].str.split('h3. Run iOS').str[0]
        project_save['fields.description'] = project_save['fields.description'].str.split('h3. Debug Android').str[0]
        project_save['fields.description'] = project_save['fields.description'].str.split('h3.Reproduction').str[0]
        project_save['fields.description'] = project_save['fields.description'].str.split('h3. Issue').str[0]
        print('tistud special headings removed')
    elif project == 'SLICE':
        #Removing unneeded headings from beginning of the description
        project_save['fields.description'] = project_save['fields.description'].str.replace('h2. Narrative', '')
        #Removing everything that follows special headings
        project_save['fields.description'] = project_save['fields.description'].str.split('h2. Back story   ').str[0]
        project_save['fields.description'] = project_save['fields.description'].str.split('h2.  Back story').str[0]
        print('slice special headings removed')
    else:
        #For mule, nexus and mesos
        print('No special header cleaning found for this project')

#PROJECT SPECIFIC CLEANING
project_specific_cleaning(project)

#GENERAL CLEANING
#Remove links to web
project_save['fields.description'] = project_save['fields.description'].apply(lambda x: re.sub('http[s]?://\S+', ' ', str(x)))
#Remove jar file extensions
project_save['fields.description'] = project_save['fields.description'].apply(lambda x: re.sub('\s+.*.jar\s*', ' ', str(x)))
#Remove code examples
project_save['fields.description'] = project_save['fields.description'].apply(lambda x: re.sub('{code(.*){code}', ' ', str(x)))
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

#Removing duplicates with same descriptions and keys
project_save = project_save.drop_duplicates(subset=['fields.description'])
print('Duplicates removed: ' + str(len(project_save)))

#Removing upper outliers using standard deviation
project_save['description_length'] = project_save['fields.description'].str.len()
mean_story_length = np.mean(project_save['description_length'])
standart_deviation_story_length = np.std(project_save['description_length'])
project_save['suitable_title_length'] = project_save['description_length'].apply(lambda x: x if x < mean_story_length + projects['{0}'.format(project)][3] * standart_deviation_story_length else 0)
project_save = project_save[project_save.suitable_title_length != 0]

# Removing summaries with less than 3 words (lower outliers) - these are not real stories, often afected by data cleaning and connot be analyesd. For example only web link in description instead of user story
project_save['nr_of_words'] = project_save['fields.description'].str.split().str.len()
project_save = project_save[project_save['nr_of_words'] > 3]


project_output = project_save[['fields.description',  'key', 'identif']]
print('Nr of rows after cleaning: ' + str(len(project_save)))

#Writing cleaned data to a csv
project_output.to_csv("C://Users/Tanel/Documents/Ylikool/Magister/Master Thesis//Analysing ASP Repo/data/cleaned_input_data/jira-{0}-allus-DS.csv".format(project), sep=',', encoding='utf-8', doublequote = True, header=False, index=False, line_terminator=",\n")
