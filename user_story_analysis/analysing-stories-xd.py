import pandas as pd
from matplotlib import pyplot
import datetime


#Read the stories (AQUSA input)
stories_project = pd.read_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/cleaned_input_data/jira-xd-allus.csv", names=['title', 'key', 'z'])
print(len(stories_project))

#Read the quality (AQUSA output)
quality_project = pd.read_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/analyzed_output_data/xd-quality-allus.csv")
print(len(quality_project))

#Merge story keys and quality issues
quality_df = pd.merge(stories_project, quality_project, how='left', left_on='title', right_on='title')
print(len(quality_df))


#Calculating the length of the text
df_text = quality_df[['key', 'title', 'role', 'means', 'ends']].drop_duplicates()
print(len(df_text))

df_text['text_len'] = df_text['title'].str.len()
df_text['role_len'] = df_text['role'].str.len()
df_text['means_len'] = df_text['means'].str.len()
df_text['ends_len'] = df_text['ends'].str.len()

df_text = df_text.drop(['title', 'role', 'means', 'ends'], axis=1)
df_text = df_text.fillna(0)


#Quantifying the quality
quality_df["penalty"] = quality_df["severity"].apply(lambda x: 1/6 if x == "high" else 1/12 if x == "minor" else 1/9 if x =="medium" else 0)

#Tagging if there is high, medium or minor errors
quality_df["high"] = quality_df["severity"].apply(lambda x: 1 if x == "high" else 0)
quality_df["minor"] = quality_df["severity"].apply(lambda x: 1 if x == "minor" else 0)
quality_df["medium"] = quality_df["severity"].apply(lambda x: 1 if x == "medium" else 0)

#Grouping the data using key field and summarising the penalties and the number of errors.
q = quality_df[["key", "penalty", "high", "minor"]].groupby(['key']).sum()
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
initial_dataset = pd.read_csv("C:/Users/Tanel/Documents/Ylikool/Magister/Master Thesis/Analysing ASP Repo/data/datasets/jiradataset_issues.csv")
initial_dataset = initial_dataset[initial_dataset['project'] == 'xd']

print(len(quality_df))
quality = pd.merge(initial_dataset[["key", "fields.created"]], quality_df, on='key', how='outer')
quality = quality[quality.quality.notnull()]
quality['fields.created'] = pd.to_datetime(quality['fields.created'], utc=True)
quality = quality.set_index(pd.DatetimeIndex(quality['fields.created']))


#SM --> semi month (15th and end of month)
#W  --> week
quality.resample('W')['quality'].mean().plot()
#quality['20150101':'20160101'].resample('SM')['quality'].mean().plot()
pyplot.show()


