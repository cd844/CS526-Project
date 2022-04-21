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
    Input('data-all', 'data'),
    Input('xaxis-col', 'value'),
    Input('yaxis-col', 'value'),
)
def update_plots(data_points, xaxis_col, yaxis_col):
    print("updating plots")
    try:
        df = pd.read_json(data_points)
    except:
        print("update_plots(), failed to read datapoints:")
        print(data_points)
        return

    scat = px.scatter(df, x=xaxis_col, y = yaxis_col, hover_name='name', size_max=60,
    hover_data=['name', 'pk',], custom_data = [df.index], template = "plotly_dark", log_x = True)
    #scat.update_traces(hovertemplate='<b>%{customdata[0]}</b>')
    langs_use = anal.count_language_use(df)
    langs_bytes = anal.count_language_bytes(df)
    lang_count_bar = px.bar(langs_use, x="language", y="count", barmode="group", template = "plotly_dark")
    lang_bytes_bar = px.bar(langs_bytes, x="language", y="bytes", barmode="group",template = "plotly_dark")
    return lang_count_bar, lang_bytes_bar, scat 



@callback(
    Output('data-all', 'data'),
    Input('limit', 'value'),
    Input('offset', 'value'),
    Input('min-watchers-filter-input', 'value'),
    Input('languages-filter-input', 'value'),
)
def update_data(limit, offset, min_watchers_filter_input, languages_filter_input):
    #num = 0
    try:
        limit_n= int(limit)
    except:
        print(f"Cannot cast limit '{limit}' to integer")
        return
    try:
        offset_n = int(offset)
    except:
        print(f"Cannot cast limit '{offset}' to integer")
        return
    min_watchers = None
    try:
        min_watchers = int(min_watchers_filter_input)
    except:
        print(f"Cannot cast limit '{min_watchers_filter_input}' to integer")
        return
    try:
        languages = languages_filter_input.split(',')
        languages = [l.upper() for l in languages]
        def check_row(languages, required_languages):
            for req in required_languages:
                if req in languages:
                    return True
            return False
        while('' in languages):
            languages.remove('')
        #print("Languages")
        #print(db.construct_where(languages, 100))
    except:
        print("Failed to construct where clause")
    try:
        where = db.construct_where(languages, min_watchers)
        df = db.db_to_dataframe(limit_n, offset_n, where)
    except Exception as e:
        print("Could not make query")
        print(
        f'''limit_n: {limit_n}
        offset_n: {offset_n}
        where: {where}'''
        )
        print(e)
        return pd.DataFrame()
    print(f'Got {len(df)} results')
    print(df)
    '''
    df_filtered = df
    try:
        df_filtered = df[df['languages'].apply(lambda x : check_row([l.upper() for l in x.keys()], languages))]
    except Exception as e:
        print(f"Failed to filter languages-filter-input: {languages_filter_input}")
        print(e)
        return
    df = df_filtered
    '''
    return df.to_json()


"""
Updates displayed repository info
"""
@callback(
    Output('data-focus-info', 'children'),
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

    return html.Div(focus_markup)


scatter_plot_axes = ['forks_count', 'size', 'watchers_count', 'contributors_count']
layout = html.Div(children=[

        html.Div([
            html.Div([
                dcc.Dropdown(
                    scatter_plot_axes, scatter_plot_axes[0],
                    id = 'xaxis-col',
                    className = 'dcc_control'
                )
            ]),
            html.Div([
                dcc.Dropdown(
                    scatter_plot_axes, scatter_plot_axes[1],
                    id = 'yaxis-col',
                    className = 'dcc_control'
                )
            ])
        ], className = 'pretty_container'),

        html.Div(children=[
            html.Div([
                html.Div(dcc.Graph(id='lang-count-bar')),
                html.Div(dcc.Graph(id = 'lang-bytes-bar'))
            ], id = 'countGraphContainer', className = "pretty_container"),

            html.Div([
                html.Div(dcc.Graph(id = 'scatter-plot')),
                html.Div(dcc.Graph(id = 'language-timeseries')),
            ], id = 'aggregateGraphContainer', className = 'pretty_container eight columns'),
        ], className = 'row'),

        html.Div([
            html.Div([
                html.P("Minimum watchers:", className = 'control_label'),
                html.Div([dcc.Input(id = 'min-watchers-filter-input', value = '1000', type='text')], className='dcc_control'),
            ], className = 'container rightCol'),
            html.Div([
                html.P("Languages Filter:", className = 'control_label'),
                html.Div([dcc.Input(id = 'languages-filter-input', value = 'Java', type='text')], className = "dcc_control")
            ], className = 'container rightCol'),
            html.Div([
                html.P("Offset:", className = 'control_label'),
                html.Div([dcc.Input(id = 'offset', value = '0', type='text')], className='dcc_control'),
            ], className = 'container rightCol'),
            html.Div([
                html.P("Set a limit:", className = 'control_label'),
                html.Div([dcc.Input(id = 'limit', value = '10', type='text')], className = 'dcc_control'),
            ], className='container rightCol'),
            html.Div([
                html.P("Set a Focus:", className = 'control_label'),
                html.Div([dcc.Input(id = 'focus', value = '0', type='text')], className = "dcc_control")
            ], className = 'container rightCol')  
        ], className = 'pretty_container row'),
        
        html.Div([
            html.A('Show Graph', href='/graph_render?source=local', target='_blank')
        ]),

        html.Div([
                html.Div(id = 'data-focus-info'),
                html.Div(id = 'data-select-info')
                ], style = {
                    'display': 'flex', 'flex-direction': 'column'
                },
        ),
        html.Div(id='violin-plot') # Hack to stop callback errors

], style = {'height': '4%', 'background-color' : '#000000'})