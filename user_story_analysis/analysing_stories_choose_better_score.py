import pandas as pd
from matplotlib import pyplot
import matplotlib
import numpy as np
import datetime
import statsmodels.api as sm
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.graphics.tsaplots import plot_pacf
from pandas.plotting import autocorrelation_plot
import warnings
import itertools
warnings.filterwarnings("ignore")
pyplot.style.use('fivethirtyeight')


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

project = "COMPASS"

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


# #PLOTTING QUALITY BY TWO WEEKS
# # #SM --> semi month (15th and end of month)
# # #W  --> week
# # #Q  --> quarter
# # #Y  --> year
# fig = pyplot.figure()
# quality.resample('SM')['quality'].mean().ffill().plot()
# #quality.resample('SM')['quality'].mean().plot()
# #quality['20150101':'20160101'].resample('SM')['quality'].mean().plot()
# project_up = project.upper()
# fig.suptitle(project_up, fontsize=20)
# pyplot.xlabel('Quality', fontsize=12)
# pyplot.ylabel('Creation time', fontsize=12)
# pyplot.show()

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




##TIME SERIES ANAYSIS - FORECASTING

#DATA PREPROCESSING
#quality = quality['20130101':'20140101']
time_series_df = quality[['fields.created', 'quality']]
#Removing outliers
time_series_df = time_series_df[time_series_df['quality'] > 0]
#Indexing date
time_series_df = time_series_df.set_index('fields.created')
time_series_df.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test2.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")
time_series_df.resample('SM')['quality'].mean().ffill().plot()
pyplot.show()
time_series_df = time_series_df.resample('SM')['quality'].mean().ffill()


##DECOMPOSING TIMESERIES
# Analysing base level, trend, seasonality and error
# freq is the number of days I am considering # multiplicative or additive
decomposition = sm.tsa.seasonal_decompose(time_series_df, freq=7, model = 'additive')
#Plotting decomposition
result = decomposition.plot()
#reversing x axis
# ax=pyplot.gca()
# ax.invert_xaxis()
#pyplot.rcParams['figure.figsize'] = [9.0, 5.0]
pyplot.show()

#ARIMA (Autoregressive Integrated Moving Average)
#reference: https://towardsdatascience.com/an-end-to-end-project-on-time-series-analysis-and-forecasting-with-python-4835e6bf050b
p = d = q = range(0, 2)
pdq = list(itertools.product(p, d, q))
seasonal_pdq = [(x[0], x[1], x[2], 12) for x in list(itertools.product(p, d, q))]

#Performing "Grid search” to find the optimal set of parameters that yields the best performance for our model
for param in pdq:
    for param_seasonal in seasonal_pdq:
        try:
            mod = sm.tsa.statespace.SARIMAX(time_series_df,
                                            order=param,
                                            seasonal_order=param_seasonal,
                                            enforce_stationarity=False,
                                            enforce_invertibility=False)

            results = mod.fit()
            print('ARIMA{}x{}12 - AIC:{}'.format(param, param_seasonal, results.aic))
        except:
            continue

#Fitting the ARIMA model
mod = sm.tsa.statespace.SARIMAX(time_series_df,
                                order=(1, 1, 1),
                                seasonal_order=(1, 1, 0, 12),
                                enforce_stationarity=False,
                                enforce_invertibility=False)
results = mod.fit()
print(results.summary().tables[1])

results.plot_diagnostics(figsize=(16, 8))
pyplot.show()

#xd first date in 2015 is 2015-01-04T09:29:27.000+0000
# results = results.tz_localize(None)
# time_series_df = time_series_df.tz_localize(None)

#pred = results.get_prediction(start=pd.to_datetime('2015-01-04 00:00:00'), dynamic=False)
# pred = results.get_prediction(start=200)
# pred_ci = pred.conf_int()
# ax = time_series_df['2013':].plot(label='observed')
# pred.predicted_mean.plot(ax=ax, label='One-step ahead Forecast', alpha=.7, figsize=(14, 7))
# ax.fill_between(pred_ci.index,
#                 pred_ci.iloc[:, 0],
#                 pred_ci.iloc[:, 1], color='k', alpha=.2)
# ax.set_xlabel('Date')
# ax.set_ylabel('Furniture Sales')
# pyplot.legend()
# pyplot.show()

pred_uc = results.get_forecast(steps=100)
pred_ci = pred_uc.conf_int()
ax = time_series_df.plot(label='observed', figsize=(14, 7))
pred_uc.predicted_mean.plot(ax=ax, label='Forecast')
ax.fill_between(pred_ci.index,
                pred_ci.iloc[:, 0],
                pred_ci.iloc[:, 1], color='k', alpha=.25)
ax.set_xlabel('Date')
ax.set_ylabel('User Story quality')
pyplot.legend()
pyplot.show()








































































# #AUTOCORRELATION & PARTIAL-AUTOCORREALTION
# correlation_df = quality[['fields.created', 'quality']]
# correlation_df = correlation_df.set_index('fields.created')

# #autocorrelation plot for testing seasonality in timeseries
# autocorrelation_plot(correlation_df['quality'].tolist())

# #autocorrelation plot
# plot_acf(correlation_df)
# pyplot.show()

# #partial-autocorrelation plot
# plot_pacf(correlation_df)
# pyplot.show()

# # #TEST
# # #time_series_df.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")

