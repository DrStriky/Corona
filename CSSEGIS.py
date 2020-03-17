import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import os

from datetime import date, timedelta, date
from scipy.optimize import curve_fit

from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.palettes import brewer

from DataPreparation import load_covid19_data
from DataPlotting import plotdata
from ParameterEstimation import parameterestimation, addmeasures
from SIR import SIRmodel


data = load_covid19_data()

plotdata(data['confirmed_nzd']['data'], title='confirmed (normalized)', ylabel='confirmend/capita (%)')
# plotdata(data['deaths_nzd']['data'], title='deaths (normalized)', ylabel='death/capita (%)')
plotdata((data['deaths_nzd']['data']/data['confirmed_nzd']['data']).replace([np.inf, -np.inf], np.nan), title='deaths per confirmed', ylabel='death/confirmed')

# diff/(confirmend-diff-death-recovered)
plotdata(data['confirmed_nzd']['data'].diff().div((data['confirmed_nzd']['data']-data['confirmed_nzd']['data'].diff()-data['deaths_nzd']['data']-data['recovered_nzd']['data'])), title='spreading rate per day', ylabel='spreading rate/day', smoothdays=2)


(data['confirmed_nzd']['data']-data['recovered_nzd']['data']-data['deaths_nzd']['data'])['KOR']


parameter = parameterestimation(data['confirmed']['data'], 'ITA', output=True)
SIRmodel(data, 'ITA', parameter, forecast=150, output=True)

parameter = parameterestimation(data['confirmed']['data'], 'AUT', output=True)
parameter = addmeasures(parameter, date(2020, 3, 16), 0.5)
SIRmodel(data, 'AUT', parameter, forecast=150, output=True)
