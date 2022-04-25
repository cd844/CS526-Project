from dash import Dash, html, dcc, Input, Output, callback
import pandas as pd
layout = html.Div([
	html.H5("Top 10 layout", className = "pretty_container"),
	html.Div(id = "list", className = "pretty_container")
	]
)


@callback(
    Output('list', 'children'),
    Input('data-all', 'data')
)
def update_list(data_all):
    df = pd.read_json(data_all)
    n = min([len(df), 10])
    print(n)
    list_contents = [None for i in range(0,n)]
    for i in range(0, n):
        repo = df.iloc[i]
        markup_i = [ html.A(html.H5(repo['name']), href=repo['html_url'])]
        markup_i += [html.A(repo.owner["login"], href = repo.owner['html_url']), html.Br()]
        markup_i += [repo.description, html.Br()]
        markup_i += [f"watchers_count: {repo.watchers_count}", html.Br()]
        list_contents[i] = html.Div(markup_i)

    return list_contents