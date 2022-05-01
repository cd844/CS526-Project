import pandas as pd
import dash
from dash import Dash, html, dcc, Input, Output, State, callback
import plotly.express as px
import analytics as anal
from db_connection import db

import pprint

@callback(
    Output('lang-count-bar', 'figure'),
    Output('lang-bytes-bar', 'figure'),
    Output('scatter-plot', 'figure'),
    Output('3d-graph-button-container', 'children'),
    Input('data-all', 'data'),
    Input('xaxis-col', 'value'),
    Input('xaxis-type', 'value'),
    Input('yaxis-col', 'value'),
    Input('yaxis-type', 'value'),
)
def update_plots(data_points, xaxis_col, xaxis_type, yaxis_col, yaxis_type):
    print("updating plots")
    try:
        df = pd.read_json(data_points)
    except:
        print("update_plots(), failed to read datapoints:")
        print(data_points)
        return

    scat = px.scatter(df, x=xaxis_col, y = yaxis_col, hover_name='name', size_max=60, color_discrete_sequence=px.colors.diverging.Temps,
    hover_data=['name', 'pk',], custom_data = [df.index], template = "plotly_dark", log_x = xaxis_type == "Log", log_y = yaxis_type == "Log")
    #scat.update_traces(hovertemplate='<b>%{customdata[0]}</b>')
    langs_use = anal.count_language_use(df)
    langs_bytes = anal.count_language_bytes(df)
    lang_count_bar = px.bar(langs_use, x="language", y="count", barmode="group", template = "plotly_dark", color_discrete_sequence=px.colors.diverging.Temps)
    lang_bytes_bar = px.bar(langs_bytes, x="language", y="bytes", barmode="group",template = "plotly_dark", color_discrete_sequence=px.colors.diverging.Temps)
    graph_button = dcc.Link(html.Button('Show 3D Graph'), href='/graph_render?source=local', target='_blank', className = 'bare_container'),
    return lang_count_bar, lang_bytes_bar, scat, graph_button



"""
Updates displayed repository info
"""
@callback(
    Output('data-focus-info', 'children'),
    #Output('data-focus-lang-figure', 'children'),
    #Input('focus', 'value'),
    Input('data-focus', 'data'),
    Input('data-all', 'data'),
)
def update_focus_info(focus, data_all):
    print("update_focus_info")
    print(focus)
    try:
        if(focus == None):
            focus_n = 0
        else:
            focus_n= int(focus)
    except:
        print(f"Cannot cast limit '{focus}' to integer")
        return
    df_m = pd.read_json(data_all)
    df = df_m.loc[df_m['pk'] == focus_n].reset_index(drop = True)
    if(len(df) != 1):
        return html.Div("Select repository on scatterplot")
    df = df.iloc[0]
    print(f"Updating to:\n {df}")

    # initialize markup
    #focus_markup = [html.A(html.H2(df['name']), href=f"https://www.github.com/{df['full_name']}")]
    focus_markup = [html.A(html.H2(df['name']), href=df.html_url)]
    focus_markup += [html.A(df.owner["login"], href = df.owner['html_url']), html.Br()]
    focus_markup += [df.description, html.Br()]
    focus_markup += [f'topics: {df.topics}', html.Br()]
    focus_markup += [f"watchers_count: {df.watchers_count}", html.Br()]
    focus_markup += [f"contributors_count: {df.contributors_count}", html.Br()]
    focus_markup += [f"created_ts: {df.created_ts}", html.Br()]
    focus_markup += [f"updated_ts: {df.updated_ts}", html.Br()]
    focus_markup += [f"pushed_ts: {df.pushed_ts}", html.Br()]
    focus_markup += [f"size: {df.size}", html.Br()]
    #focus_markup += [f"branches: {df.branches}", html.Br()]
    focus_markup += [f"languages: {df.languages}", html.Br(),]
    focus_markup += [f"forks_count: {df.forks_count}", html.Br()]
    focus_markup += ["license: ", html.A(df.license['name'], href = df.license['url']), html.Br()]


    print(df['languages'])
    langs = []
    l_bytes = []
    for l in df['languages'].keys():
        langs.append(l)
        l_bytes.append(df['languages'][l])
    print(langs)
    print(l_bytes)
    fig = px.pie(  values = l_bytes, names = langs, hole = 0.3, template = "plotly_dark", width = 300, color_discrete_sequence=px.colors.diverging.Temps)
    #fig = px.pie({'languages': langs, 'bytes': l_bytes,)

    topics_button = None
    if(len(df['topics']) > 0):
        topics_button = dcc.Link(html.Button('Show 3D Graph (Topics)'), id = '3d-graph-topics', href=f'/graph_render?source=local&topics={";".join(df["topics"])}', target='_blank')
    return [
            html.Div([
                html.Div(focus_markup), 
                html.Div([dcc.Graph(figure=fig)], className = 'pretty_container')
                ], className = 'row'),
                topics_button 
            ]
    #className = 'bare_container')


scatter_plot_axes = ['forks_count', 'watchers_count', 'contributors_count', 'size']
layout = html.Div(children=[

        html.Div(children=[
            html.Div([
                html.Div([
                    dbc.Col([
                        dcc.Graph(id='lang-count-bar')
                    ], style = {'width':'49.65%'}),
                    dbc.Col([
                        dcc.Graph(id = 'lang-bytes-bar')
                    ], style = {'width':'49.65%'})
                ], className = 'container row'),
            ], id = 'countGraphContainer', className = "pretty_container"),

            html.Div([
                html.Div([
                    html.Div([
                        dcc.Dropdown(
                            scatter_plot_axes, scatter_plot_axes[0],
                            id = 'xaxis-col',
                            className = 'dcc_control'
                        ),
                        dcc.RadioItems(
                            ['Linear', 'Log'],
                            'Linear',
                            id='xaxis-type',
                            labelStyle={'display': 'inline-block', 'marginTop': '5px'}
                        )
                    ]),
                    html.Div([
                        dcc.Dropdown(
                            scatter_plot_axes, scatter_plot_axes[1],
                            id = 'yaxis-col',
                            className = 'dcc_control'
                        ),
                        dcc.RadioItems(
                            ['Linear', 'Log'],
                            'Linear',
                            id='yaxis-type',
                            labelStyle={'display': 'inline-block', 'marginTop': '5px'}
                        )
                    ])
                ], id = 'scatter-axes-controls'),

                html.Div(dcc.Graph(id = 'scatter-plot')),
                #html.Div(dcc.Graph(id = 'language-timeseries')),
                html.Div([], id = '3d-graph-button-container', style = {'marginTop': '5px'})
            ], id = 'aggregateGraphContainer', className = 'pretty_container'),
        ], className = 'rightCol'),

        html.Div([
            html.Div([
            ],id = 'data-focus-info',
            ),
        ], className = 'pretty_container'),


        html.Div(id='violin-plot') # Hack to stop callback errors

], style = {'height': '4%', 'background-color' : '#000000'})
