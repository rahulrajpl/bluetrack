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
from analytics.Analytics import ObluAnalytics


# For reading the last line of sensor data values stored in a file
def tail():
    result = subprocess.run(['tail', '-1', 'sensor/GetData/steps.txt'], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8') 

# For offline steps plotting
# file = open('sensor/GetData/steps.txt', 'r') 
file = open('analytics/steps_test.txt', 'r') 
# ignoring the first line
file.readline()

img = Image.open('docs/rm3_1.png')

max_trail_limit = 15
X = deque(maxlen=max_trail_limit)
Y = deque(maxlen=max_trail_limit)
# counter = 0
interval = 1000 # Timer for updating the graph in msec

#Initial data
data = tail()
X.append(data.split(',')[1])
Y.append(data.split(',')[2])

external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]

# Variable for storing Departure Score from Analytics
S = deque(maxlen=max_trail_limit)
S.append(5)
# Variable for Time step
T = deque(maxlen=max_trail_limit)
T.append(1)
# Object for analytics
obj = ObluAnalytics(lag_vector_length=max_trail_limit)
UT, centroid, theta = obj.getThresholdScore('analytics/steps_train.txt')

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    style={'backgroundColor': '#111111'},
    children=[

    html.Div(
        className="app-header",
        children=[
            html.Div('bluTrack', className="app-header--title"),
        ]
    ),

    html.Div(
        className="app-header",
        children=[
            html.P('Pedestrian dead reckoning and Outlier Detection in Trajectory Data', className="app-header--sub-head")
        ],
    ),
    #------------two column divs start------
    html.Div([
        html.Div([
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
                        'displayModeBar':False,    
                    }
                    )
                ],
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
                ),
        ], className="six columns"),

        html.Div([
            # html.H3('Column 2'),
            # dcc.Graph(id='g2', figure={'data': [{'y': [1, 2, 3]}]})
            # html.P('Analytics here. Coming soon', className='header-analytics'),
            dcc.Graph(id='app-analytics', animate=True),
            dcc.Interval(id='analytics-update',interval=interval, n_intervals=0)
        ], className="six columns"),
    ], className="row"),
    #------two columns divs end------------
    ]
)

@app.callback(Output('app-analytics', 'figure'),
        [Input('analytics-update', 'n_intervals')])
def update_analytics(n):
    global S, obj, UT, centroid, theta, max_trail_limit
    global X
    global Y
    # S.append(S[-1]+(random.uniform(-.5,.5)))
    T.append(T[-1]+1)
    # print([pd.DataFrame(x) for x in zip(list(X),list(Y))])
    # print(pd.DataFrame([sum(x)/2 for x in zip(list(X), list(Y))]))
    # print('UT={}, centroid={}, theta={}'.format(UT, centroid, theta))
    if len(T)>=max_trail_limit:
        
        # stream = [sum(x)/2 for x in list(zip(list(X),list(Y)))]
        # df = pd.DataFrame(list(X))
        # df = df[0] / 2
        score = obj.getScore(UT, centroid, X, Y )
        print(score)
        S.append(score)

    data = go.Scatter(
            x = list(T),
            y = list(S),
            name = 'Realtime Anomaly Score',
            mode = 'lines',
            # showlegend=False,
        )
    threshold_data = go.Scatter(
            x = [min(T),max(T)+20],
            y = [float(theta)]*50,
            name = 'Threshold Score',
            mode = 'lines',
            # showlegend=False,
        )       
    layout = go.Layout(
                    # title='Analytics-Live',
                    xaxis=dict(range=[min(T),max(T)+20]),
                    # yaxis=dict(range=[min(S),max(S)]),
                    yaxis=dict(range=[0,100]),
                    template='plotly_dark',
                    uirevision='analytics-update',
                    
                    
        )
    
    fig = go.Figure(data = [data, threshold_data],
                    layout = layout)
    fig.update_layout(xaxis_title="No of Steps",
                    yaxis_title="Score",)
    legend=dict(
        x=0,
        y=1,
        traceorder="normal",
        font=dict(
            family="sans-serif",
            size=12,
            color="black"
        ),
        bgcolor="LightSteelBlue",
        bordercolor="Black",
        borderwidth=2
    )       
    fig.update_layout(legend=legend)
    return fig

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
    # For simulating data saved in real-time
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
    
    # # Add trace
    data = go.Scatter(
        x = list(X),
        y = list(Y),
        name = 'Scatter',
        mode = 'lines+markers'
        # mode = 'lines'  
    )

    x_range = [-20, 65]
    y_range = [-30, 65]

    layout = go.Layout(xaxis=dict(range=x_range),
                        yaxis=dict(range=y_range),
                        height=500,
                        showlegend=False,
                        uirevision='graph-update',
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        )
    
    # Create figure
    fig = go.Figure(
        data = [data],
        layout=layout
    )

    # Fine tune layout
    # fig.update_layout(template="plotly_white")
    fig.update_xaxes(showticklabels=False, zeroline=False)
    fig.update_yaxes(showticklabels=False, zeroline=False)
    fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)
    fig.update_layout(dragmode='pan')
    return fig

if __name__=='__main__':
    # app.run_server(debug=True, dev_tools_hot_reload=False)
    app.run_server(debug=True)