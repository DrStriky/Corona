#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 14 21:16:54 2020

@author: jonathan
"""

import pandas as pd
import os
import requests
import time
import json


# urls for downloading data from John Hopkins University
urls = {'confirmed': 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv',
        'deaths': 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv',
        'recovered': 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv'
        }


def load_country_code_map():
    """ load and create country to country code map"""
    country_meta_file = os.path.join('data', 'Comtrade Country Code and ISO list.csv')
    country_code_map = pd.read_csv(country_meta_file, index_col=0)
    country_code_map = country_code_map['ISO3-digit Alpha']

    return country_code_map


def load_country_correction():
    """ load and create country correction to properly map data to countries"""
    with open(os.path.join('data', 'Country_correction.json')) as f:
        country_correction = json.load(f)

    return country_correction


def load_cssegis_data(key):
    """ load and possibly update corona pandemics data from John Hopkins
    university """
    data = {}

    data['url'] = urls[key]
    data['file'] = os.path.join('data', 'CSSEGISandData', os.path.basename(urls[key]))

    # update data if older than 12 hours
    if time.time()-os.path.getmtime(data['file']) > 60*60*12:
        print('Beginning file download with requests')
        with open(data['file'], 'wb') as f:
            r = requests.get(urls[key])
            f.write(r.content)

    # import infected date --> Transpose, multiindex, grouby country
    dummy = pd.read_csv(data['file'])

    # fix 'wrong' data
    country_corrections = load_country_correction()
    for key, value in country_corrections['To Country'].items():
        dummy.at[dummy[dummy['Country/Region'] == key].index, 'Province/State'] = country_corrections['To Country'][key]['Province/State']
        dummy.at[dummy[dummy['Country/Region'] == key].index, 'Country/Region'] = country_corrections['To Country'][key]['Country/Region']

    dummy = dummy.T
    dummy.reset_index(inplace=True)

    tuples = list(zip(*[dummy.loc[0, :].to_list()[1:], dummy.loc[1, :].to_list()[1:]]))
    columns = pd.MultiIndex.from_tuples(tuples, names=['Province/State', 'Country/Region'])
    index = dummy.loc[4:, 'index'].to_list()

    dummy.drop(['index'], axis=1, inplace=True)

    data['data_complete'] = pd.DataFrame(dummy.loc[4:, :].to_numpy(), index=index, columns=columns)
    data['data'] = data['data_complete'].groupby(['Country/Region'], axis=1).sum()
    data['data'].drop('Cruise Ship', axis=1, inplace=True)

    # country codes to
    country_code_map = load_country_code_map()
    data['data'].columns = [country_code_map[country] for country in data['data'].columns]

    data['data'].index = pd.to_datetime(data['data'].index)
    return data


def load_all_cssegis_data(data_dict={}):
    """ laod all data from John Hopkins university
     currently Confirmed cases, Deaths and Recovered Cases
    """
    for key in urls.keys():
        data_dict[key] = load_cssegis_data(key)
    return data_dict


def load_population():
    """ load countries population data from 2018
    newest available data from worldbank
    """
    population_file = os.path.join('data', 'Worldbank', 'Population',
                                   'API_SP.POP.TOTL_DS2_en_csv_v2_821007.csv')
    population = pd.read_csv(population_file,
                             skiprows=4, index_col=1)['2018']
    return population


def normalize_by_population(df, population=load_population()):
    """ Transforms cases into percentage of countries population data
    (worldbank, 2018)
    """
    df_normalized = df['data'].div(population) * 100
    return df_normalized


def load_covid19_data():
    """ load data from John Hopkins University and adds the normalized per
    time series (i.e. time series as percent of the countries population)
    """
    data = load_all_cssegis_data()

    population = load_population()
    data_nzd = {}
    for key in data.keys():
        data_nzd[key+'_nzd'] = {'data': normalize_by_population(df=data[key], population=population)}

    data.update(data_nzd)
    data['population'] = population

    return data
