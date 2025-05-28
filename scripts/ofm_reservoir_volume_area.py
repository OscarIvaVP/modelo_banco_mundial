import pandas as pd
import numpy as np
# IMPORT PYWR MODULE FUNCTIONS
from pywr.parameters import Parameter

class VolumeAreaCurve(Parameter):
    
    def __init__(self, model, folder, reservoir_name):
        super().__init__(model)
        

    def value(self, timestep, scenario_index):
        return 0
    

    @classmethod
    def load(cls, model, data):
        _url = data.pop("url")
        url = _url[0]
        name = _url[1]

        c = cls(model=model, folder=url, reservoir_name=name) 
        return c