import pandas as pd
from matplotlib import pyplot
import matplotlib.ticker as ticker
import numpy as np
import matplotlib.ticker as plticker

#Possible projects
#xd 
#dnn
#compass
#apstud
#mesos -> excluded from analysis because of not enough stories
#mule
#nexus
#timob
#tistud
project = 'tistud'

#Read the quality scores
df = pd.read_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/quality_scores_data/{0}-quality-scores.csv".format(project))
print(len(df))

#Grouping and counting the quality values
counted_values = df.groupby(['quality']).size().reset_index(name='counts')

#Calculating percentage
counted_values['percentage'] = (counted_values['counts'] / counted_values['counts'].sum()) * 100

#Seting intervals
#counted_values['intervals'] = counted_values['quality'].apply(lambda x: '[0;0.25]' if x <= 0.25 else '(0.25;0.5]' if x > 0.25 and x<=0.5 else '(0.5;0.75]' if x > 0.5 and x<=0.75 else '(0.75;1]')
counted_values['intervals'] = counted_values['quality'].apply(lambda x: '[0;0.125]' if x <= 0.125 else '(0.125;0.25]' if x > 0.125 and x<=0.25 else '(0.25;0.375]' if x > 0.25 and x<=0.375 else '(0.375;0.5]' if x>0.375 and x<=0.5 else '(0.5;0.625]' if x>0.5 and x<=0.625 else '(0.625;0.75]' if x>0.625 and x<=0.75 else '(0.75;0.875]' if x>0.75 and x<=0.875 else '(0.875;1]')
#Group and sum by intervals
interval_values = counted_values.groupby(['intervals']).sum().reset_index()

#Plotting
interval_values.plot(kind='bar', x='intervals', y='percentage')
#adding upper project title
project_up = project.upper()
pyplot.title(project_up, fontsize=20)
pyplot.xticks(rotation='horizontal')
pyplot.ylabel('Intervals', fontsize=12)
pyplot.ylabel('percentage', fontsize=12)
pyplot.show()

interval_values.to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/test.csv", sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")



