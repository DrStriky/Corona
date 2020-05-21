# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 08:06:35 2020

@author: pribahsn

paramter estimation for the SIR model
fittes beta from infected at the beginning and the end
trys to get the curefew point

"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from datetime import timedelta
from scipy.optimize import curve_fit


def addmeasures(parameter, date, scaling):
    """adds a mesurment virology wise int the dataframe"""
    parameter['betagamma'] = parameter['betagamma'].append(pd.DataFrame({'beta': parameter['betagamma'].iloc[0]['beta']*scaling, 'gamma': parameter['betagamma'].iloc[0]['gamma']}, index=[date]), sort=True)

    return parameter


def parameterestimation(data, country, threshold=20, output=False, forecast=50, fristsegment=15, lastsegement=4):
    """fits the paramters for SIR model"""
    def linear(x, A, B):
        return A+B*x

    def exponential(x, A, B):
        return A*np.exp(B * x)

    data_confirmed = data[country][data[country] > threshold]
    data_confirmed_start_date = data[country][data[country] > threshold].index[0]
    data_confirmed_x = np.array(range(0, len(data_confirmed)))

    firstSegment_fit, pcov = curve_fit(linear, data_confirmed_x[:fristsegment], np.log(data_confirmed.values[:fristsegment]), p0=[100, 0.3])
    lastSegment_fit, pcov = curve_fit(linear, data_confirmed_x[-lastsegement:], np.log(data_confirmed.values[-lastsegement:]))
    prediction_first = pd.DataFrame(data=exponential(range(forecast), np.exp(firstSegment_fit[0]), firstSegment_fit[1]), index=[data_confirmed_start_date + timedelta(days=x) for x in range(forecast)])
    prediction_last = pd.DataFrame(data=exponential(range(forecast), np.exp(lastSegment_fit[0]), lastSegment_fit[1]), index=[data_confirmed_start_date + timedelta(days=x) for x in range(forecast)])
    time_curfew = prediction_first[(np.sign(prediction_first - prediction_last).diff() == 2).values].index

    gamma = 1/15
    betagamma = pd.DataFrame({'beta': firstSegment_fit[1]+gamma, 'gamma': gamma}, index=[data_confirmed_start_date])
    if len(time_curfew) == 1:
        betagamma = betagamma.append(pd.DataFrame({'beta': lastSegment_fit[1]+gamma, 'gamma': gamma}, index=[time_curfew[0]]), sort=True)

    if output:
        print(country)
        print(f'ɣ: {gamma}')
        print(f'β: {firstSegment_fit[1]+gamma}')
        print(f'I₀: {np.exp(firstSegment_fit[0])}')
        print(f'R₀: {(firstSegment_fit[1]+gamma)/gamma}')
        print(f't₀: {data_confirmed_start_date}')

        plt.plot(prediction_first)
        plt.plot(prediction_last)
        plt.plot(data_confirmed)
        plt.yscale('log')
        plt.grid(which='both')
        plt.show()

    return {'I0': np.exp(firstSegment_fit[0]), 't0': data_confirmed_start_date, 'betagamma': betagamma}
