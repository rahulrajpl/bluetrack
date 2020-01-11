import plotly
# print(plotly.__version__)

import numpy as np
import plotly.graph_objects as go

u = np.linspace(-8, 8, 100)
x, y = np.meshgrid(u, u)
r = np.sqrt(x**2+y**2)
