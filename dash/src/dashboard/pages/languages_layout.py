from re import template
import dash
from dash import Dash, html, dcc, Input, Output, callback
import pandas as pd
import analytics as anal
import plotly.express as px
import json


'''
update time-range selection
'''
@callback(
    Output('time-range-start', 'data'),
    Output('time-range-end', 'data'),
    Input('language-comparison-timeseries', 'relayoutData'))
def display_relayout_data(relayoutData):
    start_date = None
    end_date = None
    if('xaxis.range[0]' in relayoutData and 'xaxis.range[1]' in relayoutData):
        start_date = relayoutData['xaxis.range[0]']
        end_date = relayoutData['xaxis.range[1]']
    
    print(start_date, end_date)

    return start_date, end_date

'''
plot time series
'''
@callback(
    Output('language-comparison-timeseries', 'figure'),
    Input('data-all', 'data'),
    Input('language-comparison-dropdown', 'value'),
)
def update_language_time_series(data_all, languages):
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
    return px.line(time_points, x=time_label, y = count_label, color = 'language', template = 'plotly_dark', color_discrete_sequence=px.colors.diverging.Temps)

"""
Updates language comparisons
"""
@callback(
    Output('language-comparison-violin', 'figure'),
    #Output('language-comparison-timeseries', 'figure'),
    Input('language-comparison-dropdown', 'value'),
    Input('data-all', 'data'),
    Input('time-range-start', 'data'),
    Input('time-range-end', 'data'),
)
def update_language_violin(languages, data_all, time_range_start, time_range_end):
    print('update_language_comparison')
    print(time_range_start)
    print(time_range_end)
    if(not isinstance(languages, list)):
        languages = [languages]
    df = pd.read_json(data_all)
    time_label = 'created_ts'
    count_label = 'count'
    lang_label = 'language'
    
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
        violin_points = pd.concat([violin_points, violin_points_i])
        #filtered = filtered.sort_values(by=time_label)
    
    print(len(violin_points['created_ts']))
    if(time_range_start != None and time_range_end != None):
        time_range_start = pd.to_datetime(time_range_start)
        print(type(time_range_start))
        time_range_end= pd.to_datetime(time_range_end)
        print(f"Filter out range [{time_range_start},{time_range_end}]")
        violin_points['created_ts'] = violin_points['created_ts'].apply(lambda x : pd.to_datetime(x).tz_localize(None))
        violin_points = violin_points[ violin_points['created_ts'].apply(lambda time : time > time_range_start and time < time_range_end) ]
    print(len(violin_points['created_ts']))
    return px.violin(violin_points, y = violin_y_label, color = lang_label, box=True, template = 'plotly_dark', color_discrete_sequence=px.colors.diverging.Temps,
                    hover_data = ['df_index', 'full_name', 'created_ts'], points='all')


@callback(
    Output('language-comparison-dropdown', 'options'),
    Input('data-all', 'data')
)
def update_languages(data_all):
    print("update_languages_options")
    df = pd.read_json(data_all)
    languages_dropdown = []
    for langs in df['languages']:
        for l in langs:
            if l not in languages_dropdown:
                languages_dropdown.append(l) #O(n^2) lmao
    # tabulate languages

    return languages_dropdown


layout = html.Div(
        html.Div([
            html.Div([
                dcc.Dropdown(
                    [], [], multi=True,
                    id = 'language-comparison-dropdown',
                    className = 'dcc_control'
                )
            ], className = 'pretty_container'),
            html.Div([
                html.Div(dcc.Graph(id='language-comparison-violin')),
                html.Div(dcc.Graph(id='language-comparison-timeseries')),
            ], className = 'pretty_container'),
            dcc.Store(id = 'time-range-start'),
            dcc.Store(id = 'time-range-end'),
        ]),
)
