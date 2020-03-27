import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from datetime import timedelta, date
from time import mktime

import os

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px

from DataPreparation import load_covid19_data, load_world_data
from DataPlotting import plotdata
from ParameterEstimation import parameterestimation, addmeasures
from SIR import SIRmodel


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

data = load_covid19_data()
world_map = load_world_data()

data['infectionrate'] = dict()
data['infectionrate']['data'] = data['confirmed_nzd']['data'].diff().div((data['confirmed_nzd']['data']-data['confirmed_nzd']['data'].diff()-data['deaths_nzd']['data']-data['recovered_nzd']['data']))

# Dash part
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([html.Div([html.H1('Covid-19 data by country')],
                                style={'textAlign': 'center', 'padding-bottom': '30'}),
                       html.Div([html.Span('Metric to display : ', className='six columns',
                                           style={'text-align': 'right', 'width': '40%', 'padding-top': 10}),
                                 dcc.Dropdown(id='metric-selected', value='confirmed_nzd',
                                              options=[{'label': 'infected', 'value': 'confirmed'},
                                                       {'label': 'infected normalizied', 'value': 'confirmed_nzd'},
                                                       {'label': 'deaths', 'value': 'deaths'},
                                                       {'label': 'deaths normalizied', 'value': 'deaths_nzd'},
                                                       {'label': 'infection rate', 'value': 'infectionrate'},
                                                       {'label': 'recovered', 'value': 'recovered'},
                                                       {'label': 'recovered normalizied', 'value': 'recovered_nzd'},
                                                       ],
                                              style={'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto',
                                                     'width': '70%'},
                                              className='six columns')], className='row'),
                       html.Div([dcc.Slider(id='date_Slider',
                                            updatemode='mouseup',
                                            min=mktime(data['confirmed']['data'].index.min().timetuple()),
                                            max=mktime(data['confirmed']['data'].index.max().timetuple()),
                                            step=mktime((date.today()+timedelta(days=1)).timetuple())-mktime(date.today().timetuple()),
                                            value=mktime((date.today()-timedelta(days=2)).timetuple()),
                                            marks={int(mktime(xx.timetuple())): {'label': xx.isoformat(), 'style': {'writing-mode': 'vertical-rl', 'text-orientation': 'use-glyph-orientation'}} for xx in data['confirmed']['data'][np.arange(len(data['confirmed']['data'])) % 2 == 0].index},
                                            )], style={'marginBottom': '5em'}
                                ),
                       html.Div([dcc.Graph(id='graph_map', clickData={'points': [{'location': 'AUT'}]})
                                 ], style={'display': 'inline-block', 'width': '49%', 'vertical-align': 'top', 'marginTop': '2em'}),
                       html.Div([dcc.Graph(id='graph_data'),
                                 dcc.Graph(id='graph_model')
                                 ], style={'display': 'inline-block', 'width': '49%'}),
                       html.Footer(children='Programmed by Jonathan & Florian under quarantine in dash'),
                       ], className='container', style={'max-width': '1800px'})


def create_map(selected, title, setdate):
    new_data = data[selected]['data'].T[date.fromtimestamp(setdate)].to_frame().reset_index()
    new_data.columns = ['country', 'number']
    figure = px.choropleth_mapbox(data_frame=new_data,
                                  geojson=world_map,
                                  featureidkey='properties.iso_a3',
                                  locations='country',
                                  color='number',
                                  zoom=3,
                                  range_color=(0, np.nanquantile(new_data['number'], q=0.95)),
                                  height=650,
                                  labels={'number': ''},  # title
                                  )
    figure.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    figure.update_layout(mapbox_style='carto-positron', mapbox_center={'lat': 48.210033, 'lon': 16.363449})
    return figure


def create_data_series(data, country, title):
    return {
        'data': [dict(
            x=data.index,
            y=data[country],
            mode='lines+markers'
        )],
        'layout': {
            'height': 400,
            'title': {'text': title+' for '+country},
            'yaxis': {'showgrid': True},
            'xaxis': {'showgrid': True},
            'updatemenus': [{'buttons': [{'args': ['yaxis.type', 'linear'], 'label': 'linear', 'method': 'relayout'}, {'args': ['yaxis.type', 'log'], 'label': 'logarithmic', 'method': 'relayout'}], 'x': 0.05, 'xanchor': 'left'}],
        }
    }


def create_model_series(data, country, title):
    return {
        'data': [dict(x=data.index, y=data['S0'], mode='lines', line={'dash': 'dash', 'color': '#1f77b4'}, name='Susceptible w/o curfew'),
                 dict(x=data.index, y=data['S'], mode='lines+markers', line={'color': '#1f77b4'}, name='Susceptible'),
                 dict(x=data.index, y=data['R0'], mode='lines', line={'dash': 'dash', 'color': '#2ca02c'}, name='Recoverd w/o curfew'),
                 dict(x=data.index, y=data['R'], mode='lines+markers', line={'color': '#2ca02c'}, name='Recoverd'), 
                 dict(x=data.index, y=data['I0'], mode='lines', line={'dash': 'dash', 'color': '#ff7f0e'}, name='Infected w/o curfew'),
                 dict(x=data.index, y=data['I'], mode='lines+markers', line={'color': '#ff7f0e'}, name='Infected')
                 ],
        'layout': {
            'height': 400,
            'title': {'text': 'SIR model for '+country},
            'yaxis': {'showgrid': True},
            'xaxis': {'showgrid': True}
        }
    }


@app.callback(
    dash.dependencies.Output('graph_map', 'figure'),
    [dash.dependencies.Input('metric-selected', 'value'), dash.dependencies.Input('metric-selected', 'options'), dash.dependencies.Input('date_Slider', 'value')]
)
def update_map(selected, options, setdate):
    return create_map(selected, [entry['label'] for entry in options if entry['value'] == selected][0], setdate)


@app.callback(
    dash.dependencies.Output('graph_data', 'figure'),
    [dash.dependencies.Input('graph_map', 'clickData'), dash.dependencies.Input('metric-selected', 'value'), dash.dependencies.Input('metric-selected', 'options')])
def update_data_series(clickData, selected, options):
    return create_data_series(data[selected]['data'], clickData['points'][0]['location'], [entry['label'] for entry in options if entry['value'] == selected][0])


@app.callback(
    dash.dependencies.Output('graph_model', 'figure'),
    [dash.dependencies.Input('graph_map', 'clickData'), dash.dependencies.Input('metric-selected', 'value'), dash.dependencies.Input('metric-selected', 'options')])
def update_model_series(clickData, selected, options):
    parameter = parameterestimation(data['confirmed']['data'], clickData['points'][0]['location'])
    data_model = SIRmodel(data, clickData['points'][0]['location'], parameter, forecast=600)
    return create_model_series(data_model, clickData['points'][0]['location'], [entry['label'] for entry in options if entry['value'] == selected][0])


if __name__ == '__main__':
    app.run_server(debug=False)
