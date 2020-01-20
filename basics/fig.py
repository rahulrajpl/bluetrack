import plotly.graph_objects as go 

fig = go.Figure(data=[go.Bar(y=[3,2,1,4])],
                layout_title_text='A Figure'
                )

fig.show()