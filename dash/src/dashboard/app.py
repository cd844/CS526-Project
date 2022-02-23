from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd

import database as data
import analytics as anal

app = Dash(__name__)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
#app.config.from_envvar('DASH_SETTINGS')
db_path = './data/repos2_10.db'
db_type = 'sqlite'
db = data.DatabaseInterface(db_path, db_type)
df = db.db_to_dataframe(5000)
langs_use = anal.count_language_use(df)
langs_bytes = anal.count_language_bytes(df)

lang_count_fig = px.bar(langs_use, x="language", y="count", barmode="group")
lang_bytes_fig = px.bar(langs_bytes, x="language", y="bytes", barmode="group")
df['contributors'] = df['contributors'].apply(lambda x : 0 if x is None else len(x))
scat = px.scatter(df, x='contributors', y = 'watchers', hover_name='name',hover_data=['name'])
scat.update_traces(hovertemplate='<b>%{customdata[0]}</b>')


colors = {
    'background': '#111111',
    'text': '#7FDFBFF'
}

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for your data.
    '''),

    dcc.Graph(
        id='lang-count',
        figure=lang_count_fig
    ),
    
    dcc.Graph(id = 'lang-bytes',
        figure = lang_bytes_fig
    ),
    dcc.Graph(id = 'scatter',
        figure = scat
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)