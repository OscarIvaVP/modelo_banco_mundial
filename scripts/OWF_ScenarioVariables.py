
import numpy as np
import pandas as pd
import os


# Number of cpus to use for the CST simulations
nb_cpus = 1

# Path to the csv file containing the streamflow input
flow_path = '../../../input/streamflow/CST/' \
    'Metarunoff_R{}_DT{}_DP{}.csv'

# Path to the csv file containing the weather input
# Note: this is a placeholder as the current version of the CST does use any weather data
# Irrigation demand, which is sensitive to weather, is preprossed.
# Rainfall and evapo over the reservoirs are not accounted for because of lack of information regarding
# the reservoirs' rating curve (i.e., volume to area relationship).
weather_path = ''

# Path to the irrigation demand file
irrigation_path = '../input/irrigation/CST/'


# Scenarios of dispatch order (i.e., who is being served first, second, ...)
# Details regarding these scenarios can be found in Section XXXXXX of the report.
# - FCFS: First Come First Served
# - PE: Policy Enforced

dispatch_scenarios = ('FCFS', 'PE') 

# Climate realizations. 10 realizations are available, but only realizations 1 through 5 are used in the CST
# To run realizations 6 through 10, change the range to np.arange(1,11). Running those realizations 
# through other models (i.e., GR2M, Aquacrop) might be necessary should those simulations be used.
real_ = [1]#np.arange(1,6)

# Range of the scenarios used in the stress test
# dT_ = np.arange(0,1,1) is used to run the baseline temperature scenario only (i.e., no change in T)
# dP_ = np.arange(100,101,10) is used to run the baseline precipitation scenario only (i.e., no change in P)
# To run the full range of scenarios, use the following:
# dT_ = np.arange(0,6,1)
# dP_ = np.arange(70, 131, 10)
dT_ = np.arange(0,1,1)
dP_ = np.arange(100,101,10)

# For each of the scenario below, 4 values are possible: 
# 2022 (baseline) and 2030, 2040, 2050 (projections)
# Projections were obtained from extrapolation of the historical trends (cf. Section XXXXXXXXXXXXXX of the report)
# Note that the current version of the CST does not allow to separate the projections for birds, pigs, and cattle
# as they are all three combined in the 'Livestock' scenario defined by the variable 'Dliv_scenario'.
# Likewise, the current version of the CST does not allow to separate the projections for rice and palm tree
# as they are both combined in the 'Irrigation' scenario defined by the variable 'Dirr_scenario'.
Dfw_scenarios_ = (2022, 2030, 2040, 2050) # Include population and water/use/head for urban, rural
Dirr_scenarios_ = (2022, 2030, 2040, 2050) # Crop areas (include values for both Rice and Palm tree)
Dliv_scenarios_ = (2022, 2030, 2040, 2050) # Include population and water/use/head for chicken, pigs and cattle

