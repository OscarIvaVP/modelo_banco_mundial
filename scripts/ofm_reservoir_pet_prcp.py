# IMPORT OTHER FUNCTIONS
import os
import pandas as pd
import numpy as np
# IMPORT PYWR MODULE FUNCTIONS
from pywr.parameters import Parameter


class Reservoir_Evap_Demand(Parameter):

    """ Placeholder python class the could be used to calculate the evaporation over the reservoirs
    
        This calculation is not implemented in the current version of the model because the knowledge
        of the volume-area curves for the reservoirs of the system is not available.
    """

    def __init__(self, model, path_weather, hrus):
    
        super().__init__(model)
        
        
    
    def value(self, timestep, scenario_index):
    
        return 0
                
    
    @classmethod
    def load(cls, model, data):
        
        path = data.pop("url")
        hrus = data['hrus']

        c = cls(model, path, hrus)
        return c




class Reservoir_Precip(Parameter):

    """ Placeholder python class the could be used to calculate the precipitation over the reservoirs
    
        This calculation is not implemented in the current version of the model because the knowledge
        of the volume-area curves for the reservoirs of the system is not available.
    """

    def __init__(self, model, path_weather, hrus):
    
        super().__init__(model)
        

    
    def value(self, timestep, scenario_index):
    
        return 0
                
    
    @classmethod
    def load(cls, model, data):
        
        path = data.pop("url")
        hrus = data['hrus']

        c = cls(model, path, hrus)
        return c