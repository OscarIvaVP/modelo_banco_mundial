
# CONDA ENV: cmip6_env

import os
from itertools import product
import cdsapi
import pandas as pd
import geopandas as gpd
from ClimProjTools import download_CMIP6

# Read the shapefile of the Oriniquia River basin and gets it bounding box
shp = gpd.read_file('../data/shapefiles/cuencas_completas.shp')

download_CMIP6.from_ClimateDataStore(
    variables = (('tas', 'near_surface_air_temperature'), ('prcp', 'precipitation')),
    domain = shp,
    period = (1980,2085),
    pad_lat = 1,
    pad_lon = 1,
    future_experiments = ['ssp5_8_5'],
    output_dir = '../data/CMIP6/CMIP6_zip/',
    print_requests = True
)

