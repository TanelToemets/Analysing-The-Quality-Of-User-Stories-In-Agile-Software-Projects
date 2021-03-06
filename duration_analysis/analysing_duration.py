import pandas as pd
from matplotlib import pyplot
from matplotlib import dates
import datetime
import numpy as np
import matplotlib.ticker as plticker
import matplotlib.ticker as ticker

#Possible projects
#xd           +
#dnn          +
#COMPASS      +
#apstud       +
#mule         +
#nexus        +
#timob        +     
#tistud       +

project = "dnn"

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

#Identifing outliers using standart deviation
mean_duration_length = np.mean(duration_df['duration_in_days'])
standart_deviation_story_duration = np.std(duration_df['duration_in_days'])
duration_df['suitable_duration_length'] = duration_df['duration_in_days'].apply(lambda x: x if x < mean_duration_length + 1 * standart_deviation_story_duration else 0)
#Removing outliers
duration_df = duration_df[duration_df.suitable_duration_length != 0]
print(len(duration_df))

#formating datetime to date for plot readability
duration_df[projects['{0}'.format(project)][3]] = duration_df[projects['{0}'.format(project)][3]].dt.date


#Plotting duration
fig = pyplot.figure()
duration_df.resample('SM')['duration_in_days'].mean().ffill().plot()

#Adding titles and axis names
project_up = project.upper()
fig.suptitle(project_up, fontsize=20)
pyplot.xlabel('Time', fontsize=12)
pyplot.ylabel('Mean solving duration in days', fontsize=12)

pyplot.show()

duration_df.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")


#ALTERNATIVE PLOTS FOR DATA EXPLORATION
# #Plotting all user stories
# duration_df.plot(kind='bar', x=projects['{0}'.format(project)][3], y='duration_in_days')
# pyplot.xticks(rotation='vertical')
# pyplot.tight_layout()
# pyplot.gcf().autofmt_xdate()
# ax = pyplot.gca()
# ax.invert_xaxis()

# #Plotting stories over time
# fig = pyplot.figure()
# ax = fig.add_subplot(1,1,1)
# #ax.plot_date(duration_df['fields.created'], duration_df['duration_in_days'], "ro")
# ax.bar(duration_df[projects['{0}'.format(project)][3]], duration_df['duration_in_days'], width=2)
# fig.autofmt_xdate()

