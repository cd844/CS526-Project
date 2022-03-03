from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import sqlite3
import json

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options


# Create dataframe from Database
conn = sqlite3.connect(r'C:/Users/tanvi/CS526/CS526-Project/Tanvi/repos.db')
df = pd.read_sql_query("SELECT * from repos", conn)

# use this macro to convert json string to dict()
df['languages'] = df['languages'].apply(lambda x : json.loads(x)[0])

#Languages and count

list_lang = dict()
for each_lang in df['languages']:
  if each_lang != None:
    for l in each_lang.keys():
      if l not in list_lang.keys():
        list_lang[l] = 1
      else:
        list_lang[l] += 1


app.layout = html.Div([
  html.Div(children=[
    html.H1('Get the Repo Story'),
    html.Br(),
    dcc.Dropdown(options = [{'label' : 'Languages', 'value' : 'languages'}, {'label' : 'Stars', 'value' : 'star'}], 
    value ='languages', id = "graph_select")], style = {'padding': 10, 'flex': 1}),

  html.Div([
    dcc.Graph(id = 'graph1')
  ])  
  ])

@app.callback(
  Output('graph1', 'figure'),
  Input('graph_select', 'value')
)

def update_graph(graph_value):
  if graph_value == 'languages':
    lang_ct_df = pd.DataFrame()

    lang_ct_df['languages'] = list_lang.keys()
    lang_ct_df['count'] = list_lang.values()

    thresh = lang_ct_df['count'].sum() * 0.002
    low = lang_ct_df['count'] < thresh
    other_count = lang_ct_df[low]['count'].sum()
    lang_ct_df = lang_ct_df[(lang_ct_df['count'] > thresh)]
    lang_ct_df = lang_ct_df.reset_index(drop=True)
    lang_ct_df = pd.concat([lang_ct_df, pd.DataFrame({'languages':'other', 'count':other_count}, index=[0])], ignore_index=True)

    fig = px.bar(lang_ct_df, x='languages', y='count', hover_name='languages',
    title = "Number of Repositories based on languages", color = 'count', color_continuous_scale = 'darkmint')

    #fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    fig.update_xaxes(title='Languages')
    fig.update_yaxes(title='Counts')

    return fig

  else:
    lang_star_df = pd.DataFrame()

    lang_star_df['languages'] = list_lang.keys()
    lang_star_df['stars'] = df['watchers']

    thresh = lang_star_df['stars'].sum() * 0.02
    low = lang_star_df['stars'] < thresh
    other_count = lang_star_df[low]['stars'].sum()
    lang_star_df = lang_star_df[(lang_star_df['stars'] > thresh)]
    lang_star_df = lang_star_df.reset_index(drop=True)
    lang_star_df = pd.concat([lang_star_df, pd.DataFrame({'languages':'other', 'stars':other_count}, index=[0])], ignore_index=True)

    fig1 = px.bar(lang_star_df, x='languages', y='stars', hover_name='languages',
    title = "Number of Stars based on languages", color = 'stars', color_continuous_scale = 'darkmint')

    #fig1.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    fig1.update_xaxes(title='Languages')
    fig1.update_yaxes(title='Stars')

    return fig1


#app.layout = html.Div([
#    html.Div(children=[
#        html.Label('Dropdown'),
#        dcc.Dropdown(['Commit wise', 'Stars', 'Contributors'])
#    ]), style={'padding': 10, 'flex': 1}),
#    html.Br()
#    html.Div(children=[
#        html.H1(children='Hello Dash'),
#
#        html.Div(children='''
#            Dash: A web application framework for your data.
#        '''),
#        html.Br()
#        dcc.Graph(
#            id='example-graph',
#            figure=fig
#        )
#    ]), style={'padding': 10, 'flex': 1})   
#
#]), style={'display': 'flex', 'flex-direction': 'row'})

if __name__ == '__main__':
    app.run_server(debug=True)


