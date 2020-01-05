import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque

X = deque(maxlen=20)
Y = deque(maxlen=20)
X.append(1)
Y.append(1)

app = dash.Dash(__name__)
app.layout = html.Div([
    
    dcc.Graph(
        id='live-graph',
        animate=True
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
    X.append(X[-1]+X[-1]*(random.uniform(-50,50)))
    Y.append(Y[-1]+Y[-1]*(random.uniform(-50,50)))

    data = go.Scatter(
        x = list(X),
        y = list(Y),
        name = 'Scatter',
        mode = 'lines+markers'
    )
    # return {'data':[data],
    #         'layout': go.Layout(xaxis=dict(range=[min(X), max(X)]),
    #                             yaxis=dict(range=[min(Y), max(Y)])
    #                             )
    #         }
    return {'data':[data],
            'layout': go.Layout(xaxis=dict(range=[1, 100]),
                                yaxis=dict(range=[1, 100])
                                )
            }

if __name__=='__main__':
    app.run_server(debug=True)