from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd

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
    Input('data_points', 'data'),
)
def update_plots(data_points):
    df = pd.read_json(data_points)
    scat = px.scatter(df, x='forks', y = 'watchers', hover_name='name',hover_data=['name'])
    scat.update_traces(hovertemplate='<b>%{customdata[0]}</b>')
    langs_use = anal.count_language_use(df)
    langs_bytes = anal.count_language_bytes(df)
    lang_count_bar = px.bar(langs_use, x="language", y="count", barmode="group")
    lang_bytes_bar = px.bar(langs_bytes, x="language", y="bytes", barmode="group")
    return lang_count_bar, lang_bytes_bar, scat 


@app.callback(
    Output('data_points', 'data'),
    Input('limit', 'value'),
    Input('offset', 'value'),
    Input('where', 'value')
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
        print(limit_n, offset_n, where)
        df = db.db_to_dataframe(limit_n, offset_n, where)
    except:
        print("Could not make query")
    return df.to_json()

colors = {
    'background': '#111111',
    'text': '#7FDFBFF'
}

app.layout = html.Div(
    children=[
    dcc.Store(id='data_points'),
    html.H1(children='AAAAAAAAAAAAAAA'),
    html.Div(children='''
       AAAAAAAAAAAAAAAAAAAAAAAAA 
    '''),
    html.Div([
        "WHERE: ", dcc.Input(id = 'where', value = 'watchers > 10', type='text')
    ]),
    html.Div([
        "OFFSET: ", dcc.Input(id = 'offset', value = '0', type='text')
    ]),
    html.Div([
        "LIMIT: ", dcc.Input(id = 'limit', value = '10000', type='text')
    ]),

    html.Div(children=[
        html.Div(dcc.Graph(id='lang-count-bar')),
        html.Div(dcc.Graph(id = 'lang-bytes-bar'))
    ],
    style = {
        'display': 'flex', 'flex-direction': 'row'
    }),

    dcc.Graph(id = 'scatter',
                style = {
                    "height": 700
                }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)