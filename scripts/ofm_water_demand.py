
import pandas as pd
import numpy as np
import datetime
from scipy import interpolate
from pywr.parameters import Parameter
from pywr.parameters import load_parameter



class Freshwater_Demand(Parameter):


    """ This parameter/ python class calculates the freshwater demand.
        
        Note: The freshwater demand is assumed constant over time.
            It is calculated as the product of the:
            - population
            - water use per capita
            - CI (consumption index)
            - 1/loss term (i.e., the fraction of the water that is lost before reaching the consumer)

            The simulated demand is a piecewise linear function of the population because the 
            water use per capita increases at specific population thresholds.    
    """
    
    def __init__(self, model, catchment, freshwater_demand_file, community,
        freshwater_parameters_file, projection_demand_year):
        super().__init__(model)
        
        # Read the freshwater demand input file
        freshwater_demand_input = pd.read_csv(freshwater_demand_file)
        
        # Read the population for the urban community of the considered basin and scenario year
        population = freshwater_demand_input[(
            freshwater_demand_input['Community'] == community) & (
            freshwater_demand_input['Basin'] == catchment) & (
            freshwater_demand_input['Year'] == projection_demand_year)
            ]['Population'].values[0]
        
        # Read the freshwater parameter file that contains the loss and CI values
        freshwater_parameters = pd.read_csv(freshwater_parameters_file, index_col='Basin')
        CI = freshwater_parameters.loc[catchment]['{}_CI'.format(community)]
        loss_term = freshwater_parameters.loc[catchment]['{}_loss_%'.format(community)]
        
        # Water use per capita (L/day/hab): Resolution 2320 population threshold are from the 
        # RAS 2000 (Technical Regulation of the Drinking Water and Basic Sanitation Sector 
        # – Title D: Collection and management Systems of Domestic Wastewater and Rainwater )
        # https://www.minvivienda.gov.co/sites/default/files/documentos/titulo_d.pdf
        # https://comunidad.udistrital.edu.co/javalerof/files/2015/09/titulo_d_version_prueba.pdf
        if community == 'Urban':
            # Low complexity urban areas
            if population <= 2000:
                use_per_capita = 100 / 1000 # divide by 1,000 converts (L/day/hab) to (m3/day/hab)
            # Medium complexity urban areas
            elif 2000 < population <= 12500:
                use_per_capita = 125 / 1000 # divide by 1,000 converts (L/day/hab) to (m3/day/hab)
            # Medium-high complexity urban areas
            elif 12500 < population <= 60000:
                use_per_capita = 135 / 1000 # divide by 1,000 converts (L/day/hab) to (m3/day/hab)
            # High complexity urban areas
            elif population > 60000:
                use_per_capita = 150 / 1000 # divide by 1,000 converts (L/day/hab) to (m3/day/hab)
            
        
        elif community == 'Rural':
            # Rural areas are always low complexity level
            use_per_capita = 100 / 1000 # divide by 1,000 converts (L/day/hab) to (m3/day/hab)
        
        self.demand = np.round(population * use_per_capita * CI / (1-loss_term),1) # m3/day


    def value(self, timestep, scenario_index):
    
        # Demand is constant over time
        return self.demand
    
    
    @classmethod
    def load(cls, model, data):
        catchment = data['catchment']
        urban_demand_file = data['urban_demand_file']
        community = data['community']
        freshwater_parameters_file = data['freshwater_parameters']
        projection_demand_year = data['projection_demand_year']
        
        return cls(model, catchment, urban_demand_file, community, freshwater_parameters_file, 
                   projection_demand_year) 



class Livestock_Demand(Parameter):

    """ This parameter / python class calculates the livestock demand.

        Note: the Livestock demand is assumed constant over time.
        It is calculated for three animal types (birds, pigs and cattle) as the product of the: 
        - the population of each animal type
        - the water use per head and per year

    The population of the animal types is calculated using a regression of the population of the
    animal type as a function of the year. The parameters of the regression are read from the
    "livestock_demand_scenario" input file.

    The water use per head is hard coded in this class and is available via the 'water_use' dictionary.
    
    """
    
    def __init__(self, model, catchment, livestock_demand_scenario, livestock_parameters, projection_demand_year):
        super().__init__(model)
                
        # Read the livestock demand input file
        # This file contains the parameters of the regression of the population of the animal types
        livestock_demand_scenario = pd.read_csv(livestock_demand_scenario)
        
        # Read the livestock parameter file
        # This file contains the water use per head for each animal type and a loss term.
        # Parameters are defined for each catchment.
        livestock_parameters = pd.read_csv(livestock_parameters, index_col='Basin')
        water_use = {
            'Cattle': livestock_parameters.loc[catchment]['WaterUse_cattle_m3/year/head'],
            'Pigs': livestock_parameters.loc[catchment]['WaterUse_pigs_m3/year/head'],
            'Birds': livestock_parameters.loc[catchment]['WaterUse_birds_m3/year/head']
        }

        loss = {
            'Cattle': livestock_parameters.loc[catchment]['Loss_cattle'],
            'Pigs': livestock_parameters.loc[catchment]['Loss_pigs'],
            'Birds': livestock_parameters.loc[catchment]['Loss_birds']
        }
                                         
        # Calculate the livestock demand for the considered catchment
        livestock_demand_per_year = 0
        for animals in ['Birds', 'Pigs', 'Cattle']:
            
            # Read the parameter of the regression for calculating the animal population
            growth, intercept = [livestock_demand_scenario[(
                livestock_demand_scenario['Crop/Livestock'] == animals) & (
                livestock_demand_scenario['Basin'] == catchment)
                ][x].values[0] for x in ['Slope (km2/head)', 'Intercept (km2/head)']]

            # Calculate the population of the animal type using the regression parameters
            # Some regions have negative population trends. In this case, the population is set to 0
            # if the calculated population is negative.
            population = max(intercept + growth * projection_demand_year, 0)

            # Calculate the livestock demand per year for the considered animal type, and a it to 
            # total annual demand
            livestock_demand_per_year += population * water_use[animals] / (1-loss[animals])

        # Divide by 365 to get the demand per day
        self.livestock_demand_per_day =  np.round(max(livestock_demand_per_year / 365, 0),1)

    def value(self, timestep, scenario_index):
    
        # Demand can't be negative (which can happened if the trend is negative)
        return self.livestock_demand_per_day

    
    @classmethod
    def load(cls, model, data):
        catchment = data['catchment']
        livestock_demand_scenario = data['livestock_demand_scenario']
        livestock_parameters = data['livestock_parameters']
        projection_demand_year = data['projection_demand_year']
        
        return cls(model, catchment, livestock_demand_scenario, livestock_parameters, projection_demand_year)
        
        
        
class Irrigation_Demand(Parameter):

    """ This parameter / python class calculates the irrigation demand.

        Two types of plantations are considered: "crops" and "trees".

        The irrigation demand for each type is calculated based on a time series of irrigation 
        requirement (mm) obtained from either Aquacrop (for crops) or from a simple KxPET approach 
        for trees.

        The crops to be included in the calculation are listed in the "crops" attribute of the 
        irrigation demand parameter (i.e., parameter end with the suffix "_Dirr").

        The plantation dates of the crops are listed in the "crop_schedules" attribute of the
        irrigation demand parameter. As such, irrigation demand from the same crop (e.g., rice) 
        planted a different times of the year can be considered. The names listed in the crop schedules 
        are the name of the column in the .csv files that contain the time series of irrigation demand
        for each crop schedule. The path to the .csv file is provided in the irrigation demand
        parameter via the "crop_demand_file" key of the "url" attribute.

        The trees to be included in the calculation are listed in the "trees" attribute of the
        irrigation demand parameter. The plantation dates of the trees are not considered in the
        calculation because trees are assumed to be planted once and for all. The names listed in 
        the "trees" attributes are the name of the columns in the .csv file that contain the time
        series of irrigation demand (mm) for each tree type. The path to the .csv file is provided
        in the .csv file whose path is provided in the irrigation demand parameter via the 
        "trees_demand_file" key of the "url" attribute.

        The attribute "projection_demand_year" set the scenario 'year' for which the area of the 
        plantations is projected. Parameters of the regression of the area of the plantations is 
        read from the "irrigation_demand_scenario".

        The "url" attribute also provides the paths to two .csv files:
         - the "irrigation_parameters" that provides for each crop schedule the fraction of the farmland
         that is irrigated and the associated efficiency.
         - the "irrigation_demand_scenario" that contains the information to project the farmland
         area for each crop and tree type.
         
    
    """
    
    def __init__(self, model, catchment, crops, crop_schedules, trees, projection_demand_year, 
                 crop_demand_ts, trees_demand_ts, irrigation_parameters_, irrigation_demand_scenario_):
        super().__init__(model)
            
        # Initialize the dataframe that will host the time series of irrigation demand for each 
        # crop/crop schedule and tree plantation.
        irrigation_demand = pd.DataFrame()

        # Conversion factor from square kilometer (km2) to meter (m)
        conversion_km2_to_m2 = 10**6
        # Conversion factor from millimeter (mm) to meter (m)
        conversion_mm_to_m = 0.001

        
        # Read the irrigation parameters (fraction irrigated and irrigation  efficiency)
        irrigation_parameters = pd.read_csv(irrigation_parameters_, index_col='Basin')

        # Read the irrigation demand scenario
        irrigation_demand_scenario = pd.read_csv(irrigation_demand_scenario_)


        # Loop over the plantation crop types (i.e., no tree)
        for c, (crop, crop_schedule) in enumerate(zip(crops, crop_schedules)):
            
            # Plantation date
            plantation_date = crop_schedule.split('_')[0]

            # Fraction irrigated
            fraction_irrigated = irrigation_parameters.loc[catchment][
                f'{crop}_{plantation_date}_irrigated']

            # Skip the crop if it is not irrigated
            if fraction_irrigated == 0:
                continue
            
            # Irrigation efficiency
            # The (baseline) irrigation efficiency set from the 'irrigation_parameters' is 36% for
            # all crops. The actual efficiency is calculated as the product between:
            # - conveyance efficiency,
            # - application efficiency.
            # It is assumed that both of those efficiencies reflect values that would be obtained
            # from low level irrigation technology (e.g., surface irrigation) and long earthen canals
            # made with sandy soil.
            # Reference efficiency are taken from the FAO Irrigation and Drainage Paper No. 66 (Annex 1)
            # available at https://www.fao.org/4/T7202E/t7202e08.htm 
            irrigation_efficiency = irrigation_parameters.loc[catchment][
                f'{crop}_{plantation_date}_IrrEff_%']
            
            # irrigation_demand_scenario = "../input/demand_trend_scenarios/Trend_CropType_and_Livestock_OWF.csv"

            # Read the parameter of the regression for calculating the animal population
            growth, intercept = [irrigation_demand_scenario[(
                irrigation_demand_scenario['Crop/Livestock'] == crop) & (
                irrigation_demand_scenario['Basin'] == catchment)
                ][x].values[0] for x in ['Slope (km2/head)', 'Intercept (km2/head)']]

            # Calculate the population of the animal type using the regression parameters
            crop_area = intercept + growth * projection_demand_year

            # Calculate the irrigation demand from the crop and crop_schedule
            irrigation_demand['{}_{}'.format(crop,crop_schedule)] = \
                pd.read_csv(crop_demand_ts, index_col='Date', 
                    usecols = ['Date', '{}_{}_{}'.format(catchment,crop,crop_schedule)],
                    parse_dates=True) \
                * crop_area \
                * conversion_km2_to_m2 \
                * conversion_mm_to_m \
                / irrigation_efficiency \
                * fraction_irrigated
                    
        # Loop over the plantation of trees (i.e., no cereals)
        for tree in trees:
            
            # Fraction irrigated
            fraction_irrigated = irrigation_parameters.loc[catchment][
                f'{tree}_irrigated']

            # Skip the crop if it is not irrigated
            if fraction_irrigated == 0:
                continue
            
            # Irrigation efficiency
            # The (baseline) irrigation efficiency set from the 'irrigation_parameters' is 36% for
            # all crops. The actual efficiency is calculated as the product between:
            # - conveyance efficiency,
            # - application efficiency.
            # It is assumed that both of those efficiencies reflect values that would be obtained
            # from low level irrigation technology (e.g., surface irrigation) and long earthen canals
            # made with sandy soil.
            # Reference efficiency are taken from the FAO Irrigation and Drainage Paper No. 66 (Annex 1)
            # available at https://www.fao.org/4/T7202E/t7202e08.htm 
            irrigation_efficiency = irrigation_parameters.loc[catchment][
                f'{tree}_IrrEff_%']
            
            # Read the parameter of the regression for calculating the animal population
            growth, intercept = [irrigation_demand_scenario[(
                irrigation_demand_scenario['Crop/Livestock'] == tree) & (
                irrigation_demand_scenario['Basin'] == catchment)
                ][x].values[0] for x in ['Slope (km2/head)', 'Intercept (km2/head)']]

            # Calculate the population of the animal type using the regression parameters
            crop_area = intercept + growth * projection_demand_year

            # Calculate the irrigation demand from the crop and crop_schedule
            irrigation_demand['{}'.format(tree)] = \
                pd.read_csv(trees_demand_ts, index_col='Date', 
                    usecols = ['Date', '{}'.format(catchment)], parse_dates=True) \
                * crop_area \
                * conversion_km2_to_m2 \
                / irrigation_efficiency \
                * fraction_irrigated
            
     
        # Create the time series of irrigation demand at the catchment level
        irrigation_demand.clip(lower=0, inplace=True) # Set negative values to 0
        total_irr_demand = irrigation_demand.sum(axis=1)
        
        # Convert the time series to monthly time series
        self.total_irr_demand_monthly = total_irr_demand.resample('MS').mean()
        
        self.total_irr_demand_monthly.where(self.total_irr_demand_monthly.values>0,
            0, inplace=True)
        self.total_irr_demand_monthly = self.total_irr_demand_monthly.round(1)
        
    def value(self, timestep, scenario_index):
    
        self.irr_demand = \
            self.total_irr_demand_monthly.loc['{}-{}'.format(timestep.year,timestep.month)].values[0]
        
        return self.irr_demand
    
    
    @classmethod
    def load(cls, model, data):
        catchment = data['catchment']
        crops = data['crops']
        crop_schedules = data['crop_schedules']
        trees = data['trees']
        projection_demand_year = data['projection_demand_year']
        crop_demand_ts = data['url']['crop_demand_file']
        trees_demand_ts = data['url']['trees_demand_file']
        irrigation_parameters_ = data['url']['irrigation_parameters']
        irrigation_demand_scenario_ = data['url']['irrigation_demand_scenario']
        
        return cls(model, catchment, crops, crop_schedules, trees, projection_demand_year,
            crop_demand_ts, trees_demand_ts, irrigation_parameters_, irrigation_demand_scenario_)