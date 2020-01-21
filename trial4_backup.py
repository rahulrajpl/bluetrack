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
from PIL import Image;

img = Image.open('docs/rm3.png')

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

    # data = go.Scatter(
    #     x = list(X),
    #     y = list(Y),
    #     name = 'Scatter',
    #     # mode = 'lines+markers'
    #     mode = 'lines'    
    # )

    # layout = go.Layout(xaxis=dict(range=[1, 500]),
    #                     yaxis=dict(range=[1, 500]),
    #                     height=500,
    #                     showlegend=False,
    #                   
    #                     )

    # fig = {'data':[data],
    #         'layout':  layout
    #         }

    

    # Add trace
    data = go.Scatter(
        x = list(X),
        y = list(Y),
        name = 'Scatter',
        # mode = 'lines+markers'
        mode = 'lines'    
    )

    # fig.add_trace(
    #     # go.Scatter(x=[0, 0.5, 1, 2, 2.2], y=[1.23, 2.5, 0.42, 3, 11])
    #     data
    # )

    layout = go.Layout(xaxis=dict(range=[1, 500]),
                        yaxis=dict(range=[1, 500]),
                        height=500,
                        showlegend=False,
                        )
    # Create figure
    fig = go.Figure(
        data = [data],
        layout=layout
    )
        # fig = {'data':[data],
            # 'layout':layout}

    # Add images
    fig.add_layout_image(
            go.layout.Image(
                source=img,
                xref="x",
                yref="y",
                x=0,
                y=500,
                sizex=500,
                sizey=500,
                sizing="stretch",
                opacity=0.5,
                layer="below")
    )

    
    # Set templates
    fig.update_layout(template="plotly_white")


    return fig

if __name__=='__main__':
    app.run_server(debug=True)