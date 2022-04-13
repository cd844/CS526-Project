import pandas as pd
import dash
from dash import Dash, html, dcc, Input, Output, callback
import plotly.express as px
import analytics as anal
from db_connection import db

import pprint
@callback(
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

    scat = px.scatter(df, x=xaxis_col, y = yaxis_col, hover_name='name', size_max=60,
    hover_data=['name', 'pk',], custom_data = [df.index], template = "plotly_dark", log_x = True)
    #scat.update_traces(hovertemplate='<b>%{customdata[0]}</b>')
    langs_use = anal.count_language_use(df)
    langs_bytes = anal.count_language_bytes(df)
    lang_count_bar = px.bar(langs_use, x="language", y="count", barmode="group", template = "plotly_dark")
    lang_bytes_bar = px.bar(langs_bytes, x="language", y="bytes", barmode="group",template = "plotly_dark")
    return lang_count_bar, lang_bytes_bar, scat 

@callback(
    Output('language-timeseries', 'figure'),
    Input('data-all', 'data')
)
def update_language_timeseries(data_all):
    try:
        df = pd.read_json(data_all)
    except:
        print("update_time_series(), failed to read datapoints")
        return
    langs = ['JavaScript', 'Go', 'C++', 'C', 'Python', 'Rust', 'Ruby', 'TypeScript', 'C#']
    time_data = anal.bin_languages_and_year(df['languages'], df['created_ts'], langs)
    for lang in time_data.keys():
        time_data[lang]['language'] = lang
    
    lang_bins_all = pd.concat([ time_data[k] for k in time_data.keys() ])
    lang_bins_all = lang_bins_all.reset_index()
    lang_bins_all['year'] = lang_bins_all['created_ts'].dt.year
    max_y = lang_bins_all['count'].max() * 1.25

    fig = px.scatter(lang_bins_all, x='language', y='count', title='Time Series ',color="language", animation_frame="year", size="count" ,animation_group="language",range_y=[0, max_y])
    
    return fig 


# this does not need to run on startup
@callback(
    Output('focus', 'value'),
    Output('data-select-info', 'children'),
    Input('scatter', 'clickData'),
    Input('language-comparison-violin-left', 'clickData')
)
def display_selected_scatter_data(selected_data_scatter, selected_data_violin):
    if(len(dash.callback_context.triggered) > 1):
        print("This might be a problem")
        return 0, f"selected: None"
    if(len(dash.callback_context.triggered) == 0):
        return 0, f"selected: None"
    trigger = dash.callback_context.triggered[0]
    pp.pprint(trigger)
    print(len(trigger['value']['points']))
    if(trigger['prop_id'] == 'language-comparison-violin-left.clickData'):
        print("violin update")
        if(len(selected_data_violin['points']) != 1): # this might be enough to filter out non-point clicks
            return
        p = selected_data_violin['points'][0]['customdata'][0]
        print(p)
        return p, f"selected {selected_data_violin}"
    elif(trigger['prop_id'] == 'scatter.clickData'):
        print("scatter update")
        id = (selected_data_scatter['points'][0]['customdata'][0])
        return id, f"selected {selected_data_scatter}"
    else:
        print("This is definitely a problem")

        return



@callback(
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
    except Exception as e:
        print("Could not make query")
        print(
        f'''limit_n: {limit_n}
        offset_n: {offset_n}
        where: {where}'''
        )
        print(e)
        return pd.DataFrame()

    return df.to_json()


"""
Updates displayed repository info
"""
@callback(
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


"""
Updates language comparisons
"""
@callback(
    Output('language-comparison-violin-left', 'figure'),
    Output('language-comparison-timeseries-left', 'figure'),
    Input('language-comparison-dropdown-left', 'value'),
    Input('data-all', 'data')
)
def update_language_comparison_left(languages, data_all):
    if(not isinstance(languages, list)):
        languages = [languages]
    df = pd.read_json(data_all)
    
    '''
    timeseries code
    '''
    time_label = 'created_ts'
    count_label = 'count'
    lang_label = 'language'
    
    df[time_label] = anal.convert_pddatetime(df[time_label])
    bins = anal.bin_languages_and_year(df['languages'], df[time_label], languages, time_resampling='3M')
    time_points = pd.DataFrame(columns = [time_label, count_label, lang_label])
    #print(time_points)
    for b in bins:
        bins[b][lang_label] = b
        bins[b].index.names = [time_label]
        bins[b] = bins[b].reset_index()
        #print(bins[b])
        time_points = pd.concat([time_points, bins[b]])
    #print(time_points)
    
    '''
    violin plot code
    '''
    print(df)
    violin_y_label = 'watchers_count'
    cols = df.columns.names.copy()
    cols.append('df_index')
    violin_points = pd.DataFrame(columns = cols)
    
    for lang in languages:
        #print(type(df[time_label][0]))
        violin_points_i = df[df.languages.apply(lambda x : lang in x)]
        violin_points_i[lang_label] = lang
        violin_points_i.index.names = ['df_index']
        violin_points_i = violin_points_i.reset_index()
        print(violin_points_i)
        violin_points = pd.concat([violin_points, violin_points_i])
        #filtered = filtered.sort_values(by=time_label)
    
    print(violin_points)
    return px.violin(violin_points, y = violin_y_label, color = lang_label, box=True, hover_data = ['df_index', 'full_name'], points='all'), px.line(time_points, x=time_label, y = count_label, color = 'language')
    #return , px.line(time_points, color = 'language')

  



scatter_plot_axes = ['forks_count', 'size', 'watchers_count', 'contributors_count']
languages_dropdown = ['Java', 'Python', 'C', 'C++', 'JavaScript', 'PHP', 'Go', "TypeScript", 'CSS', 'React', 'Kotlin', 'Rust']
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
                html.Div(dcc.Graph(id = 'scatter')),
                html.Div(dcc.Graph(id = 'language-timeseries')),
            ], id = 'aggregateGraphContainer', className = 'pretty_container eight columns'),
        ], className = 'row'),

        html.Div([
            html.Div([
                html.P("Filter by:", className = 'control_label'),
                html.Div([dcc.Input(id = 'where', value = 'watchers_count > 1000', type='text')], className='dcc_control'),
            ], className = 'container rightCol'),
            html.Div([
                html.P("Offset:", className = 'control_label'),
                html.Div([dcc.Input(id = 'offset', value = '0', type='text')], className='dcc_control'),
            ], className = 'container rightCol'),
            html.Div([
                html.P("Set a limit:", className = 'control_label'),
                html.Div([dcc.Input(id = 'limit', value = '100000', type='text')], className = 'dcc_control'),
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
                },
        ),
        html.Div([
            html.Div(
                dcc.Dropdown(
                    languages_dropdown, languages_dropdown[0:2], multi=True,
                    id = 'language-comparison-dropdown-left',
                    className = 'dcc_control'
                )
            ),
            html.Div(dcc.Graph(id='language-comparison-violin-left')),
            html.Div(dcc.Graph(id='language-comparison-timeseries-left')),
        ]),
        html.Div(id='test')

], style = {'height': '4%', 'background-color' : '#000000'})