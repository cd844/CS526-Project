import dash
from dash import Dash, html, dcc, Input, Output, callback
import pandas as pd
import analytics as anal
import plotly.express as px


# this does not need to run on startup

"""
Updates language comparisons
"""
@callback(
    Output('language-comparison-violin', 'figure'),
    Output('language-comparison-timeseries', 'figure'),
    Input('language-comparison-dropdown', 'value'),
    Input('data-all', 'data')
)
def update_language_comparison(languages, data_all):
    
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

languages_dropdown = ['Java', 'Python', 'C', 'C++', 'JavaScript', 'PHP', 'Go', "TypeScript", 'CSS', 'React', 'Kotlin', 'Rust']
layout = html.Div(
        html.Div([
            html.Div(
                dcc.Dropdown(
                    languages_dropdown, languages_dropdown[0:2], multi=True,
                    id = 'language-comparison-dropdown',
                    className = 'dcc_control'
                )
            ),
            html.Div(dcc.Graph(id='language-comparison-violin')),
            html.Div(dcc.Graph(id='language-comparison-timeseries')),
        ]),
)