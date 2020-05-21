# -*- coding: utf-8 -*-
"""
Created on Sat Mar 14 22:34:56 2020

@author: pribahsn

support files; not used in main application
"""
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import date, timedelta

from scipy.stats.mstats import gmean
import os

shapefile = os.path.join('data', 'World_map', 'ne_50m_admin_0_countries.shp')


def plotdata(data, title, ylabel, date=date.today()-timedelta(days=1), quantile=0.95, smoothdays=1):
    # Prepare geopandas shape file for the world and europe
    worldmap = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
    worldmap.columns = ['country', 'country_code', 'geometry']
    worldmap.drop(worldmap[worldmap['country'] == 'Antarctica'].index, inplace=True)

    europemap = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
    europemap.columns = ['country', 'country_code', 'geometry']
    europe = pd.read_csv(os.path.join('data', 'World_map', 'europe.csv'))
    europemap = europemap[europemap['country_code'].isin(europe['Country_Code'].to_list())]

    # colormap
    cmap = plt.cm.get_cmap('viridis')
    cmap.set_bad('white', 1.)
    cmap.set_over('red')

    # Map data to map
    dates = [date]
    for i in range(1, smoothdays):
        dates.append(date-timedelta(days=i))
    dummy = data.loc[dates, :].mean().to_frame()
    dummy.reset_index(level=0, inplace=True)
    dummy.columns = ['country_code', 'confirmed']
    worldmap = worldmap.merge(dummy, left_on='country_code', right_on='country_code')
    europemap = europemap.merge(dummy, left_on='country_code', right_on='country_code')

    # # plot the world
    # f, ax = plt.subplots(1)
    # worldmap.plot(ax=ax, linewidth=0.1, edgecolor='0.5', cmap=cmap, column='confirmed', vmin=0, vmax=np.nanquantile(worldmap.confirmed, q=quantile),
    #                legend=True, legend_kwds={'label': ylabel, 'orientation': "horizontal", 'extend': 'max', 'pad': 0.01, 'aspect': 50, 'fraction': 0.03})
    # ax.set_title(title, fontsize=10)
    # ax.set_xticklabels([])
    # ax.set_yticklabels([])
    # ax.set_xticks([])
    # ax.set_yticks([])

    # plt.axis('equal')
    # plt.show()

    # plot europe
    f, ax = plt.subplots(1)
    europemap.plot(ax=ax, linewidth=0.1, edgecolor='0.5', cmap=cmap, column='confirmed', vmin=0, vmax=np.nanquantile(europemap.confirmed, q=quantile),
                   legend=True, legend_kwds={'label': ylabel, 'orientation': "horizontal", 'extend': 'max', 'pad': 0.01, 'aspect': 50, 'fraction': 0.03})
    ax.set_title(title, fontsize=10)
    plt.xlim(-25, 45)
    ax.set_ylim(30, 75)
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect('equal', 'box')

    plt.show()


def plot_growth_rate(data: pd.Series, smoothing_window: int = 4) -> None:
    """
    plots the daily growth rate of the time series data (i.e. index of data
    must consecutive days as DateTime-objects)
    """

    # compute daily growth rate
    rates = data / data.shift(1, pd.to_timedelta('1d'))
    rates = rates.dropna()

    # smoothen by computing thee geometric over a smoothing window
    # of the specified lenght
    rates_smooth = rates.rolling(window= smoothing_window * pd.to_timedelta('1d')).apply(gmean)
    rates_smooth = rates_smooth.dropna()

    plt.plot(rates_smooth)
    plt.plot(rates)
    plt.legend(['Smooth', 'Original'])
    plt.show()
    