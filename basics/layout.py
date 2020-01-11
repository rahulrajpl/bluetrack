import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objects as go
import plotly.express as px

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

X = []
Y = []
Z = []
X.append(random.uniform(50,60))
Y.append(random.uniform(50,55))
Z.append(random.uniform(50,55))

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    
    html.H1(
        id = 'main-header',
        children='Hello Dash',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
        ),

    html.Div(children='Dash: A web application framework for Python.', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    dcc.Graph(
        id='live-graph',
        animate = True  
    ),

    dcc.Interval(
        id='graph-update',
        interval=2000,
        n_intervals=0
    ),
])

@app.callback(
    Output('live-graph', 'figure'),
    [Input('graph-update', 'n_intervals')]
)
def update_graph(n):
    global X
    global Y
    global Z
    X.append(X[-1]+(random.uniform(-5,5)))
    Y.append(Y[-1]+(random.uniform(-5,5)))
    Z.append(Z[-1]+(random.uniform(-5,5)))


    scatter1 = dict(mode = "lines+markers",name = "Cluster 0",type = "scatter3d",    
        x = list(X),y = list(Y),z = list(Z),
        marker = dict( size=1, color='red')
    )

    layout = dict(
        scene = dict(
            xaxis = dict( zeroline=True ),
            yaxis = dict( zeroline=True ),
            zaxis = dict( zeroline=True )),
        height=700)

    fig = dict( data=[scatter1], layout=layout )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)