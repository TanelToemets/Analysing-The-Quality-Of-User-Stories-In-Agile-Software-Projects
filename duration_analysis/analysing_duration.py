import pandas as pd
from matplotlib import pyplot
import datetime
import numpy as np

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

project = "COMPASS"

projects = {
    "xd":           ("fields.resolutiondate",  "key", "project",      "fields.created", "jiradataset_issues.csv"), 
    "dnn":          ("fields.resolutiondate",  "key", "project",      "fields.created", "jiradataset_issues.csv"),
    "COMPASS":      ("resolutiondate",         "key", "project.name", "created",        "compass_issues_extracted.csv"), 
    "apstud":       ("fields.resolutiondate",  "key", "project",      "fields.created", "jiradataset_issues.csv"), 
    "mesos":        ("fields.resolutiondate",  "key", "project",      "fields.created", "jiradataset_issues.csv"), 
    "mule":         ("fields.resolutiondate",  "key", "project",      "fields.created", "jiradataset_issues.csv"), 
    "nexus":        ("fields.resolutiondate",  "key", "project",      "fields.created", "jiradataset_issues.csv"),  
    "timob":        ("fields.resolutiondate",  "key", "project",      "fields.created", "jiradataset_issues.csv"), 
    "tistud":       ("fields.resolutiondate",  "key", "project",      "fields.created", "jiradataset_issues.csv"), 	
}

#Read cleaned stories
stories_df = pd.read_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/cleaned_input_data/jira-{0}-allus-DS.csv".format(project), names=['title', 'key', 'identif', 'z'])
stories_df = stories_df[stories_df['identif'] == 0]
stories_df = stories_df.drop_duplicates(subset=['key'])
print(len(stories_df))

#Read fields.resolution.name from initial data
initial_data = pd.read_csv('C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/datasets/'+projects['{0}'.format(project)][4], usecols = [projects['{0}'.format(project)][1], projects['{0}'.format(project)][0], projects['{0}'.format(project)][3]])
print(len(initial_data))

#Merge stories with creationdate and resolutiondate
duration_df = pd.merge(stories_df, initial_data, how='left', left_on='key', right_on='key')
print(len(duration_df))

#Remove duplicates
duration_df = duration_df.drop_duplicates(subset='key', keep="first")
print(len(duration_df))

#Format dates
duration_df[projects['{0}'.format(project)][0]] = pd.to_datetime(duration_df[projects['{0}'.format(project)][0]], utc=True)
duration_df[projects['{0}'.format(project)][3]] = pd.to_datetime(duration_df[projects['{0}'.format(project)][3]], utc=True)

#Finding duration between resolutiondate and creationdate
duration_df['duration_in_days'] = (duration_df[projects['{0}'.format(project)][0]] - duration_df[projects['{0}'.format(project)][3]]).dt.days

#Indexing creationdate
duration_df = duration_df.set_index(pd.DatetimeIndex(duration_df[projects['{0}'.format(project)][3]]))

#Plotting duration
duration_df.plot(kind='bar', x=projects['{0}'.format(project)][3], y='duration_in_days')
pyplot.xticks(rotation='vertical')
pyplot.show()

duration_df.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")
