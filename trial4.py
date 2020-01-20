import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque
import pandas as pd
import subprocess
import os

# For reading the last few lines of sensor data values stored in a file
def tail():
    result = subprocess.run(['tail', '-1', 'data.csv'], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8') 

X = deque(maxlen=100)
Y = deque(maxlen=100)

#Initial data
data = tail()
X.append(data.split(',')[1])
Y.append(data.split(',')[2])

app = dash.Dash(__name__)
app.layout = html.Div([
    
    dcc.Graph(
        id='live-graph',
        animate=False,
        config={
            'autosizable':True,
            'scrollZoom':True,
            'displayModeBar':True
        }
        ),

    dcc.Interval(
        id='graph-update',
        interval=1000,
        n_intervals=0
    ),

    ]
)

@app.callback(
    Output('live-graph', 'figure'),
    [Input('graph-update','n_intervals')]
)
def update_graph(n):
    global X
    global Y

    data = tail()
    new_X = data.split(',')[1]
    new_Y = data.split(',')[2]
    if not (X==new_X and Y==new_Y):
        X.append(data.split(',')[1])
        Y.append(data.split(',')[2])

    # X.append(X[-1]+(random.uniform(-5,5)))
    # Y.append(Y[-1]+(random.uniform(-5,5)))

    data = go.Scatter(
        x = list(X),
        y = list(Y),
        name = 'Scatter',
        # mode = 'lines+markers'
        mode = 'lines'
        
    )

    layout = go.Layout()

    return {'data':[data],
            'layout': go.Layout(xaxis=dict(range=[1, 500]),
                                yaxis=dict(range=[1, 500]),
                                height=500,
                                showlegend=False
                                )
            }

if __name__=='__main__':
    app.run_server(debug=True)