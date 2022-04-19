import pandas as pd
import ast
from itertools import combinations
from collections import defaultdict



def read_topics(df, string):
    df = df[string]
    visited = set()
    # get total nodes
    for i in df:
        for val in i:
            visited.add(val)
    return visited, df


def get_combinations(df, visited):
    #combination = list(combinations(visited, 2))
    dictionary_nodes = defaultdict()


    # getting pairs for all the combinations of topics
    for i in df:
        c_list = list(combinations(i, 2))
        for pairs in c_list:
            if pairs not in dictionary_nodes:
                dictionary_nodes[pairs] = 1
            else:
                dictionary_nodes[pairs] += 1

    return dictionary_nodes


def get_pairs_less_than_two(dictionary_nodes):
    l = []
    for pairs in dictionary_nodes:
        if dictionary_nodes[pairs] < 2:
            l.append(pairs)
    return l


def remove_pairs(l, dictionary_nodes):
    for i in range(len(l)):
        dictionary_nodes.pop(l[i])

    return dictionary_nodes


def get_nodes_set(dictionary_nodes):
    new_visited = set()

    for key, value in dictionary_nodes.items():
        for j in key:
            new_visited.add(j)
    return new_visited


def get_final_list(dictionary_nodes):
    final_list = []
    for key, value in dictionary_nodes.items():
        x = []
        for j in key:
            x.append(j)
        x.append(value)
        final_list.append(x)
    return final_list


def create_nodes(new_visited):
    final_nodes = pd.DataFrame(new_visited, columns=['id'])

    #gfg_csv_data = final_nodes.to_csv('nodes_new.csv', index=False)
    return final_nodes
    #print('\nCSV String:\n', gfg_csv_data)


def create_edges(final_list):
    final_df = pd.DataFrame(final_list, columns=['source', 'target', 'weight'])

    # new csvs are created. 1st column is created. It has indexing from 0. I would drop the column manually. Then I would convert it to json manually

    #edges = final_df.to_csv('edges_new.csv')
    return final_df


def get_nodes_and_edges(df):
    #df = pd.read_csv("filtered_topics2.csv")
    string="topics"
    visited,df  = read_topics(df,string)
    dictionary_nodes = get_combinations(df, visited)
    #print(dictionary_nodes)
    l=get_pairs_less_than_two(dictionary_nodes)
    dictionary_nodes = remove_pairs(l,dictionary_nodes)
    new_visited = get_nodes_set(dictionary_nodes)
    final_list = get_final_list(dictionary_nodes)
    graph = dict()

    graph['nodes'] = create_nodes(new_visited)
    graph['edges'] = create_edges(final_list)
    return graph

def main():
    from db_connection import db
    df = db.db_to_dataframe(limit=100000)
    df = df[ df['topics'].map( lambda t : len(t)) > 0 ]
    print(df)
    print(get_nodes_and_edges(df))

if __name__ == "__main__":
    main()
