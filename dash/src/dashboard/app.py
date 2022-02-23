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
df = db.db_to_dataframe(10000, 'watchers > 10')

"""
Basic callback architecture would chain GUI update -> data update -> plot update
Ideal with optimizations
GUI Update -> DB query if necessary -> data update (primarily filtering and 'mapping' procedures) -> plot view update
"""
@app.callback(
    Output('lang-count-bar', 'figure'),
    Output('lang-bytes-bar', 'figure'),
    Output('scatter', 'figure'),
    Input('limit', 'value'),
    Input('where', 'value')
)
def update_scatter(limit, where):
    #num = 0
    try:
        num = int(limit)
        df = db.db_to_dataframe(num, where)
    except:
        print(f"Cannot cast '{where}' to integer")
        return scat
    scat = px.scatter(df, x='forks', y = 'watchers', hover_name='name',hover_data=['name'])
    scat.update_traces(hovertemplate='<b>%{customdata[0]}</b>')
    langs_use = anal.count_language_use(df)
    langs_bytes = anal.count_language_bytes(df)
    lang_count_bar = px.bar(langs_use, x="language", y="count", barmode="group")
    lang_bytes_bar = px.bar(langs_bytes, x="language", y="bytes", barmode="group")
    return lang_count_bar, lang_bytes_bar, scat 


colors = {
    'background': '#111111',
    'text': '#7FDFBFF'
}

app.layout = html.Div(children=[
    html.H1(children='AAAAAAAAAAAAAAA'),
    html.Div(children='''
       AAAAAAAAAAAAAAAAAAAAAAAAA 
    '''),
    html.Div([
        "WHERE: ", dcc.Input(id = 'where', value = 'watchers > 10', type='text')
    ]),
    html.Div([
        "LIMIT: ", dcc.Input(id = 'limit', value = '10000', type='text')
    ]),

    dcc.Graph(
        id='lang-count-bar',
    ),
    
    dcc.Graph(id = 'lang-bytes-bar',
    ),
    dcc.Graph(id = 'scatter')
])

if __name__ == '__main__':
    app.run_server(debug=True)