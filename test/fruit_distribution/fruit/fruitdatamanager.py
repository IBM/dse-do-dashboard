# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from dse_do_utils import DataManager

class FruitDataManager(DataManager):
    def __init__(self, inputs=None, outputs=None):
        super().__init__(inputs, outputs)
        
    def prepare_input_data_frames(self):
        """Called from dm.prepare_data_frames()"""
        super().prepare_input_data_frames()
        
        if 'Demand' in self.inputs:
            self.demand = (self.inputs['Demand'].set_index(['product','customer'], verify_integrity=True).sort_index())
        if 'Inventory' in self.inputs:
            self.inventory = (self.inputs['Inventory'].set_index('product', verify_integrity=True))
        if 'ProductMargin' in self.inputs:
            self.product_margin = (self.inputs['ProductMargin'].set_index('product', verify_integrity=True))
        if 'Trucks' in self.inputs:
            self.trucks = (self.inputs['Trucks'].set_index('truck_model', verify_integrity=True))


    def prepare_output_data_frames(self):
        """Called from dm.prepare_data_frames()"""
        super().prepare_output_data_frames()  # For the kpis 
        
        if 'DemandOutput' in self.inputs:
            self.demand_output = (self.inputs['DemandOutput'].set_index(['product','customer'], verify_integrity=True))
            
        if 'TruckOutput' in self.inputs:
            self.trucks_output = (self.inputs['TruckOutput'].set_index('customer', 'truck_model', verify_integrity=True))