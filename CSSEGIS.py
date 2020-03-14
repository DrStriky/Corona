# -*- coding: utf-8 -*-
"""
Created on Sat Mar 14 15:07:49 2020

"""

import geopandas as gpd
import pandas as pd
import matplotlib as plt
import numpy as np

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

# Prepare geopandas shape file
gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
gdf.columns = ['country', 'country_code', 'geometry']
gdf.drop(gdf[gdf['country'] == 'Antarctica'].index, inplace=True)

gdf.plot()
