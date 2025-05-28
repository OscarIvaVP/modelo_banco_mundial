
# CONDA ENV: WSM2

# IMPORT OTHER FUNCTIONS
import sys
import argparse
import pandas as pd
import numpy as np
import datetime
import os
import time
from itertools import product
import matplotlib.pyplot as plt
import multiprocessing as mp


# Wildcard import from the OWF_ScenarioVariables module  
from OWF_ScenarioVariables import *

we_do_need_json_files = True

path_results = '/scracth3/workspace/bfrancois_umass_edu-swot_PLD_images/OWF_CST_results/'


# IMPORT PYWR MODULE FUNCTIONS
from pywr.core import Model
from pywr.parameters import load_parameter

# FUNCTIONS WATER DEMAND
from ofm_water_demand import Freshwater_Demand
from ofm_water_demand import Livestock_Demand
from ofm_water_demand import Irrigation_Demand
Freshwater_Demand.register()
Livestock_Demand.register()
Irrigation_Demand.register()

from ofm_dam_operations import Dam_Release
Dam_Release.register()


# FUNCTIONS FOR RESERVOIRS EVAP AND PRCP
# Note that these python classes are currently placeholder as the available information at the time
# of creation of the model does not allow accounting for neither of these fluxes.
# These two python classes always return 0.
from ofm_reservoir_pet_prcp import Reservoir_Evap_Demand
from ofm_reservoir_pet_prcp import Reservoir_Precip
Reservoir_Evap_Demand.register()
Reservoir_Precip.register()

# FUNCTIONS FOR RESERVOIR VOLUME TO AREA
# Simiar to the evaporation/precipitation over the reservoirs, this python class is a placeholder.
# It currently always returns 0.
from ofm_reservoir_volume_area import VolumeAreaCurve
VolumeAreaCurve.register()



if we_do_need_json_files:
    sys.argv = [dispatch_scenarios, real_, dT_, dP_, Dfw_scenarios_, Dirr_scenarios_, Dliv_scenarios_]
    builder_script = open('Build_OWF_CST.py')
    builder = builder_script.read()
    exec(builder)


# Initialize the list of scenarios to be run
model_runs = []

# Loop over the scenarios
for dispatch_scenario, dT, dP, real, Dfw_scenario, Dirr_scenario, Dliv_scenario in product(
     dispatch_scenarios, dT_, dP_, real_, Dfw_scenarios_, Dirr_scenarios_, Dliv_scenarios_):
        
        if os.path.isfile(path_results+'OWF_{}_R{}_DT{}_DP{}_FW{}_Irr{}_Liv{}.csv'.format(
            dispatch_scenario, real, dT, dP, Dfw_scenario, Dirr_scenario, Dliv_scenario)):
            print('file exists')
            
        else:
            model_runs.append('../model_json/CST/models/OWF_{}_R{}_DT{}_DP{}_FW{}_Irr{}_Liv{}.json'.format(
                dispatch_scenario, real, dT, dP, Dfw_scenario, Dirr_scenario, Dliv_scenario))
            


def run_OWF(list_of_scenarios_per_cpu):

    for model in list_of_scenarios_per_cpu:   
        m = Model.load(model)
        m.run()
        
        results = m.to_dataframe()
        results.columns = results.columns.get_level_values(0)
        results = results.reindex(sorted(results.columns), axis=1)
        results.index.name='Date'
        
        # Output raw output files
        results.to_csv(path_results+model[25:-5]+'.csv')


                                    
#Split the scenarios to be process with multiple cpus
chunks = np.array_split(model_runs,nb_cpus)

if __name__ == '__main__':
    # Process the basins in parallel
    mp.Pool(processes=nb_cpus).map(run_OWF, chunks)





