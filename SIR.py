# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 08:33:58 2020

@author: pribahsn
"""
import pandas as pd
import matplotlib.pyplot as plt

from datetime import date, timedelta
from scipy.integrate import ode


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
    SIR_data_regular = pd.DataFrame(columns=['S', 'I', 'R'], index=[parameter['t0'] + timedelta(days=x) for x in range(forecast)], data=dummy)

    SIR_data_curefew = pd.DataFrame(columns=['S0', 'I0', 'R0'], index=[parameter['t0'] + timedelta(days=x) for x in range(forecast)])
    SIR_data_curefew.loc[parameter['t0']] = {'S': data['population'].at[country], 'I': parameter['I0'], 'R': 0, 'S0': data['population'].at[country], 'I0': parameter['I0'], 'R0': 0}
    for i in range(len(parameter['betagamma'])):
        y0 = tuple(SIR_data_curefew.loc[parameter['betagamma'].index[i]].values)
        if i != len(parameter['betagamma'])-1:
            forecast_step = (parameter['betagamma'].index[i+1]-parameter['betagamma'].index[0]).days
            t = np.linspace(0, forecast_step, forecast_step+1)
        else:
            forecast_step = (parameter['betagamma'].index[0]+timedelta(days=forecast)-parameter['betagamma'].index[i]).days
            t = np.linspace(0, forecast_step, forecast_step+1)
        dummy = odeint(deriv, y0, t, args=(data['population'].at[country], parameter['betagamma'].iloc[i]['beta'], parameter['betagamma'].iloc[i]['gamma']))
        dummy = pd.DataFrame(columns=['S0', 'I0', 'R0'], index=[parameter['betagamma'].index[i] + timedelta(days=x) for x in range(forecast_step+1)], data=dummy)
        SIR_data_curefew.update(dummy)

    SIR_data = pd.concat([SIR_data_regular, SIR_data_curefew], axis=1, join='inner')

    duration = (SIR_data['I0'].loc[SIR_data['I0'] == SIR_data['I0'].max()].index[0]-SIR_data.index[0])*2

    dates = [parameter['t0']+duration]
    for i in range(duration.days, forecast):
        dates.append(parameter['t0']+timedelta(days=i))
    SIR_data.drop(dates, inplace=True)

    if output:
        SIR_data.plot(title=country, grid=True)
        plt.show()

    return SIR_data


import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# Total population, N.
N = 1000
# Initial number of infected and recovered individuals, I0 and R0.
I0, R0 = 1, 0
# Everyone else, S0, is susceptible to infection initially.
S0 = N - I0 - R0
# Contact rate, beta, and mean recovery rate, gamma, (in 1/days).
beta, gamma = 0.2, 1./10 
# A grid of time points (in days)
t = np.linspace(0, 160, 160)

# The SIR model differential equations.
def deriv(y, t, N, beta, gamma):
    S, I, R = y
    dSdt = -beta * S * I / N
    dIdt = beta * S * I / N - gamma * I
    dRdt = gamma * I
    return dSdt, dIdt, dRdt

# Initial conditions vector
y0 = S0, I0, R0
# Integrate the SIR equations over the time grid, t.
ret = odeint(deriv, y0, t, args=(N, beta, gamma))
S, I, R = ret.T