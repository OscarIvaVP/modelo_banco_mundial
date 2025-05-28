

import os, glob
import sys
import json
from itertools import product
import numpy as np
import pandas as pd
import calendar, datetime


def get_parameters(file_contents):
    # return the parameter section
    return file_contents.get("parameters", {})
    
def get_nodes(file_contents):
    #return the nodes section
    return file_contents.get("nodes", {})



# Note: by default, the model setup include two plantation dates for Rice crop (Season 1: April 1st;
# Season 2 August 15th). The current configuration of the model setup is to consider all rice during
# Season 1 as being rainfed (i.e., no irrigation demand) while all rice grown during Season 2 is irrigated.
# Out of the cropland used to grow rice, only 15% of the land is used to grow rice during Season 2.

list_parameters_requiring_streamflow_input = (
    'flow_metica', 
    'flow_guayuriba',
    'flow_negro',
    'flow_guatiquia',
    'flow_guacavia',
    'flow_humea',
    'flow_dir_btw_hu_up',
    'flow_guavio',
    'flow_garagoa',
    'flow_lengupa',
    'flow_upia',
    'flow_lago_de_tota',
    'flow_dir_btw_gb_yu',
    'flow_yucao',
    'flow_manacacias',
    'flow_cumaral',
    'flow_melua',
    'flow_tua',
    'flow_cusiana',
    'flow_dir_btw_cu_cs',
    'flow_cravo_sur',
    'flow_guanapalo',
    'flow_pauto',
    'flow_dir_btw_p_ca',
    'flow_dir_btw_cu_ca',
    'flow_casanare',
    'flow_dir_btw_ca_or'
    )

       
list_parameters_requiring_demand_input = (
    'metica_',
    'guayuriba_',
    'negro_',
    'guatiquia_',
    'humea_',
    'dir_btw_hu_up_',
    'guacavia_',
    'guavio_',
    'garagoa_',
    'lengupa_',
    'upia_',
    'lago_de_tota_',
    'dir_btw_gb_yu_',
    'yucao_',
    'manacacias_',
    'cumaral_',
    'melua_',
    'tua_',
    'cusiana_',
    'dir_btw_cu_cs_',
    'cravo_sur_',
    'guanapalo_',
    'pauto_',
    'dir_btw_p_ca_',
    'dir_btw_cu_ca_',
    'casanare_',
    'dir_btw_ca_or_'    
    )  

# List of nodes to which track deficit

#dispatch_scenarios = ('BW_collab', 'FCFS')

for dT, dP, real, dispatch_scenario, proj_year_Dfw, proj_year_Dirr, proj_year_Dliv in product(
    dT_, dP_, real_, dispatch_scenarios, Dfw_scenarios_, Dirr_scenarios_, Dliv_scenarios_):

    # Policy Enforcement (PE)
    # ------------------------------
    # This scenario considers a policy enforcement where deliveries are
    # prioritized based on their category rather than their locations
    # Currently, Freshwater comes first, next ranching demand and last irrigation.
    # In this configuration, the environmental flows are the highest priority basin-wide
    if dispatch_scenario == 'PE':

        order = pd.read_csv('../input/parameters/dispatch_order_PE.csv', index_col='Basin')
         

    # First Come First Served
    # -----------------------
    # This scenario considered that users that have access to water will use it for 
    # their own purpose without consideration of the users downstream. Within a 
    # unit, the dispatch order also differs from the dispatch order used in BWC because rural population 
    # will be served last, and environmental flows are not enforced.
    elif dispatch_scenario == 'FCFS':

        order = pd.read_csv('../input/parameters/dispatch_order_FCFS.csv', index_col='Basin')
        

            
    # replace the index so that lower case are used only to match the name of the nodes
    order.index = order.index.str.lower()
    # replace 'space' buy '_' to match the name of the nodes (i.e., 'cravo_sur')
    order.index = order.index.str.replace(' ','_')

    # Open the json master file
    with open('../model_json/CST/Parent/OWF_CST.json') as (master_script):

        # Load the json into memory
        file_master = json.load(master_script)
        
        # Get the node section
        nodes_in_file = get_nodes(file_master)

        # Loop over the nodes
        for node in nodes_in_file:
        
            
            if node['name'][-4:] == 'Dtot':
            
                # Policy Enforced (PE) Scenario
                # ------------------------------
                # Environmental flows are enforced in this scenario.
                # Next, the dispatch order is set among: 
                # - urban freshwater (Dfwu, 1st),
                # - rural freshwater (Dfwr, 2nd),
                # - irrigation (Dirr, 3rd),
                # - ranching (Dliv, 4th).
                if dispatch_scenario == 'PE':
                
                    node['max_flows'] = [
                        node['name'][:-5]+'{}'.format('_Dfwu'),
                        node['name'][:-5]+'{}'.format('_Dfwr'),
                        node['name'][:-5]+'{}'.format('_Dirr'),
                        node['name'][:-5]+'{}'.format('_Dliv')
                    ]
                    
                    node['costs'] = [
                        float(order['Dfwu'][node['name'][:-5]]),
                        float(order['Dfwr'][node['name'][:-5]]),
                        float(order['Dirr'][node['name'][:-5]]),
                        float(order['Dliv'][node['name'][:-5]])
                    ]

                # First Come First Served (FCFS) Scenario
                # Enironmental flows are not enforced in this scenario.
                # - urban freshwater (Dfwu, 1st),
                # - irrigation (Dirr, 2nd),
                # - livestock (Dliv, 3rd),
                # - rural freshwater (Dfwr, 4th).
                elif dispatch_scenario == 'FCFS':
                
                    node['max_flows'] = [
                        node['name'][:-5]+'{}'.format('_Dfwu'),
                        node['name'][:-5]+'{}'.format('_Dirr'),
                        node['name'][:-5]+'{}'.format('_Dliv'),
                        node['name'][:-5]+'{}'.format('_Dfwr')
                    ]
                    
                    
                    node['costs'] = [
                        float(order['Dfwu'][node['name'][:-5]]),
                        float(order['Dirr'][node['name'][:-5]]),
                        float(order['Dliv'][node['name'][:-5]]),
                        float(order['Dfwr'][node['name'][:-5]])
                    ]
                    
                
                
                
            
            # Look for environmental flow nodes
            if node['name'][-4:] == 'Denv':
            
                node['costs'] = [float(order['Denv'][node['name'][:-5]]), 0]
                
                
                
        # Streamflow input file 
        # ---------------------
        # Assigning the path to the streamflow input
        for parameter in list_parameters_requiring_streamflow_input:
            
            file_master['parameters'][parameter]['url'] = flow_path.format(real,dT,dP)
                
                
        # Precip input file
        # -----------------
        """
            Will need to be added to calculate precip and evap over Guavio and 
            Garagoa reservoir. Currently, the model disregard prcp and evap
            over the reservoirs because of the lack of information we have.
        """
       
        # Update the parameters that are used to calculate the water demands
        for parameter in list_parameters_requiring_demand_input:

            # Freshwater demand input files
            # -----------------------------    
            # Projection used for the urban and rural freshwater demand. The code currently does not
            # allow to stress test the system with different projections (i.e., 'year') 
            # for urban and rural freshwater demand.
            file_master['parameters'][parameter+'Dfwu']['projection_demand_year'] = proj_year_Dfw
            file_master['parameters'][parameter+'Dfwr']['projection_demand_year'] = proj_year_Dfw
            
                    
            # Livestock demand input files
            # -----------------------------
        
            # Projection used to calculate the livestock demand.
            file_master['parameters'][parameter+'Dliv']['projection_demand_year'] = proj_year_Dliv
        
            # Irrigation demand input files
            # -----------------------------
        
            # Assigning the path to the aquacrop simulations
            file_master['parameters'][parameter+'Dirr']['url']['crop_demand_file'] = \
                irrigation_path+'Aquacrop/Rice/Rice_NetIrrSMT100_mm_' \
                'R{}_DT{}_DP{}.csv'.format(real, dT, dP)
                
            # Assigning the path to the tree irrigation demand
            file_master['parameters'][parameter+'Dirr']['url']['trees_demand_file'] = \
                irrigation_path+'OilPalm/MetaPalmoilDemand_{}_DT{}_DP{}.csv'.format(real, dT, dP)
            
            # Projection used to calculate the irrigation demand (area and efficiency).
            file_master['parameters'][parameter+'Dirr']['projection_demand_year'] = proj_year_Dirr

        # Recorders
        # ---------


                
    with open(
        '../model_json/CST/models/OWF_{}_R{}_DT{}_DP{}_FW{}_Irr{}_Liv{}.json'.format(
            dispatch_scenario, real, dT, dP, proj_year_Dfw, proj_year_Dirr, proj_year_Dliv), 'w') as outfile_master:

        json.dump(file_master,outfile_master, indent=4)
                    
        