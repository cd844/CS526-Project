import pandas as pd
import ast
from itertools import combinations
from collections import defaultdict


def read_topics(df, string):
    df = df[string]
    visited = set()
    dic = defaultdict(int)
    # get total nodes
    for i in df:
        #res = ast.literal_eval(i)
        for val in i:
            dic[val] += 1
            visited.add(val)
    return visited, df, dic


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


def get_nodes_set(dictionary_nodes, dic):
    new_visited = []
    # print(dic)
    for key, value in dictionary_nodes.items():
        for j in key:
            # print(j,dic[j])
            new_visited.append([j, dic[j]])
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
    # print(new_visited)
    for pair in new_visited:
        if pair[1] < 20:
            pair[1] = 2
        elif pair[1] >= 20 and pair[1] <= 50:
            pair[1] = 7
        else:
            pair[1] = 15

    final_nodes = pd.DataFrame(new_visited, columns=['id', 'count'])
    print(final_nodes.head)
    gfg_csv_data = final_nodes.to_csv('nodes_new.csv', index=False)
    final_nodes = final_nodes.drop_duplicates()  # TODO fix duplicate vertices
    return final_nodes


def create_edges(final_list):
    final_df = pd.DataFrame(final_list, columns=['source', 'target', 'weight'])
    return final_df

def get_nodes_and_edges(df):
    string="topics"
    visited,df,dic  = read_topics(df,string)
    dictionary_nodes = get_combinations(df, visited)
    l=get_pairs_less_than_two(dictionary_nodes)
    dictionary_nodes = remove_pairs(l,dictionary_nodes)
    #new_visited = get_nodes_set(dictionary_nodes)
    new_visited = get_nodes_set(dictionary_nodes,dic)

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
