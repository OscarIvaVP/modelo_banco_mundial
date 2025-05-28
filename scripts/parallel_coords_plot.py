
# conda: OWF_plot

import glob
import pandas as pd
import numpy as np 
from itertools import product
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import xarray as xr

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output


# Read the xarray where the performance metrics are stored
cst = xr.open_dataset('../results/CST/OWF_CST_annual_deficit_Mm3.nc')
# Convert it to a pandas dataframe
df_template = cst.to_dataframe().reset_index()
df = df_template[['basin', 'dt', 'dp', 'Dfw', 'Dirr', 'Dliv', 'dispatch']]
df.drop_duplicates(inplace=True)

# List the metrics that we will plot
frequencies = ['freq_annual_deficit_urban', 'freq_annual_deficit_rural', 'freq_annual_deficit_livestock',
               'freq_annual_deficit_agriculture', 'freq_annual_deficit_envflow']

for metric in frequencies:
    df_temporary = cst[metric].mean(dim='real').to_dataframe().reset_index()
    df[metric] = df_temporary[metric].values



# Shape the dataframe to be plotted
df['Dfw'] = df['Dfw'].astype(int)
df['Dirr'] = df['Dirr'].astype(int)  
df['Dliv'] = df['Dliv'].astype(int)
mapping = {'FCFS': 0, 'PE': 1}
with pd.option_context('future.no_silent_downcasting',True):
    df['dispatch'] = df['dispatch'].replace(mapping).infer_objects(copy=False)

# Change the Delta P so that values range from -30% to +30%
df['dp'] = df['dp'] - 100


# Create Dash app
app = dash.Dash(__name__)

# Set up the layout
app.layout = html.Div([
    html.H1("Parallel Coordinates Plot"),
    dcc.Dropdown(
        id='basin-dropdown',
        options=[
            {'label': i, 'value': i} for i in df['basin'].unique()],
            value='Metica'),
    dcc.Graph(id='parallel-coordinates-plot')
])

# Set up the callback function  
@app.callback(
    Output(component_id='parallel-coordinates-plot', component_property='figure'),
    Input(component_id='basin-dropdown', component_property='value')
)

def update_graph(basin):
    df_plot_basin = df[df['basin'] == basin]

    fig = go.Figure(data=
        go.Parcoords(
            line= dict(color=df_plot_basin['dispatch'], colorscale=[[0, 'red'], [1, 'blue']],
                       showscale=False),
            dimensions= list([
                dict(range=[0,5], label='DT (C)', values=df_plot_basin['dt'],
                     tickvals=[0,1,2,3,4,5], ticktext=['0', '1', '2', '3', '4', '5']),
                dict(range=[-30,+30], label='DP (%)', values=df_plot_basin['dp'],
                     tickvals=[-30, -20, -10, 0, 10, 20, 30], ticktext=['-30%', '-20%', '-10%', '0', '+10%', '+20%', '+30%']),
                #dict(range=[1,5], label='Realization', values=df_plot_basin['real']),
                dict(range=[2022,2050], label='Dfw', values=df_plot_basin['Dfw'],
                     tickvals=[2022, 2030, 2040, 2050], ticktext=['Proj-2022', 'Proj-2030', 'Proj-2040', 'Proj-20250']),
                dict(range=[2022,2050], label='Dirr', values=df_plot_basin['Dirr'],
                     tickvals=[2022, 2030, 2040, 2050], ticktext=['Proj-2022', 'Proj-2030', 'Proj-2040', 'Proj-20250']),
                dict(range=[2022,2050], label='Dliv', values=df_plot_basin['Dliv'],
                     tickvals=[2022, 2030, 2040, 2050], ticktext=['Proj-2022', 'Proj-2030', 'Proj-2040', 'Proj-20250']),
                #dict(range=[0,1], label='Dispatch', values=df_plot_basin['dispatch']),
                dict(range=[0,100], label='Freq. Urban\nDeficit (%)', values=df_plot_basin['freq_annual_deficit_urban']),
                dict(range=[0,100], label='Freq. Rural\nDeficit (%)', values=df_plot_basin['freq_annual_deficit_rural']),
                dict(range=[0,100], label='Freq. Livestock\nDeficit (%)', values=df_plot_basin['freq_annual_deficit_livestock']),
                dict(range=[0,100], label='Freq. Agriculture\nDeficit (%)', values=df_plot_basin['freq_annual_deficit_agriculture']),
                dict(range=[0,100], label='Freq. Envflow\nDeficit (%)', values=df_plot_basin['freq_annual_deficit_envflow'])
            ]),
            unselected=dict(line=dict(color='grey', opacity=0.1)),
        )
    )

    fig.update_traces(labelfont=dict(size=18),
                      tickfont=dict(size=16, color='black', family='Arial', weight='bold'))

    
    # Add legend manually
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=20, color='blue'),
        legendgroup='PE', showlegend=True, name='PE'
    ))

    

    fig.add_trace(go.Scatter(
        x=[None], y=[None], 
        mode='markers',
        marker=dict(size=20, color='red'),
        legendgroup='FCFS', showlegend=True, name='FCFS'
    ))

    fig.update_layout(height=1200, width=2500, plot_bgcolor='whitesmoke')
        

    return fig

# Run local server
app.run(debug=True, use_reloader=False)


