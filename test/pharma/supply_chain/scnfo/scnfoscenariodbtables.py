#######################################################
# Table specific SQL
#######################################################
from typing import List, Dict
from sqlalchemy import Table, Column, String, Integer, Float, ForeignKey, ForeignKeyConstraint
from collections import OrderedDict

# from supply_chain.folium_supply_chain import SCMapManager, MappingSCDM
# from supply_chain.plotly_supply_chain import PlotlyManager, SupplyChainPlotlyManager, WaterPlotlyManager  #, PlotlySupplyChainDataManager
from dse_do_utils.scenariodbmanager import ScenarioDbTable, ScenarioDbManager
# from supply_chain.supply_chain import DEWaterDataManager  #ScenarioDbTable, ScenarioDbManager

import pandas as pd
from dse_do_dashboard.utils.scenariodbmanager_update import ScenarioDbManagerUpdate

class ScenarioTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'scenario'):
        columns_metadata = [
            Column('scenario_name', String(256), primary_key=True),
        ]
        super().__init__(db_table_name, columns_metadata)


class LocationTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'location', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            #             Column('scenario_name', String(256), ForeignKey("scenario.scenario_name"), primary_key=True),
            Column('locationName', String(256), primary_key=True),
            Column('city', String(256), primary_key=False),
            Column('state', String(2), primary_key=False),
            Column('zip', String(64), primary_key=False),
            Column('country', String(256), primary_key=False),
            Column('latitude', Float(), primary_key=False),
            Column('longitude', Float(), primary_key=False),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata)


class PlantTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'plant', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('plantName', String(256), primary_key=True),
            Column('supplierName', String(256), primary_key=False),
            #             Column('locationName', String(256), ForeignKey("location.locationName"), primary_key=False, nullable=False),
            Column('locationName', String(256), primary_key=False, nullable=False),
        ]
        constraints_metadata = [
            ForeignKeyConstraint(['locationName'], ['location.locationName'])
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata, constraints_metadata)


class LineTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'line', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('lineName', String(256), primary_key=True),
            #             Column('plantName', String(256), ForeignKey("plant.plantName"), primary_key=False),
            Column('plantName', String(256), primary_key=False),
            Column('stageName', String(256), primary_key=False, nullable=False),
        ]
        constraints_metadata = [
            ForeignKeyConstraint(['plantName'], ['plant.plantName'])
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata, constraints_metadata)


class TimePeriodTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'time_period', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('timePeriodSeq', Integer(), primary_key=True),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata)


class ProductTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'product', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('productName', String(256), primary_key=True),
            Column('inventoryVolume', Float(), primary_key=False),
            Column('transportationVolume', Float(), primary_key=False),
            Column('transportationWeight', Float(), primary_key=False),
#             Column('turnOverRatio', Float(), primary_key=False),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata)
    
#     @staticmethod
#     def extend_metadata(self, default_columns_metadata, columns_metadata: List[Column] = None, extend_metadata:bool=True):
#         """For use in subsubclass of a ScenarioDbTable. If applicable, replaces or extends the default_columns_metadata of a class.
#         Options:
#         1. Keep default: column_metadata = None
#         2. Extend: column_metadata is not None, extend_metadata is True
#         3. Replace: column_metadata is not None, extend_metadata is False
#         """
#         if extend_metadata:
#             md = default_columns_metadata.extend(columns_metadata)
#         elif columns_metadata is not None:
#             md = columns_metadata
#         else
#             md = default_columns_metadata


class RecipeTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'recipe', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('recipeId', Integer(), primary_key=True),
            #             Column('productName', String(256), ForeignKey("product.productName") , primary_key=True),  # If also PK: we do not need unique recipeId
            Column('productName', String(256), primary_key=True),  # If also PK: we do not need unique recipeId
        ]
        constraints_metadata = [
            ForeignKeyConstraint(['productName'], ['product.productName'])
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata, constraints_metadata)


class RecipePropertiesTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'recipe_properties', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
#             Column('recipePropertiesId', String(256), primary_key=True),
            # Do we use the recipePropertiesId, or the 'natural' keys (productName, recipeId, lineName and timePeriodSeq)?
            Column('recipeId', Integer(), primary_key=True),
            Column('productName', String(256), primary_key=True),
            #             Column('recipeId', Integer(), ForeignKey("recipe.recipeId"), primary_key=False),
            #             Column('productName', String(256), ForeignKey("product.productName") , primary_key=False),
            #             Column('productName', String(256), ForeignKey("recipe.productName") , primary_key=False),
            #             Column('lineName', String(256), ForeignKey("line.lineName") , primary_key=False),
            #             Column('timePeriodSeq', Integer(), ForeignKey("time_period.timePeriodSeq"), primary_key=False),
            Column('lineName', String(256), primary_key=True),
            Column('timePeriodSeq', Integer(), primary_key=True),
            Column('timePeriodSeqPattern', String(256), primary_key=False),
            Column('capacity', Float(), primary_key=False),
            Column('yield', Float(), primary_key=False),
            Column('cost', Float(), primary_key=False),
            Column('cycleTime', Float(), primary_key=False),
        ]
        constraints_metadata = [
            ForeignKeyConstraint(['lineName'], ['line.lineName']),
            ForeignKeyConstraint(['timePeriodSeq'], ['time_period.timePeriodSeq']),
            ForeignKeyConstraint(['productName', 'recipeId'], ['recipe.productName', 'recipe.recipeId']),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata, constraints_metadata)


class BomItemTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'bom_item', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            #             Column('componentName',String(256), ForeignKey("product.productName"), primary_key=True),
            #             Column('productName', String(256), ForeignKey("product.productName") , primary_key=True),
            #             Column('recipeId', Integer(), ForeignKey("recipe.recipeId"), primary_key=True),
            Column('componentName', String(256), primary_key=True),
            Column('productName', String(256), primary_key=True),
            Column('recipeId', Integer(), primary_key=True),
            Column('quantity', Float(), primary_key=False),
        ]
        constraints_metadata = [
            ForeignKeyConstraint(['componentName'], ['product.productName']),
            #             ForeignKeyConstraint(['productName'],['product.productName']),
            ForeignKeyConstraint(['productName', 'recipeId'], ['recipe.productName', 'recipe.recipeId']),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata, constraints_metadata)


class DemandTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'demand', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('customerName', String(256), primary_key=True),
            #             Column('locationName', String(256), ForeignKey("location.locationName"), primary_key=True),
            #             Column('productName', String(256), ForeignKey("product.productName") , primary_key=True),
            #             Column('timePeriodSeq', Integer(), ForeignKey("time_period.timePeriodSeq"), primary_key=True),
            Column('locationName', String(256), primary_key=True),
            Column('productName', String(256), primary_key=True),
            Column('timePeriodSeq', Integer(), primary_key=True),
            Column('quantity', Float(), primary_key=False),
        ]
        constraints_metadata = [
            ForeignKeyConstraint(['locationName'], ['location.locationName']),
            ForeignKeyConstraint(['productName'], ['product.productName']),
            ForeignKeyConstraint(['timePeriodSeq'], ['time_period.timePeriodSeq']),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata, constraints_metadata)
        
        
class WIPTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'wip', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('productName', String(256), primary_key=True),
            Column('locationName', String(256), primary_key=True),
            Column('timePeriodSeq', Integer(), primary_key=True),
            Column('wipQuantity', Float()),
        ]
        constraints_metadata = [
            ForeignKeyConstraint(['productName'], ['product.productName']),
            ForeignKeyConstraint(['locationName'], ['location.locationName']),
            ForeignKeyConstraint(['timePeriodSeq'], ['time_period.timePeriodSeq']),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata, constraints_metadata)
        
        
class WarehouseTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'warehouse', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('warehouseName', String(256), primary_key=True),
            Column('locationName', String(256), primary_key=False, nullable=False),
        ]
        constraints_metadata = [
            ForeignKeyConstraint(['locationName'], ['location.locationName'])
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata, constraints_metadata)

        
class WarehousePropertiesTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'warehouse_properties', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('warehouseName', String(256), primary_key=True),
            Column('productName', String(256), primary_key=True),
            Column('timePeriodSeq', Integer(), primary_key=True),
            Column('timePeriodSeqPattern', String(256), primary_key=False),
        ]
        constraints_metadata = [
            ForeignKeyConstraint(['warehouseName'], ['warehouse.warehouseName']),
            ForeignKeyConstraint(['timePeriodSeq'], ['time_period.timePeriodSeq']),
            ForeignKeyConstraint(['productName'], ['product.productName']),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata, constraints_metadata)
        

class ShippingModeTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'shipping_mode', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('shippingModeName', String(256), primary_key=True),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata)

        
class ShippingLaneTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'shipping_lane', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('originLocationName', String(256), primary_key=True),
            Column('destinationLocationName', String(256), primary_key=True),
            Column('shippingMode', String(256), primary_key=True),  # TODO: switch to shippingModeName
#             Column('shippingModeName', String(256), primary_key=True),
        ]
        constraints_metadata = [
            ForeignKeyConstraint(['originLocationName'], ['location.locationName']),
            ForeignKeyConstraint(['destinationLocationName'], ['location.locationName']),
#             ForeignKeyConstraint(['shippingMode'], ['shipping_mode.shippingModeName']),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata, constraints_metadata)
        
        
class ShippingLanePropertiesTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'shipping_lane_properties', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('originLocationName', String(256), primary_key=True),
            Column('destinationLocationName', String(256), primary_key=True),
            Column('shippingMode', String(256), primary_key=True),  # TODO: switch to shippingModeName
#             Column('shippingModeName', String(256), primary_key=True),
            Column('productName', String(256), primary_key=True),
            Column('timePeriodSeq', Integer(), primary_key=True),
            Column('timePeriodSeqPattern', String(256), primary_key=False),
        ]
        constraints_metadata = [
             ForeignKeyConstraint(['originLocationName', 'destinationLocationName', 'shippingMode'], 
                                  ['shipping_lane.originLocationName', 'shipping_lane.destinationLocationName', 'shipping_lane.shippingMode']),
#             ForeignKeyConstraint(['originLocationName'], ['location.locationName']),
#             ForeignKeyConstraint(['destinationLocationName'], ['location.locationName']),
#             ForeignKeyConstraint(['shippingMode'], ['shipping_mode.shippingModeName']),
            ForeignKeyConstraint(['productName'], ['product.productName']),
            ForeignKeyConstraint(['timePeriodSeq'], ['time_period.timePeriodSeq']),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata, constraints_metadata)
        
class PlannedProductionActivityTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'planned_production_activity', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('planId', String(256), primary_key=True),
            Column('productName', String(256), primary_key=True),
            #             Column('timePeriodSeq', Integer(), ForeignKey("time_period.timePeriodSeq"), primary_key=True),
            #             Column('lineName', String(256), ForeignKey("line.lineName"), primary_key=True),
            Column('timePeriodSeq', Integer(), primary_key=True),
            Column('lineName', String(256), primary_key=True),
            Column('recipeId', Integer(), primary_key=True),
            Column('quantity', Float()),
        ]
        constraints_metadata = [
            ForeignKeyConstraint(['timePeriodSeq'], ['time_period.timePeriodSeq']),
            ForeignKeyConstraint(['lineName'], ['line.lineName']),
            ForeignKeyConstraint(['productName', 'recipeId'], ['recipe.productName', 'recipe.recipeId'])
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata, constraints_metadata)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Output Tables
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class ProductionActivityTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'production_activity', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('productName', String(256), primary_key=True),
            #             Column('timePeriodSeq', Integer(), ForeignKey("time_period.timePeriodSeq"), primary_key=True),
            #             Column('lineName', String(256), ForeignKey("line.lineName"), primary_key=True),
            Column('timePeriodSeq', Integer(), primary_key=True),
            Column('lineName', String(256), primary_key=True),
            Column('recipeId', Integer(), primary_key=True),
            Column('capacity', Float()),
            Column('yield', Float()),
            Column('cost', Float()),
            Column('cycleTime', Integer()),
            Column('supplierName', String(256)),
            #             Column('locationName', String(256), ForeignKey("location.locationName"), primary_key=False, nullable=False),
            #             Column('plantName', String(256), ForeignKey("plant.plantName"), primary_key=False),
            Column('locationName', String(256), primary_key=False, nullable=False),
            Column('plantName', String(256), primary_key=False),
            Column('xProdSol', Float()),
            Column('xProdSlackSol', Float()),
            Column('line_capacity_utilization', Float()),
            Column('production_cost', Float()),
            #             ForeignKeyConstraint(['productName','recipeId'],['recipe.productName','recipe.recipeId'])
        ]
        constraints_metadata = [
            ForeignKeyConstraint(['timePeriodSeq'], ['time_period.timePeriodSeq']),
            ForeignKeyConstraint(['lineName'], ['line.lineName']),
            ForeignKeyConstraint(['locationName'], ['location.locationName']),
            ForeignKeyConstraint(['plantName'], ['plant.plantName']),
            ForeignKeyConstraint(['productName', 'recipeId'], ['recipe.productName', 'recipe.recipeId'])
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata, constraints_metadata)


class PlantInventoryTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'plant_inventory', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            #             Column('productName', String(256), ForeignKey("product.productName") , primary_key=True),
            #             Column('plantName', String(256), ForeignKey("plant.plantName"), primary_key=True),
            #             Column('timePeriodSeq', Integer(), ForeignKey("time_period.timePeriodSeq"), primary_key=True),
            Column('productName', String(256), primary_key=True),
#             Column('plantName', String(256), primary_key=True),
            Column('locationName', String(256), primary_key=True),
            Column('timePeriodSeq', Integer(), primary_key=True),
            Column('xInvSol', Float()),
        ]
        constraints_metadata = [
            ForeignKeyConstraint(['productName'], ['product.productName']),
            ForeignKeyConstraint(['locationName'], ['location.locationName']),
#             ForeignKeyConstraint(['plantName'], ['plant.plantName']),
            ForeignKeyConstraint(['timePeriodSeq'], ['time_period.timePeriodSeq']),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata, constraints_metadata)

class WarehouseInventoryTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'warehouse_inventory', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('productName', String(256), primary_key=True),
            Column('locationName', String(256), primary_key=True),
            Column('timePeriodSeq', Integer(), primary_key=True),
#             Column('quantity', Float(), primary_key=False),
            Column('xInvSol', Float(), primary_key=False),
        ]
        constraints_metadata = [
            ForeignKeyConstraint(['locationName'], ['location.locationName']),
            ForeignKeyConstraint(['productName'], ['product.productName']),
            ForeignKeyConstraint(['timePeriodSeq'], ['time_period.timePeriodSeq']),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata, constraints_metadata)

        
class DemandInventoryTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'demand_inventory', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
#             Column('customerName', String(256), primary_key=True),
            #             Column('locationName', String(256), ForeignKey("location.locationName"), primary_key=True),
            #             Column('productName', String(256), ForeignKey("product.productName") , primary_key=True),
            #             Column('timePeriodSeq', Integer(), ForeignKey("time_period.timePeriodSeq"), primary_key=True),
            Column('productName', String(256), primary_key=True),
            Column('locationName', String(256), primary_key=True),
            Column('timePeriodSeq', Integer(), primary_key=True),
            Column('quantity', Float(), primary_key=False),
            Column('xInvSol', Float(), primary_key=False),
            Column('xBacklogSol', Float(), primary_key=False),
            Column('xBacklogResupplySol', Float(), primary_key=False),
            Column('xFulfilledDemandSol', Float(), primary_key=False),
            Column('xUnfulfilledDemandSol', Float(), primary_key=False),
#             Column('xDOSSlackSol', Float(), primary_key=False),
        ]
        constraints_metadata = [
            ForeignKeyConstraint(['locationName'], ['location.locationName']),
            ForeignKeyConstraint(['productName'], ['product.productName']),
            ForeignKeyConstraint(['timePeriodSeq'], ['time_period.timePeriodSeq']),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata, constraints_metadata)


class TransportationActivityTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'transportation_activity', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('originLocationName', String(256), primary_key=True),
            Column('destinationLocationName', String(256), primary_key=True),
            Column('shippingMode', String(256), primary_key=True),
            Column('productName', String(256), primary_key=True),
            Column('timePeriodSeq', Integer(), primary_key=True),
            Column('transitTime', Float(), primary_key=False),
            Column('xTransportationSol', Float(), primary_key=False),
            # Other columns are derived: Cognos should be able to figure these out
        ]
        constraints_metadata = [
            ForeignKeyConstraint(['originLocationName'], ['location.locationName']),
            ForeignKeyConstraint(['destinationLocationName'], ['location.locationName']),
            ForeignKeyConstraint(['shippingMode'], ['shipping_mode.shippingModeName']),
            ForeignKeyConstraint(['productName'], ['product.productName']),
            ForeignKeyConstraint(['timePeriodSeq'], ['time_period.timePeriodSeq']),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata, constraints_metadata)


class LineUtilizationTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'line_utilization', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            #             Column('lineName', String(256), ForeignKey("line.lineName"), primary_key=True),
            #             Column('timePeriodSeq', Integer(), ForeignKey("time_period.timePeriodSeq"), primary_key=True),
            #             Column('plantName', String(256), ForeignKey("plant.plantName"), primary_key=True),
            Column('lineName', String(256), primary_key=True),
            Column('timePeriodSeq', Integer(), primary_key=True),
            Column('plantName', String(256), primary_key=True),
            Column('utilization', Float(), primary_key=False),
        ]
        constraints_metadata = [
            ForeignKeyConstraint(['lineName'], ['line.lineName']),
            ForeignKeyConstraint(['timePeriodSeq'], ['time_period.timePeriodSeq']),
            ForeignKeyConstraint(['plantName'], ['plant.plantName']),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata, constraints_metadata)


class ParameterTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'parameters', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('param', String(256), primary_key=True),
            Column('value', String(256), primary_key=False),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata)


class DemandMapTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'demand_map', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('locationName', String(256), primary_key=True),
            Column('quantity', Float(), primary_key=False),
            Column('cost', Float(), primary_key=False),
            Column('type', String(256), primary_key=False),
#             Column('locationDescr', String(256), primary_key=False),
#             Column('locationType', String(256), primary_key=False),
            Column('city', String(256), primary_key=False),
            Column('state', String(256), primary_key=False),
            Column('zip', String(256), primary_key=False),
            Column('country', String(256), primary_key=False),
            Column('latitude', Float(), primary_key=False),
            Column('longitude', Float(), primary_key=False),
        ]
        constraints_metadata = [
            ForeignKeyConstraint(['locationName'], ['location.locationName']),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata, constraints_metadata)


class SupplyMapTable(ScenarioDbTable):
    """Same as DemandMapTable"""

    def __init__(self, db_table_name: str = 'supply_map', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('locationName', String(256), primary_key=True),
            Column('quantity', Float(), primary_key=False),
            Column('cost', Float(), primary_key=False),
            Column('type', String(256), primary_key=False),
#             Column('locationDescr', String(256), primary_key=False),
#             Column('locationType', String(256), primary_key=False),
            Column('city', String(256), primary_key=False),
            Column('state', String(256), primary_key=False),
            Column('zip', String(256), primary_key=False),
            Column('country', String(256), primary_key=False),
            Column('latitude', Float(), primary_key=False),
            Column('longitude', Float(), primary_key=False),
        ]
        constraints_metadata = [
            ForeignKeyConstraint(['locationName'], ['location.locationName']),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata, constraints_metadata)


class KpiTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'kpis'):
        columns_metadata = [
            Column('NAME', String(256), primary_key=True),
            Column('VALUE', Float(), primary_key=False),
        ]
        super().__init__(db_table_name, columns_metadata)
        
class BusinessKpiTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'business_kpi', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('kpi', String(256), primary_key=True),
            Column('value', Float(), primary_key=False),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata)
        
class ScnfoScenarioDbManager(ScenarioDbManagerUpdate):
    def __init__(self, input_db_tables: Dict[str, ScenarioDbTable]=None, output_db_tables: Dict[str, ScenarioDbTable]=None, 
                 credentials=None, schema: str = None, echo=False, multi_scenario: bool = True):
        if input_db_tables is None:
            input_db_tables = OrderedDict([
                ('Scenario', ScenarioTable()),
                ('Location', LocationTable()),
                ('Plant', PlantTable()),
                ('Line', LineTable()),
                ('TimePeriod', TimePeriodTable()),
                ('Product', ProductTable()),
                ('Recipe', RecipeTable()),
                ('RecipeProperties', RecipePropertiesTable()),
                ('BomItem', BomItemTable()),
                ('Demand', DemandTable()),
                ('Parameter', ParameterTable()),
            ])
        if output_db_tables is None:
            output_db_tables = OrderedDict([
                ('ProductionActivity', ProductionActivityTable()),
                ('PlantInventory', PlantInventoryTable()),
                ('WarehouseInventory', WarehouseInventoryTable()),
                ('DemandInventory', DemandInventoryTable()),
                ('LineUtilization', LineUtilizationTable()),
                ('TransportationActivity', TransportationActivityTable()),
#                 ('PlantToDemandTransportation', PlantToDemandTransportationTable()),
#                 ('DemandMap', DemandMapTable()),
#                 ('SupplyMap', SupplyMapTable()),
                ('kpis', KpiTable()),
            ])
        super().__init__(input_db_tables=input_db_tables, output_db_tables=output_db_tables, credentials=credentials, schema=schema, echo=echo, multi_scenario=multi_scenario)
