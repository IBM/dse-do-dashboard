from typing import Optional
import pandas as pd
import types

from supply_chain.scnfo.scnfodatamanager import ScnfoDataManager

class PharmaDataManager(ScnfoDataManager):
    def __init__(self, inputs=None, outputs=None):
        super().__init__(inputs, outputs)
        
    def prepare_input_data_frames(self):
        super().prepare_input_data_frames()
        
        if 'PlannedProductionActivity' in self.inputs:
            self.planned_production_activity = self.inputs['PlannedProductionActivity'].set_index(["planId","productName","timePeriodSeq","lineName","recipeId"], verify_integrity=True)
            
    def set_parameters(self):
        self.param = types.SimpleNamespace()

        self.params = self.prep_parameters()  # DataManager.prep_parameters() looks for an input table called 'Parameter' or 'Parameters' with columns `param` and `value` and indexes the data into a DataFrame. self.params is a DataFrame

        # Get parameter(s) from input
        self.param.enable_outage = ScnfoDataManager.get_parameter_value(self.params, param_name='enableOutage', param_type='bool', default_value=False)

        # Some hard-coded parameters (to be moved to parameter input table)
        self.param.planning_horizon_start_time_dt = ScnfoDataManager.get_parameter_value(self.params, 'horizon_start_time', param_type='str', default_value='2021-01-01 00:00:00')
        self.param.bucket_length_days = ScnfoDataManager.get_parameter_value(self.params, 'bucket_length_days', param_type='int', default_value=7)

        # Integer vs float dvars
        self.param.integer_dvars = ScnfoDataManager.get_parameter_value(self.params, param_name='integerDvars', param_type='bool', default_value=True)

        # enableCapacityConstraint
        self.param.enable_capacity_constraint = ScnfoDataManager.get_parameter_value(self.params, param_name='enableCapacityConstraint', param_type='bool', default_value=True)
        self.param.enable_inventory = ScnfoDataManager.get_parameter_value(self.params, param_name='enableInventory', param_type='bool', default_value=True)
    #     self.param.enable_inventory = False  # HACK!
        self.param.remove_zero_quantity_output_records = ScnfoDataManager.get_parameter_value(self.params, param_name='removeZeroQuantityOutputRecords', param_type='bool', default_value=False) # Keep false for debugging

        self.param.time_limit = ScnfoDataManager.get_parameter_value(self.params, 'solveTimeLimit', param_type='int', default_value=60)  # in seconds

        self.param.plannedProductionId = ScnfoDataManager.get_parameter_value(self.params, 'plannedProductionId', param_type='int', default_value=0)

        self.param.enable_dos = ScnfoDataManager.get_parameter_value(self.params, 'enableDOS', param_type='bool', default_value=False)
        self.param.dos = ScnfoDataManager.get_parameter_value(self.params, 'DOS', param_type='int', default_value=10)

        # Add batch parameter
        self.param.batch = ScnfoDataManager.get_parameter_value(self.params, 'batch', param_type="bool", default_value=False)
        self.param.M = ScnfoDataManager.get_parameter_value(self.params, 'M', param_type="int", default_value=999999)
        
        try:
            self.param.objective = ScnfoDataManager.get_parameter_value(self.params, 'objective', param_type="int", default_value=2)
        except:
            self.param.objective = 2
        
    def prep_time_periods(self):
        self.active_timeperiods = self.timeperiods.drop(0)
        
    def prep_active_demand(self):
        self.active_demand = (pd.merge(self.demand.reset_index(), self.active_timeperiods.reset_index(), on=['timePeriodSeq'], how = 'inner')
                     .set_index(self.demand_index_columns, verify_integrity = True)
                    )
        # Round demand in case of integer dvars
        if self.param.integer_dvars:
            self.active_demand.quantity = self.active_demand.quantity.round()
            
    def prep_line_locations(self):
        self.line_locations = (self.lines.reset_index()
                 .merge(self.plants.reset_index(), on = 'plantName')
                 .merge(self.locations.reset_index(), on = 'locationName')
                 .set_index('lineName', verify_integrity = True)
        )
        
    def prep_active_recipe_properties(self):
        df = self.recipe_properties
        df = df.drop(df[df.capacity == 0].index)

        # Explode properties
        recipe_properties_index_columns = ['lineName','productName','recipeId','timePeriodSeq']
        '''
        if "timePeriodSeqPattern" in df.columns:
            df = (explode_time_period_pattern(df.reset_index(), self.active_timeperiods, 'timePeriodSeqPattern')
                 .set_index(recipe_properties_index_columns, verify_integrity=True) # just for verification!
            )
        else:
        '''
        df = df.reset_index().set_index(recipe_properties_index_columns, verify_integrity=True)

        self.active_recipe_properties = df
        
    def prep_production_activities(self):
        self.production_activities = (
            self.active_recipe_properties.reset_index()
            .merge(self.line_locations[['supplierName','locationName', 'plantName']].reset_index())
            .set_index(self.production_activities_index_columns, verify_integrity = True)
        )
        
    def prep_plant_inventories(self):
        plant_products = (self.active_recipe_properties[['capacity']]
                          .join(self.line_locations[['locationName', 'plantName']])
                          .groupby(['locationName', 'productName']).sum()  # Groupby on locationName
                          .query("capacity > 0")  # For exceptions where the plant cannot make the product at all 
                          .join(self.bom_items[[]])
         )


        # Find all output products:
        plant_output_products = plant_products.groupby(['locationName', 'productName']).sum()[[]]


        # Find all input products:
        plant_input_products = (plant_products.groupby(['locationName', 'componentName']).sum()[[]]
                                .rename_axis(index={'componentName':'productName'})
                               )


        # Concat the input and output products in single df:
        plant_products = (pd.concat([plant_input_products, plant_output_products])
                                .groupby(['locationName', 'productName']).sum()  # To merge any input and output products from same plant
                            )


        #  Cross product with all time-periods
        plant_inventory_index_columns = ['productName', 'locationName', 'timePeriodSeq']
        self.plant_inventories = (ScnfoDataManager.df_crossjoin_ai(plant_products, self.active_timeperiods)
                                  .reset_index()
                                  .set_index(plant_inventory_index_columns, verify_integrity=True)
                                 )

    def prep_warehouse_inventories(self):
        warehouse_products = (self.warehouse_properties[[]]
                          .join(self.warehouses[['locationName']])
                          .groupby(['productName', 'locationName']).sum()
         ) 

        warehouse_inventory_index_columns = ['productName', 'locationName', 'timePeriodSeq']
        self.warehouse_inventories = (ScnfoDataManager.df_crossjoin_ai(warehouse_products[[]], self.active_timeperiods))
                  
    def prep_demand_inventories_work_around(self):
        demand_inventory_index_columns = ['productName', 'locationName', 'timePeriodSeq']
        df = pd.merge(self.active_demand.groupby(['locationName', 'productName']).sum().reset_index()[['locationName', 'productName']]
                      .assign(key=1),self.active_timeperiods.reset_index().assign(key=1), on="key")
        df = pd.merge(df, self.active_demand, 
                      on=demand_inventory_index_columns, how="left")[["locationName","productName","timePeriodSeq","quantity","actualQuantity"]].set_index(demand_inventory_index_columns).fillna(0)
        self.demand_inventories = df
                                      
    def prep_transportation(self):
        # Explode properties - df.expode() is not available in DO. Skip for now
        transportation_index_columns = ['originLocationName','destinationLocationName','shippingMode','productName','timePeriodSeq']

        df = (self.explode_time_period_pattern(self.shipping_lane_properties.reset_index(), 'timePeriodSeqPattern')
             .set_index(transportation_index_columns, verify_integrity=True)
             )
    #     df = self.shipping_lane_properties
        # Get transit time (or other properties (TODO))
        df = df.reset_index().merge(self.shipping_lanes['transitTime'].reset_index(), on=['originLocationName','destinationLocationName','shippingMode']).set_index(transportation_index_columns, verify_integrity=True)
        self.transportation_activities = df
                                      
    def get_demand_location_dos(self, dos:int):
        """Compute the quantity of product at the end of a time-period that represents the 
        Days-Of-Supply computed using the actual demand in the following time-periods.
        The quantity can be used in a days-of-supply inventory constraint or objective.
        For the last time-periods, assume demand remains constant with the value of the last time-period.

        Args:
            dos (int): Days-Of-Supply. Number of days.

        Note: use dm.demand_inventories. Is has already expanded to all time-periods.
        """
    #     num_tps = 24  # Number of time-periods

        num_days_tp = 30  # Number of days per time-period. To keep it simple, use 30 per month. HARD-CODED for now. TODO: put in parameter, or add as column in TimePeriods
        df = (self.demand_inventories[['quantity']]
              .sort_index()  # sort index so the shift will work right
             )

        num_tps = len(df.index.unique(level='timePeriodSeq'))
    #     df['numDays'] = num_days_tp
        df['demandPerDay'] = df.quantity / num_days_tp  #df.numDays
        df['nextDemandPerDay'] = df.demandPerDay  # Note we are shifting the nextDemandPerDay, so initialize once
        df['dosQuantity'] = 0  # We are incrementing the dosQuantity, so initialize

        remaining_dos = dos  # Remaining DOS in each iteration, initialize with all DOS
        shift = 0  # Only for debuging

        # Iterate over the next time-periods until it covers all requested dos days
        # Sum the DOS quantity
        # Assume demand is constant throughout the time-period
        while remaining_dos > 0:
            shift = shift + 1
            next_dos = min(remaining_dos, num_days_tp)
    #         print(f"Shift = {shift}, remaining_dos = {remaining_dos}, next_dos={next_dos}")
            df['nextDemandPerDay'] = df.groupby(['locationName','productName'])['nextDemandPerDay'].shift(-1)  #, fill_value=0)  
            df.loc[pd.IndexSlice[:,:,num_tps],'nextDemandPerDay'] = df.loc[pd.IndexSlice[:,:,num_tps],'demandPerDay']  # Fill gap from the shift with last demand
            df['dosQuantity'] = df.dosQuantity + df.nextDemandPerDay * next_dos
            remaining_dos = remaining_dos - next_dos
    #         display(df.query("locationName=='NAMIBIA'").head(24))
        df = df.drop(columns=['demandPerDay', 'nextDemandPerDay'])
        return df
                                      
    def prep_data_transformations(self):
        self.prep_time_periods()
        self.prep_active_demand()
        self.prep_line_locations()
        self.prep_active_recipe_properties()
        self.prep_production_activities()
        self.prep_plant_inventories()
        self.prep_warehouse_inventories()
        self.prep_demand_inventories_work_around()
        self.prep_transportation()