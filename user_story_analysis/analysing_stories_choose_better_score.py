import pandas as pd
from matplotlib import pyplot
import matplotlib
import numpy as np
import datetime
import statsmodels.api as sm
from statsmodels.tsa.seasonal import seasonal_decompose
from dateutil.parser import parse
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.graphics.tsaplots import plot_pacf
from pandas.plotting import autocorrelation_plot
import warnings
import itertools
import pmdarima as pm
from statsmodels.tsa.stattools import acf
from statsmodels.tsa.stattools import adfuller
warnings.filterwarnings("ignore")
pyplot.style.use('fivethirtyeight')


#Possible projects
#xd 
#dnn
#COMPASS
#apstud
#mule
#nexus
#timob
#tistud
#mesos -> excluded from analysis because of not enough stories

project = "xd"

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
#identif - text source field identifier, description is 0 and summary is 1
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


def choose_active_development_periods(quality, project):
    if project == 'dnn':
        quality = quality['20130701':'20160101']
        return quality
    elif project == 'COMPASS':
        quality = quality[['fields.created', 'quality']]
        quality = quality.reset_index(drop=True)
        quality = quality[(quality['fields.created'] > '2017-09-20') & (quality['fields.created'] < '2018-09-01')]
        quality = quality.set_index('fields.created')
        print(quality)
        return quality
    elif project == 'apstud':
        print(quality)
        quality = quality[['fields.created', 'quality']]
        quality = quality.reset_index(drop=True)
        quality = quality[(quality['fields.created'] > '2011-06-08') & (quality['fields.created'] < '2012-06-20')]
        quality = quality.set_index('fields.created')
        return quality
    elif project == 'mule':
        quality = quality[['fields.created', 'quality']]
        quality = quality.reset_index(drop=True)
        quality = quality[(quality['fields.created'] > '2013-01-01') & (quality['fields.created'] < '2014-09-01')]
        quality = quality.set_index('fields.created')
        return quality
    elif project == 'nexus':
        quality = quality['20140901':'20150401']
        return quality
    elif project == 'tistud':
        quality = quality['20110101':'20140801']
        return quality    
    else:
        return quality

quality = choose_active_development_periods(quality, project)
# quality = quality.drop_duplicates()
# print('nr of stories during active development period')
# print(len(quality))
# #print(quality)

# #PLOTTING QUALITY OVER TWO WEEKS
# #Below is a list of resampling possibilities
# #SM --> semi month (15th and end of month)
# #W  --> week
# #Q  --> quarter
# #Y  --> year
fig = pyplot.figure()
quality.resample('SM')['quality'].mean().ffill().plot()
project_up = project.upper()
fig.suptitle(project_up, fontsize=20)
pyplot.xlabel('Date', fontsize=12)
pyplot.ylabel('Quality score', fontsize=12)
pyplot.show()

#create time series dataframe for futher analysis
time_series_df = quality.resample('SM')['quality'].mean().ffill()

#Alternative
# pyplot.plot(quality[projects['{0}'.format(project)][5]],quality['quality'])
# pyplot.gcf().autofmt_xdate()
# pyplot.show()







### FORECASTING
##DECOMPOSING TIMESERIES
# Analysing base level, trend, seasonality and error
# freq is the number of days I am considering # multiplicative or additive
decomposition = sm.tsa.seasonal_decompose(time_series_df, freq=14, model = 'additive')
#Plotting decomposition
result = decomposition.plot()
pyplot.show()

#reference: https://medium.com/datadriveninvestor/time-series-prediction-using-sarimax-a6604f258c56
from statsmodels.tsa.stattools import adfuller
def test_adf(series, title=''):
    dfout={}
    dftest=sm.tsa.adfuller(series.dropna(), autolag='AIC', regression='ct')
    for key,val in dftest[4].items():
        dfout[f'critical value ({key})']=val
    if dftest[1]<=0.05:
        print("Strong evidence against Null Hypothesis")
        print("Reject Null Hypothesis - Data is Stationary")
        print("Data is Stationary", title)
    else:
        print("Strong evidence for  Null Hypothesis")
        print("Accept Null Hypothesis - Data is not Stationary")
        print("Data is NOT Stationary for", title)

test_adf(time_series_df, "Augmented Dickey-Fuller TEST RESULTS FOR PROJECT")



#reference: https://www.machinelearningplus.com/time-series/arima-model-time-series-forecasting-python/
# SARIMA model using pmdarima‘s auto_arima()
# Seasonal - fit stepwise auto-ARIMA

smodel = pm.auto_arima(time_series_df, 
                         start_p=1, start_q=1,
                         test='adf',
                         max_p=3, max_q=3, 
                         m=12, #XD & DNN & TIMOB & TISTUD
                         #m=3, #NEXUS
                         #m=6, #COMPASS & APSTUD & MULE
                         start_P=0, seasonal=True,
                         d=None, 
                         D=1, #because we have strong seasonal patterns
                         trace=True,
                         error_action='ignore',  
                         suppress_warnings=True, 
                         stepwise=True)

smodel.summary()
print(smodel.summary())

# smodel.plot_diagnostics(figsize=(7,5))
# pyplot.show()

# # Forecast
# #n_periods = 24 #XD & DNN & TIMOB & TISTUD
# #n_periods = 6 #NEXUS
# n_periods = 12 #COMPASS & APSTUD & MULE

# fitted, confint = smodel.predict(n_periods=n_periods, return_conf_int=True)
# index_of_fc = pd.date_range(time_series_df.index[-1], periods = n_periods, freq='MS')

# # make series for plotting purpose
# fitted_series = pd.Series(fitted, index=index_of_fc)
# lower_series = pd.Series(confint[:, 0], index=index_of_fc)
# upper_series = pd.Series(confint[:, 1], index=index_of_fc)

# # Plot
# pyplot.plot(time_series_df)
# pyplot.plot(fitted_series, color='darkgreen')
# pyplot.fill_between(lower_series.index, 
#                  lower_series, 
#                  upper_series, 
#                  color='k', alpha=.15)

# pyplot.title("SARIMA - User Story Quality Forecast")
# pyplot.show()




#Fitting the ARIMA model
#reference: https://towardsdatascience.com/an-end-to-end-project-on-time-series-analysis-and-forecasting-with-python-4835e6bf050b
mod = sm.tsa.statespace.SARIMAX(time_series_df,
                                exog=None, #we are not setting exogenous, therefore running SARIMA model instead of SARIMAX
                                order=(0, 1, 1), #xd
                                seasonal_order=(0, 1, 1, 12), #xd
                                #order=(1, 0, 1), #dnn
                                #seasonal_order=(1, 1, 0, 12), #dnn
                                # order=(2, 1, 1), #compass
                                # seasonal_order=(0, 1, 1, 6), #compass
                                # order=(0, 2, 2), #apstud
                                # seasonal_order=(2, 1, 0, 6), #apstud
                                # order=(1, 2, 1), #mule
                                # seasonal_order=(0, 1, 1, 6), #mule
                                # order=(1, 2, 0), #nexus
                                # seasonal_order=(0, 1, 0, 3), #nexus
                                # order=(0, 1, 1), #timob
                                # seasonal_order=(0, 1, 1, 12), #timob
                                #order=(0, 1, 2), #tistud
                                #seasonal_order=(0, 1, 1, 12), #tistud
                                enforce_stationarity=False,
                                enforce_invertibility=False)
results = mod.fit()

print(results.summary())

#Diagnostic plots
results.plot_diagnostics(figsize=(16, 8))
pyplot.show()

#reference: https://stackoverflow.com/questions/31818050/round-number-to-nearest-integer
def proper_round(num, dec=0):
    num = str(num)[:str(num).index('.')+dec+2]
    if num[-1]>='5':
        return float(num[:-2-(not dec)]+str(int(num[-2-(not dec)])+1))
    return float(num[:-1])


##VALIDATING FORECAST
###PREDICTIONS
#XD
pred = results.get_prediction(start=pd.to_datetime('2014-12-31 00:00:00+00:00'), dynamic=False)
#DNN
#pred = results.get_prediction(start=pd.to_datetime('2015-03-15 00:00:00+00:00'), dynamic=False)
#APSTUD
#pred = results.get_prediction(start=pd.to_datetime('2012-01-15 00:00:00+00:00'), dynamic=False)
#MULE
#pred = results.get_prediction(start=pd.to_datetime('2014-01-15 00:00:00+00:00'), dynamic=False)
#NEXUS
#pred = results.get_prediction(start=pd.to_datetime('2015-01-15 00:00:00+00:00'), dynamic=False)
#TIMOB
# pred = results.get_prediction(start=pd.to_datetime('2014-06-15 00:00:00+00:00'), dynamic=False)
#TISTUD
#pred = results.get_prediction(start=pd.to_datetime('2013-10-15 00:00:00+00:00'), dynamic=False)
#COMPASS
# pred = results.get_prediction(start=pd.to_datetime('2018-05-15 00:00:00+00:00'), dynamic=False)
pred_ci = pred.conf_int()

##OBSERVED VALUES
#XD
ax = time_series_df['2013':].plot(label='Actual')
#DNN
#ax = time_series_df['2013':].plot(label='observed')
#APSTUD
#ax = time_series_df['2011':].plot(label='observed')
#MULE
#ax = time_series_df['2013':].plot(label='observed')
#NEXUS
#ax = time_series_df['2014':].plot(label='observed')
#TIMOB
#ax = time_series_df['2012':].plot(label='observed')
#TISTUD
#ax = time_series_df['2011':].plot(label='observed')
#COMPASS
# ax = time_series_df['2017':].plot(label='observed')

pred.predicted_mean.plot(ax=ax, label='Forecasted', alpha=.7, figsize=(14, 7))
ax.fill_between(pred_ci.index,
                pred_ci.iloc[:, 0],
                pred_ci.iloc[:, 1], color='k', alpha=.2)
ax.set_title(project_up, fontsize=20)
ax.set_xlabel('Date')
ax.set_ylabel('User Story quality')
pyplot.legend()
pyplot.show()

#forcasted value
y_forecasted = pred.predicted_mean

#actual value
#XD
y_actual = time_series_df['2014-12-31 00:00:00+00:00':]
#DNN
#y_actual = time_series_df['2015-03-15 00:00:00+00:00':]
#APSTUD
#y_actual = time_series_df['2012-01-15 00:00:00+00:00':]
#MULE
#y_actual = time_series_df['2014-01-15 00:00:00+00:00':]
#NEXUS
#y_actual = time_series_df['2015-01-15 00:00:00+00:00':]
#TIMOB
# y_actual = time_series_df['2014-06-15 00:00:00+00:00':]
#TISTUD
#y_actual = time_series_df['2013-10-15 00:00:00+00:00':]
#COMPASS
#y_actual = time_series_df['2018-05-15 00:00:00+00:00':]

# ACCURACY METRICS
print('VALIDATION METRICS')
print(project_up)
# print('MSE')
# mse = ((y_forecasted - y_actual) ** 2).mean()
# print('The Mean Squared Error of our forecasts is {}'.format(round(mse, 2)))
# # print('MAE')
# # mae = np.mean(np.abs(y_forecasted - y_actual))    # MAE
# # print(mae)
print('MAPE')
mape = np.mean(np.abs(y_forecasted - y_actual)/np.abs(y_actual))  # MAPE
print(mape)
print('CORR')
corr = np.corrcoef(y_forecasted, y_actual)[0,1]   # corr
print(corr)
print('MINMAX')
mins = np.amin(np.hstack([y_forecasted[:,None], y_actual[:,None]]), axis=1)
maxs = np.amax(np.hstack([y_forecasted[:,None], y_actual[:,None]]), axis=1)
minmax = 1 - np.mean(mins/maxs) # minmax
print(minmax)

#Plotting forecast
pred_uc = results.get_forecast(steps=100)
pred_ci = pred_uc.conf_int()
ax = time_series_df.plot(label='observed', figsize=(14, 7))
pred_uc.predicted_mean.plot(ax=ax, label='Forecast')
ax.fill_between(pred_ci.index,
                pred_ci.iloc[:, 0],
                pred_ci.iloc[:, 1], color='k', alpha=.25)
ax.set_title(project_up, fontsize=20)
ax.set_xlabel('Date')
ax.set_ylabel('User Story quality')
pyplot.title("SARIMAX - User Story Quality Forecast - XD")
pyplot.legend()
pyplot.show()



