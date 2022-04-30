import pandas as pd
import datetime as dt
import json
def count_language_bytes(df):
    # put langs into a dict
    language_list = dict() 
    i=0
    for lang in df['languages']:
        if lang != None:
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


def convert_pddatetime(time):
    time_format = '%Y-%m-%dT%H:%M:%SZ'
    return pd.to_datetime(time, format = time_format)
    #return dt.datetime.strptime(time_str, time_format)

# Bin the occurrances of a language based on year
def bin_languages_and_year(languages, time, language_bins=['JavaScript', 'Shell', 'C', 'C++', 'Ruby', 'Python'], time_resampling = '1Y'):
    languages = languages.apply(lambda x : [ k for k in x.keys() ])
    time = convert_pddatetime(time)
    df = pd.concat([languages, time], axis=1)
    time_col = df.columns[1]
    #df = df.set_index(time_col)
    bins = {}
    for l in language_bins:
        valid_rows = df['languages'].apply( lambda langs : l in langs)
        filtered = df[valid_rows]
        filtered.set_index(time_col, inplace=True)
        bins[l] = filtered.resample(time_resampling).count()
        bins[l] = bins[l].rename(columns = {'languages' : 'count'})
    return bins

# filter out nodes and edges not in filter
def graph_filter(graph, filter):
    nodes = []
    edges = []
    nodes_ids = [n for n in filter]
    for e in graph['edges'].to_dict(orient = 'records'):
        if(e['source'] in filter or e['target'] in filter):
            edges.append(e)
            if(e['source'] not in nodes):
                nodes_ids.append(e['source'])
            if(e['target'] not in nodes):
                nodes_ids.append(e['target'])
    for n in graph['nodes'].to_dict(orient = 'records'):
        if n['id'] in nodes_ids:
            nodes.append(n)
    print(nodes)
    graph = dict()
    graph['nodes'] = nodes
    graph['edges'] = edges
    return graph

def calculate_graph_degrees(graph):

    for i,v in enumerate(graph['nodes']):
        degree = 0
        for e in graph['edges']:
            if e['source'] == v['id'] or e['target'] == v['id']:
                degree += 1
        graph['nodes'][i]['degree'] = degree
    return graph
