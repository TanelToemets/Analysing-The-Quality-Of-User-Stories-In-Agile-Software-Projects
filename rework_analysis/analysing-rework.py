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
#mesos        -
#mule         +
#nexus        -
#timob        +       
#tistud       +
project = 'tistud'

#Read changelog file for rework data
changelog_df = pd.read_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/datasets/jiradataset_changelog.csv")
print(len(changelog_df))

#Read the stories
stories_df = pd.read_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/cleaned_input_data/jira-{0}-allus.csv".format(project), names=['title', 'key', 'z'])
print(len(stories_df))

#Merge story keys and rework data
rework_df = pd.merge(stories_df, changelog_df, how='left', left_on='key', right_on='key')
print(len(rework_df))

#Selecting the project
rework_df = rework_df[rework_df['field'] == 'status']

#Selecting only Reopened stories
rework_df = rework_df[rework_df['toString'] == 'Reopened']

#Formating and indexing creationtime
rework_df['created'] = pd.to_datetime(rework_df['created'], utc=True)
rework_df = rework_df.set_index(pd.DatetimeIndex(rework_df['created']))
rework_df['rework_nr'] = 1

#Printing nr of rework cases
print ("{0} {1} {2}".format(project, "Nr of rework cases:", len(rework_df)))

#Plotting
rework_df.resample('W')['rework_nr'].sum().plot()
pyplot.show()

rework_df.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")
