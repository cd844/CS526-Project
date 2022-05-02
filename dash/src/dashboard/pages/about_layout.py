#import dash_dangerously_set_inner_html as ddsih

from dash import html, dcc

#def load_about_content():
#    print("running load_about")
#    with open('./assets/about_content.html', 'r') as file:
#        about_content = file.read()
#    file.close()
#    return about_content
# the proper way to do this would probably be to have a flask route handle this idk
#layout = html.Div([html.H2("Landing Page"), ddsih.DangerouslySetInnerHTML(load_about_content())],  id = 'about-content', className = 'pretty_container')

layout = html.Div([
    dcc.Markdown('''#### Welcome to Repo Story!'''),
    html.Br(),
    dcc.Markdown(''' Github is one of the most popular online platforms for hosting code and managing software projects. It has a wide range of users including students, programmers, computer scientists, recruiters and management, and academics. Because of its ubiquity, it is the de facto platform for people around the world to share their code, and is often used by industry to evaluate hiring candidates programming abilities.'''),
    html.Br(),
    dcc.Markdown(''' There are over 200 million repositories hosted on Github as of 2022. While Github has a search function and a public API to retrieve information on these repositories, its lack of sophisticated search options and throttling of API makes it difficult for the average user to search for repositories with specific attributes (ie languages or topics) or to look at trends on the platform as a whole.'''),
    html.Br(),
    dcc.Markdown(''' That is where "Get The Repo Story" comes in the picture. It is a user friendly application where students can compare trends on the platform and get the most interesting repository based on their inputs. With maximum interaction possible, user can not only find specific repositories but also view how topics and languages are related to one another with the help of visualizations.'''),
    html.Br(),
    dcc.Markdown(""" GTRS makes use of Plotly for enhancing the interactivity and visualization the plots in the best way possible. Our dataset consists of 2 million records scrapped using Github’s API. Our project uses a Python script for data scrapping, Pandas for analysis, SQLite for database functionality, and a web application built using all of the above tools along with flask and Plotly-Dash. The web application's core feature is a dashboard with interactive visualizations created with Plotly-Dash. We have also made use of the 3d-force-directed graph library for more sophisticated visualizations using graphs that cannot be implemented with Plotly.""")
], className = 'pretty_container')


