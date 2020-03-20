# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 08:06:35 2020

@author: pribahsn
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from datetime import timedelta
from scipy.optimize import curve_fit


def addmeasures(parameter, date, scaling):
    parameter['betagamma'] = parameter['betagamma'].append(pd.DataFrame({'beta': parameter['betagamma'].iloc[0]['beta']*scaling, 'gamma': parameter['betagamma'].iloc[0]['gamma']}, index=[date]), sort=True)

    return parameter


def parameterestimation(data, country, threshold=20, output=False, forecast=40, fristsegment=10, lastsegement=4):

    def exponential(x, A, B):
        return A * (np.exp(B * x)-1)+threshold

    data_confirmed = data[country][data[country] > threshold]
    data_confirmed_start_date = data[country][data[country] > threshold].index[0]
    data_confirmed_x = np.array(range(0, len(data_confirmed)))

    firstSegment_fit, pcov = curve_fit(exponential, data_confirmed_x[:fristsegment], data_confirmed.values[:fristsegment])
    lastSegment_fit, pcov = curve_fit(exponential, data_confirmed_x[-lastsegement:], data_confirmed.values[-lastsegement:])
    prediction_first = pd.DataFrame(data=exponential(range(forecast), firstSegment_fit[0], firstSegment_fit[1]), index=[data_confirmed_start_date + timedelta(days=x) for x in range(forecast)])
    prediction_last = pd.DataFrame(data=exponential(range(forecast), lastSegment_fit[0], lastSegment_fit[1]), index=[data_confirmed_start_date + timedelta(days=x) for x in range(forecast)])
    time_curfew = prediction_first[(np.sign(prediction_first - prediction_last).diff() == 2).values].index

    gamma = 1/15
    beta = firstSegment_fit[1]+gamma
    t0 = data_confirmed_start_date
    I0 = firstSegment_fit[0]*firstSegment_fit[1]/gamma
    betagamma = pd.DataFrame({'beta': beta, 'gamma': gamma}, index=[t0])
    if len(time_curfew) == 1:
        betagamma = betagamma.append(pd.DataFrame({'beta': lastSegment_fit[1]+gamma, 'gamma': gamma}, index=[time_curfew[0]]), sort=True)

    if output:
        print(country)
        print(f'ɣ: {gamma}')
        print(f'β: {beta}')
        print(f'I₀: {I0}')
        print(f'R₀: {beta/gamma}')
        print(f't₀: {t0}')

        plt.plot(prediction_first)
        plt.plot(prediction_last)
        plt.plot(data_confirmed)
        plt.yscale('log')
        plt.grid(which='both')
        plt.show()

    return {'I0': I0, 't0': t0, 'betagamma': betagamma}
