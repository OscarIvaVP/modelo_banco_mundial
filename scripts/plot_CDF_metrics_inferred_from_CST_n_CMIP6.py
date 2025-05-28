

import xarray as xr
import os
import numpy as np
import pandas as pd
from scipy import interpolate
import pickle as pkl
from itertools import product
from matplotlib import pyplot as plt
# Read the data
cst = xr.open_dataset('../results/CST/OWF_CST_annual_deficit_Mm3.nc')



frequency_deficit = (
    ('freq_annual_deficit_urban', 'urban deliveries'),
    ('freq_annual_deficit_rural', 'rural deliveries'),
    ('freq_annual_deficit_livestock', 'livestock deliveries'),
    ('freq_annual_deficit_agriculture', 'irrigation deliveries'),
    ('freq_annual_deficit_envflow', 'environmental flow'),
)

# Dimensions
future_periods = ('2026-2055', '2056-2085')
dispatch_order = ('FCFS', 'PE')
demand_freshwater = ('FW2022', 'FW2030', 'FW2040', 'FW2050')
demand_livestock = ('LV2022', 'LV2030', 'LV2040', 'LV2050')
demand_agriculture = ('AG2022', 'AG2030', 'AG2040', 'AG2050')
random_samples = np.arange(1000)
basins = cst.basin.data.tolist()

index = pd.MultiIndex.from_product(
    [random_samples, dispatch_order, demand_freshwater, demand_livestock, demand_agriculture, future_periods, basins],
     names=['rd_sample', 'dispatch', 'FWd', 'LVd', 'AGd', 'ClimPeriod', 'basin'])

df = pd.DataFrame(index=index, columns=[
    'dT', 'dP', 'freq_annual_deficit_urban', 'freq_annual_deficit_rural', 'freq_annual_deficit_livestock',
    'freq_annual_deficit_agriculture', 'freq_annual_deficit_envflow'])
df = df.sort_index()

we_need_to_interpolate_metrics = False

if we_need_to_interpolate_metrics:

    for basin in basins:
        
        id_basin = np.where(cst.basin.data == basin)[0][0]

        for id_dispatch, dispatch in enumerate(('FCFS', 'PE')):
            for metric, title_name in frequency_deficit:
                for id_fw, fw in enumerate(('FW2022', 'FW2030', 'FW2040', 'FW2050')):
                    for id_lv, lv in enumerate(('LV2022', 'LV2030', 'LV2040', 'LV2050')):
                        for id_ag, ag in enumerate(('AG2022', 'AG2030', 'AG2040', 'AG2050')):
                            for id_period, period in enumerate(('2026-2055', '2056-2085')):
                                
                                freq_deficit = np.nanmean(cst.variables[metric].values[
                                    id_basin, :, :, :, id_fw, id_ag, id_lv, id_dispatch],axis=2)
                                freq_deficit = freq_deficit.round(1)

                                for period in future_periods:
                                    
                                    delta_change = pd.read_excel(
                                        '../data/CMIP6/processed/random_delta_samples.xlsx',
                                        sheet_name=period, usecols=['deltaP', 'deltaT'])
                                    
                                    # Interpolate the data
                                    f = interpolate.RectBivariateSpline(np.arange(0,6,1),
                                                                        np.arange(-30,31,10),
                                                                        freq_deficit)
                                    
                                    df.loc[(slice(None), dispatch, fw, lv, ag, period, basin), metric] = f(
                                        delta_change['deltaT'], delta_change['deltaP'], grid=False).flatten()
                                    df.loc[(slice(None), dispatch, fw, lv, ag, period, basin), 'dT'] = delta_change['deltaT'].values
                                    df.loc[(slice(None), dispatch, fw, lv, ag, period, basin), 'dP'] = delta_change['deltaP'].values
                                    
                                    
                                    
    
    df.to_pickle('../results/Performance_Metrics/Frequency_of_rationing.pkl')

else:
    df =  pkl.load(open('../results/Performance_Metrics/Frequency_of_rationing.pkl', 'rb'))


# Plot the CDFs for all basins



for metric, m_name in frequency_deficit:

    fig, axes = plt.subplots(9, 3, figsize=(6, 12), sharex=True, sharey=True)

    for  basin, ax in zip(basins, axes.ravel()):

        # Select all the data for the basin and one dispatch rule and one period
        for dispatch, period in product(dispatch_order, future_periods):
            data = df.loc[(slice(None), dispatch, slice(None), slice(None), slice(None), period, basin), :][metric].values
            data = np.sort(data)

            y = np.arange(len(data)) / len(data)
            ax.plot(data, y, label=f'{dispatch} {period}')
        ax.set_title(basin)
        
        
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 1)
        ax.set_ylabel('CDF')
        ax.set_xlabel('%')

        # Set the ticks positions
        ax.set_xticks(np.arange(0, 101, 25))
        ax.set_yticks(np.arange(0, 1.1, 0.25))
        ax.grid()

    handles, labels = ax.get_legend_handles_labels()
    legend = plt.figlegend(handles, labels, columnspacing=0.5, handletextpad=0.5, 
             loc='lower center', ncol=2, bbox_to_anchor=(0.5,-0.01),
             fontsize=12)

    plt.suptitle(f'CDF of the annual frequency of deficit ({m_name})'.capitalize(), fontsize=14)
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.08)
    plt.savefig(f'../figures/CDF/Frequency_of_rationing {m_name}.png')
    #plt.show()
    plt.close()


for  basin in basins:
    #os.makedirs(f'../figures/CDF/{basin}', exist_ok=True)
    fig, axes = plt.subplots(1, 5, figsize=(12, 3), sharex=True, sharey=True)
    
    for (metric, m_name), ax in zip(frequency_deficit, axes.ravel()):

        # Select all the data for the basin and one dispatch rule and one period
        for dispatch, period in product(dispatch_order, future_periods):
            data = df.loc[(slice(None), dispatch, slice(None), slice(None), slice(None), period, basin), :][metric].values
            data = np.sort(data)

            y = np.arange(len(data)) / len(data)
            ax.plot(data, y, label=f'{dispatch} {period}')
        ax.set_title(m_name)
        
        
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 1)
        ax.set_ylabel('CDF')
        ax.set_xlabel('%')

        # Set the ticks positions
        ax.set_xticks(np.arange(0, 101, 25))
        ax.set_yticks(np.arange(0, 1.1, 0.25))
        ax.grid()

    handles, labels = ax.get_legend_handles_labels()
    legend = plt.figlegend(handles, labels, columnspacing=0.5, handletextpad=0.5, 
             loc='lower center', ncol=4, bbox_to_anchor=(0.5,-0.01),
             fontsize=12)

    plt.suptitle(f'CDF of the annual frequency of deficit in {basin}', fontsize=14)
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.26)
    plt.savefig(f'../figures/CDF/Frequency_of_rationing {m_name}_{basin}.png')
    #plt.show()
    plt.close()
    


                                
                


                              

                            