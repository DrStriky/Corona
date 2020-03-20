# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 08:33:58 2020

@author: pribahsn
"""
import pandas as pd
import matplotlib.pyplot as plt

from datetime import date, timedelta


def SIRmodel(data, country, parameter, output=False, forecast=600):

    SIR_data = pd.DataFrame(columns=['S', 'I', 'R', 'S0', 'I0', 'R0'], index=[parameter['t0'] + timedelta(days=x) for x in range(forecast)])
    SIR_data.loc[parameter['t0']] = {'S': data['population'].at[country], 'I': parameter['I0'], 'R': 0, 'S0': data['population'].at[country], 'I0': parameter['I0'], 'R0': 0}

    for day in range(1, forecast+1):
        beta = parameter['betagamma'].iloc[parameter['betagamma'].index.get_loc(parameter['t0'] + timedelta(days=day), method='pad')]['beta']
        gamma = parameter['betagamma'].iloc[parameter['betagamma'].index.get_loc(parameter['t0'] + timedelta(days=day), method='pad')]['gamma']
        SIR_data.at[parameter['t0'] + timedelta(days=day), 'S'] = SIR_data.at[parameter['t0'] + timedelta(days=day-1), 'S']+(-beta*SIR_data.at[parameter['t0'] + timedelta(days=day-1), 'S']*SIR_data.at[parameter['t0'] + timedelta(days=day-1), 'I']/data['population'].at[country])
        SIR_data.at[parameter['t0'] + timedelta(days=day), 'I'] = SIR_data.at[parameter['t0'] + timedelta(days=day-1), 'I']+(beta*SIR_data.at[parameter['t0'] + timedelta(days=day-1), 'S']*SIR_data.at[parameter['t0'] + timedelta(days=day-1), 'I']/data['population'].at[country])-gamma*SIR_data.at[parameter['t0'] + timedelta(days=day-1), 'I']
        SIR_data.at[parameter['t0'] + timedelta(days=day), 'R'] = SIR_data.at[parameter['t0'] + timedelta(days=day-1), 'R']+gamma*SIR_data.at[parameter['t0'] + timedelta(days=day-1), 'I']
        SIR_data.at[parameter['t0'] + timedelta(days=day), 'S0'] = SIR_data.at[parameter['t0'] + timedelta(days=day-1), 'S0']+(-parameter['betagamma'].iloc[0]['beta']*SIR_data.at[parameter['t0'] + timedelta(days=day-1), 'S0']*SIR_data.at[parameter['t0'] + timedelta(days=day-1), 'I0']/data['population'].at[country])
        SIR_data.at[parameter['t0'] + timedelta(days=day), 'I0'] = SIR_data.at[parameter['t0'] + timedelta(days=day-1), 'I0']+(parameter['betagamma'].iloc[0]['beta']*SIR_data.at[parameter['t0'] + timedelta(days=day-1), 'S0']*SIR_data.at[parameter['t0'] + timedelta(days=day-1), 'I0']/data['population'].at[country])-parameter['betagamma'].iloc[0]['gamma']*SIR_data.at[parameter['t0'] + timedelta(days=day-1), 'I0']
        SIR_data.at[parameter['t0'] + timedelta(days=day), 'R0'] = SIR_data.at[parameter['t0'] + timedelta(days=day-1), 'R0']+parameter['betagamma'].iloc[0]['gamma']*SIR_data.at[parameter['t0'] + timedelta(days=day-1), 'I0']

    duration = (SIR_data['I'].loc[SIR_data['I'] == SIR_data['I'].max()].index[0]-SIR_data.index[0])*2

    dates = [parameter['t0']+duration]
    for i in range(duration.days, forecast+1):
        dates.append(parameter['t0']+timedelta(days=i))
    SIR_data.drop(dates, inplace=True)

    if output:
        SIR_data.plot(title=country, grid=True)
        plt.show()

    return SIR_data
