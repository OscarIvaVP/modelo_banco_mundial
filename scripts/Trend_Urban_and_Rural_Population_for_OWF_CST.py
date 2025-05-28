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
proporcion_urbano = pd.read_excel('../data/Historical_Datos-de-Entrada//proporcion-urbano.xlsx')
proporcion_rural = pd.read_excel('../data/Historical_Datos-de-Entrada/proporcion.xlsx')
proyeccion_urbano = pd.read_excel('../data/Historical_Datos-de-Entrada/proyeccion-dane-urbano.xlsx')
proyeccion_rural = pd.read_excel('../data/Historical_Datos-de-Entrada/proyeccion-dane-rural.xlsx')

# Definimos una función para calcular la población por cuenca basado en las proporciones y la proyección poblacional de cada municipio.
def calcular_poblacion_por_cuenca(proporcion, proyeccion):
    # Unimos los DataFrames según la columna "Municipio"
    df_merged = pd.merge(proyeccion, proporcion, on="Municipio", how="right")

    # Llenamos los valores NaN con ceros
    df_merged.fillna(0, inplace=True)

    # Obtenemos las columnas que corresponden a los años y las cuencas
    columnas_anios = [col for col in df_merged.columns if isinstance(col, (int, float))]
    columnas_cuencas = [col for col in df_merged.columns if col not in columnas_anios + ["Municipio"]]

    # Calculamos la población por cuenca para cada año
    df_resultado = pd.DataFrame()
    for cuenca in columnas_cuencas:
        for anio in columnas_anios:
            poblacion_cuenca_anio = round((df_merged[anio] * df_merged[cuenca]).sum())
            df_resultado = df_resultado._append({"Cuenca": cuenca, "Año": anio, "Población": poblacion_cuenca_anio}, ignore_index=True)

    return df_resultado

# Calculamos la población por cuenca para las áreas urbana y rural
poblacion_cuenca_urbana = calcular_poblacion_por_cuenca(proporcion_urbano, proyeccion_urbano)
poblacion_cuenca_urbana["Area"] = "Urban"

poblacion_cuenca_rural = calcular_poblacion_por_cuenca(proporcion_rural, proyeccion_rural)
poblacion_cuenca_rural["Area"] = "Rural"

# Mostramos los primeros registros de cada resultado
poblacion_cuenca_urbana.head(), poblacion_cuenca_rural.head()

# Concatenamos los resultados de población urbana y rural en un solo DataFrame
poblacion_cuenca_total = pd.concat([poblacion_cuenca_urbana, poblacion_cuenca_rural], ignore_index=True)

# Reorganizamos las columnas para que estén en el orden solicitado
poblacion_cuenca_total = poblacion_cuenca_total[["Cuenca", "Area", "Año", "Población"]]

# Mostramos los primeros registros del DataFrame concatenado
poblacion_cuenca_total.head()


# Definimos una función para ajustar y predecir la población utilizando regresión lineal
def predecir_poblacion(df, anios_futuros):
    predicciones = []

    # Separamos el DataFrame por cuenca y área (urbana/rural)
    for cuenca in df["Cuenca"].unique():
        for area in df["Area"].unique():
            # Filtramos los datos correspondientes a la cuenca y el área
            df_filtrado = df[(df["Cuenca"] == cuenca) & (df["Area"] == area)]

            # Preparamos los datos para el modelo
            X = df_filtrado["Año"].values.reshape(-1, 1)
            y = df_filtrado["Población"].values

            # Creamos y entrenamos el modelo de regresión lineal
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
            #result_df = result_df._append({
            #    'Basin': lookuptable_basin[cuenca],
            #    'Crop/Livestock': cultivo,
            #    'Slope (km2/head)': np.round(slope,3),
            #    'Intercept (km2/head)': np.round(intercept,3),
            #    'R^2': r_squared,
            #    'Year-2022 (Est)': np.round(intercept + slope*2022,3),
            #    'Year-2022 (Obs)': y[-1]
            #}, ignore_index=True)




            # Realizamos las predicciones para los años futuros
            for anio in anios_futuros:
                poblacion_predicha = round(model.predict(np.array([[anio]]))[0])
                predicciones.append({"Basin": lookuptable_basin[cuenca], 
                                     "Community": area, 
                                     "Year": anio, 
                                     "Population": poblacion_predicha})

    return pd.DataFrame(predicciones)

# Definimos los años futuros para los que queremos realizar predicciones
anios_futuros = np.arange(2020, 2051)

# Realizamos las predicciones
predicciones = predecir_poblacion(poblacion_cuenca_total, anios_futuros)

# Mostramos las primeras predicciones
predicciones.head()

# Save the results to a CSV file
predicciones.to_csv(
    '../input/Freshwater_demand/CST/Projection_Urban_and_Rural_Population_for_OWF_CST.csv', 
    index=False)