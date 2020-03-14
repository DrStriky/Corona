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

plotdata(data['confirmed_nzd']['data'], title='confirmed per capita')


