from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd

import database as data
import analytics as anal

app = Dash(__name__)

"""
Ideal callback architecture would chain GUI update -> data update -> chart update
"""
@app.callback(
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
    return scat


# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
#app.config.from_envvar('DASH_SETTINGS')
db_path = './data/repos2_10.db'
db_type = 'sqlite'
db = data.DatabaseInterface(db_path, db_type)
db.debug = True
df = db.db_to_dataframe(10000, 'watchers > 10')
print(df.columns)
langs_use = anal.count_language_use(df)
langs_bytes = anal.count_language_bytes(df)

lang_count_fig = px.bar(langs_use, x="language", y="count", barmode="group")
lang_bytes_fig = px.bar(langs_bytes, x="language", y="bytes", barmode="group")
df['contributors'] = df['contributors'].apply(lambda x : 0 if x is None else len(x))
scat = px.scatter(df, x='forks', y = 'watchers', hover_name='name',hover_data=['name'])
scat.update_traces(hovertemplate='<b>%{customdata[0]}</b>')


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
        id='lang-count',
        figure=lang_count_fig
    ),
    
    dcc.Graph(id = 'lang-bytes',
        figure = lang_bytes_fig
    ),
    dcc.Graph(id = 'scatter')
])

if __name__ == '__main__':
    app.run_server(debug=True)