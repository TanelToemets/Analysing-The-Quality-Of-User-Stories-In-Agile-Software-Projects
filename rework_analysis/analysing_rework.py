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
#xd           -
#dnn          +
#COMPASS      -
#apstud       +
#mesos        +
#mule         +
#nexus        +
#timob        +       
#tistud       +
project = 'dnn'

projects = {
    "xd":      ("Done",  "In Progress" ), #65 Currently only Done -> In Progress ||Other: In Progress -> In PR | In Progress -> To Do | In PR -> In Progress | In PR -> To Do
	"dnn":     ("XXXX", "Reopened"     ), #128 | Fine
    "COMPASS": ("XXXX", "XXXX"         ), #NO DATA 
	"apstud":  ("XXXX", "Reopened"     ), #49  |#Many are going from a Closed to Closed? | Otherwise fine
    "mesos":   ("XXXX", "Reopened"     ), #0   |Reopened state exists but none of the stories we are analysing have this state 
    "mule":    ("Closed", "Reopened"   ), #4   | Fine
    "nexus":   ("XXXX", "XXXX"         ), #0   |Reopened state and Closed->Open states exists but none of the stories we are analysing have this state 
    "timob":   ("Closed", "Reopened"   ), #7   |#Two are going from a Closed to Closed?  | Otherwise fine
    "tistud":  ("Closed", "Reopened"   ), #178 |#Many are going from a Closed to Closed? | Otherwise fine
}

#Read changelog file for rework data
changelog_df = pd.read_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/datasets/jiradataset_changelog.csv")
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
rework_df = rework_df[rework_df['toString'] == projects['{0}'.format(project)][1]]

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
rework_df.resample('SM')['rework_nr'].sum().plot()
pyplot.show()

#rework_df.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")
