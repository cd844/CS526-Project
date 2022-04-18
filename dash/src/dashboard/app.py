from cmath import log
from re import template
from tkinter import W
from tkinter.ttk import Style
from xml.etree.ElementTree import ProcessingInstruction
import dash
from dash import Dash, html, dcc, Input, Output, callback
import plotly.express as px
import pandas as pd
import json
from flask import render_template, request

import database as data
import analytics as anal

import pprint

import graph_gen as gg
from pages import main_layout, graph_layout, error_404

from db_connection import db
pp = pprint.PrettyPrinter(indent = 4)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#app = Dash(__name__, external_stylesheets=external_stylesheets)

app = Dash(__name__, suppress_callback_exceptions=False)
app.layout = html.Div([dcc.Location(id = 'url', refresh = False),
    html.Div([
        html.Div(html.H4('GET THE REPO STORY'), className = 'eight columns')
    ], id = 'header', className = 'row'),
    dcc.Store(id='data-all'),
    dcc.Store(id='data-filtered'),
    dcc.Store(id='data-focus'),
    html.Div(id = 'page-content')
])


@callback(Output('page-content', 'children'),
    [Input('url', 'pathname')])
def display_page(pathname):
    print(pathname)
    if(pathname == '/'):
        return main_layout.layout
    elif(pathname == '/languages'):
        return 
    elif(pathname == '/graph'):
        return graph_layout.layout
    else:
        return error_404.layout

@app.server.route('/graph_render', methods = ['GET'])
def graph_route():
    graph_args = request.args
    print(graph_args)
    limit = 1000
    if('limit' in graph_args):
        limit = graph_args['limit']

    df = db.db_to_dataframe(limit=limit)
    df = df[ df['topics'].map( lambda t : len(t)) > 0 ]
    graph = gg.get_nodes_and_edges(df)
    
    #nodes = graph['nodes'].to_json(orient = 'records')
    nodes = graph['nodes'].to_dict('records')
    print(nodes)
    edges = graph['edges'].to_dict(orient = 'records')
    '''
    nodes = [{'id': 'a'},
    { 'id': 'b'}
    ]
    edges = [ {'source': 'a', 'target':'b', 'weight':2}]
    '''
    return render_template('graph_render.html', nodes = nodes, edges = edges)

if __name__ == '__main__':
    print("starting server")
    app.run_server(debug=True)