

import pandas as pd
import numpy as np
import datetime
from scipy import interpolate
from pywr.parameters import Parameter
from pywr.parameters import load_parameter


class Dam_Release(Parameter):

    """
    
        The parameter calculates the water release from the reservoir in the 
        system. Advanced knowledge of the operations of the reservoir are 
        required to emulate the reservoir operations. Since the required 
        information is not available, the parameter below simulate a water release
        so that the simulated storage is close to the inter-annual average 
        storage cycle.
        
        Monthly storage targets are obtained from observed storage.    
    """
        

    def __init__(self, model, reservoir, catchment, irr_upstream_deliveries):
        super().__init__(model)
        
        
        # Add the 'children' parameters (i.e., *_Dfwu, *_Dirr, *_Dliv, *_Dfwr).
        # This ensures that demand for the basin upstream the reservoirs are calculated prior 
        # to the release calculation.
        # It is assumed here that the users of the basin will be served prior water enters the reservoir.
        for self.irr_upstream_users in irr_upstream_deliveries:
            self.children.add(self.irr_upstream_users)
        
        self.catchment = catchment
        
        # Monthly storage target (Mm3)
        # First value is for January, last value is for December
        # The target values below are the average monthly values obtained from  
        # the local partners
        if reservoir == 'Bata':
            self.storage_target = (
                379.5, 263.4, 168.3, 153.7, 240.7, 384.2, 505.8, 554.4, 542.4,
                539.7, 533.4, 482)
                
        elif reservoir == 'Guavio':
            self.storage_target = (
                483.4, 359.4, 278.6, 305.3, 422.6, 556.3, 645.1, 673.0, 654.3, 
                640.1, 570.4, 514.8)
            
        # Fraction of the flow from the basin that is captured by the reservoir
        if reservoir == 'Bata':
            self.captured_fraction = 1.0
        elif reservoir == 'Guavio':
            self.captured_fraction = 0.945


    def value(self, timestep, scenario_index):
    
        # Current storage (m3)
        current_storage = self.model.nodes['{}_reservoir'.format(self.catchment)].volume[0]
        
        # Difference between target and current storage (m3)
        diff_storage = (self.storage_target[timestep.month-1]*10**6 - current_storage)
        
        # Inflow to the reservoir (m3)
        # Here, we assume that users are served prior the water reaches the reservoir
        inflow_to_res = max(
            self.model.parameters['flow_{}'.format(self.catchment)].get_value(scenario_index) \
            * self.captured_fraction \
            - self.model.parameters[f'{self.catchment}_Dfwr'].get_value(scenario_index) \
            - self.model.parameters[f'{self.catchment}_Dfwu'].get_value(scenario_index) \
            - self.model.parameters[f'{self.catchment}_Dirr'].get_value(scenario_index) \
            - self.model.parameters[f'{self.catchment}_Dliv'].get_value(scenario_index),
            0) * timestep.day
        
        # The dam is currently below its target. The release equal the 
        # inflow in surplus, given 'diff_storage'. If the inflow is not enough
        # to fill the storage up to its target, the release will equal 10% of the 
        # inflow.
        if diff_storage>=0:
        
            return np.round(max(inflow_to_res-diff_storage, 0.1*inflow_to_res)/timestep.day,1)
        
        # The dam is above target. The release equals 95% of the current inflow
        # plus 'diff_storage'
        else:
            return np.round((-diff_storage+0.95*inflow_to_res)/timestep.day,1)
            
         
    @classmethod
    def load(cls, model, data):
        
        reservoir = data['reservoir']
        catchment = data['catchment']
        irr_upstream_deliveries = [load_parameter(model, parameter_data)
                               for parameter_data in data.pop('irr_upstream_deliveries')]
        
        return cls(model, reservoir, catchment, irr_upstream_deliveries) 