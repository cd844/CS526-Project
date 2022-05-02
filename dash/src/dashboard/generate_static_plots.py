import sqlite3
import pandas as pd
import ast
import statistics
import plotly
import plotly.express as px
def create_df():
    
    con = sqlite3.connect('./data/new_repos.db')
    cur = con.cursor()
    rows = cur.execute('SELECT * FROM repos LIMIT 100000')

    attributes = [description[0] for description in cur.description]
    data = dict()
    for a in attributes:
        data[a] = [] # preallocating would be a better optimization


    for r in rows:
        for i, a in enumerate(attributes):
            data[a].append(r[i])

    df = pd.DataFrame(data)
    return df
def lang_vs_count(df):
    new_df = df[['name','languages','topics','created_ts','watchers_count']]
    dictionary ={}
    i=0
    for lang in df['languages']:
        res = ast.literal_eval(lang)
        for j in res:
            if j not in dictionary:
                dictionary[j]=0
            dictionary[j]+=1
    lst=[]
    avg=statistics.mean(dictionary.values())
    for key,value in dictionary.items():
        if value>avg:
            lst.append([key,value])
    df2=pd.DataFrame(lst,columns=['languages','count'])
    
    barfig = px.bar(df2, x="languages", y="count",color="count", template = 'plotly_dark', color_discrete_sequence=px.colors.diverging.Temps,

                  title='language vs count')
    # fig.update_xaxes(
    #     rangeslider_visible=True)

    piefig = px.pie(df2, values='count', names='languages', color = 'count', template = 'plotly_dark', color_discrete_sequence=px.colors.diverging.Temps)
    #fig.write_html('pie.html', output_type = 'div')
    return barfig, piefig

def lang_vs_watcher(df):
    new_df = df[['name','languages','topics','created_ts','watchers_count']]
    new_list = []
    for lang in new_df.iterrows():
        if lang[1][4]>50:

            res = ast.literal_eval(lang[1][1])
            for i in res:
                first = i
                break
            lang[1][1] = first
            new_list.append([lang[1][0],lang[1][1],lang[1][2],lang[1][3],lang[1][4]])
    df_count = pd.DataFrame(new_list,columns=['name', 'languages', 'topics', 'created_ts', 'watchers_count'])
   

    fig = px.scatter(df_count, x="languages", y="watchers_count",color="watchers_count",hover_name = 'name', template = 'plotly_dark',

                  title='Languages that are dominant in the repositories with their watchers count', color_discrete_sequence=px.colors.diverging.Temps)
    # fig.update_xaxes(
    #     rangeslider_visible=True)

    return fig
def lang_vs_fork(df):
    topic_df = df[['languages','forks_count','created_ts']]
    # [language , fork count] 
    fork_list = []
    for lang in topic_df.iterrows():
        if lang[1][1]>50:
            res = ast.literal_eval(lang[1][0])
            #print("res:",res)
            m=0
            for lan in res:
                m=max(m,res[lan])
                if res[lan]> m//2:
                    fork_list.append([lan,lang[1][1]])

                #fork_list.append([lang[1][0],lang[1][1]])
    df_topics_new=pd.DataFrame(fork_list,columns=['languages','fork_count'])
   

    fig = px.scatter(df_topics_new, x="languages", y="fork_count",color="fork_count",hover_name = 'languages',

                  template = 'plotly_dark', title='Languages vs their forks count', color_discrete_sequence=px.colors.diverging.Temps)
    # fig.update_xaxes(
    #     rangeslider_visible=True)

    return fig

def topics_vs_count(df):
    df_contri = df[['topics','contributors_count','created_ts','forks_count','watchers_count']]
    topic_dictionary_count = {}
    for lang in df_contri.iterrows():
        res = ast.literal_eval(lang[1][0])
        for lan in res:
            if lan not in topic_dictionary_count :
                topic_dictionary_count[lan]=0
            topic_dictionary_count[lan]+=1


    topic_dic_list = []
    #print()
    for key,val in topic_dictionary_count.items():
        #print(key,val)
        #break
        if val> 10:
            topic_dic_list.append([key,val])
            
    topic_dic_list.sort(key = lambda x : -x[1])
    topic_dic_count_df=pd.DataFrame(topic_dic_list,columns=['topics','count'])

    fig = px.bar(topic_dic_count_df, x="topics", y="count",color="topics",hover_name = 'topics',

                  color_discrete_sequence=px.colors.diverging.Temps, template = 'plotly_dark', title='topics vs their count')
    # fig.update_xaxes(
    #     rangeslider_visible=True)

    return fig


    #topic_dic_list

def main():
    df = create_df()
    lang_vs_count(df)


if __name__ == '__main__':
    main()
