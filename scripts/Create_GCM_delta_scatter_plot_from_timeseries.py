# Using the magic encoding  
# -*- coding: utf-8 -*-

import os
import sys 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)


RCP = ['rcp85', 'rcp60', 'rcp45', 'rcp26']
REGION = ['MetaRiver']
FUTURE_1 = ['2026-01-01', '2055-12-31']
FUTURE_2 = ['2056-01-01', '2085-12-31']
HISTORICAL = ['1976-01-01', '2005-11-30']

# Loop over RCP 
for rcp in RCP:

    # Creating list to host Deltas
    absolute_annual_change_T_fut1 = []
    absolute_annual_change_T_fut2 = []
    realtive_change_P_fut1 = []
    realtive_change_P_fut2 = []
    relative_CV_fut1 = []
    relative_CV_fut2 = []
    available_gcm = []
    
    
    ratio_change_T_fut1 = []
    ratio_change_T_fut2 = []
    ratio_change_std_T_fut1 = []
    ratio_change_std_T_fut2 = []
    ratio_change_std_annual_T_fut1 = []
    ratio_change_std_annual_T_fut2 = []
    ratio_change_P_fut1 = []
    ratio_change_P_fut2 = []
    ratio_change_std_P_fut1 = []
    ratio_change_std_P_fut2 = []
    ratio_change_std_annual_P_fut1 = []
    ratio_change_std_annual_P_fut2 = []

    
    # Listing the GCMs available for the selected RCP
    GCM = [x[0] for x in os.walk('../data/CMIP5_projections/{}/'.format(rcp))]
    
    # Loop over the available GCM for the selected RCP
    # First index, which we drop, is the parent folder.
    for gcm_path in GCM[1:]:
        
        # Get the name of the GCM
        _, _, gcm = gcm_path.rpartition('{}/'.format(rcp))
        
        # Read the contribution from each grid cell
        f = pd.read_excel(
            '../data/CMIP5_projections/MetaRiver_cmip5grid.xlsx',
            sheet_name=gcm)
    
        # Loop over the grid cell
        df_precip_f = pd.DataFrame()
        df_temp_f = pd.DataFrame()
        
        df_precip_h = pd.DataFrame()
        df_temp_h = pd.DataFrame()
        
        for grid in range(f.shape[0]):
            
            # Latitude, longitude and contribution (%) from each grid cell
            lat, lon, contrib = \
                f.loc[grid]['Lat'], f.loc[grid]['Lon'], f.loc[grid]['Area(%)']
            
            # CMIP5 data (Future)                
            grid_future = \
                np.loadtxt('../data/CMIP5_projections/{}/{}/{}_{}'.format(
                    rcp, gcm, format(lat,'.6f'), format(lon,'.6f')))
            
            df_precip_f[grid] = contrib/100 * grid_future[:,2]
            df_temp_f[grid] = contrib/100 * grid_future[:,3]
            
            # CMIP5 data (historical)
            grid_historical = \
                np.loadtxt('../data/CMIP5_projections/historical/{}/{}_{}'.format(
                    gcm, format(lat,'.6f'), format(lon,'.6f')))
            
            df_precip_h[grid] = contrib/100 * grid_historical[:,2]
            df_temp_h[grid] = contrib/100 * grid_historical[:,3]

        # Create time index
        timeindex_future = pd.period_range(
            start='{}-{}'.format(int(grid_future[0,0]),int(grid_future[0,1])),
            end='{}-{}'.format(int(grid_future[-1,0]),int(grid_future[-1,1])),
            freq='M')
    
        timeindex_historical = pd.period_range(
            start='{}-{}'.format(int(grid_historical[0,0]),int(grid_historical[0,1])),
            end='{}-{}'.format(int(grid_historical[-1,0]),int(grid_historical[-1,1])),
            freq='M')
    
        # Creating dataframe with catchment-wide weather variable       
        df_future = \
            pd.DataFrame(data={'precip': df_precip_f.sum(axis=1).values,
                         'temp': df_temp_f.sum(axis=1).values},
                         index=timeindex_future)

        
        df_historical = \
            pd.DataFrame(data={'precip': df_precip_h.sum(axis=1).values, 
                         'temp': df_temp_h.sum(axis=1).values},
                         index=timeindex_historical)
        
        
    
        # Truncating the dataframe 
        df_baseline = \
            df_historical.truncate(before=HISTORICAL[0], after=HISTORICAL[1])
        df_baseline.index=pd.date_range(start=HISTORICAL[0], end=HISTORICAL[1], freq='M')
        df_baseline.index.name = 'Date'
        df_baseline_annual = df_baseline.groupby(pd.Grouper(level='Date',freq='A-SEP')).mean()
            
        
        df_close_future = \
            df_future.truncate(before=FUTURE_1[0], after=FUTURE_1[1])
        df_close_future.index=pd.date_range(start=FUTURE_1[0], end=FUTURE_1[1], freq='M')
        df_close_future.index.name='Date'
        df_close_future_annual = df_close_future.groupby(pd.Grouper(level='Date',freq='A-SEP')).mean()
        
        df_far_future = \
            df_future.truncate(before=FUTURE_2[0], after=FUTURE_2[1])
        df_far_future.index=pd.date_range(start=FUTURE_2[0], end=FUTURE_2[1], freq='M')
        df_far_future.index.name='Date'
        df_far_future_annual = df_far_future.groupby(pd.Grouper(level='Date',freq='A-SEP')).mean()
            
            
        
                                           
            
        # Append the lists of Deltas
        absolute_annual_change_T_fut1.append(
            df_close_future['temp'].mean() - df_baseline['temp'].mean())
        
        absolute_annual_change_T_fut2.append(
            df_far_future['temp'].mean() - df_baseline['temp'].mean())            
        
        
        realtive_change_P_fut1.append(
            (df_close_future['precip'].mean() - df_baseline['precip'].mean()) \
            / df_baseline['precip'].mean() * 100)
        
        realtive_change_P_fut2.append(
            (df_far_future['precip'].mean() - df_baseline['precip'].mean()) \
            / df_baseline['precip'].mean() * 100)
        
        
        df_baseline_annual_CV = \
            np.std(df_baseline['precip'].resample('A').sum()) \
            / np.mean(df_baseline['precip'].resample('A').sum())
        
        
        df_close_future_annual_CV = \
            np.std(df_close_future['precip'].resample('A').sum()) \
            / np.mean(df_close_future['precip'].resample('A').sum())
        
        
        df_far_future_annual_CV = \
            np.std(df_far_future['precip'].resample('A').sum()) \
            / np.mean(df_far_future['precip'].resample('A').sum())
            
        relative_CV_fut1.append(
            (df_close_future_annual_CV - df_baseline_annual_CV) \
            / df_baseline_annual_CV * 100)
            
        relative_CV_fut2.append(
            (df_far_future_annual_CV - df_baseline_annual_CV) \
            / df_baseline_annual_CV * 100)
            
            
            
        
        ratio_change_T_fut1.append(
            np.mean(df_close_future['temp'])/np.mean(df_baseline['temp']) *100)
        
        ratio_change_T_fut2.append(
            np.mean(df_far_future['temp'])/np.mean(df_baseline['temp']) *100)
        
        ratio_change_P_fut1.append(
            np.mean(df_close_future['precip'])/np.mean(df_baseline['precip']) *100)
        
        ratio_change_P_fut2.append(
            np.mean(df_far_future['precip'])/np.mean(df_baseline['precip']) *100)
        
        ratio_change_std_T_fut1.append(
            np.std(df_close_future['temp'])/np.std(df_baseline['temp']) *100)
        
        ratio_change_std_T_fut2.append(
            np.std(df_far_future['temp'])/np.std(df_baseline['temp']) *100)
            
        ratio_change_std_P_fut1.append(
            np.std(df_close_future['precip'])/np.std(df_baseline['precip']) *100)
        
        ratio_change_std_P_fut2.append(
            np.std(df_far_future['precip'])/np.std(df_baseline['precip']) *100)
        
        
        ratio_change_std_annual_P_fut1.append(
            np.std(df_close_future_annual['precip'])/np.std(df_baseline_annual['precip']) *100)
        
        ratio_change_std_annual_P_fut2.append(
            np.std(df_far_future_annual['precip'])/np.std(df_baseline_annual['precip']) *100)
        
        
        ratio_change_std_annual_T_fut1.append(
            np.std(df_close_future_annual['temp'])/np.std(df_baseline_annual['temp']) *100)
        
        ratio_change_std_annual_T_fut2.append(
            np.std(df_far_future_annual['temp'])/np.std(df_baseline_annual['temp']) *100)
            
        
        
        # Appending the list of available gcm for the selected RCP
        available_gcm.append(gcm)
    
    df = pd.DataFrame({'dT(C) (2026-2055)':absolute_annual_change_T_fut1,
                   'dT(C) (2056-2085)':absolute_annual_change_T_fut2,
                   'dP(%) (2026-2055)':realtive_change_P_fut1,
                   'dP(%) (2056-2085)':realtive_change_P_fut2,
                   'dCVP(%) (2026-2055)': relative_CV_fut1,
                   'dCVP(%) (2056-2085)': relative_CV_fut2},
                   index=available_gcm)
    
    df = df.sort_index()
    df.index.name = 'GCM'
    
    df.to_csv('../data/CMIP5_projections/DeltaChange/delta_change_CMIP5_{}_MetaRiver'\
        '_baseline=1976-2005.csv'.format(rcp))
        
    #####################    
    df2 = pd.DataFrame({'dT(ratio) (2026-2055)':ratio_change_T_fut1,
                   'dT(ratio) (2056-2085)':ratio_change_T_fut2,
                   'dP(ratio) (2026-2055)':ratio_change_P_fut1,
                   'dP(raio) (2056-2085)':ratio_change_P_fut2,
                   'dTstd(ratio monthly) (2026-2055)': ratio_change_std_T_fut1,
                   'dTstd(ratio monthly) (2056-2085)': ratio_change_std_T_fut2,
                   'dPstd(ratio monthly) (2026-2055)': ratio_change_std_P_fut1,
                   'dPstd(ratio monthly) (2056-2085)': ratio_change_std_P_fut2,
                   
                   'dTstd(ratio annual) (2026-2055)': ratio_change_std_annual_T_fut1,
                   'dTstd(ratio annual) (2056-2085)': ratio_change_std_annual_T_fut2,
                   'dPstd(ratio annual) (2026-2055)': ratio_change_std_annual_P_fut1,
                   'dPstd(ratio annual) (2056-2085)': ratio_change_std_annual_P_fut2},
                   index=available_gcm)
    
    df2 = df2.sort_index()
    df2.index.name = 'GCM'
    
    df2.to_csv('../data/CMIP5_projections/Ratios/Ratios_CMIP5_{}_MetaRiver'\
        '_baseline=1976-2005.csv'.format(rcp))



"""
    The plot below shows the GCM data only
    No barplot on the edges
"""




for region in REGION:
    rcp = 'rcp85'
    delta = pd.read_csv('../data/CMIP5_projections/DeltaChange/delta_change_CMIP5_{}_MetaRiver'\
            '_baseline=1976-2005.csv'.format(rcp),
            index_col='GCM')
    
    # Scatter Plot with Projections and Expert and distribution
    fig, ax = plt.subplots(figsize=(6,4.05))
    #fig = plt.figure(figsize=(9,6), constrained_layout=False)
    
    
    ax.scatter(delta['dP(%) (2026-2055)'].values,
                delta['dT(C) (2026-2055)'].values,
                c=['#ffffcc' for x in range(delta.shape[0])],
                s=120,
                edgecolors='k',
                alpha=0.8,
                label='RCP8.5 (2040)')
    
    ax.scatter(delta['dP(%) (2056-2085)'].values,
                delta['dT(C) (2056-2085)'].values,
                c=['#41b6c4' for x in range(delta.shape[0])],
                s=120,
                edgecolors='k',
                alpha=0.8,
                label='RCP8.5 (2070)')
    
    rectangle = plt.Rectangle((-40,0), 70, 5, edgecolor='red', fill=None, alpha=1,
        linestyle='--', linewidth=2, label='Stress Test range')
    plt.gca().add_patch(rectangle)
    
    ax.set_xticks(np.arange(-40,31,10))
    ax.set_yticks(np.arange(-1,9,1))
    ax.set_xlim(-45,35)
    ax.set_ylim(-1,6)
    
    ax.set_ylabel('$\Delta\ T(^{\circ}C)$', fontsize=12)
    ax.set_xlabel('$\Delta\ P(\%)$', fontsize=12)
    
    ax.grid(which='major')
    
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    #plt.minorticks_on()
    ax.tick_params(axis='x', which='minor')
    ax.grid(which='minor', axis='x')
    #ax.legend()
    
    handles, labels = ax.get_legend_handles_labels()
    plt.figlegend(handles, labels, loc = 'lower center', ncol=3, bbox_to_anchor=(0.5,-0.004))
    plt.tight_layout()
    plt.subplots_adjust(top=0.92, bottom=0.2)
    plt.suptitle('Meta River (CMIP5 climate projections)', fontsize=14)
    
    plt.savefig('../figures/ClimateProjections/'
        '{}_Scatter_Plots_GCM_RCP8.5_Baseline=1976-2005.png'.format(region),
        dpi=130)
    
    #plt.show()
    plt.close()

sdf

for region in REGION:
    rcp = 'rcp85'
    delta = pd.read_csv('../data/ClimateProjections/DeltaChange/{}_delta_change_CMIP5_{}_SC'\
            '_LTVA_baseline=1970-2001.csv'.format(region,rcp),
            index_col='GCM')
    
    # Scatter Plot with Projections and Expert and distribution
    fig, ax = plt.subplots(figsize=(6,4.05))
    #fig = plt.figure(figsize=(9,6), constrained_layout=False)
    
    
    ax.scatter(delta['dP(%) (2026-2055)'].values,
                delta['dT(C) (2026-2055)'].values,
                c=['#ffffcc' for x in range(delta.shape[0])],
                s=120,
                edgecolors='k',
                alpha=0.8,
                label='RCP8.5 (2040)')

    ax.scatter(delta['dP(%) (2056-2085)'].values,
                delta['dT(C) (2056-2085)'].values,
                c=['#41b6c4' for x in range(delta.shape[0])],
                s=120,
                edgecolors='k',
                alpha=0.8,
                label='RCP8.5 (2070)')

    #rectangle = plt.Rectangle((-40,0), 80, 7, edgecolor='red', fill=None, alpha=1,
    #    linestyle='--', linewidth=3, label='LTVA range')
    #plt.gca().add_patch(rectangle)
    
    ax.set_xticks(np.arange(-40,65,10))
    ax.set_yticks(np.arange(-1,9,1))
    ax.set_xlim(-45,70)
    ax.set_ylim(-1,8)

    ax.set_ylabel('$\Delta\ T(^{\circ}C)$', fontsize=12)
    ax.set_xlabel('$\Delta\ P(\%)$', fontsize=12)
    
    ax.grid(which='major')
    
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    #plt.minorticks_on()
    ax.tick_params(axis='x', which='minor')
    ax.grid(which='minor', axis='x')
    #ax.legend()

    handles, labels = ax.get_legend_handles_labels()
    plt.figlegend(handles, labels, loc = 'lower center', ncol=3, bbox_to_anchor=(0.5,-0.004))
    plt.tight_layout()
    plt.subplots_adjust(top=0.92, bottom=0.2)
    plt.suptitle(region, fontsize=14)
    
    plt.savefig('../figures/ClimateProjections/'
        '{}_Scatter_Plots_GCM_RCP8.5__2.png'.format(region),
        dpi=130)
    
    #plt.show()
    plt.close()


for region in REGION:
    rcp = 'rcp85'
    delta = pd.read_csv('../data/ClimateProjections/DeltaChange/{}_delta_change_CMIP5_{}_SC'\
            '_LTVA_baseline=1970-2001.csv'.format(region,rcp),
            index_col='GCM')
    
    # Scatter Plot with Projections and Expert and distribution
    fig, ax = plt.subplots(figsize=(6,4.05))
    #fig = plt.figure(figsize=(9,6), constrained_layout=False)
    
    
    ax.scatter(delta['dP(%) (2026-2055)'].values,
                delta['dT(C) (2026-2055)'].values,
                c=['#ffffcc' for x in range(delta.shape[0])],
                s=120,
                edgecolors='k',
                alpha=0.8,
                label='RCP8.5 (2040)')

    ax.scatter(delta['dP(%) (2056-2085)'].values,
                delta['dT(C) (2056-2085)'].values,
                c=['#41b6c4' for x in range(delta.shape[0])],
                s=120,
                edgecolors='k',
                alpha=0.8,
                label='RCP8.5 (2070)')

    rectangle = plt.Rectangle((-40,0), 80, 7, edgecolor='red', fill=None, alpha=1,
        linestyle='--', linewidth=3, label='Stress Test range')
    plt.gca().add_patch(rectangle)
    
    ax.set_xticks(np.arange(-40,65,10))
    ax.set_yticks(np.arange(-1,9,1))
    ax.set_xlim(-45,70)
    ax.set_ylim(-1,8)

    ax.set_ylabel('$\Delta\ T(^{\circ}C)$', fontsize=12)
    ax.set_xlabel('$\Delta\ P(\%)$', fontsize=12)
    
    ax.grid(which='major')
    
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    #plt.minorticks_on()
    ax.tick_params(axis='x', which='minor')
    ax.grid(which='minor', axis='x')
    #ax.legend()

    handles, labels = ax.get_legend_handles_labels()
    plt.figlegend(handles, labels, loc = 'lower center', ncol=3, bbox_to_anchor=(0.5,-0.004))
    plt.tight_layout()
    plt.subplots_adjust(top=0.92, bottom=0.2)
    plt.suptitle(region, fontsize=14)
    
    plt.savefig('../figures/ClimateProjections/'
        '{}_Scatter_Plots_GCM_RCP8.5.png'.format(region),
        dpi=130)
    
    #plt.show()
    plt.close()

for region in REGION:
    rcp = 'rcp85'
    delta = pd.read_csv('../data/ClimateProjections/DeltaChange/{}_delta_change_CMIP5_{}_SC'\
            '_LTVA_baseline=1970-2001.csv'.format(region,rcp),
            index_col='GCM')
    
    # Scatter Plot with Projections and Expert and distribution
    fig, ax = plt.subplots(figsize=(6,4.05))
    #fig = plt.figure(figsize=(9,6), constrained_layout=False)
    
    
    ax.scatter(delta['dP(%) (2026-2055)'].values,
                delta['dT(C) (2026-2055)'].values,
                c=['#ffffcc' for x in range(delta.shape[0])],
                s=120,
                edgecolors='k',
                alpha=0.8,
                label='RCP8.5 (2040)')

    #ax.scatter(delta['dP(%) (2056-2085)'].values,
    #            delta['dT(C) (2056-2085)'].values,
    #            c=['#41b6c4' for x in range(delta.shape[0])],
    #            s=120,
    #            edgecolors='k',
    #            alpha=0.8,
    #            label='RCP8.5 (2070)')

    #rectangle = plt.Rectangle((-40,0), 80, 7, edgecolor='red', fill=None, alpha=1,
    #    linestyle='--', linewidth=3, label='LTVA range')
    #plt.gca().add_patch(rectangle)
    
    ax.set_xticks(np.arange(-40,65,10))
    ax.set_yticks(np.arange(-1,9,1))
    ax.set_xlim(-45,70)
    ax.set_ylim(-1,8)

    ax.set_ylabel('$\Delta\ T(^{\circ}C)$', fontsize=12)
    ax.set_xlabel('$\Delta\ P(\%)$', fontsize=12)
    
    ax.grid(which='major')
    
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    #plt.minorticks_on()
    ax.tick_params(axis='x', which='minor')
    ax.grid(which='minor', axis='x')
    #ax.legend()

    handles, labels = ax.get_legend_handles_labels()
    plt.figlegend(handles, labels, loc = 'lower center', ncol=3, bbox_to_anchor=(0.5,-0.004))
    plt.tight_layout()
    plt.subplots_adjust(top=0.92, bottom=0.2)
    plt.suptitle(region, fontsize=14)
    
    plt.savefig('../figures/ClimateProjections/'
        '{}_Scatter_Plots_GCM_RCP8.5__3.png'.format(region),
        dpi=130)
    
    #plt.show()
    plt.close()


for region in REGION:
    rcp = 'rcp85'
    delta = pd.read_csv('../data/ClimateProjections/DeltaChange/{}_delta_change_CMIP5_{}_SC'\
            '_LTVA_baseline=1970-2001.csv'.format(region,rcp),
            index_col='GCM')
    
    # Scatter Plot with Projections and Expert and distribution
    fig, ax = plt.subplots(figsize=(6,4.05))
    #fig = plt.figure(figsize=(9,6), constrained_layout=False)
    
    
    ax.scatter(delta['dP(%) (2026-2055)'].values,
                delta['dCVP(%) (2026-2055)'].values,
                c=['#ffffcc' for x in range(delta.shape[0])],
                s=120,
                edgecolors='k',
                alpha=0.8,
                label='RCP8.5 (2040)')
    
    ax.scatter(delta['dP(%) (2056-2085)'].values,
                delta['dCVP(%) (2056-2085)'].values,
                c=['#41b6c4' for x in range(delta.shape[0])],
                s=120,
                edgecolors='k',
                alpha=0.8,
                label='RCP8.5 (2070)')
    
    #rectangle = plt.Rectangle((-40,0), 80, 7, edgecolor='red', fill=None, alpha=1,
    #    linestyle='--', linewidth=3, label='LTVA range')
    #plt.gca().add_patch(rectangle)
    
    ax.set_xticks(np.arange(-40,65,10))
    ax.set_yticks(np.arange(-40,70,10))
    ax.set_xlim(-45,70)
    ax.set_ylim(-45,70)
    
    ax.set_ylabel('$\Delta\ CV_P(\%)$', fontsize=12)
    ax.set_xlabel('$\Delta\ P(\%)$', fontsize=12)
    
    ax.grid(which='major')
    
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    #plt.minorticks_on()
    ax.tick_params(axis='x', which='minor')
    ax.grid(which='minor', axis='x')
    #ax.legend()
    
    handles, labels = ax.get_legend_handles_labels()
    plt.figlegend(handles, labels, loc = 'lower center', ncol=3, bbox_to_anchor=(0.5,-0.004))
    plt.tight_layout()
    plt.subplots_adjust(top=0.92, bottom=0.2)
    plt.suptitle(region, fontsize=14)
    
    plt.savefig('../figures/ClimateProjections/'
        '{}_Scatter_Plots_GCM_RCP8.5_wCV.png'.format(region),
        dpi=130)
    
    plt.show()
    plt.close()

    
sdf



#fut1, = ax1.scatter(delta['dP(%) (2026-2055)'], delta['dT(C) (2026-2055)'],
#        'o', markerfacecolor='g', markersize=8, markeredgecolor='w',
#        label='RCP8.5 (2040)')

#fut2, = ax1.scatter(delta['dP(%) (2056-2085)'], delta['dT(C) (2056-2085)'],
#        'o', markerfacecolor='k', markersize=8, markeredgecolor='w', 
#        label='RCP8.5 (2070)')

#ax1.scatter(delta.loc[CAL_ADAPT]['dP(%) (2026-2055)'].values,
#                     delta.loc[CAL_ADAPT]['dT(C) (2026-2055)'].values,
#                     c=['#f0f9e8' for x in range(4)], label='RCP8.5 CalAapt (shortlist) (2040)')

#fut2_cal, = ax1.scatter(delta.loc[CAL_ADAPT]['dP(%) (2056-2085)'],
#                     delta.loc[CAL_ADAPT]['dT(C) (2056-2085)'],
#                     'o', markerfacecolor='k', markersize=8, markeredgecolor='r',
#                     markeredgewidth=12, label='RCP8.5 CalAapt (shortlist) (2070)')

#fut1_cal_all, = ax1.scatter(delta.loc[CAL_ADAPT_ALL]['dP(%) (2026-2055)'],
#                     delta.loc[CAL_ADAPT_ALL]['dT(C) (2026-2055)'],
#                     'o', markerfacecolor='g', markersize=8, markeredgecolor='b',
#                     markeredgewidth=3, label='RCP8.5 CalAapt (2040)')

#fut2_cal_all, = ax1.scatter(delta.loc[CAL_ADAPT_ALL]['dP(%) (2056-2085)'],
#                     delta.loc[CAL_ADAPT_ALL]['dT(C) (2056-2085)'],
#                     'o', markerfacecolor='k', markersize=8, markeredgecolor='b',
#                     markeredgewidth=3, label='RCP8.5 CalAapt (2070)')




for region in REGION:
    rcp = 'rcp85'
    delta = pd.read_csv('../data/GCM/DeltaChange/{}_delta_change_CMIP5_{}_SFPUC'\
            '_LTVA_baseline=1986-2005.csv'.format(region,rcp),
            index_col='GCM')
    
    # Scatter Plot with Projections and Expert and distribution
    fig = plt.figure(figsize=(9,6))
    #fig = plt.figure(figsize=(9,6), constrained_layout=False)
    gs = fig.add_gridspec(6, 6, wspace=0.3, hspace=0.5, left=0.08, right=0.98, top=0.9)
    ax1 = plt.subplot(gs[0:-2, 2:])
    
    ax1.scatter(delta['dP(%) (2026-2055)'].values,
                delta['dT(C) (2026-2055)'].values,
                c=['#ffffcc' for x in range(delta.shape[0])],
                s=120,
                edgecolors='k',
                label='RCP8.5 (2040)')

    ax1.scatter(delta['dP(%) (2056-2085)'].values,
                delta['dT(C) (2056-2085)'].values,
                c=['#41b6c4' for x in range(delta.shape[0])],
                s=120,
                edgecolors='k',
                label='RCP8.5 (2070)')

    #ax1.scatter(delta.loc[CAL_ADAPT]['dP(%) (2026-2055)'].values,
    #            delta.loc[CAL_ADAPT]['dT(C) (2026-2055)'].values,
    #            c=['#c7e9b4' for x in range(delta.loc[CAL_ADAPT].shape[0])],
    #            s=120,
    #            edgecolors='k',
    #            label='RCP8.5 CalAapt (shortlist) (2040)')

    #ax1.scatter(delta.loc[CAL_ADAPT]['dP(%) (2056-2085)'].values,
    #            delta.loc[CAL_ADAPT]['dT(C) (2056-2085)'].values,
    #            c=['#2c7fb8' for x in range(delta.loc[CAL_ADAPT].shape[0])],
    #            s=120,
    #            edgecolors='k',
    #           label='RCP8.5 CalAapt (shortlist) (2070)')

    #ax1.scatter(delta.loc[CAL_ADAPT_ALL]['dP(%) (2026-2055)'].values,
    #            delta.loc[CAL_ADAPT_ALL]['dT(C) (2026-2055)'].values,
    #            c=['#7fcdbb' for x in range(delta.loc[CAL_ADAPT_ALL].shape[0])],
    #            edgecolors='k',
    #            s=120,
    #            label='RCP8.5 CCATG (2040)')

    #ax1.scatter(delta.loc[CAL_ADAPT_ALL]['dP(%) (2056-2085)'],
    #            delta.loc[CAL_ADAPT_ALL]['dT(C) (2056-2085)'],
    #            c=['#253495' for x in range(delta.loc[CAL_ADAPT_ALL].shape[0])],
    #            s=120,
    #            edgecolors='k',
    #            label='RCP8.5 CCATG (2070)')
                     
    ax1.plot(Expert_2040['X'].values, Expert_2040['Y'].values, color='g', 
        marker='x', markersize=9, linestyle='None', 
        label='Elicitation (2040)')
        
    ax1.plot(Expert_2070rcp85['X'].values, Expert_2070rcp85['Y'].values, 
        color='k', marker='x', markersize=9, linestyle='None', 
        label='Elicitation (2070)')

    ax1.set_xticks(np.arange(-40,65,10))
    ax1.set_xlim(-45,70)
    ax1.set_ylim(-1,8)

    ax1.grid()
    ax1.legend()

    ax2T = plt.subplot(gs[0:-2, 1], sharey=ax1)
    sns.distplot(delta['dT(C) (2026-2055)'].values, color='g', vertical=True, 
        bins=np.linspace(-0.25,7.75,17), label = '2040', ax=ax2T, kde=False)
    sns.distplot(delta['dT(C) (2056-2085)'].values, color='k', vertical=True,
        bins=np.linspace(-0.25,7.75,17), label = '2070', ax=ax2T, kde=False)

    ax2T.grid()
    ax2T.set_xticks([0,5,10])
    ax2T.set_xlabel('# GCM', fontsize=10)
    ax2T.set_ylabel('$\Delta\ T(^{\circ}C)$', fontsize=12)
    ax2T.legend(fontsize=8)

    ax2P = plt.subplot(gs[-2, 2:], sharex=ax1)
    sns.distplot(delta['dP(%) (2026-2055)'].values, color='g', vertical=False, 
        bins=np.linspace(-32.5,32.5,14), label = '2040', ax=ax2P, kde=False)
    sns.distplot(delta['dP(%) (2056-2085)'].values, color='k', vertical=False, 
        bins=np.linspace(-32.5,32.5,14), label = '2070', ax=ax2P, kde=False)

    ax2P.grid()
    ax2P.set_yticks([0,5,10])
    ax2P.set_ylabel('# GCM', fontsize=10)
    ax2P.set_xlabel('$\Delta\ P(\%)$', fontsize=12)
    ax2P.legend(fontsize=8)

    ax3T = plt.subplot(gs[0:-2, 0], sharey=ax1)
    sns.distplot(Expert_2040['Y'].values, color='g', vertical=True, 
        bins=np.linspace(-0.25,7.75,17), label = '2040', ax=ax3T, kde=False)
    sns.distplot(Expert_2070rcp85['Y'].values, color='k', vertical=True, 
        bins=np.linspace(-0.25,7.75,17), label = '2070', ax=ax3T, kde=False)
    

    ax3T.grid()
    ax3T.set_xticks([0,5,10])
    ax3T.set_xlabel('# Elicitation', fontsize=10)
    ax3T.set_ylabel('$\Delta\ T(^{\circ}C)$', fontsize=12)
    ax3T.legend(fontsize=8)

    ax3P = plt.subplot(gs[-1, 2:], sharex=ax1)
    sns.distplot(Expert_2040['X'].values, color='g', vertical=False, 
        bins=np.linspace(-32.5,32.5,14), label = '2040', ax=ax3P, kde=False)
    sns.distplot(Expert_2070rcp85['X'].values, color='k', vertical=False,
        bins=np.linspace(-32.5,32.5,14), label = '2070', ax=ax3P, kde=False)
    

    ax3P.grid()
    ax3P.set_yticks([0,5,10])
    ax3P.set_ylabel('# Elicitation', fontsize=10)
    ax3P.set_xlabel('$\Delta\ P(\%)$', fontsize=12)
    ax3P.legend(fontsize=8)
    plt.savefig('../figures_revision_LTVA/Climate/'
        '{}_Scatter_Plots_GCM_RCP8.5._with_Expert.png'.format(region),
        dpi=130)
        
    handles, labels = ax1.get_legend_handles_labels()
    plt.figlegend(handles, labels, loc = 'lower center', ncol=4, bbox_to_anchor=(0.5,-0.004))
    plt.tight_layout()
    plt.subplots_adjust(bottom = 0.18, top=0.99)
    plt.suptitle(region, fontsize=14)
    plt.show()
    plt.close()
        


