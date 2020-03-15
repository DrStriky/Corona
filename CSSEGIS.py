import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import os

from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.palettes import brewer

from DataPreparation import load_covid19_data
from DataPlotting import plotdata


data = load_covid19_data()

plotdata(data['confirmed_nzd']['data'], title='confirmed (normalized)', ylabel='confirmend/capita (%)')
plotdata(data['deaths_nzd']['data'], title='deaths (normalized)', ylabel='death/capita (%)')

plotdata((data['deaths_nzd']['data']/data['confirmed_nzd']['data']).replace([np.inf, -np.inf], np.nan), title='deaths per confirmed', ylabel='death/confirmed')

# diff/(confirmend-diff-death-recovered)
plotdata(data['confirmed_nzd']['data'].diff().div((data['confirmed_nzd']['data']-data['confirmed_nzd']['data'].diff()-data['deaths_nzd']['data']-data['recovered_nzd']['data'])), title='spreading rate per day', ylabel='spreading rate/day', smoothdays=2)
