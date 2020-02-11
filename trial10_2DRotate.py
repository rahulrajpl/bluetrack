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
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# For reading the last few lines of sensor data values stored in a file
def tail():
    result = subprocess.run(['tail', '-1', 'sensor/GetData/steps.txt'], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8') 

# For offline steps plotting
file = open('sensor/GetData/steps.txt', 'r') 
file.readline()

X = deque(maxlen=100)
Y = deque(maxlen=100)

#Initial data
data = tail()
X.append(data.split(',')[1])
Y.append(data.split(',')[2])

app = dash.Dash(__name__)
# colors = {
#     'background': '#111111',
#     'text': '#7F0000'
# }
app.layout = html.Div(children=[

    html.Div(id="container",
            children=[html.Div(
                id="elem",  
                children=[html.Div(
                    className="elem-cell",
                    children=[html.Span('They see me rolling', className="visual-elem")]

                )]
            )]
        ),


    html.Div(
        className="app-header",
        
        children=[
            html.Div('ObluTrack', className="app-header--title"),
        ]
    ),

    
    html.Div(
        className="app-header",
        children=[
            html.P('Pedestrian dead reckoning and Outlier Detection in Trajectory Data', className="app-header--sub-head")
        ]
    ),

    html.Div(
        className="app-image",
        children=[
        html.Img(src=img, alt='bg_image')
        ]
        ),

    html.Div(
        className="app-plot",
        id="app-plotid",
        children=[
            dcc.Graph(
            id='live-graph',
            animate=False,
            config={
                'autosizable':True,
                'scrollZoom':True,
                'displayModeBar':True
            }
            )
        ]
        ),

    dcc.Interval(
        id='graph-update',
        interval=10000,
        n_intervals=0
        )
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
    # new_X = str(tail()).split(',')[1]
    # new_Y = str(tail()).split(',')[2]

    # For simulated real-time plot
    if not file=="":
        new_X = file.readline().split(',')[1]
        new_Y = file.readline().split(',')[2]
    else:
        file.seek(0,0)
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
    x_range = [-10, 65]
    y_range = [-30, 65]

    layout = go.Layout(xaxis=dict(range=x_range),
                        yaxis=dict(range=y_range),
                        height=500,
                        showlegend=False,
                        uirevision='graph-update',
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                        )
    
    # Create figure
    fig = go.Figure(
        data = [data],
        layout=layout
    )

    # Set templates
    fig.update_layout(template="plotly_white")
    fig.update_xaxes(showticklabels=False, zeroline=False)
    fig.update_yaxes(showticklabels=False, zeroline=False)
    fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)
    return fig

if __name__=='__main__':
    app.run_server(debug=True, dev_tools_hot_reload=False)
    # app.run_server(debug=True)