import pandas as pd
from matplotlib import pyplot
import datetime as dt

project = "nexus"

projects = {
    "xd":      ("fields.issuetype.name",  "fields.status.name",                 "Done",      "jiradataset_issues.csv",       "project",     "fields.created"),
	"dnn":     ("fields.issuetype.name",  "fields.status.statusCategory.name",  "Done",      "jiradataset_issues.csv",       "project",     "fields.created"),
    #"COMPASS": ("issuetype.name",         "status.statusCategory.name",         "Done",      "compass_issues_extracted.csv", "project.key", "created"),
	"apstud":  ("fields.issuetype.name",  "fields.status.statusCategory.name",  "Done",      "jiradataset_issues.csv",       "project",     "fields.created"),
    #"mesos":  ("fields.issuetype.name",  "fields.status.statusCategory.name",  "Done",      "jiradataset_issues.csv",       "project",     "fields.created"),
    #"mule":    ("fields.issuetype.name",  "fields.status.statusCategory.name",  "Complete",  "jiradataset_issues.csv",       "project",     "fields.created"),
    "nexus":   ("fields.issuetype.name",  "fields.status.statusCategory.name",  "Done",      "jiradataset_issues.csv",       "project",     "fields.created"),
    "timob":   ("fields.issuetype.name",  "fields.status.statusCategory.name",  "Done",      "jiradataset_issues.csv",       "project",     "fields.created"),
    #"tistud":  ("fields.issuetype.name",  "fields.status.statusCategory.name",  "Done",      "jiradataset_issues.csv",       "project",      "fields.created"),
}

xd = pd.read_csv('C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/datasets/jiradataset_issues.csv')
xd = xd[xd['project'] == project]

df = xd[(xd[projects['{0}'.format(project)][0]] == 'Bug') & (xd[projects['{0}'.format(project)][1]] == 'Done')]
print(len(df))


df2 = df[[projects['{0}'.format(project)][0], projects['{0}'.format(project)][5], projects['{0}'.format(project)][1], 'key']].drop_duplicates()

df2[projects['{0}'.format(project)][5]] = pd.to_datetime(df2[projects['{0}'.format(project)][5]], utc=True)
df3 = df2.set_index(pd.DatetimeIndex(df2[projects['{0}'.format(project)][5]]))
df3['bugnr'] = 1

df3.resample('W')['bugnr'].sum().plot()
#df3['20150101':'20160101'].resample('W')['bugnr'].sum().plot()
pyplot.show()



