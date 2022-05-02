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
        dcc.Graph(id = 'bar-lang-vs-count'),
        #html.Div(ddsih.DangerouslySetInnerHTML(load_pie()), className = "pretty_container"),
        dcc.Graph(id = 'pie-lang-vs-count'),
        dcc.Markdown('''This is a languages vs its Count  plot, that shows how frequently each programming languages are used in the projects/ repositories. Javascript is one of the most used languages in most of the repositories followed by CSS.'''),
        #html.H3(''' The Pie chart above shows the distribution of all the languages in the entire dataset. It shows the contribution of each language in the data that was scrapped. It looks like Javascript ,HTML and CSS have been the most popular programming languages . '''),
        dcc.Graph(id = 'scatter-lang-vs-watchers'),
        dcc.Markdown(''' The plot above is a languages vs watcher’s count scatter plot that shows how frequently a certain repository that had the above-mentioned language as the highest contributor were viewed. This reflects how  popular a repository is for that particular language. It can be noticed how a repository that made use of c++ the most has the highest watcher’s count followed by JS. This also shows the distribution based on the popularity of each language'''),
        dcc.Graph(id = 'scatter-lang-vs-fork'),
        dcc.Markdown('''The bar plot about compares how frequently the above-mentioned topic repository was created. It shows that python containing projects were created more than others.
        '''),
        dcc.Graph(id = 'bar-topics-vs-count'),
        dcc.Markdown(''' The languages vs fork_count compares which repositories were interesting based on how frequently they were forked owing to their importance. Repositories in python, JS and Java have been forked more frequently as compared to others. 
        '''),
        html.Div(id = 'dummy_input_insights'),
    ],
    className = "pretty_container"
)
