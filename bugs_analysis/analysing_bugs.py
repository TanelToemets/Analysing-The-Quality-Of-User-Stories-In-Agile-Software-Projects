import pandas as pd
from matplotlib import pyplot
import datetime as dt

project = "tistud"

projects = {
    "xd":      ("fields.issuetype.name",  "fields.status.name",                 "Done",      "jiradataset_issues.csv",       "project",     "fields.created"),
	"dnn":     ("fields.issuetype.name",  "fields.status.statusCategory.name",  "Done",      "jiradataset_issues.csv",       "project",     "fields.created"),
    "COMPASS": ("issuetype.name",         "status.statusCategory.name",         "Done",      "compass_issues_extracted.csv", "project.key", "created"),
	"apstud":  ("fields.issuetype.name",  "fields.status.statusCategory.name",  "Done",      "jiradataset_issues.csv",       "project",     "fields.created"),
    "mesos":  ("fields.issuetype.name",  "fields.status.statusCategory.name",  "Complete",      "jiradataset_issues.csv",       "project",     "fields.created"),
    "mule":    ("fields.issuetype.name",  "fields.status.statusCategory.name",  "Complete",  "jiradataset_issues.csv",       "project",     "fields.created"),
    "nexus":   ("fields.issuetype.name",  "fields.status.statusCategory.name",  "Done",      "jiradataset_issues.csv",       "project",     "fields.created"),
    "timob":   ("fields.issuetype.name",  "fields.status.statusCategory.name",  "Done",      "jiradataset_issues.csv",       "project",     "fields.created"),
    "tistud":  ("fields.issuetype.name",  "fields.status.statusCategory.name",  "Done",      "jiradataset_issues.csv",       "project",      "fields.created"),
}

#Reading the initial dataset
project_bugs = pd.read_csv('C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/datasets/'+projects['{0}'.format(project)][3])
#Selecting the project
project_bugs = project_bugs[project_bugs[projects['{0}'.format(project)][4]] == project]

#Taking only Bugs that have been Done/Compleated
df = project_bugs[(project_bugs[projects['{0}'.format(project)][0]] == 'Bug') & (project_bugs[projects['{0}'.format(project)][1]] == projects['{0}'.format(project)][2])]
print(len(df))

#Removing duplicates by issuetype, creation time, status and key
df2 = df[[projects['{0}'.format(project)][0], projects['{0}'.format(project)][5], projects['{0}'.format(project)][1], 'key']].drop_duplicates()

#Formating and indexing creationtime
df2[projects['{0}'.format(project)][5]] = pd.to_datetime(df2[projects['{0}'.format(project)][5]], utc=True)
df3 = df2.set_index(pd.DatetimeIndex(df2[projects['{0}'.format(project)][5]]))
df3['bugnr'] = 1

#Plotting bugs
df3.resample('W')['bugnr'].sum().plot()
#df3['20150101':'20160101'].resample('W')['bugnr'].sum().plot()
pyplot.show()



