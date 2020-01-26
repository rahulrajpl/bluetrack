import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objects as go
from collections import deque
import pandas as pd
import subprocess
import os
from time import sleep
from PIL import Image;

img = Image.open('docs/rm3.jpg')

# For reading the last few lines of sensor data values stored in a file
def tail():
    result = subprocess.run(['tail', '-1', 'sensor/GetData/steps.txt'], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8') 

# For offline steps plotting
# file = open('sensor/GetData/steps.txt', 'r') 
# file.readline()

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
    
    # For real-time plot
    new_X = str(tail()).split(',')[1]
    new_Y = str(tail()).split(',')[2]

    # For simulated real-time plot
    # new_X = file.readline().split(',')[1]
    # new_Y = file.readline().split(',')[2]

    # print(new_X, new_Y)

    if not (X==new_X and Y==new_Y):
        X.append(new_X)
        Y.append(new_Y)

    # Add trace
    data = go.Scatter(
        x = list(X),
        y = list(Y),
        name = 'Scatter',
        # mode = 'lines+markers'
        mode = 'lines'  
    )

    # Layout the map
    x_range = [-6, 25]
    y_range = [-2, 25]

    layout = go.Layout(xaxis=dict(range=x_range),
                        yaxis=dict(range=y_range),
                        height=500,
                        showlegend=False,
                        )
    
    # Create figure
    fig = go.Figure(
        data = [data],
        layout=layout
    )

    # Add images
    fig.add_layout_image(
            go.layout.Image(
                source=img,
                xref="x",
                yref="y",
                x=x_range[0],
                y=y_range[1],
                sizex=30,
                sizey=30,
                sizing="stretch",
                opacity=0.5,
                layer="below")
    )

    # Set templates
    fig.update_layout(template="plotly_white")

    return fig

if __name__=='__main__':
    app.run_server(debug=True)