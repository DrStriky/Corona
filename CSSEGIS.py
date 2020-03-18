import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from datetime import datetime, timedelta, date
from time import mktime

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objs as go

from DataPreparation import load_covid19_data
from DataPlotting import plotdata
from ParameterEstimation import parameterestimation, addmeasures
from SIR import SIRmodel


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

data = load_covid19_data()

# plotdata(data['confirmed_nzd']['data'], title='confirmed (normalized)', ylabel='confirmend/capita (%)')
# plotdata(data['deaths_nzd']['data'], title='deaths (normalized)', ylabel='death/capita (%)')
# plotdata((data['deaths_nzd']['data']/data['confirmed_nzd']['data']).replace([np.inf, -np.inf], np.nan), title='deaths per confirmed', ylabel='death/confirmed')

# # diff/(confirmend-diff-death-recovered)
# plotdata(data['confirmed_nzd']['data'].diff().div((data['confirmed_nzd']['data']-data['confirmed_nzd']['data'].diff()-data['deaths_nzd']['data']-data['recovered_nzd']['data'])), title='spreading rate per day', ylabel='spreading rate/day', smoothdays=2)


# (data['confirmed_nzd']['data']-data['recovered_nzd']['data']-data['deaths_nzd']['data'])['KOR']


# parameter = parameterestimation(data['confirmed']['data'], 'ITA', output=True)
# SIRmodel(data, 'ITA', parameter, forecast=300, output=True)
# parameter = addmeasures(parameter, datetime(2020, 3, 8), 0.6)
# SIRmodel(data, 'ITA', parameter, forecast=300, output=True)

parameter = parameterestimation(data['confirmed']['data'], 'AUT', output=True)
SIRmodel(data, 'AUT', parameter, forecast=300, output=True)
parameter = addmeasures(parameter, date(2020, 3, 8), 0.6)
SIR_data = SIRmodel(data, 'AUT', parameter, forecast=300, output=True)

# Dash part
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([html.Div([html.H1('Covid-19 data by country')],
                                style={'textAlign': 'center', 'padding-bottom': '30'}),
                       html.Div(children='Programmed by Jonathan & Florian under quarantine in dash'),
                       html.Div([html.Span('Metric to display : ', className='six columns',
                                           style={'text-align': 'right', 'width': '40%', 'padding-top': 10}),
                                 dcc.Dropdown(id='metric-selected', value='confirmed',
                                              options=[{'label': 'infected', 'value': 'confirmed'},
                                                       {'label': 'infected normalizied', 'value': 'confirmed_nzd'},
                                                       {'label': 'recovered', 'value': 'recovered'},
                                                       {'label': 'recovered normalizied', 'value': 'recovered_nzd'},
                                                       {'label': 'deaths', 'value': 'deaths'},
                                                       {'label': 'deaths normalizied', 'value': 'deaths_nzd'}],
                                              style={'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto',
                                                     'width': '70%'},
                                              className='six columns')], className='row'),
                       html.Div([dcc.Slider(id='date_Slider',
                                            updatemode='mouseup',
                                            min=mktime(data['recovered_nzd']['data'].index.min().timetuple()),
                                            max=mktime(data['recovered_nzd']['data'].index.max().timetuple()),
                                            step=mktime((date.today()+timedelta(days=1)).timetuple())-mktime(date.today().timetuple()),
                                            value=mktime((date.today()-timedelta(days=1)).timetuple()),
                                            marks={int(mktime(xx.timetuple())): {'label': xx.isoformat(), 'style': {'writing-mode': 'vertical-rl', 'text-orientation': 'use-glyph-orientation'}} for xx in data['recovered_nzd']['data'][np.arange(len(data['recovered_nzd']['data'])) % 2 == 0].index},
                                            )], style={'marginBottom': '5em'}
                                ),
                       html.Div([dcc.Graph(id='graph_map')], style={'display': 'inline-block', 'width': '49%', 'vertical-align': 'top'}),
                       html.Div([dcc.Graph(id='graph_data',
                                 figure={'data': [
                                     {'x': SIR_data.index, 'y': SIR_data['S'].values, 'type': 'line', 'name': 'S'},
                                     {'x': SIR_data.index, 'y': SIR_data['I'].values, 'type': 'line', 'name': 'I'},
                                     {'x': SIR_data.index, 'y': SIR_data['R'].values, 'type': 'line', 'name': 'R'}],
                                     'layout': {'title': 'SIR model for AUT'}
                                     }
                                 ),
                                 dcc.Graph(id='graph_model',
                                 figure={'data': [
                                     {'x': SIR_data.index, 'y': SIR_data['S'].values, 'type': 'line', 'name': 'S'},
                                     {'x': SIR_data.index, 'y': SIR_data['I'].values, 'type': 'line', 'name': 'I'},
                                     {'x': SIR_data.index, 'y': SIR_data['R'].values, 'type': 'line', 'name': 'R'}],
                                     'layout': {'title': 'SIR model for AUT'}
                                     }
                                 )], style={'display': 'inline-block', 'width': '49%'})
                       ], className='container', style={'width': '1500px', 'max-width': '1700px'})


@app.callback(
    dash.dependencies.Output('graph_map', 'figure'),
    [dash.dependencies.Input('metric-selected', 'value'), dash.dependencies.Input('metric-selected', 'options'), dash.dependencies.Input('date_Slider', 'value')]
)

def update_figure(selected, options, setdate):
    trace = go.Choropleth(locations=data[selected]['data'].T.index,  # Spatial coordinates
                          z=data[selected]['data'].T[date.fromtimestamp(setdate)],  # Data to be color-coded
                          locationmode='ISO-3',  # set of locations match entries in `locations`
                          colorscale='Viridis',
                          zmin=0,
                          zmax=np.nanquantile(data[selected]['data'].T[date.fromtimestamp(setdate)], q=0.95),
                          colorbar_title=[entry['label'] for entry in options if entry['value'] == selected][0])
    return {'data': [trace],
            'layout': go.Layout(title=[entry['label'] for entry in options if entry['value'] == selected][0], height=700, geo={'showframe': False, 'showcoastlines': False, 'projection': {'type': 'miller'}})}


if __name__ == '__main__':
    app.run_server(debug=False)
