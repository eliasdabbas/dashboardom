import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd

app = dash.Dash(__name__, serve_locally=False,
                external_scripts=[
        '//platform-api.sharethis.com/js/sharethis.js#property=5ae10d5b688e0f0017268884&product=inline-follow-buttons',
        'https://cdn.rawgit.com/eliasdabbas/dashboardom/598ed983/scripts/gtag.js',
    ])
server = app.server
app.title = 'Interactive Dashboards | Dashboardom'

app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
    <h1 font-size=40><a href="/"> Dashboardom</a></h1>
    <p>
    <strong>dashboard:</strong>
             noun /ˈdæʃ.bɔːrd/ an interface with a current summary and controls, in graphic form
    <br>

    <strong>-dom:  </strong> wisdom, freedom, random... hopefully not boredom!




        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""


link_style = {'text-decoration': 'underline',
              'color': '#0A4DCC'}

dashboard_df = pd.read_csv('data/dashboards_df.csv', keep_default_na=False)

dashboard_components = html.Div([
    html.Div([
        html.A(dashboard_df['name'][x] + ':',
               href='/' + dashboard_df['dashboard'][x],
               style={'font-size': 20}),
        html.P(),
        html.Div(dashboard_df['description'][x]),
        html.Div([
            'Data: ',
            html.A(dashboard_df['data'][x],
                   href=dashboard_df['data_link'][x])
        ]),
        html.Div([
            'Git repo: ',
            html.A(dashboard_df['git_repo'][x],
                   href=dashboard_df['git_repo'][x])
        ]),
        html.Div('Tags: ' + dashboard_df['tags'][x]),
        html.Hr(style={'width': 400, 'margin-left': '2%'}),
        html.P(), html.P(),  
    ])
    for x in range(len(dashboard_df))
], style={'line-height': '20px'})



app.layout = html.Div([
    html.Div([
        html.Br(),
#         html.A('Dashboardom', style={'font-size': 40, 'text-decoration': 'none'}, 
#                href='/'),
#         html.Div([
#             html.Strong('dashboard: '),
#             "noun /ˈdæʃ.bɔːrd/ an interface with a current summary and controls, in graphic form"
#         ],),
#         html.Div([
#             html.Strong('-dom: '),
#             'wisdom, freedom, random... hopefully not boredom!'
#         ]),
        html.P(),
        html.Hr(style={'width': '80%', 'align': 'center', 'color': '#efefef'}),
    ], style={'margin-left': '5%', }),

    html.Div([
        html.P(), html.P(), html.P(),
        dcc.Dropdown(id='dashboards_dropdown',
                     placeholder='Explore other dashboards:',
                     options=[{'label': name, 'value': dashboard}
                              for name,dashboard in zip(dashboard_df['name'], 
                                                        dashboard_df['dashboard'])]),
    ], style={'width': '30%', 'margin-right': '10%', 'float': 'right',
              'margin-top': -90, 'text-color': '#ff0000'}),
        
    dcc.Location(id='url', refresh=True),
    html.Div(id='content'),
    
    html.P(), html.P(),
    html.Iframe(id='iframe',
                style={'width': '96%', 'height': 1000, 'border': 'none',
                       'scrolling': 'no', 'margin-left': '4%'}),
    
    html.Div(id='dashboard_components',
             children=dashboard_components,
             style={'margin-left': '15%'}),

    html.Div([
        html.P(), html.P(),
        html.Hr(style={'width': '80%', 'align': 'center', 'color': '#efefef'}),
        html.P(),
        html.Div([
            html.Div([
                html.Div('About', style={'font-size': 25}), 
                html.P(),
                html.Div(['A collection of dashboards and apps, made by Elias Dabbas. ', 
                          'For data exploration, learning, fun, ',
                          'prototyping, and sharing.', html.Br(),
                          'Mostly made with Plotly\'s Dash (Python).'])
            ], style={'width': '25%', 'display': 'inline-block'}),
            html.Div([
                html.Div('Connect', style={'font-size': 25}),
                html.P(),
                html.Div(className='sharethis-inline-follow-buttons'),
            ], style={'width': '20%', 'display': 'inline-block',
                      'float': 'right', 'margin-right': '50%'})
        ]),
    ], style={'margin-left': '10%', 'height': 250}),
    html.P(), html.P(), html.P(), html.P(),
    
    ], style={'font-family': 'Palatino', 'background-color': '#fafafa'})


@app.callback(Output('dashboard_components', 'hidden'),
             [Input('url', 'pathname')])
def show_hide_links_to_dashboards(pathname):
    if pathname != '/' and pathname[1:] in dashboard_df['dashboard'].values:
        return True
    return False

@app.callback(Output('iframe', 'hidden'),
             [Input('url', 'pathname')])
def show_hide_iframe(pathname):
    if pathname != '/' and pathname[1:] in dashboard_df['dashboard'].values:
        return False
    return True

@app.callback(Output('iframe', 'src'),
             [Input('url', 'pathname')])
def get_iframe_src(pathname):
    if pathname != '/' and pathname[1:] in dashboard_df['dashboard'].values:
        return 'https://' + pathname[1:] + '.herokuapp.com'
    
@app.callback(Output('url', 'pathname'),
             [Input('dashboards_dropdown', 'value')])
def change_url_based_on_dropdown(value):
    if value is not None:
        return '/' + value

# app.scripts.append_script({
#     'external_url': [
#         '//platform-api.sharethis.com/js/sharethis.js#property=5ae10d5b688e0f0017268884&product=inline-follow-buttons',
#         'https://cdn.rawgit.com/eliasdabbas/dashboardom/598ed983/scripts/gtag.js',
#     ]
# })

if __name__ == '__main__':
    print(app.scripts)
    app.run_server(debug=True)
