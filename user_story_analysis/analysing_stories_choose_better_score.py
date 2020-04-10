import pandas as pd
from matplotlib import pyplot
import numpy as np
import datetime
import statsmodels.api as sm
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.graphics.tsaplots import plot_pacf
from pandas.plotting import autocorrelation_plot

#Possible projects
#xd 
#dnn
#COMPASS
#apstud
#mesos -> excluded from analysis because of not enough stories
#mule
#nexus
#timob
#tistud

project = "tistud"

projects = {
    "xd":      ("fields.issuetype.name",  "fields.status.name",                 "Done",      "jiradataset_issues.csv",        "project",    "fields.created"),
	"dnn":     ("fields.issuetype.name",  "fields.status.statusCategory.name",  "Done",      "jiradataset_issues.csv",        "project",    "fields.created"),
    "COMPASS": ("issuetype.name",         "status.statusCategory.name",         "Done",      "compass_issues_extracted.csv",  "project.key", "created"),
	"apstud":  ("fields.issuetype.name",  "fields.status.statusCategory.name",  "Done",      "jiradataset_issues.csv",        "project",     "fields.created"),
    "mesos":   ("fields.issuetype.name",  "fields.status.statusCategory.name",  "Done",      "jiradataset_issues.csv",        "project",     "fields.created"),
    "mule":    ("fields.issuetype.name",  "fields.status.statusCategory.name",  "Complete",  "jiradataset_issues.csv",        "project",     "fields.created"),
    "nexus":   ("fields.issuetype.name",  "fields.status.statusCategory.name",  "Done",      "jiradataset_issues.csv",        "project",     "fields.created"),
    "timob":   ("fields.issuetype.name",  "fields.status.statusCategory.name",  "Done",      "jiradataset_issues.csv",        "project",     "fields.created"),
    "tistud":  ("fields.issuetype.name",  "fields.status.statusCategory.name",  "Done",      "jiradataset_issues.csv",        "project",     "fields.created"),
}

#Read the stories (AQUSA input)
#title - the text of user story
#key - unique identifier of user story
#identif - text source identifier, description is 0 and summary is 1
stories_project = pd.read_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/cleaned_input_data/jira-{0}-allus-DS.csv".format(project), names=['title', 'key', 'identif', 'z'])
print(len(stories_project))

#Read the quality (AQUSA output)
quality_project = pd.read_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/analyzed_output_data/{0}-quality-allus-DS.csv".format(project))
print(len(quality_project))

#Merge story keys and quality issues
quality_df = pd.merge(stories_project, quality_project, how='left', left_on='title', right_on='title')
print(len(quality_df))

#Adding source identifier to story key
quality_df['identif_key'] = quality_df['identif'].apply(str) + '+' + quality_df['key']

#Calculating the length of the text
df_text = quality_df[['identif_key', 'title', 'role', 'means', 'ends']].drop_duplicates()
print(len(df_text))

def manage_nullvalues(current_column, len_column):
    if (pd.isnull(df_text[current_column]).all()):
        df_text[len_column] = 0
    else:
        df_text[len_column] = df_text[current_column].str.len()    

manage_nullvalues('title', 'text_len')
manage_nullvalues('role', 'role_len')
manage_nullvalues('means', 'means_len')
manage_nullvalues('ends', 'ends_len')

df_text = df_text.drop(['title', 'role', 'means', 'ends'], axis=1)
df_text = df_text.fillna(0)

#Quantifying the quality
quality_df["penalty"] = quality_df["severity"].apply(lambda x: 1/6 if x == "high" else 1/12 if x == "minor" else 1/9 if x =="medium" else 0)

#Tagging if there is high, medium or minor errors
quality_df["high"] = quality_df["severity"].apply(lambda x: 1 if x == "high" else 0)
quality_df["minor"] = quality_df["severity"].apply(lambda x: 1 if x == "minor" else 0)
quality_df["medium"] = quality_df["severity"].apply(lambda x: 1 if x == "medium" else 0)

#Grouping the data using key field and summarising the penalties and the number of errors.
q = quality_df[["identif_key", "penalty", "high", "minor", "medium"]].groupby(['identif_key']).sum()
q = q.reset_index()


#Adding kind and subkind and creating table presenting all issues
qc = quality_df[["identif_key", "kind", "subkind"]].groupby(['identif_key', "kind", "subkind"]).count()
qc = qc.reset_index()

qc.index = qc["identif_key"]
dummies = pd.get_dummies(qc[["kind", "subkind"]])
dummies = dummies.reset_index()
dummies = dummies.groupby(['identif_key']).sum()

qj = q.join(dummies, on="identif_key")

#Split source identifier and story key
qj[['identif','key']] = qj['identif_key'].str.split("+",expand=True) 

#Calculating the total quality Q = 1 - P
qj["quality"] = 1 - qj["penalty"]

#Sorting values, from highest value to lowest
qj = qj.sort_values('quality', ascending=False)
#qj.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")

#Removing duplicates to keep ones only the ones with higher value
qj = qj.drop_duplicates(subset='key', keep='first')
#df_text.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test2.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")

#Mergeing text and quality dataframes
quality_df = pd.merge(df_text, qj, on='identif_key')
quality_df = quality_df.fillna(0)

#Merging the data from initial dataset (dates and quality scores)
initial_dataset = pd.read_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/datasets/"+projects['{0}'.format(project)][3] )
initial_dataset = initial_dataset[initial_dataset[projects['{0}'.format(project)][4]] == '{0}'.format(project)]

print(len(quality_df))
quality = pd.merge(initial_dataset[["key", projects['{0}'.format(project)][5]]], quality_df, on='key', how='outer')
quality = quality[quality.quality.notnull()]

#Writing keys and quality scores to csv
quality_scores = quality.drop_duplicates(subset='key', keep="first")
quality_scores[["key", "quality", projects['{0}'.format(project)][5]]].to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/quality_scores_data/{0}-quality-scores.csv".format(project), sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")

#Formating datetime and indexing. Needed for resampling
quality['fields.created'] = pd.to_datetime(quality[projects['{0}'.format(project)][5]], utc=True)
quality = quality.set_index(pd.DatetimeIndex(quality[projects['{0}'.format(project)][5]]))


#PLOTTING QUALITY BY TWO WEEKS
# #SM --> semi month (15th and end of month)
# #W  --> week
# #Q  --> quarter
# #Y  --> year
fig = pyplot.figure()
quality.resample('SM')['quality'].mean().ffill().plot()
#quality.resample('SM')['quality'].mean().plot()
#quality['20150101':'20160101'].resample('SM')['quality'].mean().plot()
project_up = project.upper()
fig.suptitle(project_up, fontsize=20)
pyplot.xlabel('Quality', fontsize=12)
pyplot.ylabel('Creation time', fontsize=12)
pyplot.show()

#Alternative
# pyplot.plot(quality[projects['{0}'.format(project)][5]],quality['quality'])
# pyplot.gcf().autofmt_xdate()
# pyplot.show()

def manage_compass_field_names(quality, project):
    if project == 'COMPASS':
        quality = quality.rename(columns={'created': 'field.created'})
        return quality
    else:
        return quality

quality = manage_compass_field_names(quality, project)


# #TIME SERIES ANAYSIS
# #Analysing base leve, trend, seasonality and error
#quality = quality['20130101':'20140101']
time_series_df = quality[['fields.created', 'quality']]
#Removing outliers
time_series_df = time_series_df[time_series_df['quality'] > 0]
#Indexing date
time_series_df = time_series_df.set_index('fields.created')
#Decomposing timeseries. freq is the number of days I am considering
#multiplicative or additive
decomposition = sm.tsa.seasonal_decompose(time_series_df, freq=7, model = 'additive')
#Plotting
result = decomposition.plot()
#reversing x axis
ax=pyplot.gca()
ax.invert_xaxis()
#pyplot.rcParams['figure.figsize'] = [9.0, 5.0]
pyplot.show()



#AUTOCORRELATION & PARTIAL-AUTOCORREALTION
correlation_df = quality[['fields.created', 'quality']]
correlation_df = correlation_df.set_index('fields.created')

#autocorrelation plot for testing seasonality in timeseries
autocorrelation_plot(correlation_df['quality'].tolist())

#autocorrelation plot
plot_acf(correlation_df)
pyplot.show()

#partial-autocorrelation plot
plot_pacf(correlation_df)
pyplot.show()

# #TEST
# #time_series_df.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")






















































































# #FINDING CROSS-CORRELATION WITH NR OF BUGS
# #Reading the initial dataset
# project_bugs = pd.read_csv('C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/datasets/'+projects['{0}'.format(project)][3])
# #Selecting the project
# project_bugs = project_bugs[project_bugs[projects['{0}'.format(project)][4]] == project]
# #Taking only Bugs that have been Done/Compleated
# DONE = ['Closed', 'Done', 'Resolved', 'Complete']
# df = project_bugs[(project_bugs[projects['{0}'.format(project)][0]] == 'Bug') & (project_bugs[projects['{0}'.format(project)][1]].isin(DONE))]
# print(len(df))
# #Removing duplicates by issuetype, creation time, status and key
# df2 = df[[projects['{0}'.format(project)][0], projects['{0}'.format(project)][5], projects['{0}'.format(project)][1], 'key']].drop_duplicates()
# #Formating and indexing creationtime
# df2[projects['{0}'.format(project)][5]] = pd.to_datetime(df2[projects['{0}'.format(project)][5]], utc=True)
# #df2 = df2.set_index(pd.DatetimeIndex(df2[projects['{0}'.format(project)][5]]))

# #adding bugnr to be able to count later
# df2['bugnr'] = 1
# #renaming to make naming same for all projects
# df2 = df2.rename(columns={projects['{0}'.format(project)][5]: 'fields.created'})
# df2 = df2[['fields.created', 'bugnr']]
# #df2.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test2.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")

# #counting nr of bugs by day
# #crosscorr_bugs_df = df2['bugnr'].groupby(df2['fields.created'].dt.to_period('D')).sum().reset_index()
# crosscorr_bugs_df = df2.groupby(['fields.created']).sum().reset_index()

# #crosscorr_bugs_df.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")

# #finding cross-correlation between nr of bugs and user story quality
# crosscorr_quality_df = quality[['fields.created', 'quality']]
# crosscorr_bugs_df = crosscorr_bugs_df[['fields.created', 'bugnr']]
# crosscorr_bugs_df = crosscorr_bugs_df.set_index(pd.DatetimeIndex(crosscorr_bugs_df['fields.created']))

# print(len(crosscorr_bugs_df))
# crosscorr_bugs_df = crosscorr_bugs_df[:516] #For tring
# print(len(crosscorr_bugs_df))
# print(len(crosscorr_quality_df))

# #FIRST TRY WITH PANDAS
# crosscorr_quality_df.apply(crosscorr_bugs_df['bugnr'].corr).plot()
# pyplot.show()

# #SECOND TRY WITH NUMPYS
# np.correlate(crosscorr_bugs_df['bugnr'].to_numpy(),crosscorr_quality_df['quality'].to_numpy(),"full")
# pyplot.show()

