import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1('Dash Tutorial Intro'),
    html.Div(id="container",
            children=[html.Div(
                id="elem",  
                children=[html.Div(
                    className="elem-cell",
                    children=[html.Span('They see me rolling', className="visual-elem")]
                )]
            )]
        ),
    
    dcc.Graph(id='example',
            figure={
                'data': [
                    {'x': [1,2,3,4,5], 'y': [5,6,4,5,2], 'type': 'line', 'name':'boats'},
                    {'x': [1,2,3,4,5], 'y': [1,2,8,5,4], 'type': 'bar', 'name':'cars'},
                    ],
                'layout': {
                    'title':'Basic Stats Charts',
                    }
            }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)