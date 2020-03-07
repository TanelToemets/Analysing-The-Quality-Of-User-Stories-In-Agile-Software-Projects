import pandas as pd
from matplotlib import pyplot
import matplotlib.ticker as ticker

#Possible projects
#xd 
#dnn
#compass #failed
#apstud
#mesos #failed
#mule
#nexus #failed
#timob
#tistud

projects = {
    "xd": ("fields.issuetype.name", "fields.status.name", "Done", "jiradataset_issues.csv", "project"),
	"dnn": ("fields.issuetype.name", "fields.status.statusCategory.name", "Done", "jiradataset_issues.csv", "project"),
    "COMPASS": ("issuetype.name", "status.statusCategory.name", "Done", "compass_issues_extracted.csv", "project.key"),
	"apstud": ("fields.issuetype.name", "fields.status.statusCategory.name", "Done", "jiradataset_issues.csv", "project"),
    "mule": ("fields.issuetype.name", "fields.status.statusCategory.name", "Complete", "jiradataset_issues.csv", "project"),
    "timob": ("fields.issuetype.name", "fields.status.statusCategory.name", "Done", "jiradataset_issues.csv", "project"),
    "tistud": ("fields.issuetype.name", "fields.status.statusCategory.name", "Done", "jiradataset_issues.csv", "project"),
}

#print(projects["dnn"][1])

project_list = ['xd', 'dnn', 'COMPASS', 'apstud', 'mule', 'timob', 'tistud']
for x in project_list:

    #Getting user story data
    df = pd.read_csv('C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/datasets/' + projects['{0}'.format(x)][3])

    #Selecting project
    df_project = df[df[projects['{0}'.format(x)][4]] == '{0}'.format(x)]

    #Filtering out only user stories that have been compleated
    project_initial = df_project[(df_project[projects['{0}'.format(x)][0]] == 'Story') & (df_project[projects['{0}'.format(x)][1]] == projects['{0}'.format(x)][2])]

    #Number of stories before cleaning (including duplicates etc)
    print ("{0} {1} {2}".format(x, "Nr of stories before cleaning:", len(project_initial)))

    #Number of stories after cleaning
    project_cleaned = pd.read_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/cleaned_input_data/jira-{0}-allus.csv".format(x), names=['title', 'key', 'z'])
    print ("{0} {1} {2} {3}".format(x, "Nr of stories after cleaning:", len(project_cleaned), "\n"))

    #TO BE COMPLETED: Number of bugs


