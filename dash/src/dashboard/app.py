from cmath import log
from distutils.log import error
from re import template
from tkinter import W
from tkinter.ttk import Style
from xml.etree.ElementTree import ProcessingInstruction
import dash
from dash import Dash, html, dcc, Input, Output, callback
import plotly.express as px
import pandas as pd
import json

import database as data
import analytics as anal

import pprint

from pages import main_layout, graph_layout, error_404

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
    elif(pathname == '/graph'):
        return graph_layout.layout
    else:
        return error_404.layout

if __name__ == '__main__':
    print("starting server")
    app.run_server(debug=True)