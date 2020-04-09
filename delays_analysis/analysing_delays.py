import pandas as pd
from matplotlib import pyplot
import datetime

#Possible projects
#xd           +
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
    "xd":      ("jiradataset_issues.csv"         ),
	"dnn":     ("jiradataset_issues.csv"         ),
    "COMPASS": ("compass_issues_extracted.csv"   ),
	"apstud":  ("jiradataset_issues.csv"         ),
    "mule":    ("jiradataset_issues.csv"         ), 
    "nexus":   ("jiradataset_issues.csv"         ), 
    "timob":   ("jjiradataset_issues.csv"         ), 
    "tistud":  ("jiradataset_issues.csv"         ), 
}

#Read sprints file
sprints_df = pd.read_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/datasets/jiradataset_sprints.csv")
print(len(sprints_df))

#Read cleaned stories
stories_df = pd.read_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/cleaned_input_data/jira-{0}-allus-DS.csv".format(project), names=['title', 'key', 'identif', 'z'])
stories_df = stories_df[stories_df['identif'] == 0]
stories_df = stories_df.drop_duplicates(subset=['key'])
print(len(stories_df))

#Merge story keys and sprints data
story_sprint_df = pd.merge(stories_df, sprints_df, how='left', left_on='key', right_on='key')
print(len(story_sprint_df))

#Read resolutiondate from initial data
# initial_data = pd.read_csv('C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/datasets/jiradataset_issues.csv', usecols = ['fields.resolutiondate','key', 'project'])
# initial_data = initial_data[initial_data['project'] == project]
# print(len(initial_data))


def manage_initial_data(project):
    if project == 'COMPASS':
        initial_data = pd.read_csv('C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/datasets/compass_issues_extracted.csv', usecols = ['resolutiondate','key', 'project.key'])
        initial_data = initial_data.rename(columns={'resolutiondate': 'fields.resolutiondate'})
        initial_data = initial_data.rename(columns={'project.key': 'project'})
        initial_data = initial_data[initial_data['project'] == project]
        print(len(initial_data))
        print('compass managed')
        return initial_data
    else:
        initial_data = pd.read_csv('C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/datasets/jiradataset_issues.csv', usecols = ['fields.resolutiondate','key', 'project'])
        initial_data = initial_data[initial_data['project'] == project]
        print(len(initial_data))
        print('project managed')
        return initial_data

initial_data = manage_initial_data(project)



#Merge resolutiondates, sprints and story data
delays_df = pd.merge(story_sprint_df, initial_data, how='left', left_on='key', right_on='key')
print(len(delays_df))

#format dates
delays_df['fields.resolutiondate'] = pd.to_datetime(delays_df['fields.resolutiondate'], utc=True)
delays_df['sprint.endDate'] = pd.to_datetime(delays_df['sprint.endDate'], utc=True)
#df = df.apply(pd.to_datetime, errors='ignore')

#Compare endDate and resolutiondate
delays_df = delays_df.loc[delays_df['sprint.endDate'] < delays_df['fields.resolutiondate']]
print(len(delays_df))

#Remove duplicates
delays_df = delays_df.drop_duplicates(subset='key', keep="first")

#Indexing resolutiondate
delays_df = delays_df.set_index(pd.DatetimeIndex(delays_df['fields.resolutiondate']))

#Printing nr of stories that needed rework
print ("{0} {1} {2}".format(project, "Nr of stories that had delays:", len(delays_df)))
#Calculating overal percentage of delayd stories
overal_percentage_of_delayd_stories = (len(delays_df)/len(stories_df))*100
print("{0} {1}".format("Overal percentage of delayd stories", overal_percentage_of_delayd_stories))

#Plotting delays
fig = pyplot.figure()
delays_df['delay_nr'] = 1/len(stories_df)
delays_df.resample('SM')['delay_nr'].sum().plot()
project_up = project.upper()
fig.suptitle(project_up, fontsize=20)
pyplot.xlabel('Time', fontsize=12)
pyplot.ylabel('Percentage of all stories', fontsize=12)
pyplot.show()

delays_df.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test2.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")
