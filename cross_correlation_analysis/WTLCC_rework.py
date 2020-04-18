import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
sns.set_context('talk',font_scale=.8)
import datetime
from sklearn.metrics import r2_score

#Possible projects
#xd 
#dnn
#compass
#apstud
#mule
#nexus
#timob
#tistud
project = 'tistud'

#Read the quality scores
quality_scores_df = pd.read_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/quality_scores_data/{0}-quality-scores.csv".format(project))
print('len of quality scores file')
print(len(quality_scores_df))
#Read nr of rework
rework_df = pd.read_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/WTLCC_input_data/{0}-rework-for-WTLCC.csv".format(project))
print('len of rework file')
print(len(rework_df))

def manage_compass_field_names(df, project):
    if project == 'compass':
        df = df.rename(columns={'created': 'fields.created'})
        print('compass labels managed')
        return df
    else:
        return df

def choose_active_development_periods(quality, project):
    if project == 'dnn':
        quality = quality['20130701':'20160101']
        return quality
    elif project == 'compass':
        quality = quality.reset_index(drop=True)
        quality = quality[(quality['fields.created'] > '2017-09-20') & (quality['fields.created'] < '2018-09-01')]
        quality = quality.set_index('fields.created')
        return quality
    elif project == 'apstud':
        quality = quality.reset_index(drop=True)
        quality = quality[(quality['fields.created'] > '2011-06-08') & (quality['fields.created'] < '2012-06-20')]
        quality = quality.set_index('fields.created')
        return quality
    elif project == 'mule':
        quality = quality.reset_index(drop=True)
        quality = quality[(quality['fields.created'] > '2013-01-01') & (quality['fields.created'] < '2014-09-01')]
        quality = quality.set_index('fields.created')
        return quality
    elif project == 'nexus':
        quality = quality.reset_index(drop=True)
        quality = quality[(quality['fields.created'] > '2014-09-01') & (quality['fields.created'] < '2015-04-01')]
        quality = quality.set_index('fields.created')
        #quality = quality['20140901':'20150401']
        return quality
    elif project == 'tistud':
        quality = quality['20110101':'20140801']
        return quality    
    else:
        return quality


rework_df = rework_df.rename(columns={'created': 'fields.created'})
quality_scores_df = manage_compass_field_names(quality_scores_df, project)

#indexing creationtime
quality_scores_df['fields.created'] = pd.to_datetime(quality_scores_df['fields.created'], utc=True)
quality_scores_df = quality_scores_df.set_index(pd.DatetimeIndex(quality_scores_df['fields.created']))
rework_df['fields.created'] = pd.to_datetime(rework_df['fields.created'], utc=True)
rework_df = rework_df.set_index(pd.DatetimeIndex(rework_df['fields.created']))

#taking only active development period
quality_scores_df = choose_active_development_periods(quality_scores_df, project)
rework_df = choose_active_development_periods(rework_df, project)
# print(quality_scores_df)
# print(rework_df)

#resamplying (SM-->semi month (15th and end of month) | B-->business day | W-->week))
resampled_quality = quality_scores_df.resample('B')['quality'].mean().ffill()#.plot()
resampled_rework = rework_df.resample('B')['rework_nr'].sum()#.plot()
plt.show()

#replacing empty string with NaN
nan_value = float("NaN")
resampled_quality.replace("", nan_value, inplace=True)

#inner join on resampled quality and rework
quality_rework_df = pd.merge(resampled_quality, resampled_rework, left_index=True, right_index=True)
print('len of quality_rework_df')
print(len(quality_rework_df))

## IMPUTING MISSING VALUES. 
## reference: https://medium.com/@drnesr/filling-gaps-of-a-time-series-using-python-d4bfddd8c460
## Article scores different ways for imputation in order to suggest best imputation method for time-series analysis. Results suggest 'time' interpolation.  
# print(quality_rework_df.index)
quality_rework_df = quality_rework_df.assign(InterpolateTime=quality_rework_df['quality'].interpolate(method='time'))
quality_rework_df = quality_rework_df.drop(['quality'], axis=1)
quality_rework_df = quality_rework_df.rename(columns={'InterpolateTime': 'quality'})
#If there was NaN values at the start of the time frame imputation was not possible, therefore NaN values will be dropped
quality_rework_df.dropna( inplace=True)
print(len(quality_rework_df))

# Test files
quality_rework_df.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")


#CROSS CORREALTION
#reference: https://towardsdatascience.com/four-ways-to-quantify-synchrony-between-time-series-data-b99136c4a9c9
def crosscorr(datax, datay, lag=0, wrap=False):
    """ Lag-N cross correlation. 
    Shifted data filled with NaNs 
    
    Parameters
    ----------
    lag : int, default 0
    datax, datay : pandas.Series objects of equal length

    Returns
    ----------
    crosscorr : float
    """
    if wrap:
        shiftedy = datay.shift(lag)
        shiftedy.iloc[:lag] = datay.iloc[-lag:].values
        return datax.corr(shiftedy)
    else: 
        return datax.corr(datay.shift(lag))


### Windowed time lagged cross correlation (WTLCC)


#reference: https://stackoverflow.com/questions/31818050/round-number-to-nearest-integer
def proper_round(num, dec=0):
    num = str(num)[:str(num).index('.')+dec+2]
    if num[-1]>='5':
        return float(num[:-2-(not dec)]+str(int(num[-2-(not dec)])+1))
    return float(num[:-1])


#Time window settings
#no_splits = 4                                               #SETTING 1 - 4 time windows
no_splits = int(proper_round(len(quality_rework_df)/66))    #SETTING 2 len/66B | Quarter | 1Q ~ 66B
#no_splits = int(proper_round(len(quality_rework_df)/22))    #SETTING 3 len/22B | Months  | 1M ~ 22B 
#no_splits = int(proper_round(len(quality_rework_df)/10))    #SETTING 4 len/10B | Sprint  |~2W = 10B 


#calculating cross correlation matrix
samples_per_split = quality_rework_df.shape[0]/no_splits  #samples_per_split = whole length of time series/time window  #673/4=168.25 
u = int(proper_round(samples_per_split/2)) #int(round(samples_per_split/2) #168/2=84
l = -u
rss=[]
for t in range(0, no_splits):
    quality_rework_df.reset_index()
    d1 = quality_rework_df['quality'].reset_index(drop=True).loc[(t)*samples_per_split:(t+1)*samples_per_split] #red on matrix shows that US quality is leading
    d2 = quality_rework_df['rework_nr'].reset_index(drop=True).loc[(t)*samples_per_split:(t+1)*samples_per_split] #blue then bug nr is leading
    rs = [crosscorr(d1,d2, lag) for lag in range(l,u)]
    rss.append(rs)
rss = pd.DataFrame(rss)

#test files
# rss.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")
# d1.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test2.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")

#Plotting
f,ax = plt.subplots(figsize=(10,5))
sns.heatmap(rss,cmap='RdBu_r',ax=ax)
ax.set(title=f'WTLCC for user story quality and rework cases',xlim=[0,u+u], xlabel='Lag in business days',ylabel='Time window')
ax.set_xticklabels([int(item-(u)) for item in ax.get_xticks()])
# plt.ylabel('Sprints (2 week)', fontsize=12)
project_up = project.upper()
f.suptitle(project_up, fontsize=20)
plt.show()