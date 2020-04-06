import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
sns.set_context('talk',font_scale=.8)
import datetime
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
project = 'xd'

#Read the quality scores
quality_scores_df = pd.read_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/quality_scores_data/{0}-quality-scores.csv".format(project))
print('len of quality scores file')
print(len(quality_scores_df))
#Read nr of bugs
bugs_df = pd.read_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/WTLCC_input_data/{0}-bugs-for-WTLCC.csv".format(project))
print('len of bugs file')
print(len(bugs_df))

#indexing datetime
quality_scores_df['fields.created'] = pd.to_datetime(quality_scores_df['fields.created'], utc=True)
quality_scores_df = quality_scores_df.set_index(pd.DatetimeIndex(quality_scores_df['fields.created']))
bugs_df['fields.created'] = pd.to_datetime(bugs_df['fields.created'], utc=True)
bugs_df = bugs_df.set_index(pd.DatetimeIndex(bugs_df['fields.created']))

#resamplying by SM (SM --> semi month (15th and end of month) | B-->business day | W-->week)
resampled_qaulity = quality_scores_df.resample('B')['quality'].mean()#.ffill()
resampled_bugs = bugs_df.resample('B')['bugnr'].sum()

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





## IMPUTING MISSING VALUES. reference: https://medium.com/@drnesr/filling-gaps-of-a-time-series-using-python-d4bfddd8c460
# print(quality_bugs_df.index)
#quality_bugs_df = quality_bugs_df.assign(FillMean=quality_bugs_df['quality'].fillna(quality_bugs_df['quality'].mean()))
quality_bugs_df = quality_bugs_df.assign(FillMedian=quality_bugs_df['quality'].fillna(quality_bugs_df['quality'].median()))
# imputing using the rolling average
# quality_bugs_df = quality_bugs_df.assign(RollingMean=quality_bugs_df['quality'].fillna(quality_bugs_df['quality'].rolling(24,min_periods=1,).mean()))
#quality_bugs_df = quality_bugs_df.assign(InterpolateLinear=quality_bugs_df['quality'].interpolate(method='linear'))
quality_bugs_df = quality_bugs_df.drop(['quality'], axis=1)
quality_bugs_df = quality_bugs_df.rename(columns={'FillMedian': 'quality'})




# Test files
# resampled_qaulity.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")
# resampled_bugs.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test2.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")

quality_bugs_df.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test2.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")
#df_filled.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test1.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")


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
l = -5 #
u = 5
no_splits = 22  #67 sprints (two week period 673/10)
samples_per_split = quality_bugs_df.shape[0]/no_splits  #673/67=10 (for every sprint we have 10 business days)
rss=[]
for t in range(0, no_splits):
    quality_bugs_df.reset_index()
    d1 = quality_bugs_df['quality'].reset_index(drop=True).loc[(t)*samples_per_split:(t+1)*samples_per_split]
    d2 = quality_bugs_df['bugnr'].reset_index(drop=True).loc[(t)*samples_per_split:(t+1)*samples_per_split]
    rs = [crosscorr(d1,d2, lag) for lag in range(l,u)]
    rss.append(rs)
rss = pd.DataFrame(rss)

#test files
# rss.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")
# d1.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test2.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")

#plotting
f,ax = plt.subplots(figsize=(10,5))
sns.heatmap(rss,cmap='RdBu_r',ax=ax)
ax.set(title=f'Windowed Time Lagged Cross Correlation for XD',xlim=[0,u+u], xlabel='Offset',ylabel='Window epochs')
ax.set_xticks([0, 5, 10, 15, 20, 25, 30])
ax.set_xticklabels([-15, -10, -5, 0, 5, 10, 15])
plt.ylabel('Sprints (2 week)', fontsize=12)
plt.show()