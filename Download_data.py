# -*- coding: utf-8 -*-
"""
Created on Sat Mar 14 14:51:24 2020

@author: pribahsn
"""

import requests
import os


print('Beginning file download with requests')

urls = ['https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv',
       'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv',
       'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv']

for url in urls:
    with open(os.path.join('data', 'CSSEGISandData', os.path.basename(url)), 'wb') as f:
        r = requests.get(url)
        f.write(r.content)
