

# CONDA ENV: WSM
from itertools import product
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.ticker import FormatStrFormatter
from ShiftedColorMap import shiftedColorMap


dispatch_scenarios = ('BW_collab', 'FCFS')
real_ =  [1]
dT_ = np.arange(0,6,1)
dP_ = np.arange(70,131,10)

real = real_[0]

annual_max_deficit = np.zeros((dT_.shape[0], dP_.shape[0]))
frequency_def = np.zeros_like(annual_max_deficit)
flow_meta_outlet_m3_per_s = np.zeros_like((annual_max_deficit))

for dispatch_scenario in dispatch_scenarios:

    for id_t, dT in enumerate(dT_):
        for id_p , dP in enumerate(dP_):
    
            ofm = pd.read_csv('../results/CST/OWF_{}_R{}_DT{}_DP{}.csv'.format(
                dispatch_scenario, real, dT, dP), index_col='Date', parse_dates=True)
                
            ofm_annual = ofm.resample('A').sum()
            
            total_demand = ofm_annual['Demand_FreshWaterRural_TOTAL_cmd'] \
                         + ofm_annual['Demand_FreshWaterUrban_TOTAL_cmd'] \
                         + ofm_annual['Demand_Irrigation_TOTAL_cmd'] \
                         + ofm_annual['Demand_Livestock_TOTAL_cmd']
                         
            deliveries = ofm_annual['Deliveries_cmd']
            
            deficit= total_demand - deliveries
            
            annual_max_deficit[id_t,id_p] = deficit.max() / 10**6
            
            frequency_def[id_t,id_p] = \
                deficit[deficit>0.1].count() / deficit.shape[0] * 100
                
            flow_meta_outlet_m3_per_s[id_t,id_p] = \
                ofm['Meta_downstream_carreno_cmd'].mean() / 3600 / 24
    
    
    
    variables = (
        ('Annual maximum deficit', annual_max_deficit, '$Mm^3$', 150, cm.bwr),
        ('Frequency of deficit', frequency_def, '%', 100, cm.bwr),
        ('Average daily flow at Puerto Carreno', flow_meta_outlet_m3_per_s, '$m^3s^{-1}$', 10000, cm.bwr_r)
        )
        
    for name, var, unit, max_scale_label, cmap in variables:
        
        
        # Univariate response functions
        # -----------------------------
        
        # X-axis is precip
        fig, ax = plt.subplots(1,1, figsize=(7,4))
        
        ax.plot(dP_, var[0,:], color='k', lw=2, label='No Change')
        ax.plot(dP_, var[1,:], color='#fdd49e', lw=2, label=r'$\Delta T=+1^{\circ}C$')
        ax.plot(dP_, var[2,:], color='#fdbb84', lw=2, label=r'$\Delta T=+2C$')
        ax.plot(dP_, var[3,:], color='#fc8d59', lw=2, label=r'$\Delta T=+3C$')
        ax.plot(dP_, var[4,:], color='#e34a33', lw=2, label=r'$\Delta T=+4C$')
        ax.plot(dP_, var[5,:], color='#b30000', lw=2, label=r'$\Delta T=+5C$')
        
        ax.set_xlabel('$\Delta P (\%)$', fontsize=12)
        ax.set_ylabel(unit, fontsize=12)
        
        handles, labels = ax.get_legend_handles_labels()
        plt.figlegend(handles, labels, loc = 'lower center', ncol=4, 
            bbox_to_anchor=(0.5,-0.004), fontsize=10, handlelength=1)
        
        plt.title('{} - {}'.format(name, dispatch_scenario), fontsize=12)
        ax.grid()
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.25)
        fig.savefig('../figures/Performance_metrics/{}_{}_XDeltaP.png'.format(
            name, dispatch_scenario), dpi=130)
        #plt.show()
        plt.close()
        
        
        # X-axis is temperature
        fig, ax = plt.subplots(1,1, figsize=(7,4))
        
        ax.plot(dT_, var[:,0], color='#b2182b', lw=2, label=r'$\Delta P=-30\%$')
        ax.plot(dT_, var[:,1], color='#ef8a62', lw=2, label=r'$\Delta P=-20\%$')
        ax.plot(dT_, var[:,2], color='#fddbc7', lw=2, label=r'$\Delta P=-10\%$')
        ax.plot(dT_, var[:,3], color='k', lw=2, label=r'No Change')
        ax.plot(dT_, var[:,4], color='#d1e5f0', lw=2, label=r'$\Delta P=+10\%$')
        ax.plot(dT_, var[:,5], color='#67a9cf', lw=2, label=r'$\Delta P=+20\%$')
        ax.plot(dT_, var[:,6], color='#2166ac', lw=2, label=r'$\Delta P=+30\%$')
        
        ax.set_xlabel('$\Delta T (C)$', fontsize=12)
        ax.set_ylabel(unit, fontsize=12)
        handles, labels = ax.get_legend_handles_labels()
        plt.figlegend(handles, labels, loc = 'lower center', ncol=4, 
            bbox_to_anchor=(0.5,-0.004), fontsize=10, handlelength=1)
        
        plt.title('{} - {}'.format(name, dispatch_scenario), fontsize=12)
        ax.grid()
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.25)
        fig.savefig('../figures/Performance_metrics/{}_{}_XDeltaT.png'.format(
            name, dispatch_scenario), dpi=130)
        #plt.show()
        plt.close()
        
        # Bi-variate response functions
        fig, ax = plt.subplots(1,1, figsize=(7,7))

        midpoint = var[0,3] / max_scale_label

        crf = ax.imshow(var, 
                  extent=(-35, 35,-0.5, 5.5), 
                  cmap=shiftedColorMap(cmap, midpoint=midpoint, name='shifted'),
                  aspect='auto',
                  vmin=0,
                  vmax=max_scale_label,
                  origin='lower')
        
        cbar = fig.colorbar(crf, ax=ax)
        cbar.set_label('{}'.format(unit), fontsize=20)
        crf.figure.axes[1].tick_params(axis="y", labelsize=16)
        
        
        contour = ax.contour(dP_-100, dT_, var, 
            levels=8, colors='k', linewidths=3)
        ax.clabel(contour, inline=1, fmt='%1.0f', fontsize=12, colors='k')

        ax.set_xlabel('$\Delta P (\%)$', fontsize=16)
        ax.set_ylabel('$\Delta T (C)$', fontsize=16)
        
        ax.set_xticklabels(ax.get_xticks(), fontsize=16)
        ax.set_yticklabels(ax.get_yticks(), fontsize=16)
        ax.xaxis.set_major_formatter(FormatStrFormatter('%1.0f'))
        ax.yaxis.set_major_formatter(FormatStrFormatter('%1.0f'))
        
        plt.title('{} - {}'.format(name, dispatch_scenario), fontsize=16)
        
        plt.tight_layout()
        fig.savefig('../figures/Performance_metrics/CRF_{}_{}.png'.format(
            name, dispatch_scenario), dpi=130)
        #plt.show()
        plt.close()
    
        
        
        