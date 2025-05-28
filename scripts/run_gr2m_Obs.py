

import pandas as pd
import numpy as np
from gr2m import gr2m
from matplotlib import pyplot as plt
from itertools import product
from datetime import datetime

params_all_basins = pd.read_csv('../input/streamflow/GR2M_PARAMETERS_META_V02.csv', index_col='name')

basin_lookuptable = {
    'Garagoa': 'garagoa',
    'Dir_btw_Ca_Or': 'directos_CO',
    'Pauto': 'pauto',
    'Dir_btw_Cu_Ca': 'directos_cusianacarare',
    'Guanapalo': 'guanapalo',
    'Lengupa': 'lengupa',
    'Upia': 'upia',
    'Tua': 'tua',
    "Cravo Sur": 'cravo sur',
    'Dir_btw_Cu_CS': 'directos_cusianacravo',
    'Cusiana': 'cusiana',
    'Yucao': 'Yucao',
    'Guatiquia': 'guatiquia',
    'Humea': 'humea',
    'Guacavia': 'guacavia',
    'Guavio': 'guavio',
    'Metica': 'metica',
    'Guayuriba': 'guayuriba',
    'Dir_btw_Gb_Yu': 'directos_meticaguayuriba',
    'Dir_btw_Hu_Up': 'directos_humeaupia',
    'Melua': 'melua',
    'Cumaral': 'melua', # There is no weather data for Cumaral - need to check w/ Julian
    'Manacacias': 'manacacias',
    'Dir_btw_P_Ca': 'directos_pautocarare',
    'Negro': 'negro',
    'Lago de Tota': 'tota',
    'Casanare': 'casanare'
}

df_vs_julian = pd.DataFrame()
df_vs_obs = pd.DataFrame()

for basin in params_all_basins.columns:

    param = {'X1':params_all_basins.loc['X1', basin],  
        'X2': params_all_basins.loc['x2', basin],
        'area_OWF_km2': params_all_basins.loc['area_basin', basin],
        'area_gage_km2': params_all_basins.loc['area_model', basin]}

    weather = pd.read_csv('../input/weather/historical/{}.txt'.format(basin_lookuptable[basin]), sep='\t')
    weather.drop(columns=['Day', 'Month', 'Year'], inplace=True)
    weather.index = pd.date_range('1980-01-01', '2014-12-31', freq='D')

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
    sim_vs_julian = pd.DataFrame({basin:
        np.array(sim).ravel() # flow in mm/month
        / 10**3 # convert mm to m
        * param['area_OWF_km2'] * 10**6 # multiplied by the basin area (in m2)
        },
        index=weather_monthly.index.values)
    
    sim_vs_obs = pd.DataFrame({basin:
        np.array(sim).ravel() # flow in mm/month
        / 10**3 # convert mm to m
        * param['area_gage_km2'] * 10**6 # multiplied by the basin area (in m2)
        },
        index=weather_monthly.index.values)


    # Append the results to the DataFrame
    df_vs_julian = pd.concat([df_vs_julian, sim_vs_julian], axis=1)
    df_vs_obs = pd.concat([df_vs_obs, sim_vs_obs], axis=1)

# Need to divide the daily value by the number of days in the month to get the daily flow values
df_vs_julian = df_vs_julian.div(df_vs_julian.index.days_in_month, axis=0)
df_vs_obs = df_vs_obs.div(df_vs_obs.index.days_in_month, axis=0)

# Reindex the dataframe to be daily
# This is because PYWR models, although they can run at monthly time step, require daily data
# as input.
date_range = pd.date_range(start='1980-01-01', end='2014-12-31', freq='D')
df_vs_julian = df_vs_julian.reindex(date_range, method='bfill')
df_vs_julian.index.name = 'Date'
df_vs_obs = df_vs_obs.reindex(date_range, method='bfill')
df_vs_obs.index.name = 'Date'

# Round the results to 1 decimal place and save the results
df_vs_julian.round(decimals=1).to_csv(f'../input/streamflow/historical/GR2M_flow_Sim_w_ObsMet_OWF_basin_area.csv')
df_vs_obs.round(decimals=1).to_csv(f'../input/streamflow/historical/GR2M_flow_Sim_w_ObsMet_gage_basin_area.csv')

# Comparison with the SimObs provided by Julian
SimObs_julian = pd.read_csv('../input/streamflow/historical/observed_monthly_flows_cmd.csv', index_col='Date',
                            parse_dates=True) # !! This is using the basin area used for the OWF model (not the area used to calibrate the model)

for b in df_vs_julian.columns:
    fig,ax = plt.subplots(figsize=(10,5))
    plt.plot(df_vs_julian[b].resample('ME').mean() / 86400, 'k', label='SimOBs New')
    plt.plot(SimObs_julian[b].resample('ME').mean() / 86400, 'b', lw=2, label='SimObs Julian')
    ax.set_title(b)
    ax.set_ylabel('Flow (cms)')
    plt.legend()
    plt.tight_layout()
    fig.savefig('../figures/check_gr2m_simobs/{}_simobs.png'.format(b))
    plt.close()
    #plt.show()


# Comparison with the Observed data
cols = list(pd.read_csv('../input/streamflow/historical/GR2M_flow_Sim_w_ObsMet.csv').columns)
Obs_cms = pd.read_csv('../data/Historical_Flows/Q_MENSUAL_obs_cms.csv',
                      usecols=[i for i in cols if i != 'Date']) # Don't read the date column cause it's a weird forma) 

Obs_cms.index = pd.date_range('1980-01-01', '2014-12-31', freq='ME')
Obs_cms.index.name = 'Date'


basin_calibrated = ('Garagoa', 'Upia', 'Cravo Sur', 'Cusiana', 'Yucao', 'Guatiquia', 'Humea', 
                    'Guacavia', 'Guavio', 'Metica', 'Guayuriba', 'Melua'
                    )

performance_metrics = pd.DataFrame(index=basin_calibrated, 
                                   columns=['NSE', 'RMSE', 'RMSE(%)', 'R2', 'bias', 'bias(%)',
                                            'SimMean', 'ObsMean', 'SimStd', 'ObsStd'])

for b in basin_calibrated:

    # Calculate the performance metrics
    Qobs = Obs_cms[b]
    Qsim = df_vs_obs[b].resample('ME').mean() / 86400
    Qsim = Qsim.loc[np.isnan(Qobs) == False]
    Qobs = Qobs.loc[np.isnan(Qobs) == False]

    NSE = 1 - np.sum((Qobs - Qsim)**2) / np.sum((Qobs - np.mean(Qobs))**2)
    RMSE = np.sqrt(np.mean((Qobs - Qsim)**2))
    RMSE_perc = RMSE / np.mean(Qobs) * 100
    R2 = np.corrcoef(Qobs, Qsim)[0,1]**2
    bias = np.mean(Qsim - Qobs)
    bias_perc = bias / np.mean(Qobs) * 100

    sim_mean = np.mean(Qsim)
    obs_mean = np.mean(Qobs)
    sim_std = np.std(Qsim)
    obs_std = np.std(Qobs)

    performance_metrics.loc[b] = [NSE, RMSE, RMSE_perc, R2, bias, bias_perc, sim_mean, obs_mean, sim_std, obs_std]

    fig,ax = plt.subplots(figsize=(10,5))
    plt.plot(df_vs_obs[b].resample('ME').mean() / 86400, 'k', label='SimOBs New')
    #plt.plot(SimObs_julian[b] / 86400, 'b', lw=2, label='SimObs Julian') We can't plot this cause it's simulated with OWF basin area
    plt.plot(Obs_cms[b], 'r', lw=2, label='Obs')
    ax.set_title(b)
    ax.set_ylabel('Flow (cms)')
    plt.legend()
    plt.tight_layout()
    fig.savefig('../figures/check_gr2m_simobs/{}_obs.png'.format(b))
    #plt.close()
    plt.show()