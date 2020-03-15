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

plotdata(data['confirmed_nzd']['data'], title='confirmed (normalized)')
plotdata(data['deaths_nzd']['data'], title='deaths (normalized)')

plotdata((data['deaths_nzd']['data']/data['confirmed_nzd']['data']).replace([np.inf, -np.inf], np.nan), title='deaths per confirmed (normalized)')

plotdata(data['confirmed_nzd']['data'].diff()/(data['confirmed_nzd']['data']-data['confirmed_nzd']['data'].diff()), title='spreading rate (normalized)', smoothdays=2)
