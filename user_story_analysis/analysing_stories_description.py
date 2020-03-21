import pandas as pd
from matplotlib import pyplot
import datetime

#Possible projects
#xd 
#dnn
#COMPASS
#apstud
#mesos
#mule
#nexus
#timob
#tistud

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
stories_project = pd.read_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/cleaned_input_data/jira-{0}-allus.csv".format(project), names=['title', 'key', 'identif', 'z'])
print(len(stories_project))

#Selecting stories by text source identifier
# Description = 0 and summary = 1
stories_project = stories_project[stories_project['identif'] == 0]

#Read the quality (AQUSA output)
quality_project = pd.read_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/analyzed_output_data/{0}-quality-allus.csv".format(project))
print(len(quality_project))

#Merge story keys and quality issues
quality_df = pd.merge(stories_project, quality_project, how='left', left_on='title', right_on='title')
print(len(quality_df))

#Calculating the length of the text
df_text = quality_df[['key', 'title', 'role', 'means', 'ends']].drop_duplicates()
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
q = quality_df[["key", "penalty", "high", "minor", "medium"]].groupby(['key']).sum()
q = q.reset_index()


#Adding kind and subkind and creating table presenting all issues
qc = quality_df[["key", "kind", "subkind"]].groupby(['key', "kind", "subkind"]).count()
qc = qc.reset_index()

qc.index = qc["key"]
dummies = pd.get_dummies(qc[["kind", "subkind"]])
dummies = dummies.reset_index()
dummies = dummies.groupby(['key']).sum()

qj = q.join(dummies, on="key")


#Calculating the total quality Q = 1 - P
qj["quality"] = 1 - qj["penalty"]
quality_df = pd.merge(df_text, qj, on='key')
quality_df = quality_df.fillna(0)


#Merging the data from initial dataset (dates and quality scores)
initial_dataset = pd.read_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/datasets/"+projects['{0}'.format(project)][3] )
initial_dataset = initial_dataset[initial_dataset[projects['{0}'.format(project)][4]] == '{0}'.format(project)]

print(len(quality_df))
quality = pd.merge(initial_dataset[["key", projects['{0}'.format(project)][5]]], quality_df, on='key', how='outer')
quality = quality[quality.quality.notnull()]

#Formating datetime and indexing. Needed for resampling
quality['fields.created'] = pd.to_datetime(quality[projects['{0}'.format(project)][5]], utc=True)
quality = quality.set_index(pd.DatetimeIndex(quality[projects['{0}'.format(project)][5]]))

#Writing keys and quality scores to csv
quality_scores = quality.drop_duplicates(subset='key', keep="first")
quality_scores[["key", "quality"]].to_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/quality_scores_data/{0}-quality-scores.csv".format(project), sep=',', encoding='utf-8', doublequote = True, header=True, index=False, line_terminator=",\n")


# #SM --> semi month (15th and end of month)
# #W  --> week
# #Q  --> quarter
# #Y  --> year
quality.resample('SM')['quality'].mean().plot()
#quality['20150101':'20160101'].resample('SM')['quality'].mean().plot()
pyplot.show()

#Alternative
# pyplot.plot(quality[projects['{0}'.format(project)][5]],quality['quality'])
# pyplot.gcf().autofmt_xdate()
# pyplot.show()