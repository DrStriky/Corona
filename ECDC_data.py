# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# import geopandas as gpd
import pandas as pd
import matplotlib as plt


import os


data = pd.read_excel(os.path.join('data', 'ECDC', 'COVID-19-geographic-disbtribution-worldwide-2020-03-14.xls'))


data = data.pivot(index='DateRep', columns='GeoId', values=['NewConfCases', 'NewDeaths'])

data['NewConfCases'].plot(legend=False, grid=True, title='Infections per day')

data['NewConfCases'].cumsum().plot(legend=False, grid=True, title='Infected cumulated')


