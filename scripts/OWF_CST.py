
# CONDA ENV: OWF_env

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
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Wildcard import from the OWF_ScenarioVariables module  
from OWF_ScenarioVariables import *

# Logical variable to determine whether we need to create the json files or not
we_do_need_json_files = True

# Path to the folder the output .csv files will be saved to
path_results = '../results/CST/'

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

# If we_do_need_json_files is True, we will create the json files
# The .json files for each scenario are created by the script Build_OWF_CST.py
if we_do_need_json_files:
    sys.argv = [dispatch_scenarios, real_, dT_, dP_, Dfw_scenarios_, Dirr_scenarios_, Dliv_scenarios_]
    builder_script = open('Build_OWF_CST.py')
    builder = builder_script.read()
    exec(builder)

# Initialize the list of scenarios to be run
model_runs = []

# Create a list of all combinations of the scenarios to be run
# Loop over the scenarios
for dispatch_scenario, dT, dP, real, Dfw_scenario, Dirr_scenario, Dliv_scenario in product(
     dispatch_scenarios, dT_, dP_, real_, Dfw_scenarios_, Dirr_scenarios_, Dliv_scenarios_):
        
        # If an output file already exists, we skip the scenario
        # Note that the output file name is constructed based on the scenario variables
        # This is to avoid running the same scenario multiple times
        # and to save time and resources.
        # If you want to run a scenario that has already been run,
        # you can either delete the output file or change the name of the output file
        if os.path.isfile(path_results+'OWF_{}_R{}_DT{}_DP{}_FW{}_Irr{}_Liv{}.csv'.format(
            dispatch_scenario, real, dT, dP, Dfw_scenario, Dirr_scenario, Dliv_scenario)):
            #print('file exists')
            continue
            
        else:
            model_runs.append('../model_json/CST/models/OWF_{}_R{}_DT{}_DP{}_FW{}_Irr{}_Liv{}.json'.format(
                dispatch_scenario, real, dT, dP, Dfw_scenario, Dirr_scenario, Dliv_scenario))
            

print('Number of scenarios to run: {}'.format(len(model_runs)))

# Create a function to run the OWF model. 
# This function will be run in parallel for each scenario
def run_OWF(list_of_scenarios_per_cpu):

    # Loop over the scenarios to be run
    for model in list_of_scenarios_per_cpu:   
        print(model)

        # Load the model from the json file
        # Note that the model is loaded with presolve enabled. 
        # The experience has shown that solver option sometimes prevents the model from
        # randomly failing.
        m = Model.load(model, solver_args={'use_presolve': True})

        # Run the model
        m.run()
        
        # Collect the results and convert them to a DataFrame
        results = m.to_dataframe()
        # Delete the first row of the DataFrame that is empty
        results.columns = results.columns.get_level_values(0)
        # Sort the columns of the DataFrame by alphabetical order
        results = results.reindex(sorted(results.columns), axis=1)
        # Name the index of the DataFrame
        results.index.name='Date'
        
        # Save the dataframe to a csv file
        results.to_csv(path_results+model[25:-5]+'.csv')

                                    
# Split the scenarios to be processed with multiple cpus
# The `chunks` variable is a list of lists, where each sublist contains the scenarios to be run by 
# a single cpu
# The number of cpus to be used is defined by the variable `nb_cpus`, which is defined in the
# OWF_ScenarioVariables.py module.
chunks = np.array_split(model_runs,nb_cpus)

if __name__ == '__main__':
    # Process the basins in parallel
    mp.Pool(processes=nb_cpus).map(run_OWF, chunks)
