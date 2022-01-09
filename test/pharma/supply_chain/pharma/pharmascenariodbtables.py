#######################################################
# Table specific SQL
#######################################################
from typing import List, Dict
from sqlalchemy import Table, Column, String, Integer, Float, ForeignKey, ForeignKeyConstraint
from collections import OrderedDict

# from supply_chain.folium_supply_chain import SCMapManager, MappingSCDM
# from supply_chain.plotly_supply_chain import PlotlyManager, SupplyChainPlotlyManager, WaterPlotlyManager  #, PlotlySupplyChainDataManager

from supply_chain.scnfo.scnfoscenariodbtables import ProductTable, ScnfoScenarioDbManager, ScenarioTable, LocationTable, \
    PlantTable, LineTable, TimePeriodTable, DemandTable, RecipeTable, RecipePropertiesTable, BomItemTable, \
    ParameterTable, ProductionActivityTable, LineUtilizationTable, DemandMapTable, SupplyMapTable, KpiTable, \
    PlantInventoryTable, DemandInventoryTable, WIPTable, WarehouseTable, WarehousePropertiesTable, ShippingModeTable, \
    ShippingLaneTable, ShippingLanePropertiesTable, WarehouseInventoryTable, TransportationActivityTable,\
    PlannedProductionActivityTable, BusinessKpiTable
from dse_do_utils.scenariodbmanager import ScenarioDbTable, AutoScenarioDbTable  #, ScenarioDbManager
# from supply_chain.water.dewaterdatamanager import DEWaterDataManager  #ScenarioDbTable, ScenarioDbManager



import pandas as pd

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Pharma use-case
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# class ProductTable(ScenarioDbTable):
#     def __init__(self, db_table_name: str = 'product', extended_columns_metadata: List[Column] = []):
#         columns_metadata = [
#             Column('productName', String(256), primary_key=True),
#             Column('inventoryVolume', Float(), primary_key=False),
#             Column('transportationVolume', Float(), primary_key=False),
#             Column('transportationWeight', Float(), primary_key=False),
# #             Column('turnOverRatio', Float(), primary_key=False),
#         ]
#         columns_metadata.extend(extended_columns_metadata)
#         super().__init__(db_table_name, columns_metadata)

class PharmaProductTable(ProductTable):
    def __init__(self, db_table_name: str = 'product', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('productGroup', String(256), primary_key=False),
            Column('productCountry', String(256), primary_key=False),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata)
        
class PharmaLocationTable(LocationTable):
    def __init__(self, db_table_name: str = 'location', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('countryIso', String(3), primary_key=False),
            Column('region', String(256), primary_key=False),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata)
        
class PharmaDemandTable(DemandTable):
    def __init__(self, db_table_name: str = 'demand', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('actualQuantity', Float(), primary_key=False),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata)
        
class PharmaShippingLanePropertiesTable(ShippingLanePropertiesTable):
    def __init__(self, db_table_name: str = 'shipping_lane_properties', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('transitCost', Float(), primary_key=False),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata)
        
class StochasticScenarioTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'stochastic_scenario', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('stochasticScenarioId', String(256), primary_key=True),
            Column('stage1id', String(256), primary_key=False),
            Column('stage2id', String(256), primary_key=False),
            Column('replication', Integer(), primary_key=False),
            Column('stochasticDemandId', String(256), primary_key=False),
            Column('minDemandIncrease', Float(), primary_key=False),
            Column('maxDemandIncrease', Float(), primary_key=False),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata)

class ProductionActivityStochasticTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'production_activity_stocastic'):
        columns_metadata = [
            Column('stochasticScenarioId', String(256), primary_key=True),
            Column('productName', String(256), primary_key=True),
            Column('timePeriodSeq', Integer(), primary_key=True),
            Column('lineName', String(256), primary_key=True),
            Column('recipeId', Integer(), primary_key=True),
            Column('xProdSol_mean', Float()),
            Column('xProdSol_std', Float()),
            Column('xProdSlackSol_mean', Float()),
            Column('xProdSlackSol_std', Float()),
        ]
        constraints_metadata = [
            ForeignKeyConstraint(['stochasticScenarioId'], ['stochastic_scenario.stochasticScenarioId']),
            ForeignKeyConstraint(['productName', 'recipeId'], ['recipe.productName', 'recipe.recipeId']),
            ForeignKeyConstraint(['timePeriodSeq'], ['time_period.timePeriodSeq']),
            ForeignKeyConstraint(['lineName'], ['line.lineName']),
        ]
        super().__init__(db_table_name, columns_metadata, constraints_metadata)
        
class PlantInventoryStochasticTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'plant_inventory_stochastic', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('stochasticScenarioId', String(256), primary_key=True),
            Column('productName', String(256), primary_key=True),
            Column('locationName', String(256), primary_key=True),
            Column('timePeriodSeq', Integer(), primary_key=True),
            Column('xInvSol_mean', Float()),
            Column('xInvSol_std', Float()),
        ]
        constraints_metadata = [
            ForeignKeyConstraint(['stochasticScenarioId'], ['stochastic_scenario.stochasticScenarioId']),
            ForeignKeyConstraint(['productName'], ['product.productName']),
            ForeignKeyConstraint(['locationName'], ['location.locationName']),
            ForeignKeyConstraint(['timePeriodSeq'], ['time_period.timePeriodSeq']),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata, constraints_metadata)
        
class WarehouseInventoryStochsticTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'warehouse_inventory_stochastic', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('stochasticScenarioId', String(256), primary_key=True),
            Column('productName', String(256), primary_key=True),
            Column('locationName', String(256), primary_key=True),
            Column('timePeriodSeq', Integer(), primary_key=True),
            Column('xInvSol_mean', Float()),
            Column('xInvSol_std', Float()),
        ]
        constraints_metadata = [
            ForeignKeyConstraint(['stochasticScenarioId'], ['stochastic_scenario.stochasticScenarioId']),
            ForeignKeyConstraint(['locationName'], ['location.locationName']),
            ForeignKeyConstraint(['productName'], ['product.productName']),
            ForeignKeyConstraint(['timePeriodSeq'], ['time_period.timePeriodSeq']),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata, constraints_metadata)
        
class DemandInventoryStochasticTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'demand_inventory_stochastic', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('stochasticScenarioId', String(256), primary_key=True),
            Column('productName', String(256), primary_key=True),
            Column('locationName', String(256), primary_key=True),
            Column('timePeriodSeq', Integer(), primary_key=True),
            Column('xInvSol_mean', Float()),
            Column('xInvSol_std', Float()),
            Column('xBacklogSol_mean', Float(), primary_key=False),
            Column('xBacklogSol_std', Float(), primary_key=False),
            Column('xBacklogResupplySol_mean', Float(), primary_key=False),
            Column('xBacklogResupplySol_std', Float(), primary_key=False),
            Column('xFulfilledDemandSol_mean', Float(), primary_key=False),
            Column('xFulfilledDemandSol_std', Float(), primary_key=False),
            Column('xUnfulfilledDemandSol_mean', Float(), primary_key=False),
            Column('xUnfulfilledDemandSol_std', Float(), primary_key=False),
        ]
        constraints_metadata = [
            ForeignKeyConstraint(['stochasticScenarioId'], ['stochastic_scenario.stochasticScenarioId']),
            ForeignKeyConstraint(['locationName'], ['location.locationName']),
            ForeignKeyConstraint(['productName'], ['product.productName']),
            ForeignKeyConstraint(['timePeriodSeq'], ['time_period.timePeriodSeq']),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata, constraints_metadata)
        
class TransportationActivityStochasticTable(ScenarioDbTable):
    def __init__(self, db_table_name: str = 'transportation_activity_stochastic', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('stochasticScenarioId', String(256), primary_key=True),
            Column('originLocationName', String(256), primary_key=True),
            Column('destinationLocationName', String(256), primary_key=True),
            Column('shippingMode', String(256), primary_key=True),
            Column('productName', String(256), primary_key=True),
            Column('timePeriodSeq', Integer(), primary_key=True),
            Column('xTransportationSol_mean', Float(), primary_key=False),
            Column('xTransportationSol_std', Float(), primary_key=False),
        ]
        constraints_metadata = [
            ForeignKeyConstraint(['stochasticScenarioId'], ['stochastic_scenario.stochasticScenarioId']),
            ForeignKeyConstraint(['originLocationName'], ['location.locationName']),
            ForeignKeyConstraint(['destinationLocationName'], ['location.locationName']),
            ForeignKeyConstraint(['shippingMode'], ['shipping_mode.shippingModeName']),
            ForeignKeyConstraint(['productName'], ['product.productName']),
            ForeignKeyConstraint(['timePeriodSeq'], ['time_period.timePeriodSeq']),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata, constraints_metadata)


class PharmaDemandInventoryTable(DemandInventoryTable):
    def __init__(self, db_table_name: str = 'demand_inventory', extended_columns_metadata: List[Column] = []):
        columns_metadata = [
            Column('xDOSSlackSol', Float(), primary_key=False),
            Column('dosTargetDays', Integer(), primary_key=False),
            Column('dosTargetQuantity', Float(), primary_key=False),
        ]
        columns_metadata.extend(extended_columns_metadata)
        super().__init__(db_table_name, columns_metadata)

class PharmaScenarioDbManager(ScnfoScenarioDbManager):
    def __init__(self, credentials=None, schema: str = None, echo=False, multi_scenario: bool = True):
        input_db_tables = OrderedDict([
            ('Scenario', ScenarioTable()),
            ('Location', PharmaLocationTable()),
            ('Plant', PlantTable()),
            ('Line', LineTable()),
            ('TimePeriod', TimePeriodTable()),
            ('Product', PharmaProductTable()),
            ('Demand', PharmaDemandTable()),
            ('Recipe', RecipeTable()),
            ('RecipeProperties', RecipePropertiesTable()),
            ('BomItem', BomItemTable()),
            ('WIP', WIPTable()),
            ('Warehouse', WarehouseTable()),
            ('WarehouseProperties', WarehousePropertiesTable()),
            ('ShippingMode', ShippingModeTable()),
            ('ShippingLane', ShippingLaneTable()),
            ('ShippingLaneProperties', PharmaShippingLanePropertiesTable()),
            ('Parameter', ParameterTable()),
            ('PlannedProductionActivity', PlannedProductionActivityTable()),
            ('StochasticScenario', StochasticScenarioTable()),
        ])
        output_db_tables = OrderedDict([
            ('ProductionActivity', ProductionActivityTable()),
            ('PlantInventory', PlantInventoryTable()),
            ('WarehouseInventory', WarehouseInventoryTable()),
            ('DemandInventory', PharmaDemandInventoryTable()),
            ('LineUtilization', LineUtilizationTable()),
            ('TransportationActivity', TransportationActivityTable()),
            ('DemandMap', DemandMapTable()),
            ('SupplyMap', SupplyMapTable()),
            ('BusinessKPIs', BusinessKpiTable()),
            ('kpis', KpiTable()),
            ('ProductionActivityStochastic', ProductionActivityStochasticTable()),
            ('PlantInventoryStochastic', PlantInventoryStochasticTable()),
            ('WarehouseInventoryStochastic', WarehouseInventoryStochsticTable()),
            ('DemandInventoryStochastic', DemandInventoryStochasticTable()),
            ('TransportationActivityStochastic', TransportationActivityStochasticTable()),
            
        ])
        super().__init__(input_db_tables=input_db_tables, output_db_tables=output_db_tables, credentials=credentials, schema=schema, echo=echo,
                         multi_scenario=multi_scenario)
