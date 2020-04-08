import pandas as pd
from matplotlib import pyplot
import datetime

#field = status
#created = date when change was made
#fromString = start state
#toString = end state
#Closed -> Reopened   happens if client finds an error
#Resolved -> Reopened happens if testing finds an errors


#Possible projects
#xd           +
#dnn          +
#COMPASS      +
#apstud       +
#mesos        +
#mule         +
#nexus        +
#timob        +       
#tistud       +
project = 'tistud'

projects = {
    "xd":      ("Done",  "In Progress", "jiradataset_changelog.csv" ), #65 Cnly Done -> In Progress| Fine  ||Other but not in our interest: In Progress -> In PR | In Progress -> To Do | In PR -> In Progress | In PR -> To Do
	"dnn":     ("XXXX", "Reopened", "jiradataset_changelog.csv"     ), #128 | Fine
    "COMPASS": ("XXXX", "XXXX", "compass_changelog_extracted.csv"   ), #3 
	"apstud":  ("XXXX", "Reopened", "jiradataset_changelog.csv"     ), #49  |#Many are going from a Closed to Closed? | Otherwise fine
    "mule":    ("Closed", "Reopened", "jiradataset_changelog.csv"   ), #4   | Fine
    "nexus":   ("XXXX", "XXXX", "jiradataset_changelog.csv"         ), #0   |Reopened state and Closed->Open states exists but none of the stories we are analysing have this state 
    "timob":   ("Closed", "Reopened", "jiradataset_changelog.csv"   ), #7   |#Two are going from a Closed to Closed?  | Otherwise fine
    "tistud":  ("Closed", "Reopened", "jiradataset_changelog.csv"   ), #178 |#Many are going from a Closed to Closed? | Otherwise fine
}

#Read changelog file for rework data
changelog_df = pd.read_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/datasets/"+projects['{0}'.format(project)][2])
print(len(changelog_df))

#Read the stories
stories_df = pd.read_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/cleaned_input_data/jira-{0}-allus-DS.csv".format(project), names=['title', 'key', 'identif', 'z'])
print(len(stories_df))

#Selecting stories by text source identifier
# Description = 0 and summary = 1
stories_df = stories_df[stories_df['identif'] == 0]
stories_df = stories_df.drop_duplicates(subset=['key'])
print(len(stories_df))

#Merge story keys and rework data
rework_df = pd.merge(stories_df, changelog_df, how='left', left_on='key', right_on='key')
print(len(rework_df))

#Selecting the project
rework_df = rework_df[rework_df['field'] == 'status']

#rework_df = rework_df[rework_df['fromString'] == projects['{0}'.format(project)][0]]
#Selecting Reopened stories

#rework_df = rework_df[rework_df['toString'] == projects['{0}'.format(project)][1]]

#finction for project specific state changes
def manage_special_filters(project):
    if project == 'COMPASS':
        rework_df_managed = rework_df[rework_df['fromString'] == 'Closed']
        rework_df_managed = rework_df_managed[(rework_df_managed['toString'] == 'Open') | (rework_df_managed['toString'] == 'In Progress') | (rework_df_managed['toString'] == 'Ready for Work') | (rework_df_managed['toString'] == 'Reopened')]
        print('compass managed')
        return rework_df_managed
    elif project == 'xd':
        rework_df_managed = rework_df[rework_df['fromString'] == 'Done']
        rework_df_managed = rework_df_managed[rework_df_managed['toString'] == 'In Progress']
        print('xd managed')
        return rework_df_managed
    else:
        rework_df_managed = rework_df[rework_df['toString'] == projects['{0}'.format(project)][1]]
        print('project managed')
        return rework_df_managed

rework_df = manage_special_filters(project)

#Formating and indexing creationtime
rework_df['created'] = pd.to_datetime(rework_df['created'], utc=True)
rework_df = rework_df.set_index(pd.DatetimeIndex(rework_df['created']))
#Adding a row showing the percentage of each separate story 
rework_df['rework_nr'] = 1/len(stories_df)
rework_df = rework_df.drop_duplicates(subset=['key'])


#reading sprints data
# sprints_df = pd.read_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/datasets/jiradataset_sprints.csv")
# sprints_df = sprints_df[sprints_df['project'] == project]
# sprints_df = sprints_df[['key', 'sprint.startDate', 'sprint.completeDate']]
# print('sprints')
# print(len(sprints_df))
# #Merge stories with sprint data
# sprints_rework_df = pd.merge(rework_df, sprints_df, how='left', left_on='key', right_on='key')
# print('sprints and rework merged')
# print(len(sprints_rework_df))
# sprints_rework_df.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")


#Printing nr of rework cases
print ("{0} {1} {2}".format(project, "Nr of rework cases:", len(rework_df)))

#Plotting
fig = pyplot.figure()
rework_df.resample('SM')['rework_nr'].sum().plot()
project_up = project.upper()
fig.suptitle(project_up, fontsize=20)
pyplot.xlabel('Time', fontsize=12)
pyplot.ylabel('Percentage of all stories', fontsize=12)
pyplot.show()

#rework_df.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")
