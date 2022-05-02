import generate_static_plots as gsp
import dash_dangerously_set_inner_html as ddsih
from dash import Dash, html, dcc, Input, Output, callback

@callback(
    Output('bar-lang-vs-count', 'figure'),
    Output('pie-lang-vs-count', 'figure'),
    Output('scatter-lang-vs-watchers', 'figure'),
    Output('scatter-lang-vs-fork', 'figure'),
    Output('bar-topics-vs-count', 'figure'),
    Input('dummy_input_insights', 'children')
)
def load_figures(dummy_input):
    print("loading static plots")
    df = gsp.create_df()
    (barfig_lang_count, piefig_lang_count) = gsp.lang_vs_count(df)
    scatter_lang_watcher = gsp.lang_vs_watcher(df)
    scatter_lang_fork = gsp.lang_vs_fork(df)
    bar_topics_count = gsp.topics_vs_count(df)
    return barfig_lang_count,piefig_lang_count, scatter_lang_watcher, scatter_lang_fork, bar_topics_count



layout = html.Div([
        html.Div(html.H5("Insights")),
        #html.Div(ddsih.DangerouslySetInnerHTML(load_pie()), className = "pretty_container"),
        dcc.Graph(id = 'bar-lang-vs-count'),
        dcc.Graph(id = 'pie-lang-vs-count'),
        dcc.Graph(id = 'scatter-lang-vs-watchers'),
        dcc.Graph(id = 'scatter-lang-vs-fork'),
        dcc.Graph(id = 'bar-topics-vs-count'),
        html.Div(id = 'dummy_input_insights'),
    ],
    className = "pretty_container"
)