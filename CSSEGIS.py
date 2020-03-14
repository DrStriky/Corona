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


urls = ['https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv',
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv',
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv']

data = dict()

# Download and normalize data
print('Beginning file download with requests')
for url in urls:
    with open(os.path.join('data', 'CSSEGISandData', os.path.basename(url)), 'wb') as f:
        r = requests.get(url)
        f.write(r.content)

    key = os.path.splitext(os.path.basename(url))[0].split('-')[-1]
    data[key] = dict()
    data[key]['file'] = url

    # import infected date --> Transpose, multiindex, grouby country
    dummy = pd.read_csv(os.path.join('data', 'CSSEGISandData', 'time_series_19-covid-Confirmed.csv'))

    dummy = dummy.T
    dummy.reset_index(inplace=True)

    tuples = list(zip(*[dummy.loc[0, :].to_list()[1:], dummy.loc[1, :].to_list()[1:]]))
    columns = pd.MultiIndex.from_tuples(tuples, names=['Province/State', 'Country/Region'])
    index = dummy.loc[4:, 'index'].to_list()

    dummy.drop(['index'], axis=1, inplace=True)

    data[key]['data_complete'] = pd.DataFrame(dummy.loc[4:, :].to_numpy(), index=index, columns=columns)
    data[key]['data'] = data[key]['data_complete'].groupby(['Country/Region'], axis=1).sum()


