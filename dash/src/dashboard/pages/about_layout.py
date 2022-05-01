import dash_dangerously_set_inner_html as ddsih

from dash import html

def load_about_content():
    print("running load_about")
    with open('src/dashboard/assets/about_content.html', 'r') as file:
        about_content = file.read()
    file.close()
    return about_content
# the proper way to do this would probably be to have a flask route handle this idk
layout = html.Div([html.H2("Landing Page"), ddsih.DangerouslySetInnerHTML(load_about_content())],  id = 'about-content', className = 'pretty_container')

