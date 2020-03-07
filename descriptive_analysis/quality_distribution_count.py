import pandas as pd
from matplotlib import pyplot
import matplotlib.ticker as ticker

#Possible projects
#xd 
#dnn
#compass
#apstud
#mesos
#mule
#nexus
#timob
#tistud
project = 'nexus'

#Read the quality scores
df = pd.read_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/quality_scores_data/{0}-quality-scores.csv".format(project))
print(len(df))

#Grouping and counting the quality values
counted_values = df.groupby(['quality']).size().reset_index(name='counts')

#Plotting
counted_values.plot(kind='bar', x='quality', y='counts')
pyplot.xticks(rotation='vertical')
pyplot.show()

counted_values.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")
