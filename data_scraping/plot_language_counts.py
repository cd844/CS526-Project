import json
import pprint
import pandas as pd
import sqlite3

import plotly.express as px

pp = pprint.PrettyPrinter(indent = 4)

def db_to_dataframe(dbname, limit = None):
    con = sqlite3.connect(dbname)
    cur = con.cursor()
    if limit == None:
        rows = cur.execute("SELECT * FROM repos")
    else:
        rows = cur.execute("SELECT * FROM repos LIMIT (?)", (limit,))

    attributes = [description[0] for description in cur.description]
    data = dict()
    for a in attributes:
        data[a] = [] # preallocating would be a better optimization

    for r in rows:
        for i, a in enumerate(attributes):
            data[a].append(r[i])

    df = pd.DataFrame(data)
    # use this macro to convert json string to dict()
    df['languages'] = df['languages'].apply(lambda x : json.loads(x)[0])
    return df
    
def count_language_bytes(df):
    # put langs into a dict
    language_list = dict() 
    i=0
    for lang in df['languages']:
        if lang != None:
            print(i)
            i+=1
            for l in lang.keys():
                if l not in language_list.keys():
                    language_list[l] = 0
                language_list[l] += lang[l]

    # dict to dataframe
    lang_df = pd.DataFrame()
    lang_df['language'] = [l for l in language_list.keys()]
    lang_df['bytes'] = [language_list[l] for l in language_list.keys()]
    #print(lang_df)

    # remove rows that make up less than .1% of the total, aggregate into 'other'
    total_bytes = lang_df['bytes'].sum()
    thresh = total_bytes * 1e-3
    #low = lang_df[lang_df['bytes'] < thresh]
    low = lang_df['bytes'] < thresh
    other_count = lang_df[low]['bytes'].sum()
    lang_df = lang_df[(lang_df['bytes'] > thresh)]
    lang_df = lang_df.reset_index(drop=True)
    lang_df = pd.concat([lang_df, pd.DataFrame({'language':'other', 'bytes':other_count}, index=[0])], ignore_index=True)
    return lang_df

# same as above but each use of language per repo is weighed the same
def count_language_use(df):
    # put langs into a dict
    total = 0
    language_list = dict() 
    i=0
    for lang in df['languages']:
        if lang != None:
            print(i)
            i+=1
            for l in lang.keys():
                total += 1
                if l not in language_list.keys():
                    language_list[l] = 0
                language_list[l] += 1

    # dict to dataframe
    lang_df = pd.DataFrame()
    lang_df['language'] = [l for l in language_list.keys()]
    lang_df['count'] = [language_list[l] for l in language_list.keys()]
    #print(lang_df)

    # find better way to aggregate OTHER category
    #low = lang_df[lang_df['bytes'] < thresh]
    thresh = total * 1e-3
    low = lang_df['count'] < thresh
    other_count = lang_df[low]['count'].sum()
    lang_df = lang_df[(lang_df['count'] > thresh)]
    lang_df = lang_df.reset_index(drop=True)
    lang_df = pd.concat([lang_df, pd.DataFrame({'language':'other', 'count':other_count}, index=[0])], ignore_index=True)

    return lang_df
def main():
    df = db_to_dataframe('repos2_13.db')
    print(df.head())
        
    lang_df = count_language_use(df)
    
    pie_fig = px.pie(lang_df, values = 'count', names='language', title='repos with language')
    pie_fig.show()
    bar_fig = px.bar(lang_df, x='language', y='count')
    bar_fig.show()

    lang_df = count_language_bytes(df)
    pie_fig = px.pie(lang_df, values = 'bytes', names='language', title='bytes in language')
    pie_fig.show()
    bar_fig = px.bar(lang_df, x='language', y='bytes')
    bar_fig.show()

if __name__ == "__main__":
    main()