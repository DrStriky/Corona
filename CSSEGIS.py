import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from datetime import timedelta, date
from time import mktime

import os
import json

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.express as px

from DataPreparation import load_covid19_data
from DataPlotting import plotdata
from ParameterEstimation import parameterestimation, addmeasures
from SIR import SIRmodel


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

data = load_covid19_data()

with open(os.path.join('data', 'World_map', 'world.geo.json')) as f:
    world_map = json.load(f)

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

# parameter = parameterestimation(data['confirmed']['data'], 'AUT', output=True)
# SIRmodel(data, 'AUT', parameter, forecast=300, output=True)
# parameter = addmeasures(parameter, date(2020, 3, 8), 0.6)
# SIR_data = SIRmodel(data, 'AUT', parameter, forecast=300, output=True)

# Dash part
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([html.Div([html.H1('Covid-19 data by country')],
                                style={'textAlign': 'center', 'padding-bottom': '30'}),
                       html.Div(children='Programmed by Jonathan & Florian under quarantine in dash'),
                       html.Div([html.Span('Metric to display : ', className='six columns',
                                           style={'text-align': 'right', 'width': '40%', 'padding-top': 10}),
                                 dcc.Dropdown(id='metric-selected', value='confirmed_nzd',
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
                                            value=mktime((date.today()-timedelta(days=2)).timetuple()),
                                            marks={int(mktime(xx.timetuple())): {'label': xx.isoformat(), 'style': {'writing-mode': 'vertical-rl', 'text-orientation': 'use-glyph-orientation'}} for xx in data['recovered_nzd']['data'][np.arange(len(data['recovered_nzd']['data'])) % 2 == 0].index},
                                            )], style={'marginBottom': '5em'}
                                ),
                       html.Div([dcc.Graph(id='graph_map', hoverData={'points': [{'location': 'AUT'}]})
                                 ], style={'display': 'inline-block', 'width': '49%', 'vertical-align': 'top'}),
                       html.Div([dcc.Graph(id='graph_data'),
                                 dcc.Graph(id='graph_model')
                                 ], style={'display': 'inline-block', 'width': '49%'})
                       ], className='container', style={'width': '1700px', 'max-width': '1700px'})


def create_map(selected, options, setdate):
    new_data = data[selected]['data'].T[date.fromtimestamp(setdate)].to_frame().reset_index()
    new_data.columns = ['country', 'number']
    figure = px.choropleth(new_data,
                           geojson=world_map,
                           featureidkey='properties.iso_a3',
                           locations='country',
                           color='number',
                           projection="robinson"
                           )
    return figure


def create_data_series(data, country, title):
    return {
        'data': [dict(
            x=data.index,
            y=data[country],
            mode='lines+markers'
        )],
        'layout': {
            'height': '350px',
            'title': {'text': title+' for '+country},
            'yaxis': {'showgrid': True},
            'xaxis': {'showgrid': True}
        }
    }


def create_model_series(data, country, title):
    return {
        'data': [dict(x=data.index, y=data['S'], mode='lines+markers', name='Susceptible'),
                 dict(x=data.index, y=data['I'], mode='lines+markers', name='Infected'),
                 dict(x=data.index, y=data['R'], mode='lines+markers', name='Recoverd')],
        'layout': {
            'height': '350px',
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
    return create_map(selected, options, setdate)
    # return {'data': create_map(selected, options, setdate)}

    # trace = go.Choropleth(locations=data[selected]['data'].T.index,  # Spatial coordinates
    #                       z=data[selected]['data'].T[date.fromtimestamp(setdate)],  # Data to be color-coded
    #                       locationmode='ISO-3',  # set of locations match entries in `locations`
    #                       colorscale='Viridis',
    #                       zmin=0,
    #                       zmax=np.nanquantile(data[selected]['data'].T[date.fromtimestamp(setdate)], q=0.95),
    #                       colorbar_title=[entry['label'] for entry in options if entry['value'] == selected][0])
    # return {'data': [trace],
    #         'layout': go.Layout(title=[entry['label'] for entry in options if entry['value'] == selected][0], height=700, geo={'showframe': False, 'showcoastlines': False, 'projection': {'type': 'miller'}})}


@app.callback(
    dash.dependencies.Output('graph_data', 'figure'),
    [dash.dependencies.Input('graph_map', 'hoverData'), dash.dependencies.Input('metric-selected', 'value'), dash.dependencies.Input('metric-selected', 'options')])
def update_data_series(hoverData, selected, options):
    return create_data_series(data[selected]['data'], hoverData['points'][0]['location'], [entry['label'] for entry in options if entry['value'] == selected][0])


@app.callback(
    dash.dependencies.Output('graph_model', 'figure'),
    [dash.dependencies.Input('graph_map', 'hoverData'), dash.dependencies.Input('metric-selected', 'value'), dash.dependencies.Input('metric-selected', 'options')])
def update_model_series(hoverData, selected, options):
    parameter = parameterestimation(data['confirmed']['data'], hoverData['points'][0]['location'])
    data_model = SIRmodel(data, hoverData['points'][0]['location'], parameter, forecast=300)
    return create_model_series(data_model, hoverData['points'][0]['location'], [entry['label'] for entry in options if entry['value'] == selected][0])


if __name__ == '__main__':
    app.run_server(debug=False)
