

import pandas as pd
import numpy as np
from gr2m import gr2m
from matplotlib import pyplot as plt
from itertools import product

params_all_basins = pd.read_csv('../input/streamflow/GR2M_PARAMETERS_META_V03.csv', index_col='name')

DT = np.arange(0,6)
DP = np.arange(70,131,10)
REALIZATIONS = np.arange(1,6)

for dt, dp, real in product(DT, DP, REALIZATIONS):

    df = pd.DataFrame()

    for basin in params_all_basins.columns:

        param = {'X1':params_all_basins.loc['X1', basin],  
                'X2': params_all_basins.loc['x2', basin],
                'area_km2': params_all_basins.loc['area_basin', basin]}

        weather = pd.read_csv(f'../input/weather/CST/{basin}_{real}_DT{dt}_DP{dp}.txt', sep='\t')
        weather.drop(columns=['Day', 'Month', 'Year'], inplace=True)
        weather.index = pd.date_range('2020-01-01', '2070-12-31', freq='D')

        weather_monthly = weather.resample('ME').sum()
        
        # Repeat the climatology for 3 years to create a warm up period of the state variables
        weather_IAM = weather_monthly.groupby([weather_monthly.index.month]).mean()
        weather_warm_up = pd.DataFrame(np.tile(weather_IAM.values, (3, 1)), columns=weather.columns)   
        
        sim_ini = gr2m(weather_warm_up['Prcp'].values,
                weather_warm_up['Et0'].values,
                param, return_state = True) 
        
        sim = gr2m(weather_monthly['Prcp'].values,
                weather_monthly['Et0'].values,
                param, states = {'production_store': sim_ini[1]['production_store'],
                                'routing_store': sim_ini[1]['routing_store']}) 
        
        # conversion from mm/month to m3/month
        sim = pd.DataFrame({basin:
                            np.array(sim).ravel() # flow in mm/month
                            / 10**3 # convert mm to m
                            * param['area_km2'] * 10**6 # multiplied by the basin area (in m2)
                            },
                        index=weather_monthly.index.values)
        
        # Append the results to the DataFrame
        df = pd.concat([df, sim], axis=1)

    # Need to divide the daily value by the number of days in the month to get the daily flow values
    df = df.div(df.index.days_in_month, axis=0)
    
    # Reindex the dataframe to be daily
    # This is because PYWR models, although they can run at monthly time step, require daily data
    # as input.
    date_range = pd.date_range(start='2020-01-01', end='2070-12-31', freq='D')
    df = df.reindex(date_range, method='bfill')
    df.index.name = 'Date'

    # Round the results to 1 decimal place and save the results
    df.round(decimals=1).to_csv(f'../input/streamflow/CST/Metarunoff_R{real}_DT{dt}_DP{dp}.csv')

   

