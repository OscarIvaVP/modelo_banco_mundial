
"""
    This python script was initially developed by Oscar Ivan Vargas Pineda (https://github.com/OscarIvaVP)
    as a Jupyter Notebook.

    The notebook was initially used to create time series of future evolution of crops, livestock
    and population (urban and rural) across the Orinoquia watershed.

    The notebook (available here: https://github.com/OscarIvaVP/Creacion-escenarios-futuros/blob/main/Escenario_tendencial_sin_limites.ipynb)
    was converted to a python script. It was also modified so that it returns trends rather than
    time series.

    Author: Baptiste (bfrancois@umass.edu)

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.formula.api import ols
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

lookuptable_basin = {
    'Casanare': 'Casanare',
    'Caño Cumaral': 'Cumaral',
    'Caño Guanápalo y otros directos al Meta': 'Guanapalo',
    'Directos Bajo Meta entre ríos Casanare y Orinoco': 'Dir_btw_Ca_Or',
    'Directos Rio Metica entre ríos Guayuriba y Yucao': 'Dir_btw_Gb_Yu',
    'Directos al Meta entre ríos Cusiana y Cravo Sur': 'Dir_btw_Cu_CS',
    'Directos al Río Meta entre ríos Cusiana y Carare': 'Dir_btw_Cu_Ca',
    'Directos al Río Meta entre ríos Humea y Upia (mi)': 'Dir_btw_Hu_Up',
    'Directos al Río Meta entre ríos Pauto y Carare': 'Dir_btw_P_Ca',
    'Lago de Tota': 'Lago de Tota',
    'Rio Metica (Guamal - Humadea)': 'Metica',
    'Río Cravo Sur': 'Cravo Sur',
    'Río Cusiana': 'Cusiana',
    'Río Garagoa': 'Garagoa',
    'Río Guacavía': 'Guacavia',
    'Río Guatiquía': 'Guatiquia',
    'Río Guavio': 'Guavio',
    'Río Guayuriba': 'Guayuriba',
    'Río Humea': 'Humea',
    'Río Lengupá': 'Lengupa',
    'Río Manacacias': 'Manacacias',
    'Río Melúa': 'Melua',
    'Río Negro': 'Negro',
    'Río Pauto': 'Pauto',
    'Río Túa y otros directos al Meta': 'Tua',
    'Río Upía': 'Upia',
    'Río Yucao': 'Yucao'
}

# Read the raw data
historico_palma = pd.read_excel('../data/Historical_Datos-de-Entrada/historico-palma.xlsx')
historico_arroz = pd.read_excel('../data/Historical_Datos-de-Entrada//historico-arroz.xlsx')
historico_cacao = pd.read_excel('../data/Historical_Datos-de-Entrada//historico-cacao.xlsx')
historico_porcino = pd.read_excel('../data/Historical_Datos-de-Entrada/historico-porcino.xlsx')
historico_ave = pd.read_excel('../data/Historical_Datos-de-Entrada/historico-ave.xlsx')
historica_bovino_animal = pd.read_excel('../data/Historical_Datos-de-Entrada/historico-bovino-animal.xlsx')
proporcion = pd.read_excel('../data/Historical_Datos-de-Entrada/proporcion.xlsx')

need_processed_data = True
if need_processed_data:
    # Calcular hectáreas de cada cultivo en cada cuenca
    
    # Note from Baptiste Francois (01-2025); despite the column name being 'hectareas' - it is actually
    # 'animal count' for 'Ave' and 'Porcino'. 

    # Below, the calculation of the crop areas and/or number of animals from the municipality level
    # to the basin level assumes a uniform distribution in space of the crop area/animal. 

    # For instance, should be municipality spreads over two basins, its crop area and animal count will
    # be split between the two basins with respect to the spatial coverage. As a result, the number 
    # of birds and pigs estimated from this calculation can lead to a float rather than an integer.
    def calcular_hectareas(historico, cultivo):
        df = historico.melt(id_vars=['Municipio'], var_name='Año', value_name='Hectáreas')
        df['Cultivo'] = cultivo
        df = df.merge(proporcion, left_on='Municipio', right_on='Municipio')
        df['Año'] = df['Año'].astype(int)
        for cuenca in proporcion.columns[1:]:
            df[cuenca] = df['Hectáreas'] * df[cuenca]
        df.drop(['Hectáreas', 'Municipio'], axis=1, inplace=True)
        df = df.melt(id_vars=['Año', 'Cultivo'], var_name='Cuenca', value_name='Hectáreas')
        return df

    resultado_palma = calcular_hectareas(historico_palma, 'OilPalm')
    resultado_arroz = calcular_hectareas(historico_arroz, 'Rice')
    resultado_cacao = calcular_hectareas(historico_cacao, 'Cacao') # We do not need Cacao
    resultado_porcino = calcular_hectareas(historico_porcino, 'Pigs')
    resultado_ave = calcular_hectareas(historico_ave, 'Birds')
    resultado_bovino = calcular_hectareas(historica_bovino_animal, 'Cattle')

    # Concatenar datos
    resultado_agrupado = pd.concat(
        [resultado_palma, resultado_arroz, resultado_cacao, resultado_porcino,resultado_ave, resultado_bovino],
          ignore_index=True)
    resultado_agrupado = resultado_agrupado.groupby(['Año', 'Cuenca', 'Cultivo']).sum().reset_index()
    # Guardar resultados
    resultado_agrupado.to_excel('../data/Historical_Datos-de-Entrada/historico-cuenca.xlsx', index = False)
    resultado_agrupado.head()


df = pd.read_excel('../data/Historical_Datos-de-Entrada/historico-cuenca.xlsx')

# Initialize an empty DataFrame to store the results
result_df = pd.DataFrame(columns=['Basin', 
                                  'Crop/Livestock',
                                  'Slope (km2/head)', 
                                  'Intercept (km2/head)', 
                                  'R2', 
                                  'Year-2022 (Est)', 
                                  'Year-2022 (Obs)'])

# Group the data by 'Cuenca' and 'Cultivo'
grouped = df.groupby(['Cuenca', 'Cultivo'])

# Loop through each group to fit a simple linear regression model
for (cuenca, cultivo), group_data in grouped:
    X = group_data['Año'].values.reshape(-1, 1)
    

    if cultivo == 'Birds' or cultivo == 'Pigs' or cultivo == 'Cattle':
        y = group_data['Hectáreas'].values
    elif cultivo == 'OilPalm' or cultivo == 'Rice' or cultivo == 'Cacao':
        y = group_data['Hectáreas'].values / 100 # Convert from hectares to km^2


    # Remove the null values at the beginning of the time series (which indicate missing values)
    # The number of values used to establish the linear regression may vary depending on the crop
    # of livestock type; and from one municipality to another.
    # The idea was to use as much data as possible, so the number of datapoint used to fit the model
    # is not necessarily the same for all the groups.
    no_null_y = np.where(y>0)[0]
    
    if len(no_null_y) == 0:
        slope = 0
        intercept = 0

    else:
        X = np.asarray([X[i] for i in range(no_null_y[0],len(X))])
        y = y[no_null_y[0]:]

        
        # Fit the model
        model = LinearRegression()
        model.fit(X, y)

        # Get the slope and intercept of the line
        slope = model.coef_[0]
        intercept = model.intercept_

        # Get the R^2 value
        r_squared = model.score(X, y)

        # Create the equation of the line
        # equation = f'y = {slope:.4f} * x + {intercept:.4f}'

    # Append the results to the DataFrame
    result_df = result_df._append({
        'Basin': lookuptable_basin[cuenca],
        'Crop/Livestock': cultivo,
        'Slope (km2/head)': np.round(slope,3),
        'Intercept (km2/head)': np.round(intercept,3),
        'R2': r_squared,
        'Year-2022 (Est)': np.round(intercept + slope*2022,3),
        'Year-2022 (Obs)': y[-1]
    }, ignore_index=True)

result_df.to_csv('../input/demand_trend_scenarios/Trend_CropType_and_Livestock_OWF.csv', index = False)
result_df.head()