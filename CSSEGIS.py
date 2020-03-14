import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.palettes import brewer

import os
import requests
import time


urls = ['https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv',
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv',
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv']

shapefile = os.path.join('data', 'World_map', 'ne_50m_admin_0_countries.shp')

data = dict()

# create country to country code map
country_meta_file = os.path.join('data', 'Comtrade Country Code and ISO list.csv')
country_code_map = pd.read_csv(country_meta_file, index_col = 0)
country_code_map = country_code_map['ISO3-digit Alpha']

# Download if necessary and normalize Covid-19 data
for url in urls:
    key = os.path.splitext(os.path.basename(url))[0].split('-')[-1].lower()
    data[key] = dict()
    data[key]['url'] = url
    data[key]['file'] = os.path.join('data', 'CSSEGISandData', os.path.basename(url))

    if time.time()-os.path.getmtime(data[key]['file']) > 60*60*12:
        print('Beginning file download with requests')
        with open(data[key]['file'], 'wb') as f:
            r = requests.get(url)
            f.write(r.content)

    # import infected date --> Transpose, multiindex, grouby country
    dummy = pd.read_csv(data[key]['file'])

    dummy = dummy.T
    dummy.reset_index(inplace=True)

    tuples = list(zip(*[dummy.loc[0, :].to_list()[1:], dummy.loc[1, :].to_list()[1:]]))
    columns = pd.MultiIndex.from_tuples(tuples, names=['Province/State', 'Country/Region'])
    index = dummy.loc[4:, 'index'].to_list()

    dummy.drop(['index'], axis=1, inplace=True)

    data[key]['data_complete'] = pd.DataFrame(dummy.loc[4:, :].to_numpy(), index=index, columns=columns)
    data[key]['data'] = data[key]['data_complete'].groupby(['Country/Region'], axis=1).sum()
    data[key]['data'].drop('Cruise Ship', axis=1, inplace=True)

    data[key]['data'].columns = [country_code_map[country] for country in data[key]['data'].columns]

# load countries population data from worldbank 2018
population_file = os.path.join('data', 'Worldbank', 'Population', 'API_SP.POP.TOTL_DS2_en_csv_v2_821007.csv')
population = pd.read_csv(population_file, skiprows=4, index_col=1)['2018']

# normalize infections by population
data['confirmedPerCapita'] = dict()
data['confirmedPerCapita']['data'] = data['confirmed']['data'].div(population)


# Prepare geopandas shape file for the world and europe
worldmap = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
worldmap.columns = ['country', 'country_code', 'geometry']
worldmap.drop(worldmap[worldmap['country'] == 'Antarctica'].index, inplace=True)

europemap = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
europemap.columns = ['country', 'country_code', 'geometry']
europe = pd.read_csv(os.path.join('data', 'World_map', 'europe.csv'))
europemap = europemap[europemap['country_code'].isin(europe['Country_Code'].to_list())]


# Map data to map
dummy = data['confirmedPerCapita']['data'].tail(1).T
dummy.reset_index(level=0, inplace=True)
dummy.columns = ['country_code', 'confirmed']
worldmap = worldmap.merge(dummy, left_on='country_code', right_on='country_code')
europemap = europemap.merge(dummy, left_on='country_code', right_on='country_code')

# colormap
cmap = plt.cm.get_cmap('viridis')
cmap.set_bad('white',1.)
cmap.set_over('red')

# plot the world
f, ax = plt.subplots(1)
worldmap.plot(ax=ax, linewidth=0.1, edgecolor='0.5', cmap=cmap, legend=True, column='confirmed', vmax=np.nanquantile(europemap.confirmed, q=0.95))
ax.set_title('confirmed cases', fontsize=15)
ax.set_xticklabels([])
ax.set_yticklabels([])
ax.set_xticks([])
ax.set_yticks([])

plt.axis('equal')
plt.show()


# plot europe
f, ax = plt.subplots(1)
europemap.plot(ax=ax, linewidth=0.1, edgecolor='0.5', cmap=cmap, legend=True, column='confirmed', vmax=np.nanquantile(europemap.confirmed, q=0.95))
ax.set_title('confirmed cases', fontsize=15)
plt.xlim(-25, 45)
ax.set_ylim(30, 75)
ax.set_xticklabels([])
ax.set_yticklabels([])
ax.set_xticks([])
ax.set_yticks([])

plt.show()
