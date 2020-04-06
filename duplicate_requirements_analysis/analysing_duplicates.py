import pandas as pd
from matplotlib import pyplot
import datetime

#Possible projects
#xd           +
#dnn          +
#COMPASS      +
#apstud       +
#mule         +
#nexus        +
#timob        +       
#tistud       +

project = "tistud"

projects = {
    "xd":           ("fields.resolution.name",  "key", "project",      "fields.created", "jiradataset_issues.csv"), 
    "dnn":          ("fields.resolution.name",  "key", "project",      "fields.created", "jiradataset_issues.csv"),
    "COMPASS":      ("resolution.name",         "key", "project.name", "created",        "compass_issues_extracted.csv"), 
    "apstud":       ("fields.resolution.name",  "key", "project",      "fields.created", "jiradataset_issues.csv"), 
    "mule":         ("fields.resolution.name",  "key", "project",      "fields.created", "jiradataset_issues.csv"), 
    "nexus":        ("fields.resolution.name",  "key", "project",      "fields.created", "jiradataset_issues.csv"),  
    "timob":        ("fields.resolution.name",  "key", "project",      "fields.created", "jiradataset_issues.csv"), 
    "tistud":       ("fields.resolution.name",  "key", "project",      "fields.created", "jiradataset_issues.csv"), 	
}

#Read cleaned stories
stories_df = pd.read_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/cleaned_input_data/jira-{0}-allus-DS.csv".format(project), names=['title', 'key', 'identif', 'z'])
stories_df = stories_df[stories_df['identif'] == 0]
stories_df = stories_df.drop_duplicates(subset=['key'])
print(len(stories_df))

#Read fields.resolution.name from initial data
initial_data = pd.read_csv('C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/datasets/'+projects['{0}'.format(project)][4], usecols = [projects['{0}'.format(project)][0],projects['{0}'.format(project)][1], projects['{0}'.format(project)][2], projects['{0}'.format(project)][3]])
print(len(initial_data))

#Merge stories and fields.resolution.name
duplicates_df = pd.merge(stories_df, initial_data, how='left', left_on='key', right_on='key')
print(len(duplicates_df))

#Filtering out duplicate requirements
duplicates_df = duplicates_df[duplicates_df[projects['{0}'.format(project)][0]] == 'Duplicate']
print(len(duplicates_df))

#Remove duplicates
duplicates_df = duplicates_df.drop_duplicates(subset='key', keep="first")
print(len(duplicates_df))

#Printing nr of deplicate requirements
print ("{0} {1} {2}".format(project, "Nr of duplicate requirements:", len(duplicates_df)))

#Formating and indexing creationdate
duplicates_df[projects['{0}'.format(project)][3]] = pd.to_datetime(duplicates_df[projects['{0}'.format(project)][3]], utc=True)
duplicates_df = duplicates_df.set_index(pd.DatetimeIndex(duplicates_df[projects['{0}'.format(project)][3]]))

#Plotting duplicates
fig = pyplot.figure()
duplicates_df['duplicate_nr'] = 1/len(stories_df)
duplicates_df.resample('SM')['duplicate_nr'].sum().plot()
project_up = project.upper()
fig.suptitle(project_up, fontsize=20)
pyplot.xlabel('Time', fontsize=12)
pyplot.ylabel('Percentage of all stories', fontsize=12)
pyplot.show()

duplicates_df.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")

