import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
sns.set_context('talk',font_scale=.8)
import datetime
from sklearn.metrics import r2_score
# from sklearn.impute import KNNImputer
# from sklearn.impute import SimpleImputer

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
#Read nr of bugs
bugs_df = pd.read_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/WTLCC_input_data/{0}-bugs-for-WTLCC.csv".format(project))
print('len of bugs file')
print(len(bugs_df))


def manage_compass_field_names(df, project):
    if project == 'compass':
        df = df.rename(columns={'created': 'fields.created'})
        print('compass labels managed')
        return df
    else:
        return df

#managing compass field names
quality_scores_df = manage_compass_field_names(quality_scores_df, project)
bugs_df = manage_compass_field_names(bugs_df, project)
quality_scores_df.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")


#indexing datetime
quality_scores_df['fields.created'] = pd.to_datetime(quality_scores_df['fields.created'], utc=True)
quality_scores_df = quality_scores_df.set_index(pd.DatetimeIndex(quality_scores_df['fields.created']))
bugs_df['fields.created'] = pd.to_datetime(bugs_df['fields.created'], utc=True)
bugs_df = bugs_df.set_index(pd.DatetimeIndex(bugs_df['fields.created']))

#resamplying by SM (SM --> semi month (15th and end of month) | B-->business day | W-->week)
resampled_qaulity = quality_scores_df.resample('B')['quality'].mean()#.ffill()#.plot()
resampled_bugs = bugs_df.resample('B')['bugnr'].sum()
#plt.show()

#replacing empty string with NaN
nan_value = float("NaN")
resampled_qaulity.replace("", nan_value, inplace=True)
#removing empty quality values
# resampled_qaulity.dropna( inplace=True)
# print(len(resampled_qaulity))

#inner join on resampled quality and bugs
quality_bugs_df = pd.merge(resampled_qaulity, resampled_bugs, left_index=True, right_index=True)
print('len of quality_bugs_df')
print(len(quality_bugs_df))



## IMPUTING MISSING VALUES. 
## reference: https://medium.com/@drnesr/filling-gaps-of-a-time-series-using-python-d4bfddd8c460
## Article scores different ways for imputation in order to suggest best imputation method for time-series analysis. Results suggest 'time' interpolation.  
# print(quality_bugs_df.index)
# Different ways for imputing
# quality_bugs_df = quality_bugs_df.assign(RollingMean=quality_bugs_df['quality'].fillna(quality_bugs_df['quality'].rolling(24,min_periods=1,).mean()))
# quality_bugs_df = quality_bugs_df.assign(InterpolateLinear=quality_bugs_df['quality'].interpolate(method='linear'))
# quality_bugs_df = quality_bugs_df.assign(FillMean=quality_bugs_df['quality'].fillna(quality_bugs_df['quality'].mean()))
# quality_bugs_df = quality_bugs_df.assign(FillMedian=quality_bugs_df['quality'].fillna(quality_bugs_df['quality'].median()))
quality_bugs_df = quality_bugs_df.assign(InterpolateTime=quality_bugs_df['quality'].interpolate(method='time'))
quality_bugs_df = quality_bugs_df.drop(['quality'], axis=1)
quality_bugs_df = quality_bugs_df.rename(columns={'InterpolateTime': 'quality'})

#If there was NaN values at the start of the time frame imputation was not possible, therefore NaN values will be dropped
quality_bugs_df.dropna( inplace=True)
print(len(quality_bugs_df))

# Test files
quality_bugs_df.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")


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


# Windowed time lagged cross correlation
# we have 673 business days in xd

#reference: https://stackoverflow.com/questions/31818050/round-number-to-nearest-integer
def proper_round(num, dec=0):
    num = str(num)[:str(num).index('.')+dec+2]
    if num[-1]>='5':
        return float(num[:-2-(not dec)]+str(int(num[-2-(not dec)])+1))
    return float(num[:-1])


#Time window settings
#no_splits = 4                                             #SETTING 1 - 4 time windows
#no_splits = int(proper_round(len(quality_bugs_df)/66))    #SETTING 2 len/66B | Quarter | 1Q ~ 66B
#no_splits = int(proper_round(len(quality_bugs_df)/22))    #SETTING 3 len/22B | Months  | 1M ~ 22B 
no_splits = int(proper_round(len(quality_bugs_df)/10))    #SETTING 4 len/10B | Sprint  |~2W = 10B 


#calculating cross correlation matrix
samples_per_split = quality_bugs_df.shape[0]/no_splits  #samples_per_split = whole length of time series/time window  #673/4=168.25 
u = int(proper_round(samples_per_split/2)) #int(round(samples_per_split/2) #168/2=84
l = -u
rss=[]
for t in range(0, no_splits):
    quality_bugs_df.reset_index()
    d1 = quality_bugs_df['quality'].reset_index(drop=True).loc[(t)*samples_per_split:(t+1)*samples_per_split] #red on matrix shows that US quality is leading
    d2 = quality_bugs_df['bugnr'].reset_index(drop=True).loc[(t)*samples_per_split:(t+1)*samples_per_split] #blue then bug nr is leading
    rs = [crosscorr(d1,d2, lag) for lag in range(l,u)]
    rss.append(rs)
rss = pd.DataFrame(rss)

#test files
# rss.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")
# d1.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test2.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")

#Plotting
f,ax = plt.subplots(figsize=(10,5))
sns.heatmap(rss,cmap='RdBu_r',ax=ax)
ax.set(title=f'Windowed Time Lagged Cross Correlation',xlim=[0,u+u], xlabel='Offset',ylabel='Window epochs')
ax.set_xticklabels([int(item-(u)) for item in ax.get_xticks()])
# plt.ylabel('Sprints (2 week)', fontsize=12)
project_up = project.upper()
f.suptitle(project_up, fontsize=20)
plt.show()