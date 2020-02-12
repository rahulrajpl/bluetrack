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
from PIL import Image
import numpy as np


# For reading the last line of sensor data values stored in a file
def tail():
    result = subprocess.run(['tail', '-1', 'sensor/GetData/steps.txt'], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8') 

# Define a function that rotates 
# about a point, (cx, cy), the points of coordinates given in the 
# arrays x, y, of the same shape:
def rotation2d(x, y, theta, cx=0, cy=0):
    #rotation of the points (x[k],y[k])k=0, ...(len(x)-1) about (cx, cy), with theta radians
    # x: array of x-coordinates of the rotating points 
    # y: array of y-coordinates --""--
    
    x, y = np.asarray(x), np.asarray(y)
    return cx + np.cos(theta)*x-np.sin(theta)*y, cy + np.sin(theta)*x+np.cos(theta)*y

# def get_sliders(n_frames, fr_duration=100, x_pos=0.0, slider_len=1.0):
#     # Function that returns the slider to control direction of rotation
#     # n_frames: int-  number of animation frames
#     # fr_duration: int - duration in milliseconds of each frame
#     # x_pos:  x-coordinate of the slider starting position
#     # slider_len - float  in (0,1]; gives the slider length as a fraction of x-axis length 
#     return [dict(steps= [dict(method= 'animate',
#                               args= [ [ f'frame{k+1}' ],  #frame name
#                                       dict(mode= 'immediate',
#                                            frame= dict( duration=fr_duration, redraw= False ),
#                                            transition=dict( duration= 0)
#                                           )
#                                     ],
#                               label='' # no label
#                              ) for k in range(n_frames)], 
#                 transition= { 'duration': 0 },
#                 x=x_pos,
#                 len=slider_len)]

# cx, cy = -1.5, 1.5  # (cx, cy) -  the coordinates of the rotating square center


# For offline steps plotting
# file = open('sensor/GetData/steps.txt', 'r') 
file = open('analytics/steps_train.txt', 'r') 
# ignoring the first line
file.readline()

img = Image.open('docs/rm3.jpg')

X = deque(maxlen=15)
Y = deque(maxlen=15)
counter = 0
interval = 1500 # Timer for updating the graph in msec

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
                'displayModeBar':'hover',
                
            }
            )
        ],
        style={
            # 'position': 'absolute',
            # 'top': '15%',
            # 'left': '5%',
            # 'right':'5%',
            # 'textAlign': 'center',
            # 'display': 'block',
            'transform': 'rotate(10deg)',
        } 
    ),

    dcc.Slider(
        id='rotate-slider',
        min=-180,
        max=180,
        step=2,
        value=0
    ),

    html.Div(id='slider-output-container'),

    dcc.Interval(
        id='graph-update',
        interval=interval, 
        n_intervals=0
        )
    ]
)

@app.callback(Output('app-plotid', 'style'), 
        [Input('rotate-slider', 'value')])
def update_style(value):
    return {'transform': 'rotate({}deg)'.format(value)}

@app.callback(
    dash.dependencies.Output('slider-output-container', 'children'),
    [dash.dependencies.Input('rotate-slider', 'value')])
def update_output(value):
    return 'Drag the slider to set orientation of plot. Current: {} deg'.format(value)

@app.callback(
    Output('live-graph', 'figure'),
    [Input('graph-update','n_intervals')]
)
def update_graph(n):
    global X
    global Y
    # global counter
    # counter += interval/1000
    #-----------------------------------------------------
    # For real-time plot
    # new_X = str(tail()).split(',')[1]
    # new_Y = str(tail()).split(',')[2]
    #-----------------------------------------------------

    #-----------------------------------------------------
    # For simulated real-time plot
    if not file=="":
        data = file.readline().split(',')
        new_X, new_Y = data[1], data[2]
    else:
        file.seek(0,0)
    # # print(new_X, new_Y)
    #-----------------------------------------------------

    if not (X==new_X and Y==new_Y):
        X.append(new_X)
        Y.append(new_Y)

    # cx, cy = -1.5, 1.5  # (cx, cy) -  the coordinates of the rotating square center

    # fig = go.Figure()

    # fig.add_scatter(
    #     x = list(X),
    #     y = list(Y),
    #     name = 'Scatter',
    #     mode = 'lines+markers'
    #     )
    
    # # Add trace
    data = go.Scatter(
        x = list(X),
        y = list(Y),
        name = 'Scatter',
        mode = 'lines+markers'
        # mode = ''  
    )

    # Frame definition:
    # theta =  np.linspace(0, 2*np.pi, 36)
    # frames =[]
    # for k in range(len(theta)):
    #     # X, Y  = rotation2d(X,Y, -theta[k], cx=cx, cy=cy) # if the slider is moved to the right, the square rotates clockwise
    #     frames.append(go.Frame(data=[go.Scatter(x=[X[-1]],y=[Y[-1]])],
    #                         name=f'frame{k+1}'
    #                         ))
    # fig.frames = frames

    # fig.update_layout(
    #     xaxis=dict(range=[-10, 65]),
    #     yaxis=dict(range=[-30, 65]),
    #     height=500,
    #     showlegend=False,
    #     uirevision='graph-update',
    #     paper_bgcolor='rgba(0,0,0,0)',
    #     plot_bgcolor='rgba(0,0,0,0)',
    #     sliders=get_sliders(len(frames), fr_duration=100, x_pos=0.0, slider_len=1.0),
    # )
    # Layout the map
    x_range = [-10, 65]
    y_range = [-30, 65]

    layout = go.Layout(xaxis=dict(range=x_range),
                        yaxis=dict(range=y_range),
                        height=500,
                        showlegend=False,
                        uirevision='graph-update',
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        # sliders=get_sliders(360, fr_duration=100, x_pos=0.0, slider_len=1.0),
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
    # app.run_server(debug=True, dev_tools_hot_reload=False)
    app.run_server(debug=True)