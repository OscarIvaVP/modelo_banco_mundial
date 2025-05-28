
from ClimProjTools.process_CMIP6 import (
    extract_basin_average_from_CMIP6_data, calculate_delta_change, random_sampling_from_copula,
    plot_delta_change)



we_need_to_extract_time_series = False
we_need_to_create_delta_change = False
we_need_random_sampling_from_CMIP6 = False

if we_need_to_extract_time_series:
    # Extract basin average for each variable and experiment
    extract_basin_average_from_CMIP6_data(
        variables=['tas', 'prcp'], experiments=['historical', 'ssp5_8_5'], 
        basin_shapefile='../data/shapefiles/cuencas_completas.shp',
        epsg=2317, # EPSG 2317 is a good projection to calculate areas for the Orinoco River basin (Colombia)
        gcm_directory='../data/CMIP6/CMIP6_zip/', 
        output_directory='../data/CMIP6/processed/')
    
if we_need_to_create_delta_change:

    calculate_delta_change(
        path_historical_file='../data/CMIP6/processed/',
        path_future_file='../data/CMIP6/processed/',
        variables=['tas', 'prcp'],
        future_experiment='ssp5_8_5',
        reference_period=(1985, 2014),
        future_periods=((2026, 2055), (2056, 2085)),
        output_directory='../data/CMIP6/processed/'
    )
    
if we_need_random_sampling_from_CMIP6:

    random_sampling_from_copula(
        future_periods=((2026, 2055), (2056, 2085)),
        experiment='ssp5_8_5',
        path_deltaT = f'../data/CMIP6/processed/delta_tas.xlsx',
        path_deltaP = f'../data/CMIP6/processed/delta_prcp.xlsx',
        number_random_samples = 1000,
        random_seed = 42, # "The answer to the Ultimate Question of Life, the Universe, and Everything"
        output_directory = '../data/CMIP6/processed/',
        plot = True,
        xlim = (-42.5, 20),
        ylim = (0, 8),
    )


plot_delta_change(path_deltaT='../data/CMIP6/processed/delta_tas.xlsx',
                  path_deltaP='../data/CMIP6/processed/delta_prcp.xlsx',
                  future_exp='ssp5_8_5',
                  colors=['#fee8c8', '#e34a33'],
                  xlim=(-42.5, 20),
                  ylim=(0, 8),
                  figure_title='CMIP6 models (SSP5-8.5) across Orinoquia Basin',
                  path_figure='../data/CMIP6/figures/CMIP6_delta_change_w_sides.png'
                  )
    
plot_delta_change(path_deltaT='../data/CMIP6/processed/delta_tas.xlsx',
                  path_deltaP='../data/CMIP6/processed/delta_prcp.xlsx',
                  future_exp='ssp5_8_5',
                  colors=['#fee8c8', '#e34a33'],
                  xlim=(-42.5, 20),
                  ylim=(0, 8),
                  figure_title='CMIP6 models (SSP5-8.5) across Orinoquia Basin',
                  path_figure='../data/CMIP6/figures/CMIP6_delta_change.png',
                  with_gcm_distribution_on_the_side=False,
                  )
