

# META_aquacrop.py
# --------------

# This script reads weather data for each hydrological response unit (hru) and
# create time series of irrigation for selected crops and irrigation practices

# The type of crops can be modified via the tuple 'crops'
# The type of irrigation management can be modified via the tuple 'irr_mngts'

# This version of this script runs climate stress test scenarios.

# CONDA ENV: 'aquacrop'

import os
os.environ['DEVELOPMENT'] = 'DEVELOPMENT'

from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent, IrrigationManagement
from aquacrop.utils import prepare_weather, get_filepath
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import product
import multiprocessing as mp


# Simulation start and end dates
sim_start = '2020/01/01'
sim_end = '2070/12/31'


#Note: No data is available for Cumaral catchment. Irrigation requirement for this basin uses 
#the weather time series from the nearby 'Melua' catchment (i.e., the time series within the files
# 'Cumaral_*' are copied/pasted from the 'Melua_*' files). 

# Set the range of scenario we are investigating
real_ = np.arange(1,6,1)
dT_ = np.arange(0,6,1)
dP_ = np.arange(70,131,10)

# List of the HRUs where irrigation demand is calculated
# The path points out to weather inputs data (i.e., Tmin(C), Tmax(C), Prcp(mm)
# and ET0(mm) that have been already been pre-processed and formated
#for dT, dP, real in product(dT_, dP_, real_):

def cst_aquacrop(list_cst_scenarios):

    for dT, dP, real in list_cst_scenarios:

        HRUs = (
            ('Metica', '../input/weather/CST/Metica_{}_DT{}_DP{}.txt'.format(real,dT,dP)),
            ('Guayuriba', '../input/weather/CST/Guayuriba_{}_DT{}_DP{}.txt'.format(real,dT,dP)),
            ('Guatiquia', '../input/weather/CST/Guatiquia_{}_DT{}_DP{}.txt'.format(real,dT,dP)),
            ('Guacavia', '../input/weather/CST/Guacavia_{}_DT{}_DP{}.txt'.format(real,dT,dP)),
            ('Humea', '../input/weather/CST/Humea_{}_DT{}_DP{}.txt'.format(real,dT,dP)),
            ('Guavio', '../input/weather/CST/Guavio_{}_DT{}_DP{}.txt'.format(real,dT,dP)),
            ('Garagoa', '../input/weather/CST/Garagoa_{}_DT{}_DP{}.txt'.format(real,dT,dP)),
            ('Lengupa', '../input/weather/CST/Lengupa_{}_DT{}_DP{}.txt'.format(real,dT,dP)),
            ('Upia', '../input/weather/CST/Upia_{}_DT{}_DP{}.txt'.format(real,dT,dP)),
            ('Lago de Tota', '../input/weather/CST/Lago de Tota_{}_DT{}_DP{}.txt'.format(real,dT,dP)),
            ('Tua', '../input/weather/CST/Tua_{}_DT{}_DP{}.txt'.format(real,dT,dP)),
            ('Manacacias', '../input/weather/CST/Manacacias_{}_DT{}_DP{}.txt'.format(real,dT,dP)),
            ('Melua', '../input/weather/CST/Melua_{}_DT{}_DP{}.txt'.format(real,dT,dP)),
            ('Yucao', '../input/weather/CST/Yucao_{}_DT{}_DP{}.txt'.format(real,dT,dP)),
            ('Cusiana', '../input/weather/CST/Cusiana_{}_DT{}_DP{}.txt'.format(real,dT,dP)),
            ('Cravo Sur', '../input/weather/CST/Cravo Sur_{}_DT{}_DP{}.txt'.format(real,dT,dP)),
            ('Guanapalo', '../input/weather/CST/Guanapalo_{}_DT{}_DP{}.txt'.format(real,dT,dP)),
            ('Pauto', '../input/weather/CST/Pauto_{}_DT{}_DP{}.txt'.format(real,dT,dP)),
            ('Dir_btw_Ca_Or', '../input/weather/CST/Dir_btw_Ca_Or_{}_DT{}_DP{}.txt'.format(real,dT,dP)),
            ('Dir_btw_Cu_Ca', '../input/weather/CST/Dir_btw_Cu_Ca_{}_DT{}_DP{}.txt'.format(real,dT,dP)),
            ('Dir_btw_Cu_CS', '../input/weather/CST/Dir_btw_Cu_CS_{}_DT{}_DP{}.txt'.format(real,dT,dP)),
            ('Dir_btw_Hu_Up', '../input/weather/CST/Dir_btw_Hu_Up_{}_DT{}_DP{}.txt'.format(real,dT,dP)),
            ('Dir_btw_Gb_Yu', '../input/weather/CST/Dir_btw_Gb_Yu_{}_DT{}_DP{}.txt'.format(real,dT,dP)),
            ('Dir_btw_P_Ca', '../input/weather/CST/Dir_btw_P_Ca_{}_DT{}_DP{}.txt'.format(real,dT,dP)),
            ('Negro', '../input/weather/CST/Negro_{}_DT{}_DP{}.txt'.format(real,dT,dP)),
            ('Casanare', '../input/weather/CST/Casanare_{}_DT{}_DP{}.txt'.format(real,dT,dP)),
            ('Cumaral', '../input/weather/CST/Cumaral_{}_DT{}_DP{}.txt'.format(real,dT,dP))
            )


        # List of the crop type for which we calculate the irrigation requirement

        ## ----- BELOW ARE CROP CALENDAR INFORMATION WE CAN FIND ONLINE -----
        ## ===================================================================

        # https://www.fao.org/3/y4347e/y4347e0h.htm

        #Cropping season  Planting  Harvesting
        #Main season        3-4        7-8
        #Second season      8-10       1-2

        # Farmers able ti irrigate might start on January 20th because of higher economic
        # profit (i.e., from Julian and stakeholder engagement workshop)

        crops = (
            ('Rice_PDate=04-01', Crop('PaddyRice', planting_date='04/01')),
            ('Rice_PDate=08-15', Crop('PaddyRice', planting_date='08/15'))
            )

        # Soil Type
        # Placeholder
        soil_type = 'Default' 

        # Type of irrigation schedule
        # ---------------------------
        # Based on a sensitivty analysis, the NetIrrSMT80 was shown to perform best
        # among the considered scheduled (see below). 
        # However, the NetIrrSMT100 schedule was chosen because it corresponds to the irrigation
        # schedule used by the farmers in the region (i.e., flood irrigation)

        #irr_mngts = (
        #    ('Rainfed', IrrigationManagement(irrigation_method=0)),
        #    ('SMT80', IrrigationManagement(irrigation_method=1,SMT=[80]*4)),
        #    ('NetIrrSMT80', IrrigationManagement(irrigation_method=4, NetIrrSMT=80)),
        #    ('NetIrrSMT100', IrrigationManagement(irrigation_method=4, NetIrrSMT=100))
        #    )
            
        irr_mngts = (
            ('NetIrrSMT100', IrrigationManagement(irrigation_method=4, NetIrrSMT=100))
            )

        
        ## DataFrame hosting the results
        # Time series of irrigation demand 
        df_ts = pd.DataFrame(index=pd.date_range(start=sim_start, end=sim_end))
            
        # Loop over the irrigation district
        for (hru, path_weather) in HRUs:
            
                        
            # Weather dataframe
            wdf = prepare_weather(path_weather)
            # Loop over the crop and irrigation management
            #for (crop_name, crop) , (irr_mngt_name, irr_mngt) in product(crops, irr_mngts):
            irr_mngt_name = irr_mngts[0]
            irr_mngt = irr_mngts[1]
            for crop_name, crop in crops:
                model = AquaCropModel(
                    sim_start_time=sim_start,
                    sim_end_time=sim_end,
                    weather_df=wdf,
                    soil=Soil(soil_type),
                    crop=crop,
                    initial_water_content=InitialWaterContent(value=['FC']),
                    irrigation_management=irr_mngt)
                
                model._initialize() # initialize model
                model.run_model(till_termination=True, process_outputs=True)
                results = model.get_simulation_results()
                flux = model.get_water_flux()
                # Note: the 'np.where' function below ensures that no negative 
                # values are returned. Experience using this package has been that 
                # very small negative values are sometimes simulated rather than
                # true 0.
                df_ts['{}_{}_{}'.format(hru,crop_name, irr_mngt_name)] = \
                    np.where(flux['IrrDay'].values>0,np.round(flux['IrrDay'].values,2),0)
                
                # Write seasonal irrig and yield into a excel file
                #crop_perf['{}_{}'.format(crop_name,irr_mngt_name)] = \
                #        [np.round(results['Seasonal irrigation (mm)'].mean(),3), 
                #        np.round(results['Yield (tonne/ha)'].mean(),3),
                #        np.round(results['Yield (tonne/ha)'].mean()/results['Seasonal irrigation (mm)'].mean(),3)]
                        
                #crop_perf.to_excel(writer_crop_performance, sheet_name='{}'.format(hru),
                #        index=False)
            
        df_ts.index.name = 'Date'


        df_ts.to_csv('../input/irrigation/CST/Aquacrop/Rice/'
            'Rice_NetIrrSMT100_mm_R{}_DT{}_DP{}.csv'.format(real,dT,dP))
        
        #df_ts.to_pickle('../input/irrigation/CST/Aquacrop/Rice/'
        #    'Rice_NetIrrSMT100_mm_R{}_DT{}_DP{}.pkl'.format(real,dT,dP))


all_scenarios = np.asarray([x for x in product(dT_, dP_, real_)])
# Split the scenarios to be process with multiple cpus
chunks = np.array_split(all_scenarios,5)

if __name__ == '__main__':
    # Process the basins in parallel
    mp.Pool(processes=8).map(cst_aquacrop, chunks)