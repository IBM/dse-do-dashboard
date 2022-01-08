from typing import Optional

from dse_do_utils.datamanager import DataManager
import pandas as pd

class ScnfoDataManager(DataManager):
    def __init__(self, inputs=None, outputs=None):
        super().__init__(inputs, outputs)
        self.demand_index_columns = ['customerName', 'locationName', 'productName', 'timePeriodSeq']
        self.production_activities_index_columns = ['productName', 'timePeriodSeq', 'lineName',
                                                    'recipeId']  # We'll be using these later on
        self.recipe_properties_index_columns = self.production_activities_index_columns

    #TODO: move generic parts to DataManager
    def prepare_data_frames(self):
        if (self.inputs is not None) and (len(self.inputs) > 0):
            self.prepare_input_data_frames()
        if (self.outputs is not None) and (len(self.outputs) > 0):
            self.prepare_output_data_frames()

    def prepare_input_data_frames(self):
        if 'TimePeriod' in self.inputs:
            self.timeperiods = (self.inputs['TimePeriod'].set_index('timePeriodSeq', verify_integrity=True))

        self.demand_index_columns = ['customerName', 'locationName', 'productName', 'timePeriodSeq']
        if 'Demand' in self.inputs:
            self.demand = (self.inputs['Demand'].astype({'productName': str}).set_index(self.demand_index_columns, verify_integrity=True))

        #         if 'ActualDemand' in self.inputs:
        #             self.actual_demand = (self.inputs['ActualDemand'].set_index(self.demand_index_columns, verify_integrity=True))

        if 'Product' in self.inputs:
            self.products = self.inputs['Product'].astype({'productName': str}).set_index('productName', verify_integrity=True)

        if 'BomItem' in self.inputs:
            self.bom_items = self.inputs['BomItem'].astype({'productName': str}).set_index(['componentName', 'productName', 'recipeId'], verify_integrity = True)
        else:
            self.bom_items = pd.DataFrame(columns=['componentName', 'productName', 'recipeId', 'quantity']).astype({'productName': str}).set_index(['componentName', 'productName', 'recipeId'])

        # Recipe properties natural keys:
        self.production_activities_index_columns = ['productName', 'timePeriodSeq', 'lineName',
                                                    'recipeId']  # We'll be using these later on
        self.recipe_properties_index_columns = self.production_activities_index_columns
        if 'RecipeProperties' in self.inputs:
            self.recipe_properties = (self.inputs['RecipeProperties'].astype({'productName': str})
                                      .set_index(self.recipe_properties_index_columns, verify_integrity=True)
                                      )
            if 'recipePropertiesId' in self.recipe_properties.columns:
                self.recipe_properties = self.recipe_properties.drop(['recipePropertiesId'], axis=1)  # If we use the natural keys, we don't need the recipePropertiesId

        if 'Line' in self.inputs:
            self.lines = self.inputs['Line'].set_index('lineName', verify_integrity=True)

        if 'Plant' in self.inputs:
            self.plants = self.inputs['Plant'].set_index('plantName', verify_integrity=True)

        if 'Location' in self.inputs:
            self.locations = self.inputs['Location'].set_index('locationName', verify_integrity=True)

        if 'ShippingLane' in self.inputs:
            self.shipping_lanes = self.inputs['ShippingLane'].set_index(['originLocationName', 'destinationLocationName', 'shippingMode'], verify_integrity=True)

        if 'ShippingLaneProperties' in self.inputs:
            self.shipping_lane_properties = self.inputs['ShippingLaneProperties'].set_index(['originLocationName', 'destinationLocationName', 'shippingMode', 'productName', 'timePeriodSeq'], verify_integrity=True)

        if 'Warehouse' in self.inputs:
            self.warehouses = self.inputs['Warehouse'].set_index('warehouseName', verify_integrity=True)

        if 'WarehouseProperties' in self.inputs:
            self.warehouse_properties = self.inputs['WarehouseProperties'].astype({'productName': str}).set_index(['warehouseName','productName','timePeriodSeqPattern'], verify_integrity=True)

        if 'ControlScenario' in self.inputs:
            self.control_scenarios = self.inputs['ControlScenario'].set_index('controlScenarioId', verify_integrity=True)

        if 'StochasticScenario' in self.inputs:
            self.stochastic_scenarios = self.inputs['StochasticScenario'].set_index('stochasticScenarioId', verify_integrity=True)
            
        if 'WIP' in self.inputs:
            self.WIP = self.inputs['WIP'].astype({'productName': str}).set_index(['productName','locationName','timePeriodSeq'], verify_integrity=True)

    def prepare_output_data_frames(self):
        #Beware: self.production_activities_index_columns defined in prepare_input_data_frames
        if 'ProductionActivity' in self.outputs:
            self.production_activities = (self.outputs['ProductionActivity'].astype({'productName': str})
                                          .set_index(self.production_activities_index_columns, verify_integrity = True))

        if 'PlantInventory' in self.outputs:
            self.plant_inventories = (self.outputs['PlantInventory'].astype({'productName': str})
                                      .set_index(['productName','locationName','timePeriodSeq'], verify_integrity = True)
                                      )
        if 'WarehouseInventory' in self.outputs:
            self.warehouse_inventories = (self.outputs['WarehouseInventory'].astype({'productName': str})
                                       .set_index(['productName','locationName','timePeriodSeq'], verify_integrity = True)
                                       )
        if 'DemandInventory' in self.outputs:
            self.demand_inventories = (self.outputs['DemandInventory'].astype({'productName': str})
                                       .set_index(['productName','locationName','timePeriodSeq'], verify_integrity = True)
                                       )
        if 'TransportationActivity' in self.outputs:
            self.transportation_activities = (self.outputs['TransportationActivity']
                                              .set_index(['originLocationName','destinationLocationName','shippingMode','productName','timePeriodSeq'], verify_integrity = True))

        if 'LineUtilization' in self.outputs:
            self.line_utilization = (self.outputs['LineUtilization']
                                     .set_index(['lineName','timePeriodSeq'], verify_integrity = True)
                                     )
        #         if 'SupplyMap' in self.outputs:
        #             self.supply_map = (self.outputs['SupplyMap']
        #                            .set_index(['locationName'], verify_integrity = True)
        #         )
        #         if 'DemandMap' in self.outputs:
        #             self.demand_map = (self.outputs['DemandMap']
        #                            .set_index(['locationName'], verify_integrity = True)
        #         )
        if 'DemandSupplyMap' in self.outputs:
            self.demand_supply_map = (self.outputs['DemandSupplyMap']
                                      .set_index(['locationName'], verify_integrity = True)
                                      )
            
        if 'BusinessKPIs' in self.outputs:
            self.business_kpis = (self.outputs['BusinessKPIs']
                                     .set_index(['kpi'], verify_integrity = True)
                                     )
    
        if 'kpis' in self.outputs and self.outputs['kpis'].shape[0] > 0:
            """Note: for some reason an imported scenario uses 'Name' and 'Value' as column names!"""
            df = self.outputs['kpis']
            df.columns= df.columns.str.upper()
#             if 'Name' in df.columns:
#                 df = df.rename(columns={'Name':'NAME'})
#             if 'Value' in df.columns:
#                 df = df.rename(columns={'Value':'VALUE'})
            self.kpis = (df
                         .set_index(['NAME'], verify_integrity = True)
                         )
    
    def select_time_periods(self, pattern, time_periods):
        if isinstance(pattern, int):
            df = time_periods.query("timePeriodSeq == @pattern")
        elif pattern == '*':
            df = time_periods.query("timePeriodSeq >= 1")  # Exclude the period 0
        elif isinstance(pattern, str) and 't' in pattern:
            p2 = pattern.replace('t', 'timePeriodSeq', 1)
            df = time_periods.query(p2)
        else:
            df = pd.DataFrame({'timePeriodSeq': []}).set_index('timePeriodSeq')

        #     tps = df.timePeriodSeq.to_list()
        tps = df.index.get_level_values('timePeriodSeq')
        return tps
            
    def explode_time_period_pattern(self, df, pattern_column:str='timePeriodSeqPattern'):
        """Explode rows based on pattern for timePeriodSeq
        Assumes column named by pattern_column with the pattern
        Replaces/add `timePeriodSeq`. Drops pattern_column.
        """
        df['timePeriodSeq'] = df[pattern_column].apply(lambda x: self.select_time_periods(x, self.active_timeperiods))
        df = df.explode('timePeriodSeq')
        df = df.drop(columns=[pattern_column])
        return df
