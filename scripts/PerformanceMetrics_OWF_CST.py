
# conda: owf_env
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
from itertools import product
from tqdm import tqdm

path_results_CST = '../results/CST/'

real_ = np.arange(1,6,1)
DT_ = np.arange(0,6,1)
DP_ = np.arange(70,131,10)
Dfw_ = ['2022', '2030', '2040', '2050']
Dirr_ = ['2022', '2030', '2040', '2050']
Dliv_ = ['2022', '2030', '2040', '2050']
Dispatch_ = ['FCFS', 'PE']

# Create an output files that contains average deficit per customer and per region
list_of_subbasins = [
    'Metica', 'Guayuriba', 'Negro', 'Guatiquia', 'Guacavia', 'Humea', 'Dir_btw_hu_up',
    'Guavio', 'Garagoa', 'Lengupa', 'Lago_de_tota', 'Upia', 'Dir_btw_gb_yu', 'Yucao', 'Manacacias',
    'Cumaral', 'Melua', 'Tua', 'Cusiana', 'Dir_btw_cu_cs', 'CravoSur', 'Guanapalo',
    'Pauto', 'Dir_btw_p_ca', 'Dir_btw_cu_ca', 'Casanare', 'Dir_btw_ca_or']


performance_metrics = ['AnnualDeficit_Dfw_mean_Mm3', 
                       'AnnualDeficit_Dirr_mean_Mm3', 
                       'AnnualDeficit_Dliv_mean_Mm3', 
                       'AnnualDeficit_Denv_mean_Mm3',
                       'AnnualDeficit_Dfw_max_Mm3', 
                       'AnnualDeficit_Dirr_max_Mm3', 
                       'AnnualDeficit_Dliv_max_Mm3', 
                       'AnnualDeficit_Denv_max_Mm3',
                       'AnnualDeficit_Dfw_q95_Mm3', 
                       'AnnualDeficit_Dirr_q95_Mm3', 
                       'AnnualDeficit_Dliv_q95_Mm3', 
                       'AnnualDeficit_Denv_q95_Mm3',
                       'AnnualDeficit_Dfw_q75_Mm3', 
                       'AnnualDeficit_Dirr_q75_Mm3', 
                       'AnnualDeficit_Dliv_q75_Mm3', 
                       'AnnualDeficit_Denv_q75_Mm3']

deficit_per_basin = pd.DataFrame(columns=('urban', 'rural', 'livestock', 'agriculture', 'envflow'),
    index=list_of_subbasins)

models = []

for dt, dp, real, Dfw, Dirr, Dliv, dispatch in product(DT_, DP_, real_, Dfw_, Dirr_, Dliv_, Dispatch_):

    models.append('OWF_{}_R{}_DT{}_DP{}_FW{}_Irr{}_Liv{}.csv'.format(dispatch, real, dt, dp, Dfw, Dirr, Dliv))

# Create the arrays to store the results
annual_average_urban = np.ones((len(list_of_subbasins), len(DT_), len(DP_), len(real_), len(Dfw_),
                                  len(Dirr_), len(Dliv_), len(Dispatch_))) * -999.9
annual_max_urban = np.ones_like(annual_average_urban) * -999.9
annual_q95_urban = np.ones_like(annual_average_urban) * -999.9
annual_q75_urban = np.ones_like(annual_average_urban) * -999.9

annual_average_rural = np.ones_like(annual_average_urban) * -999.9
annual_max_rural = np.ones_like(annual_average_urban) * -999.9
annual_q95_rural = np.ones_like(annual_average_urban) * -999.9
annual_q75_rural = np.ones_like(annual_average_urban) * -999.9

annual_average_livestock = np.ones_like(annual_average_urban) * -999.9
annual_max_livestock = np.ones_like(annual_average_urban) * -999.9
annual_q95_livestock = np.ones_like(annual_average_urban) * -999.9
annual_q75_livestock = np.ones_like(annual_average_urban) * -999.9

annual_average_agriculture = np.ones_like(annual_average_urban) * -999.9
annual_max_agriculture = np.ones_like(annual_average_urban) * -999.9
annual_q95_agriculture = np.ones_like(annual_average_urban) * -999.9
annual_q75_agriculture = np.ones_like(annual_average_urban) * -999.9

annual_average_envflow = np.ones_like(annual_average_urban) * -999.9
annual_max_envflow = np.ones_like(annual_average_urban) * -999.9
annual_q95_envflow = np.ones_like(annual_average_urban) * -999.9
annual_q75_envflow = np.ones_like(annual_average_urban) * -999.9

annual_average_total = np.ones_like(annual_average_urban) * -999.9
annual_max_total = np.ones_like(annual_average_urban) * -999.9
annual_q95_total = np.ones_like(annual_average_urban) * -999.9
annual_q75_total = np.ones_like(annual_average_urban) * -999.9

freq_annual_deficit_urban = np.ones_like(annual_average_urban) * -999.9
freq_annual_deficit_rural = np.ones_like(annual_average_urban) * -999.9
freq_annual_deficit_livestock = np.ones_like(annual_average_urban) * -999.9
freq_annual_deficit_agriculture = np.ones_like(annual_average_urban) * -999.9
freq_annual_deficit_envflow = np.ones_like(annual_average_urban) * -999.9


annual_average_total_basin = np.ones((len(DT_), len(DP_), len(real_), len(Dfw_), len(Dirr_),
                                        len(Dliv_), len(Dispatch_))) * -999.9
annual_max_total_basin = np.ones_like(annual_average_total_basin) * -999.9
annual_q95_total_basin = np.ones_like(annual_average_total_basin) * -999.9
annual_q75_total_basin = np.ones_like(annual_average_total_basin) * -999.9

annual_average_urban_basin = np.ones_like(annual_average_total_basin) * -999.9
annual_max_urban_basin = np.ones_like(annual_average_total_basin) * -999.9
annual_q95_urban_basin = np.ones_like(annual_average_total_basin) * -999.9
annual_q75_urban_basin = np.ones_like(annual_average_total_basin) * -999.9

annual_average_rural_basin = np.ones_like(annual_average_total_basin) * -999.9
annual_max_rural_basin = np.ones_like(annual_average_total_basin) * -999.9
annual_q95_rural_basin = np.ones_like(annual_average_total_basin) * -999.9
annual_q75_rural_basin = np.ones_like(annual_average_total_basin) * -999.9

annual_average_livestock_basin = np.ones_like(annual_average_total_basin) * -999.9
annual_max_livestock_basin = np.ones_like(annual_average_total_basin) * -999.9
annual_q95_livestock_basin = np.ones_like(annual_average_total_basin) * -999.9
annual_q75_livestock_basin = np.ones_like(annual_average_total_basin) * -999.9

annual_average_agriculture_basin = np.ones_like(annual_average_total_basin) * -999.9
annual_max_agriculture_basin = np.ones_like(annual_average_total_basin) * -999.9
annual_q95_agriculture_basin = np.ones_like(annual_average_total_basin) * -999.9
annual_q75_agriculture_basin = np.ones_like(annual_average_total_basin) * -999.9



for model in tqdm(models, desc='Processing models', total=len(models)):

    #model = 'OWF_{}_R{}_DT{}_DP{}_FW{}_Irr{}_Liv{}.csv'.format('FCFS', 1, 3, 90, '2040', '2040', '2040')

    if os.path.exists(path_results_CST+model) == False:
        continue
    else:
        owf = pd.read_csv(path_results_CST+model, index_col='Date', parse_dates=True)

    # Extract the parameters from the model name
    split = model.split('_')
    dispatch = split[1]
    real = split[2][1]
    dt = split[3][2]
    dp = split[4][2:]
    Dfw = split[5][2:]
    Dirr = split[6][3:]
    Dliv = split[7][3:-4]

    # Find the indices of the parameters in the list
    idx_real = np.where(real_ == int(real))[0][0]
    idx_dt = np.where(DT_ == int(dt))[0][0]
    idx_dp = np.where(DP_ == int(dp))[0][0]
    idx_Dfw = np.where(np.asarray(Dfw_) == Dfw)[0][0]
    idx_Dirr = np.where(np.asarray(Dirr_) == Dirr)[0][0]
    idx_Dliv = np.where(np.asarray(Dliv_) == Dliv)[0][0]
    idx_dispatch = np.where(np.asarray(Dispatch_) == dispatch)[0][0]

    
    basinwide = pd.DataFrame(0, columns=['urban', 'rural', 'livestock', 'agriculture', 'envflow', 'total'],
        index=owf.resample('YE').sum().index)
    
    for b, basin in enumerate(list_of_subbasins):
           
        # In the First Come First Served (FCFS) scenario, the dispatch order w/ each basin is the following:
        # - urban customers
        # - agricultural customers
        # - livestock customers
        # - rural customers
        if dispatch == 'FCFS':

            # Deficit urban : Urban customers are being served first
            deficit_urban = np.where(
                owf['Deliveries_{}_cmd'.format(basin)] - owf['Dfwu_{}_cmd'.format(basin)]<0,
                owf['Dfwu_{}_cmd'.format(basin)] - owf['Deliveries_{}_cmd'.format(basin)],
                0)
            
            # Leftover supply once the urban customers have been served
            leftover_after_urban = np.maximum(
                owf['Deliveries_{}_cmd'.format(basin)] - owf['Dfwu_{}_cmd'.format(basin)],
                0)
            
            # Deficit Agriculture : Farmers are being served second
            deficit_agg = np.where(
                leftover_after_urban - owf['Dirr_{}_cmd'.format(basin)]<0,
                owf['Dirr_{}_cmd'.format(basin)] - leftover_after_urban,
                0
            )

            # Leftover supply once the urban and farmer customers have been served
            leftover_after_farmers = np.maximum(
                leftover_after_urban - owf['Dirr_{}_cmd'.format(basin)],
                0
            )

            # Deficit Livestock : Livestock industries are being served third
            deficit_livestock = np.where(
                leftover_after_farmers - owf['Dliv_{}_cmd'.format(basin)]<0,
                owf['Dliv_{}_cmd'.format(basin)] - leftover_after_farmers,
                0
            )

            # Leftover supply once the livestock industries have been served
            leftover_after_livestock = np.maximum(
                leftover_after_farmers - owf['Dliv_{}_cmd'.format(basin)],
                0
            )

            # Deficit rural : Rural customers are being served last
            deficit_rural = np.where(
                leftover_after_livestock - owf['Dfwr_{}_cmd'.format(basin)]<0,
                owf['Dfwr_{}_cmd'.format(basin)] - leftover_after_livestock,
                0
            )

            # Deficit environmental flows
            deficit_env = np.where(
                owf['To_downstream_from_{}_cmd'.format(basin)] - owf['Denv_{}_cmd'.format(basin)]<0,
                owf['Denv_{}_cmd'.format(basin)] - owf['To_downstream_from_{}_cmd'.format(basin)],
                0
            )


        # In Policy Enforcement Scenario (PES), the dispatch order w/ each basin is the following:
        # - urban customers
        # - rural customers
        # - livestock customers
        # - agricultural customers
        elif dispatch == 'PE':
            
            
            # Deficit urban : Urban customers are being served first
            deficit_urban = np.where(
                owf['Deliveries_{}_cmd'.format(basin)] - owf['Dfwu_{}_cmd'.format(basin)]<0,
                owf['Dfwu_{}_cmd'.format(basin)] - owf['Deliveries_{}_cmd'.format(basin)],
                0)
            
            # Leftover supply once the urban customers have been served
            leftover_after_urban = np.maximum(
                owf['Deliveries_{}_cmd'.format(basin)] - owf['Dfwu_{}_cmd'.format(basin)],
                0)
            
            # Deficit rural : Rural customers are being served second after urban customers
            deficit_rural = np.where(
                leftover_after_urban - owf['Dfwr_{}_cmd'.format(basin)]<0,
                owf['Dfwr_{}_cmd'.format(basin)] - leftover_after_urban,
                0
            )

            # Leftover supply once the rural customers have been served
            leftover_after_rural = np.maximum(
                leftover_after_urban - owf['Dfwr_{}_cmd'.format(basin)],
                0)
            
            # Deficit Agriculture : Farmers are being served third
            deficit_agg = np.where(
                leftover_after_rural - owf['Dirr_{}_cmd'.format(basin)]<0,
                owf['Dirr_{}_cmd'.format(basin)] - leftover_after_rural,
                0
            )

            # Leftover supply once the urban and farmer customers have been served
            leftover_after_farmers = np.maximum(
                leftover_after_rural - owf['Dirr_{}_cmd'.format(basin)],
                0
            )
            
            # Deficit Livestock : Livestock industries are being last (fourth)
            deficit_livestock = np.where(
                leftover_after_farmers - owf['Dliv_{}_cmd'.format(basin)]<0,
                owf['Dliv_{}_cmd'.format(basin)] - leftover_after_farmers,
                0
            )

            # Leftover supply once the livestock industries have been served
            leftover_after_livestock = np.maximum(
                leftover_after_rural - owf['Dliv_{}_cmd'.format(basin)],
                0
            )
            
            
            # Deficit environmental flows
            deficit_env = np.where(
                owf['To_downstream_from_{}_cmd'.format(basin)] - owf['Denv_{}_cmd'.format(basin)]<0,
                owf['Denv_{}_cmd'.format(basin)] - owf['To_downstream_from_{}_cmd'.format(basin)],
                0
            )

        deficit = pd.DataFrame(columns=['urban', 'rural', 'livestock', 'agriculture', 'envflow'],
            index=owf.index)
        deficit['urban'] = deficit_urban * deficit.index.days_in_month
        deficit['rural'] = deficit_rural * deficit.index.days_in_month
        deficit['livestock'] = deficit_livestock * deficit.index.days_in_month
        deficit['agriculture'] = deficit_agg * deficit.index.days_in_month
        deficit['envflow'] = deficit_env * deficit.index.days_in_month
        # Here, total does not include the environmental flow deficit
        deficit['total'] = deficit['urban'] + deficit['rural'] + deficit['livestock'] + deficit['agriculture']
        
        deficit_annual = deficit.resample('YE').sum()

        
        # Average annual deficit statistics
        annual_average_urban[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['urban'].mean() / 10**6
        annual_max_urban[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['urban'].max() / 10**6
        annual_q95_urban[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['urban'].quantile(0.95) / 10**6
        annual_q75_urban[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['urban'].quantile(0.75) / 10**6

        annual_average_rural[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['rural'].mean() / 10**6
        annual_max_rural[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['rural'].max() / 10**6
        annual_q95_rural[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['rural'].quantile(0.95) / 10**6
        annual_q75_rural[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['rural'].quantile(0.75) / 10**6

        annual_average_livestock[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['livestock'].mean() / 10**6
        annual_max_livestock[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['livestock'].max() / 10**6
        annual_q95_livestock[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['livestock'].quantile(0.95) / 10**6
        annual_q75_livestock[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['livestock'].quantile(0.75) / 10**6

        annual_average_agriculture[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['agriculture'].mean() / 10**6
        annual_max_agriculture[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['agriculture'].max() / 10**6
        annual_q95_agriculture[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['agriculture'].quantile(0.95) / 10**6
        annual_q75_agriculture[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['agriculture'].quantile(0.75) / 10**6

        annual_average_envflow[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['envflow'].mean() / 10**6
        annual_max_envflow[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['envflow'].max() / 10**6
        annual_q95_envflow[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['envflow'].quantile(0.95) / 10**6
        annual_q75_envflow[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['envflow'].quantile(0.75) / 10**6

        annual_average_total[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['total'].mean() / 10**6
        annual_max_total[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['total'].max() / 10**6
        annual_q95_total[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['total'].quantile(0.95) / 10**6
        annual_q75_total[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['total'].quantile(0.75) / 10**6
        
        # Annual average and max deficit for the entire basin
        basinwide['urban'] += deficit['urban'].resample('YE').sum()
        basinwide['rural'] += deficit['rural'].resample('YE').sum()
        basinwide['livestock'] += deficit['livestock'].resample('YE').sum()
        basinwide['agriculture'] += deficit['agriculture'].resample('YE').sum()
        basinwide['total'] += deficit['total'].resample('YE').sum()

        # Frequency of annual deficit
        freq_annual_deficit_urban[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['urban'].gt(0.001).sum() / len(deficit_annual['urban']) * 100
        freq_annual_deficit_rural[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['rural'].gt(0.001).sum() / len(deficit_annual['rural']) * 100
        freq_annual_deficit_livestock[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['livestock'].gt(0.001).sum() / len(deficit_annual['livestock']) * 100
        freq_annual_deficit_agriculture[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['agriculture'].gt(0.001).sum() / len(deficit_annual['agriculture']) * 100
        freq_annual_deficit_envflow[b,idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
            deficit_annual['envflow'].gt(0.001).sum() / len(deficit_annual['envflow']) * 100
    

    

    # Store the basinwide results
    annual_average_total_basin[idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
        basinwide['total'].mean() / 10**6
    annual_max_total_basin[idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
        basinwide['total'].max() / 10**6
    annual_q95_total_basin[idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
        basinwide['total'].quantile(0.95) / 10**6
    annual_q75_total_basin[idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
        basinwide['total'].quantile(0.75) / 10**6
    
    annual_average_urban_basin[idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
        basinwide['urban'].mean() / 10**6
    annual_max_urban_basin[idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
        basinwide['urban'].max() / 10**6
    annual_q95_urban_basin[idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
        basinwide['urban'].quantile(0.95) / 10**6
    annual_q75_urban_basin[idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
        basinwide['urban'].quantile(0.75) / 10**6
    
    annual_average_rural_basin[idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
        basinwide['rural'].mean() / 10**6
    annual_max_rural_basin[idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
        basinwide['rural'].max() / 10**6
    annual_q95_rural_basin[idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
        basinwide['rural'].quantile(0.95) / 10**6
    annual_q75_rural_basin[idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
        basinwide['rural'].quantile(0.75) / 10**6
    
    
    annual_average_livestock_basin[idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
        basinwide['livestock'].mean() / 10**6
    annual_max_livestock_basin[idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
        basinwide['livestock'].max() / 10**6
    annual_q95_livestock_basin[idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
        basinwide['livestock'].quantile(0.95) / 10**6
    annual_q75_livestock_basin[idx_dt,idx_dp,idx_real,idx_Dfw,idx_Dirr,idx_Dliv,idx_dispatch] = \
        basinwide['livestock'].quantile(0.75) / 10**6


# Create a dataset using xarray

# Create the dimensions
dims = ['basin', 'dt', 'dp', 'real', 'Dfw', 'Dirr', 'Dliv', 'dispatch']
dims_orinoquia = ['dt', 'dp', 'real', 'Dfw', 'Dirr', 'Dliv', 'dispatch']
coords = [list_of_subbasins, DT_, DP_, real_, Dfw_, Dirr_, Dliv_, Dispatch_]


dataset_deficit = xr.Dataset(
    data_vars=dict(
        annual_average_urban=(dims, annual_average_urban),
        annual_max_urban=(dims, annual_max_urban),
        annual_q95_urban=(dims, annual_q95_urban),
        annual_q75_urban=(dims, annual_q75_urban),

        annual_average_rural=(dims, annual_average_rural),
        annual_max_rural=(dims, annual_max_rural),
        annual_q95_rural=(dims, annual_q95_rural),
        annual_q75_rural=(dims, annual_q75_rural),

        annual_average_livestock=(dims, annual_average_livestock),
        annual_max_livestock=(dims, annual_max_livestock),
        annual_q95_livestock=(dims, annual_q95_livestock),
        annual_q75_livestock=(dims, annual_q75_livestock),

        annual_average_agriculture=(dims, annual_average_agriculture),
        annual_max_agriculture=(dims, annual_max_agriculture),
        annual_q95_agriculture=(dims, annual_q95_agriculture),
        annual_q75_agriculture=(dims, annual_q75_agriculture),

        annual_average_envflow=(dims, annual_average_envflow),
        annual_max_envflow=(dims, annual_max_envflow),
        annual_q95_envflow=(dims, annual_q95_envflow),
        annual_q75_envflow=(dims, annual_q75_envflow),

        annual_average_total=(dims, annual_average_total),
        annual_max_total=(dims, annual_max_total),
        annual_q95_total=(dims, annual_q95_total),
        annual_q75_total=(dims, annual_q75_total),

        freq_annual_deficit_urban=(dims, freq_annual_deficit_urban),
        freq_annual_deficit_rural=(dims, freq_annual_deficit_rural),
        freq_annual_deficit_livestock=(dims, freq_annual_deficit_livestock),
        freq_annual_deficit_agriculture=(dims, freq_annual_deficit_agriculture),
        freq_annual_deficit_envflow=(dims, freq_annual_deficit_envflow),

        annual_average_total_basin=(dims_orinoquia, annual_average_total_basin),
        annual_max_total_basin=(dims_orinoquia, annual_max_total_basin),
        annual_q95_total_basin=(dims_orinoquia, annual_q95_total_basin),
        annual_q75_total_basin=(dims_orinoquia, annual_q75_total_basin),

        annual_average_urban_basin=(dims_orinoquia, annual_average_urban_basin),
        annual_max_urban_basin=(dims_orinoquia, annual_max_urban_basin),
        annual_q95_urban_basin=(dims_orinoquia, annual_q95_urban_basin),
        annual_q75_urban_basin=(dims_orinoquia, annual_q75_urban_basin),

        annual_average_rural_basin=(dims_orinoquia, annual_average_rural_basin),
        annual_max_rural_basin=(dims_orinoquia, annual_max_rural_basin),
        annual_q95_rural_basin=(dims_orinoquia, annual_q95_rural_basin),
        annual_q75_rural_basin=(dims_orinoquia, annual_q75_rural_basin),

        annual_average_livestock_basin=(dims_orinoquia, annual_average_livestock_basin),
        annual_max_livestock_basin=(dims_orinoquia, annual_max_livestock_basin),
        annual_q95_livestock_basin=(dims_orinoquia, annual_q95_livestock_basin),
        annual_q75_livestock_basin=(dims_orinoquia, annual_q75_livestock_basin),

        annual_average_agriculture_basin=(dims_orinoquia, annual_average_agriculture_basin),
        annual_max_agriculture_basin=(dims_orinoquia, annual_max_agriculture_basin),
        annual_q95_agriculture_basin=(dims_orinoquia, annual_q95_agriculture_basin),
        annual_q75_agriculture_basin=(dims_orinoquia, annual_q75_agriculture_basin),

    ),
    coords=dict(
        basin=list_of_subbasins,
        dt=DT_,
        dp=DP_,
        real=real_,
        Dfw=Dfw_,
        Dirr=Dirr_,
        Dliv=Dliv_,
        dispatch=Dispatch_
    )
)

dataset_deficit = dataset_deficit.where(dataset_deficit != -999.9, np.nan)
dataset_deficit.to_netcdf(path_results_CST+'OWF_CST_annual_deficit_Mm3.nc')

