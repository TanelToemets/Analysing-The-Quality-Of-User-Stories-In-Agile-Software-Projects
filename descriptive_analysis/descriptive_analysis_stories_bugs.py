import pandas as pd
from matplotlib import pyplot
import matplotlib.ticker as ticker

#Possible projects
#xd 
#dnn
#compass 
#apstud
#mesos
#mule
#nexus
#timob
#tistud

projects = {
    "xd":      ("fields.issuetype.name",  "fields.status.name",                 "Done",      "jiradataset_issues.csv",       "project",     "fields.created"),
	"dnn":     ("fields.issuetype.name",  "fields.status.statusCategory.name",  "Done",      "jiradataset_issues.csv",       "project",     "fields.created"),
    "COMPASS": ("issuetype.name",         "status.statusCategory.name",         "Done",      "compass_issues_extracted.csv", "project.key", "created"       ),
	"apstud":  ("fields.issuetype.name",  "fields.status.statusCategory.name",  "Done",      "jiradataset_issues.csv",       "project",     "fields.created"),
    "mesos":   ("fields.issuetype.name",  "fields.status.statusCategory.name",  "Done",      "jiradataset_issues.csv",       "project",     "fields.created"),
    "mule":    ("fields.issuetype.name",  "fields.status.statusCategory.name",  "Complete",  "jiradataset_issues.csv",       "project",     "fields.created"),
    "nexus":   ("fields.issuetype.name",  "fields.status.statusCategory.name",  "Done",      "jiradataset_issues.csv",       "project",     "fields.created"),
    "timob":   ("fields.issuetype.name",  "fields.status.statusCategory.name",  "Done",      "jiradataset_issues.csv",       "project",     "fields.created"),
    "tistud":  ("fields.issuetype.name",  "fields.status.statusCategory.name",  "Done",      "jiradataset_issues.csv",       "project",     "fields.created"),
    "SLICE":   ("issuetype.name",         "status.name",         "Done",      "slice_issues_extracted.csv", "project.key",        "created"),
}

#print(projects["dnn"][1])

project_list = ['xd', 'dnn', 'COMPASS', 'apstud', 'mesos', 'mule', 'nexus', 'timob', 'tistud', 'SLICE']
for x in project_list:

    #Getting user story data
    df = pd.read_csv('C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/datasets/' + projects['{0}'.format(x)][3])

    #Selecting project
    df_project = df[df[projects['{0}'.format(x)][4]] == '{0}'.format(x)]

    #Filtering out only user stories that have been compleated
    DONE = ['Closed', 'Done', 'Resolved', 'Complete']
    project_initial = df_project[(df_project[projects['{0}'.format(x)][0]] == 'Story') & (df_project[projects['{0}'.format(x)][1]].isin(DONE))]

    #Number of stories before cleaning (including duplicates etc)
    print ("{0} {1} {2}".format(x, "Nr of stories before cleaning:", len(project_initial)))

    #Number of stories after cleaning
    project_cleaned = pd.read_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/cleaned_input_data/jira-{0}-allus-DS.csv".format(x), names=['key', 'identif', 'z'])
    project_cleaned = project_cleaned.drop_duplicates(subset=['key'])
    print ("{0} {1} {2}".format(x, "Nr of stories after cleaning:", len(project_cleaned)))

    #Number of bugs
    #Takeing only rows with issuetype Bug and status Done/Complete
    project_bugs = df_project[(df_project[projects['{0}'.format(x)][0]] == 'Bug') & (df_project[projects['{0}'.format(x)][1]].isin(DONE))] 
    #Removing duplicate bugs by issutype, statusCategory, creation time and key     
    project_bugs = project_bugs[[projects['{0}'.format(x)][0], projects['{0}'.format(x)][1], projects['{0}'.format(x)][5], 'key']].drop_duplicates()    
    print ("{0} {1} {2} {3}".format(x, "Nr of bugs:", len(project_bugs), "\n"))

