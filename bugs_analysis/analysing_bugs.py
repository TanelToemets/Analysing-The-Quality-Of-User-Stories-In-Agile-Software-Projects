import pandas as pd
from matplotlib import pyplot
import datetime as dt

project = "COMPASS"

projects = {
    "xd":      ("fields.issuetype.name",  "fields.status.name",                 "jiradataset_issues.csv",         "project",     "fields.created"),
	"dnn":     ("fields.issuetype.name",  "fields.status.statusCategory.name",  "jiradataset_issues.csv",         "project",     "fields.created"),
    "COMPASS": ("issuetype.name",         "status.statusCategory.name",         "compass_issues_extracted.csv",   "project.key", "created"       ),
	"apstud":  ("fields.issuetype.name",  "fields.status.statusCategory.name",  "jiradataset_issues.csv",         "project",     "fields.created"),
    "mesos":   ("fields.issuetype.name",  "fields.status.statusCategory.name",  "jiradataset_issues.csv",         "project",     "fields.created"),
    "mule":    ("fields.issuetype.name",  "fields.status.statusCategory.name",  "jiradataset_issues.csv",         "project",     "fields.created"),
    "nexus":   ("fields.issuetype.name",  "fields.status.statusCategory.name",  "jiradataset_issues.csv",         "project",     "fields.created"),
    "timob":   ("fields.issuetype.name",  "fields.status.statusCategory.name",  "jiradataset_issues.csv",         "project",     "fields.created"),
    "tistud":  ("fields.issuetype.name",  "fields.status.statusCategory.name",  "jiradataset_issues.csv",         "project",     "fields.created"),
}

#Reading the initial dataset
project_bugs = pd.read_csv('C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/datasets/'+projects['{0}'.format(project)][2])
#Selecting the project
project_bugs = project_bugs[project_bugs[projects['{0}'.format(project)][3]] == project]

#Taking only Bugs that have been Done/Compleated
DONE = ['Closed', 'Done', 'Resolved', 'Complete']
df = project_bugs[(project_bugs[projects['{0}'.format(project)][0]] == 'Bug') & (project_bugs[projects['{0}'.format(project)][1]].isin(DONE))]
print(len(df))

#Removing duplicates by issuetype, creation time, status and key
df2 = df[[projects['{0}'.format(project)][0], projects['{0}'.format(project)][4], projects['{0}'.format(project)][1], 'key']].drop_duplicates()

#Producing a input for furter WTLCC analysis
WTLCC_input = df2
WTLCC_input['bugnr'] = 1
WTLCC_input[['key','bugnr',projects['{0}'.format(project)][4]]].to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/WTLCC_input_data/{0}-bugs-for-WTLCC.csv".format(project), sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")

#Formating and indexing creationtime
df2[projects['{0}'.format(project)][4]] = pd.to_datetime(df2[projects['{0}'.format(project)][4]], utc=True)
df3 = df2.set_index(pd.DatetimeIndex(df2[projects['{0}'.format(project)][4]]))
df3['bugnr'] = 1

#Plotting bugs
fig = pyplot.figure()
df3.resample('SM')['bugnr'].sum().plot()
#df3['20150101':'20160101'].resample('W')['bugnr'].sum().plot()
#Fixing range for plot
pyplot.ylim(0, 60)
project_up = project.upper()
fig.suptitle(project_up, fontsize=20)
pyplot.xlabel('Time', fontsize=12)
pyplot.ylabel('Nr of bugs', fontsize=12)
pyplot.show()



