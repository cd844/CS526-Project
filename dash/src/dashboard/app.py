from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import json

import database as data
import analytics as anal

app = Dash(__name__)
db_path = './data/repos2_10.db'
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
    print(xaxis_col)
    print(yaxis_col)
    try:
        df = pd.read_json(data_points)
    except:
        print("Failed to datapoints = :")
        print(data_points)
        return

    scat = px.scatter(df, x=xaxis_col, y = yaxis_col, hover_name='name',hover_data=['name'])
    scat.update_traces(hovertemplate='<b>%{customdata[0]}</b>')
    langs_use = anal.count_language_use(df)
    langs_bytes = anal.count_language_bytes(df)
    lang_count_bar = px.bar(langs_use, x="language", y="count", barmode="group")
    lang_bytes_bar = px.bar(langs_bytes, x="language", y="bytes", barmode="group")
    return lang_count_bar, lang_bytes_bar, scat 


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

    return df.to_json()


"""
Updates displayed repository info
"""
@app.callback(
    Output('data-focus-info', 'children'),
    Input('focus', 'value'),
    Input('data-all', 'data'),
)
def update_focus(focus, data_all):
    try:
        focus_n= int(focus)
    except:
        print(f"Cannot cast limit '{focus}' to integer")
        return
    df = pd.read_json(data_all).iloc[focus_n]

    # initialize markup
    focus_markup = [html.A(html.H2(df['name']), href=f"https://www.github.com/{df['name']}")]
    focus_markup += [df.description, html.Br()]
    for cont in df.contributors:
        focus_markup += [html.A(cont['login'], href = f"https://www.github.com/{cont['login']}"), html.Br()]

    focus_markup += [f'topics: {df.topics}', html.Br()]
    focus_markup += [f"watchers: {df.watchers}", html.Br()]
    focus_markup += [f"created: {df.created}", html.Br()]
    focus_markup += [f"updated: {df.updated}", html.Br()]
    focus_markup += [f"pushed: {df.pushed}", html.Br()]
    focus_markup += [f"size: {df.size}", html.Br()]
    focus_markup += [f"branches: {df.branches}", html.Br()]
    focus_markup += [f"languages: {df.languages}", html.Br(),]
    focus_markup += [f"forks: {df.forks}", html.Br()]
    focus_markup += [f"license: {df.license}", html.Br()]

    return html.Div(focus_markup)


app.layout = html.Div(
    children=[
    dcc.Store(id='data-all'),
    dcc.Store(id='data-filtered'),
    dcc.Store(id='data-focus'),
    html.H1(children='Data visualization and analytics'),
    html.Div([
        "WHERE: ", dcc.Input(id = 'where', value = 'watchers > 10', type='text')
    ]),
    html.Div([
        "OFFSET: ", dcc.Input(id = 'offset', value = '0', type='text')
    ]),
    html.Div([
        "LIMIT: ", dcc.Input(id = 'limit', value = '1000', type='text')
    ]),
    html.Div([
        "Focus: ", dcc.Input(id = 'focus', value = '0', type='text')
    ]),

    html.Div(id = 'data-focus-info'),

    html.Div(children=[
        html.Div(dcc.Graph(id='lang-count-bar')),
        html.Div(dcc.Graph(id = 'lang-bytes-bar')),
    ],
    style = {
        'display': 'flex', 'flex-direction': 'row'
    }),

    html.Div([
        html.Div([
            dcc.Dropdown(
                ['forks', 'size', 'watchers'], 'forks',
                id = 'xaxis-col'
            )
        ], style={'width': '48%', 'display': 'inline-block'}
        ),
        html.Div([
            dcc.Dropdown(
                ['forks', 'size', 'watchers'], 'watchers',
                id = 'yaxis-col'
            )
        ], style = {'width':'48%', 'float': 'right', 'display': 'inline-block'})
    ]),

    dcc.Graph(
        id = 'scatter',
        style = {
            "height": 700
        }
    )
])

if __name__ == '__main__':
    print("starting server")
    app.run_server(debug=True)