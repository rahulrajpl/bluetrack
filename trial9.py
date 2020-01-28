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
import plotly.express as px

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
Z = deque(maxlen=100)
interval = 3000
#Initial data
data = tail()
X.append(data.split(',')[1])
Y.append(data.split(',')[2])

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}
app.layout = html.Div(
    # style={'backgroundColor': colors['background'],
    #                         }, 
    children=[
    html.H1('ObluTrack',
            style={
            'textAlign': 'center',
            'color': colors['text']
        }),

    html.Div(children=[
        html.P('Deck reckoning of security personnel'),
        html.P('Data analytics on deck reckoning data to identify stealthy diversion of surveillance route')
        ],
        style={
        'textAlign': 'center',
        'color': colors['text'],
        
        }), 
    
    html.Div(children=[
        dcc.Graph(
        id='live-graph-analytics',
        animate=False,
        config={
            'autosizable':True,
            'scrollZoom':True,
            'displayModeBar':True
        }
        ),
    ]
        ), 

    html.Div(children=[
        html.Img(src=img,
                alt='bg_image', style={'height':'75%',
        'width':'75%'}),
        ],
        style={
        'textAlign': 'center',
        'opacity': '0.3',
   
        }),
    
    html.Div(children=[
        dcc.Graph(
        id='live-graph',
        animate=False,
        config={
            'autosizable':True,
            'scrollZoom':True,
            'displayModeBar':True
        }
        ),
    ],
    style={
        'position': 'absolute',
        'top': '87%',
        'left': '5%',
        'right':'5%',
        }
        ),
    

    dcc.Interval(
        id='graph-update',
        interval=interval,
        n_intervals=0
        ),

    dcc.Interval(
        id='graph-update-analytics',
        interval=interval,
        n_intervals=0
        )
    ]
)

df = pd.read_csv('docs/analytics.csv')

@app.callback(
    Output('live-graph-analytics', 'figure'),
    [Input('graph-update-analytics','n_intervals')]
)
def update_graph_analytics(n):
    '''
    Analytics code here
    '''
    
    fig = px.line(df, x='Date', y='AAPL.High')

    return fig


@app.callback(
    Output('live-graph', 'figure'),
    [Input('graph-update','n_intervals')]
)
def update_graph(n):
    global X
    global Y
    global Z
    # For real-time plot
    # new_X = str(tail()).split(',')[1]
    # new_Y = str(tail()).split(',')[2]

    # For simulated real-time plot
    if not file=="":
        new_X = file.readline().split(',')[1]
        new_Y = file.readline().split(',')[2]
        # new_Z = file.readline().split(',')[3]
        new_Z = 0
    else:
        file.seek(0,0)
    # print(new_X, new_Y)

    if not (X==new_X and Y==new_Y and Z==new_Z):
        X.append(new_X)
        Y.append(new_Y)
        Z.append(new_Z)

    # Add trace
    data = go.Scatter3d(type='scatter3d',
                        x=list(X),
                        y = list(Y),
                        z = list(Z),
                        mode='lines'
                ) 
    
    
    layout = go.Layout(
        title= 'Plotly Graph',
        scene= dict(
                xaxis= dict(
                    title= '',
                    autorange= True,
                    showgrid= False,
                    zeroline= False,
                    showline= False,
                    # autotick= True,
                    ticks= '',
                    showticklabels= False,
                    showbackground= False
                ),
                yaxis= dict(
                    title= '',
                    autorange= True,
                    showgrid= False,
                    zeroline= False,
                    showline= False,
                    # autotick= True,
                    ticks='',
                    showticklabels= False,
                    showbackground= False
                ),
                zaxis= dict(
                    title= '',
                    autorange= True,
                    showgrid= False,
                    zeroline= False,
                    showline= False,
                    # autotick= True,
                    ticks= '',
                    showticklabels= False,
                    showbackground= False
                )
            ),
        margin= dict(
            l= 0,
            r= 0,
            b= 0,
            t= 0
        ),

        showlegend= True,
        uirevision='graph-update',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    
    # # Create figure
    fig = go.Figure(
        data = [data],
        layout=layout
    )

    

    return fig

if __name__=='__main__':
    app.run_server(debug=True)