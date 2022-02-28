# -*- coding: utf-8 -*-
"""repostory_basic.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/138erLdrdYkxHnW4fpvLIgQjc0o0G2jkZ
"""

#from google.colab import drive

#drive.mount('/content/gdrive')

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv('github_data.csv')

df.head()

df = df.drop(['Unnamed: 0', 'Unnamed: 0.1'], axis =1)

df.columns

df.describe

df.info()

df.at[700, 'issue'] = str(5000)

Numerical_columns = ["star","fork","watch","issue","pull_requests","projects","commits","branches","packages","releases","contributers"]
# Github_data[Numerical_columns] = Github_data[Numerical_columns].apply(lambda x: x.replace(',','').astype(float) if ',' in str(x) else x)

df[Numerical_columns] = df[Numerical_columns].fillna(0)
df["issue"] = df["issue"].apply(lambda x: x.replace(',', '') if ',' in x else x).astype(float)
df["pull_requests"] = df["pull_requests"].apply(lambda x: x.replace(',', '') if ',' in x else x).astype(float)
df["commits"] = df["commits"].apply(lambda x: x.replace(',', '') if ',' in x else x).astype(float)
df["branches"] = df["branches"].apply(lambda x: x.replace(',', '') if ',' in x else x).astype(float)
df["contributers"] = df["contributers"].apply(lambda x: x.replace(',', '') if ',' in x else x).astype(float)

df['fork'] = df['fork'].apply(lambda x: float(x.replace('k',''))*1000 if 'k' in x else x)
df['star'] = df['star'].apply(lambda x: float(x.replace('k',''))*1000 if 'k' in x else x)
df['watch'] = df['watch'].apply(lambda x: float(x.replace('k',''))*1000 if 'k' in x else x)

import ast
unique_tags = []
df['topic_tag'].apply(lambda x: unique_tags.append(ast.literal_eval(x)))
# unique_tags = list(set([item for sublist in unique_tags for item in sublist]))
all_tag = np.array([item for sublist in unique_tags for item in sublist])
unique, counts = np.unique(all_tag, return_counts=True)
print("Total number of tags in 1500 repository : ",len(all_tag))
print("Total number of unique tags in 1500 repository : ",len(unique))
tag_dataframe = pd.DataFrame({"unique":unique,"counts":counts})
tag_dataframe = tag_dataframe.sort_values(['counts'],ascending=[False])

fig = px.bar(tag_dataframe[:20],x="unique",y="counts",color='counts', title = "Tags and count",
             labels = {"unique": "Unique Tags in repositories", "counts": "Number of unique tags"},
             color_continuous_scale = "darkmint")
fig.show()

df['star'] = df['star'].astype(float)
star_topicwise = df.groupby('topic').sum()['star']
fig = px.bar(star_topicwise,x=star_topicwise.index,y="star",
             labels = {"star": "Stars",
                       "topic": "Repository topics"},
             title = "Starred topics",
             color=star_topicwise.index)
fig.update_traces(marker_color="darkgoldenrod")
fig.show()

commit_topicwise = df.groupby('topic').sum()['commits']
#fig = px.pie(commit_topicwise, values='commits', names=commit_topicwise.index, title='Commit Distribution topic wise',
#             color_discrete_sequence=px.colors.qualitative.Set3)

fig = go.Figure(data=[go.Pie(labels=commit_topicwise.index, values=commit_topicwise.values, hole=.3,
                             marker_colors = px.colors.qualitative.Set3)])
fig.update_layout(title = "Topic wise commits")
fig.show()

contributers_topicwise = df.groupby('topic').sum()['contributers']
fig = go.Figure(data=[go.Pie(labels=contributers_topicwise.index, values=contributers_topicwise.values, hole=.3,
                             marker_colors=px.colors.qualitative.Set3)])
fig.update_layout(title = "Contributors wise commits")
fig.show()

"""######machine-learning repositories are more forked then java-scriped repositories rether then java-script repositories are more stared"""

github_group = df.groupby('topic')
num_of_top_repository = 10
fig = go.Figure()
for name, group in github_group:
    
    fig.add_trace(go.Bar(
    x=list(range(1,num_of_top_repository+1)),
    y=group["fork"].values[:num_of_top_repository+1],
    name=name))
fig.update_layout(barmode='group', xaxis_tickangle=-45)
fig.show()

"""#####here more stared repositories have less contributers"""

github_group = df.groupby('topic')
num_of_top_repository = 10
fig = go.Figure()
for name, group in github_group:
    
    fig.add_trace(go.Bar(
    x=list(range(1,num_of_top_repository+1)),
    y=group["contributers"].values[:num_of_top_repository+1],
    name=name
    ))
fig.update_layout(barmode='group', xaxis_tickangle=-45)
fig.show()

from wordcloud import WordCloud, STOPWORDS
from PIL import Image

# create a string with all the topic tags
github_tags = (" ").join(all_tag)

git_mask = np.array(Image.open('/content/gdrive/MyDrive/github_icon.png'))

# instantiate a word cloud object
tags_wc = WordCloud(
    mask = git_mask,
    colormap='coolwarm',
    background_color='white',
    max_font_size=120,
    max_words=200
)

# generate the word cloud
tags_wc.generate(github_tags)

# plot wordcloud and set title
plt.figure(figsize=(6,6),dpi=100)
plt.imshow(tags_wc, interpolation='bilinear')
plt.axis('off')
plt.tight_layout(pad=0)
plt.title('Most common tags used in Github Repositories',fontdict={'size': 15,'color': 'maroon','verticalalignment': 'center'})
plt.show()
