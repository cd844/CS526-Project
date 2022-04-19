from cmath import log
from re import template
from tkinter import W
from tkinter.ttk import Style
from xml.etree.ElementTree import ProcessingInstruction
from dash import Dash, html, dcc, Input, Output, callback
import plotly.express as px
import pandas as pd
from flask import render_template, request

import database as data
import analytics as anal
import dash

import pprint

import graph_gen as gg
from pages import main_layout, graph_layout, error_404,languages_layout 

from db_connection import db
pp = pprint.PrettyPrinter(indent = 4)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#app = Dash(__name__, external_stylesheets=external_stylesheets)

app = Dash(__name__, suppress_callback_exceptions=False)
app.layout = html.Div([
    dcc.Location(id = 'url', refresh = False),
    dcc.Link('Languages', href='/languages'),
    html.Div([
        html.Div(html.H4('GET THE REPO STORY'), className = 'eight columns')
    ], id = 'header', className = 'row'),
    dcc.Store(id='data-all'),
    dcc.Store(id='data-filtered'),
    dcc.Store(id='data-focus'),
    html.Div(id = 'page-content')
])

# this does not need to run on startup
# 
@callback(
    Output('focus', 'value'),
    Output('data-focus', 'data'),
    Input('scatter-plot', 'clickData'),
    Input('violin-plot', 'clickData'),
)
def display_selected_scatter_data(selected_data_scatter, selected_data_violin):
    if(len(dash.callback_context.triggered) > 1):
        print("This might be a problem")
        return 0, f'{0}'
    if(len(dash.callback_context.triggered) == 0):
        return 0, f"{0}"
    trigger = dash.callback_context.triggered[0]
    if(trigger['value'] == None):
        return 0, f"selected {selected_data_scatter}"
    if(trigger['prop_id'] == 'language-comparison-violin-left.clickData'):
        print("violin update")
        if(len(selected_data_violin['points']) != 1): # this might be enough to filter out non-point clicks
            return
        p = selected_data_violin['points'][0]['customdata'][0]
        print(p)
        return p, f"selected {selected_data_violin}"
    elif(trigger['prop_id'] == 'scatter-plot.clickData'):
        print("scatter update")
        id = (selected_data_scatter['points'][0]['customdata'][0])
        return id, f"{id}"
    else:
        print("This is definitely a problem")
        return
    '''
    if(trigger['prop_id'] == 'scatter-plot.clickData'):
        print("scatter update")
        id = (selected_data_scatter['points'][0]['customdata'][0])
        return id, f"{id}"
    else:
        print("Error")

    '''


@callback(Output('page-content', 'children'),
    [Input('url', 'pathname')])
def display_page(pathname):
    print(pathname)
    if(pathname == '/'):
        return main_layout.layout
    elif(pathname == '/languages'):
        return languages_layout.layout
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
    nodes = graph['nodes'].to_dict(orient = 'records')
    edges = graph['edges'].to_dict(orient = 'records')
    print(f"generated graph |V|={len(nodes)}, |E|={len(edges)}")
    return render_template('graph_render.html', nodes = nodes, edges = edges)

if __name__ == '__main__':
    print("starting server")
    app.run_server(debug=True)