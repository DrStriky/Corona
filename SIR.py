# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 08:33:58 2020

@author: pribahsn
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from datetime import timedelta
from scipy.integrate import odeint


def SIRmodel(data, country, parameter, output=False, forecast=600):

    def deriv(y, t, N, beta, gamma):
        S, I, R = y
        dSdt = -beta * S * I / N
        dIdt = beta * S * I / N - gamma * I
        dRdt = gamma * I
        return dSdt, dIdt, dRdt

    y0 = data['population'].at[country], parameter['I0'], 0
    t = np.linspace(0, forecast-1, forecast)

    dummy = odeint(deriv, y0, t, args=(data['population'].at[country], parameter['betagamma'].iloc[0]['beta'], parameter['betagamma'].iloc[0]['gamma']))
    SIR_data_regular = pd.DataFrame(columns=['S0', 'I0', 'R0'], index=[parameter['t0'] + timedelta(days=x) for x in range(forecast)], data=dummy)

    SIR_data_curefew = pd.DataFrame(columns=['S', 'I', 'R'], index=[parameter['t0'] + timedelta(days=x) for x in range(forecast)])
    SIR_data_curefew.loc[parameter['t0']] = {'S': data['population'].at[country], 'I': parameter['I0'], 'R': 0}
    for i in range(len(parameter['betagamma'])):
        y0 = tuple(SIR_data_curefew.loc[parameter['betagamma'].index[i]].values)
        if i != len(parameter['betagamma'])-1:
            forecast_step = (parameter['betagamma'].index[i+1]-parameter['betagamma'].index[0]).days
            t = np.linspace(0, forecast_step, forecast_step+1)
        else:
            forecast_step = (parameter['betagamma'].index[0]+timedelta(days=forecast)-parameter['betagamma'].index[i]).days
            t = np.linspace(0, forecast_step, forecast_step+1)
        dummy = odeint(deriv, y0, t, args=(data['population'].at[country], parameter['betagamma'].iloc[i]['beta'], parameter['betagamma'].iloc[i]['gamma']))
        dummy = pd.DataFrame(columns=['S', 'I', 'R'], index=[parameter['betagamma'].index[i] + timedelta(days=x) for x in range(forecast_step+1)], data=dummy)
        SIR_data_curefew.update(dummy)

    SIR_data = pd.concat([SIR_data_regular, SIR_data_curefew], axis=1, join='inner')

    duration = (SIR_data['I'].loc[SIR_data['I'] == SIR_data['I'].max()].index[0]-SIR_data.index[0])*2

    if duration.days < forecast:
        dates = [parameter['t0']+duration]
        for i in range(duration.days, forecast):
            dates.append(parameter['t0']+timedelta(days=i))
        SIR_data.drop(dates, inplace=True)

    if output:
        SIR_data.plot(title=country, grid=True)
        plt.show()

    return SIR_data
