from cmath import log
from re import template
from tkinter.ttk import Style
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import json

import database as data
import analytics as anal

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#app = Dash(__name__, external_stylesheets=external_stylesheets)
app = Dash(__name__)
db_path = './data/new_repos.db'
db_type = 'sqlite'
db = data.DatabaseInterface(db_path, db_type)
db.debug = True

"""
Basic callback architecture would chain GUI update -> data update -> plot update
Ideal with optimizations
GUI Update -> DB query if necessary -> data update (primarily filtering and 'mapping' procedures) -> plot view update
"""
@app.callback(
    Output('lang-count-bar', 'figure'),
    Output('lang-bytes-bar', 'figure'),
    Output('scatter', 'figure'),
    Input('data-all', 'data'),
    Input('xaxis-col', 'value'),
    Input('yaxis-col', 'value'),
)
def update_plots(data_points, xaxis_col, yaxis_col):
    try:
        df = pd.read_json(data_points)
    except:
        print("update_plots(), failed to read datapoints:")
        #print(data_points)
        return

    scat = px.scatter(df, x=xaxis_col, y = yaxis_col, hover_name='name', size_max=60, size='size',
    hover_data=['name', 'pk',], custom_data = [df.index], template = "plotly_dark", log_x = True)
    #scat.update_traces(hovertemplate='<b>%{customdata[0]}</b>')
    langs_use = anal.count_language_use(df)
    langs_bytes = anal.count_language_bytes(df)
    lang_count_bar = px.bar(langs_use, x="language", y="count", barmode="group", template = "plotly_dark")
    lang_bytes_bar = px.bar(langs_bytes, x="language", y="bytes", barmode="group",template = "plotly_dark")
    return lang_count_bar, lang_bytes_bar, scat 

@app.callback(
    Output('language-timeseries', 'figure'),
    Input('data-all', 'data')
)
def update_time_series(data_all):
    try:
        df = pd.read_json(data_all)
    except:
        print("update_time_series(), failed to read datapoints")
        return
    langs = ['JavaScript', 'Go', 'C++', 'C', 'Python', 'Rust', 'Ruby', 'TypeScript', 'C#']
    time_data = anal.bin_languages_and_year(df['languages'], df['created_ts'], langs)
    for lang in time_data.keys():
        time_data[lang]['language'] = lang
        print(time_data[lang])
    
    lang_bins_all = pd.concat([ time_data[k] for k in time_data.keys() ])
    lang_bins_all = lang_bins_all.reset_index()
    lang_bins_all['year'] = lang_bins_all['created_ts'].dt.year
    print(lang_bins_all)
    max_y = lang_bins_all['count'].max() * 1.25

    fig = px.scatter(lang_bins_all, x='language', y='count', title='Time Series ',color="language", animation_frame="year", size="count" ,animation_group="language",range_y=[0, max_y])


    #fig = px.scatter(df3, x='languages', y='total', title='Time Series ',color="languages", animation_frame="year",size="total" ,animation_group="languages",range_y=[100,12000])
    
    return fig 


# this does not need to run on startup
@app.callback(
    Output('focus', 'value'),
    Output('data-select-info', 'children'),
    Input('scatter', 'clickData')
)
def display_selected_scatter_data(selected_data):
    if(selected_data == None):
        return 0, f"selected: None"
    id = (selected_data['points'][0]['customdata'][0])
    return id, f"selected {selected_data}"
    



@app.callback(
    Output('data-all', 'data'),
    Input('limit', 'value'),
    Input('offset', 'value'),
    Input('where', 'value'),
)
def update_data(limit, offset, where):
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
    try:
        df = db.db_to_dataframe(limit_n, offset_n, where)
    except:
        print("Could not make query")
        print(
        f'''limit_n: {limit_n}
        offset_n: {offset_n}
        where: {where}'''
        )
        return pd.DataFrame()

    return df.to_json()


"""
Updates displayed repository info
"""
@app.callback(
    Output('data-focus-info', 'children'),
    Input('focus', 'value'),
    Input('data-all', 'data'),
)
def update_focus_info(focus, data_all):
    try:
        focus_n= int(focus)
    except:
        print(f"Cannot cast limit '{focus}' to integer")
        return
    df_m = pd.read_json(data_all)
    df = df_m.iloc[focus_n]

    # initialize markup
    focus_markup = [html.A(html.H2(df['name']), href=f"https://www.github.com/{df['name']}")]
    focus_markup += [df.description, html.Br()]

    focus_markup += [f'topics: {df.topics}', html.Br()]
    focus_markup += [f"watchers_count: {df.watchers_count}", html.Br()]
    focus_markup += [f"created_ts: {df.created_ts}", html.Br()]
    focus_markup += [f"updated_ts: {df.updated_ts}", html.Br()]
    focus_markup += [f"pushed_ts: {df.pushed_ts}", html.Br()]
    focus_markup += [f"size: {df.size}", html.Br()]
    focus_markup += [f"branches: {df.branches}", html.Br()]
    focus_markup += [f"languages: {df.languages}", html.Br(),]
    focus_markup += [f"forks_count: {df.forks_count}", html.Br()]
    focus_markup += [f"license: {df.license}", html.Br()]

    return html.Div(focus_markup)


scatter_plot_axes = ['forks_count', 'size', 'watchers_count']

app.layout = html.Div(children=[

        dcc.Store(id='data-all'),
        dcc.Store(id='data-filtered'),
        dcc.Store(id='data-focus'),

        html.Div([
            html.Div(html.H4('GET THE REPO STORY'), className = 'eight columns')
        ], id = 'header', className = 'row'),

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
                html.Div(dcc.Graph(id = 'scatter')),
                html.Div(dcc.Graph(id = 'language-timeseries')),
            ], id = 'aggregateGraphContainer', className = 'pretty_container eight columns'),
        ], className = 'row'),

        html.Div([
            html.Div([
                html.P("Filter by:", className = 'control_label'),
                html.Div([dcc.Input(id = 'where', value = 'watchers_count > 10', type='text')], className='dcc_control'),
            ], className = 'container rightCol'),
            html.Div([
                html.P("Offset:", className = 'control_label'),
                html.Div([dcc.Input(id = 'offset', value = '0', type='text')], className='dcc_control'),
            ], className = 'container rightCol'),
            html.Div([
                html.P("Set a limit:", className = 'control_label'),
                html.Div([dcc.Input(id = 'limit', value = '1000', type='text')], className = 'dcc_control'),
            ], className='container rightCol'),
            html.Div([
                html.P("Set a Focus:", className = 'control_label'),
                html.Div([dcc.Input(id = 'focus', value = '0', type='text')], className = "dcc_control")
            ], className = 'container rightCol')  
        ], className = 'pretty_container row'),

        html.Div([
                html.Div(id = 'data-focus-info'),
                html.Div(id = 'data-select-info')
                ], style = {
                    'display': 'flex', 'flex-direction': 'column'
                },)

], style = {'height': '4%', 'background-color' : '#000000'})


if __name__ == '__main__':
    print("starting server")
    app.run_server(debug=True)