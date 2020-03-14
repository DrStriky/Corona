# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os

data = pd.read_excel(
    os.path.join('data', 'ECDC', 
                 'COVID-19-geographic-disbtribution-worldwide-2020-03-14.xls')
    )

# plot Österreich

austria = data.loc[data['GeoId']=='AT']
ax = austria.plot(x='DateRep', y='NewConfCases')

weekdays = austria['DateRep'].dt.weekday
colors = pd.Series('r',index=weekdays.index)
colors[(weekdays==5) | (weekdays==6)] = 'g'

austria.plot(x='DateRep', y='NewConfCases', kind='scatter', c=colors, ax=ax)
plt.title('Neuinfektionen in Österreich')
plt.show()


# plot selection of countries

selection = ['AT', 'UK', 'FR', 'CH', 'US']
new_by_country = data.pivot(index='DateRep', columns='GeoId', 
                           values='NewConfCases')
new_by_country[selection].plot()
plt.log
