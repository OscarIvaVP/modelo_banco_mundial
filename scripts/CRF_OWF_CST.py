


import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import os
from CST_PlottingTools import CRF_lineplot
from CST_PlottingTools import CRF_heatmap



# Read the data
cst = xr.open_dataset('../results/CST/OWF_CST_annual_deficit_Mm3.nc')

basins = ('Metica',  'CravoSur', 'Yucao', 'Guatiquia')# 'Dir_btw_hu_up',

frequency_deficit = (
    ('freq_annual_deficit_urban', 'urban deliveries'),
    ('freq_annual_deficit_rural', 'rural deliveries'),
    ('freq_annual_deficit_livestock', 'livestock deliveries'),
    ('freq_annual_deficit_agriculture', 'irrigation deliveries'),
    ('freq_annual_deficit_envflow', 'environmental flow'),
)



annual_average_basin = (
    ('annual_average_urban_basin', 'Average annual urban deliveries (Mm$^3$)'),
    ('annual_average_rural_basin', 'Average annual rural deliveries (Mm$^3$)'),
    ('annual_average_livestock_basin', 'Average annual livestock deliveries (Mm$^3$)'),
    ('annual_average_agriculture_basin', 'Average annual irrigation deliveries (Mm$^3$)')
)

annual_max_basin = (
    ('annual_max_urban_basin', 'Maximum annual urban deliveries (Mm$^3$)'),
    ('annual_max_rural_basin', 'Maximum annual rural deliveries (Mm$^3$)'),
    ('annual_max_livestock_basin', 'Maximum annual livestock deliveries (Mm$^3$)'),
    ('annual_max_agriculture_basin', 'Maximum annual irrigation deliveries (Mm$^3$)')
)




weplot_heatmaps = True
if weplot_heatmaps:
    for basin in basins:
        os.makedirs(f'../figures/CRF/{basin}', exist_ok=True)
        id_basin = np.where(cst.basin.data == basin)[0][0]

        for id_dispatch, dispatch in enumerate(('FCFS', 'PE')):
        
            for metric, title_name in frequency_deficit:

                freq_deficit = np.nanmean(np.moveaxis(cst.variables[metric].values[
                    id_basin, :, :, :, np.arange(4), np.arange(4), np.arange(4), id_dispatch],0,3),axis=2)
                freq_deficit = freq_deficit.round(1)
                
                for id_demand, proj in enumerate(('2022', '2030', '2040', '2050')):

                    
                    CRF_heatmap.Heatmap(
                        data=freq_deficit[:,:,id_demand], 
                        x_labels=np.arange(-30,31,10), 
                        y_labels=np.arange(6),
                        title=f'Frequency of annual deficit in {title_name}\n{basin} - Demand as in {proj} - {dispatch}',
                        xlabel=r'$\Delta P\ (\%)$',
                        ylabel=r'$\Delta T\ (C)$',
                        colorbar_label = '(%)',
                        grid=True,
                        vmin = freq_deficit.min(),
                        vmax = freq_deficit.max(),
                        vcenter = freq_deficit[0,3,id_demand],
                        no_change = (0,0),
                        contour_levels = np.arange(0,101,10),
                        contour_linewidth=2,
                        savepath=f'../figures/CRF/{basin}/CRF_DP-DT_{title_name}_D{proj}_{dispatch}.png',
                        path_deltaT = '../data/CMIP6/processed/delta_tas.xlsx',
                        path_deltaP = '../data/CMIP6/processed/delta_prcp.xlsx',
                        sheet_deltaT = 'Delta T (C) -- ssp5_8_5',
                        sheet_deltaP = 'Delta P (%) -- ssp5_8_5',
                        color_gcm = ['#fee8c8', '#e34a33'],
                        bin_widthT = 0.5,
                        bin_widthP = 2.5,
                        show=False)
                


# b, i_dt, i_dp, i_real, i_Dfw, i_Dirr, i_Dliv, i_dispatch

# Create a few response functions for some basins
for basin in basins:
        
    os.makedirs(f'../figures/CRF/{basin}', exist_ok=True)

    id_basin = np.where(cst.basin.data == basin)[0][0]

    for metric, title_name in frequency_deficit:
    
        for i_dh, dispatch in enumerate(('FCFS', 'PE')):

            freq_deficit = np.nanmean(cst.variables[metric].values[id_basin, :, :, :, 3, 3, 3, i_dh], axis=2)
            

            # Plot the CRF = f(DeltaT) with multiple DeltaP scenarios - 1 dispatch scenario and 1 basin
            CRF_lineplot.TwoVarLineplot(
                freq_deficit, 
                x_axis=np.arange(6), 
                z_dim=np.arange(7), 
                title=f'{basin} - {dispatch} - D2040 - Frequency of annual deficit in {title_name}',
                ylabel='(%)',
                xlabel=r'Temperature increase ($^oC$)',
                colors=['#d73027', '#fc8d59', '#fee090', '#ffffbf', '#e0f3f8' ,'#91bfdb', '#4575b4'],
                caption_labels=['-30%', '-20%', '-10%', '0%', '+10%', '+20%', '+30%'],
                label_fontsize=14,
                facecolor='lightgrey',
                legend_facecolor='lightgrey',
                path_delta_change='../data/CMIP6/processed/delta_tas.xlsx',
                sheet_delta_change='Delta T (C) -- ssp5_8_5',
                color_gcm = ['#fee8c8', '#e34a33'],
                savepath=f'../figures/CRF/{basin}/CRF_DT-DP_{metric}_{basin}_{dispatch}.png',
            )
            
            # Plot the CRF = f(DeltaP) with multiple DeltaT scenarios - 1 dispatch scenario and 1 basin      
            CRF_lineplot.TwoVarLineplot(
                freq_deficit.T, 
                x_axis=np.arange(-30,31,10), 
                z_dim=np.arange(6), 
                title=f'{basin} - {dispatch} - D2040 - Frequency of annual deficit in {title_name}',
                ylabel='(%)',
                xlabel='Change in precipitation (%)',
                colors=['#ffffb2', '#fed976', '#feb24c', '#fd8d3c', '#f03b20', '#bd0026'],
                caption_labels=['+0C', '+1C', '+2C', '+3C', '+4C', '+5C'],
                label_fontsize=14,
                facecolor='lightgrey',
                legend_facecolor='lightgrey',
                path_delta_change='../data/CMIP6/processed/delta_prcp.xlsx',
                sheet_delta_change='Delta P (%) -- ssp5_8_5',
                color_gcm = ['#fee8c8', '#e34a33'],
                savepath=f'../figures/CRF/{basin}/CRF_DP-DT_{metric}_{basin}_{dispatch}.png'
            )

            # Plot the CRF = f(DeltaP) for multiple demand scenarios - 1 dispatch scenario and 1 basin
            freq_deficit = np.nanmean(cst.variables[metric].values[
                id_basin, 0, :, :, np.arange(4), np.arange(4), np.arange(4), i_dh], axis=2)
            CRF_lineplot.TwoVarLineplot(
                freq_deficit.T, 
                x_axis=np.arange(-30,31,10), 
                z_dim=np.arange(4), 
                title=f'{basin} - {dispatch} - Frequency of annual deficit in {title_name}',
                ylabel='(%)',
                xlabel='Change in precipitation (%)',
                colors=['#f0f9e8', '#bae4bc', '#7bccc4', '#2b8cbe'],
                caption_labels=['2022', '2030', '2040', '2050'],
                label_fontsize=14,
                facecolor='lightgrey',
                legend_facecolor='lightgrey',
                path_delta_change='../data/CMIP6/processed/delta_prcp.xlsx',
                sheet_delta_change='Delta P (%) -- ssp5_8_5',
                color_gcm = ['#fee8c8', '#e34a33'],
                savepath=f'../figures/CRF/{basin}/CRF_DP-DemandScenario_{metric}_{basin}_{dispatch}.png'
            )



# Create a few response functions for the entire basins
os.makedirs(f'../figures/CRF/OriniquiaRiverBasin', exist_ok=True)

for metric, title_name in (*annual_average_basin, *annual_max_basin):

    for i_dh, dispatch in enumerate(('FCFS', 'PE')):

        deficit = cst.variables[metric].values[:, :, 0, 3, 3, 3, i_dh]

        # Plot the CRF = f(DeltaT) with multiple DeltaP scenarios - 1 dispatch scenario and 1 basin
        CRF_lineplot.TwoVarLineplot(
            deficit, 
            np.arange(6), 
            np.arange(7), 
            f'Orinoquia River Basin - {dispatch} - D2040 - {title_name}',
            '(%)',
            r'Temperature increase ($^oC$)',
            ['#d73027', '#fc8d59', '#fee090', '#ffffbf', '#e0f3f8' ,'#91bfdb', '#4575b4'],
            caption_labels=['-30%', '-20%', '-10%', '0%', '+10%', '+20%', '+30%'],
            label_fontsize=14,
            facecolor='lightgrey',
            legend_facecolor='lightgrey',
            path_delta_change='../data/CMIP6/processed/delta_tas.xlsx',
            sheet_delta_change='Delta T (C) -- ssp5_8_5',
            color_gcm = ['#fee8c8', '#e34a33'],
            savepath=f'../figures/CRF/OriniquiaRiverBasin/CRF_DT-DP_{metric}_{dispatch}.png'
        )

        # Plot the CRF = f(DeltaP) with multiple DeltaT scenarios - 1 dispatch scenario and 1 basin      
        CRF_lineplot.TwoVarLineplot(
            deficit.T, 
            np.arange(-30,31,10), 
            np.arange(6), 
            f'Orinoquia River Basin - {dispatch} - {title_name}',
            '(%)',
            'Change in precipitation (%)',
            ['#ffffb2', '#fed976', '#feb24c', '#fd8d3c', '#f03b20', '#bd0026'],
            caption_labels=['+0C', '+1C', '+2C', '+3C', '+4C', '+5C'],
            label_fontsize=14,
            facecolor='lightgrey',
            legend_facecolor='lightgrey',
            path_delta_change='../data/CMIP6/processed/delta_prcp.xlsx',
            sheet_delta_change='Delta P (%) -- ssp5_8_5',
            color_gcm = ['#fee8c8', '#e34a33'],
            savepath=f'../figures/CRF/OriniquiaRiverBasin/CRF_DP-DT_{metric}_{dispatch}.png'
        )
        
        # Plot the CRF = f(DeltaP) for multiple demand scenarios - 1 dispatch scenario and 1 basin
        deficit = cst.variables[metric].values[0, :, 0, np.arange(4), np.arange(4), np.arange(4), i_dh]
        CRF_lineplot.TwoVarLineplot(
            deficit.T, 
            np.arange(-30,31,10), 
            np.arange(4), 
            f'Orinoquia River Basin - {dispatch} - {title_name}',
            '(%)',
            'Change in precipitation (%)',
            ['#f0f9e8', '#bae4bc', '#7bccc4', '#2b8cbe'],
            caption_labels=['2022', '2030', '2040', '2050'],
            label_fontsize=14,
            facecolor='lightgrey',
            legend_facecolor='lightgrey',
            path_delta_change='../data/CMIP6/processed/delta_prcp.xlsx',
            sheet_delta_change='Delta P (%) -- ssp5_8_5',
            color_gcm = ['#fee8c8', '#e34a33'],
            savepath=f'../figures/CRF/OriniquiaRiverBasin/CRF_DP-DemandScenario_{metric}_{dispatch}.png'
            #show=True
        )

