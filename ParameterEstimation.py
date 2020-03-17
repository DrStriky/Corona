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


def parameterestimation(data, country, threshold=3, output=False, forecast=50):

    def exponential(x, A, B):
        return A * (np.exp(B * x)-1)+threshold

    data_confirmed = data[country][data[country] > threshold]
    data_confirmed_start_date = data[country][data[country] > threshold].index[0]
    data_confirmed_x = np.array(range(0, len(data_confirmed)))

    result_confirmed, pcov = curve_fit(exponential, data_confirmed_x, data_confirmed.values)
    prediction = pd.DataFrame(data=exponential(range(forecast), result_confirmed[0], result_confirmed[1]), index=[data_confirmed_start_date + timedelta(days=x) for x in range(forecast)])

    gamma = 1/15
    beta = result_confirmed[1]+gamma
    t0 = data_confirmed_start_date  # ?????
    I0 = result_confirmed[0]*result_confirmed[1]/gamma

    if output:
        print(f'ɣ: {gamma}')
        print(f'β: {beta}')
        print(f'I₀: {I0}')
        print(f'R₀: {beta/gamma}')
        print(f't₀: {t0}')

        plt.plot(prediction)
        plt.plot(data_confirmed)
        plt.yscale('log')
        plt.grid(which='both')
        plt.show()

    return {'beta': beta, 'gamma': gamma, 'I0': I0, 't0': t0}
