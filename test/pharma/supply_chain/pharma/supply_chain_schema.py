"""
Experiment to define keys, columns, foreign keys in Named Tuples
"""

from typing import Dict, List

from utils.dash_common_utils import ForeignKeySchema, ScenarioTableSchema, PivotTableConfig

"""
Defines the 'schema' for the dataframes in a DataManager.
Is used for:
* Automatically set the index of a table
* 'Expand' a table by recursively joining tables from the foreign keys.
This is used so that a PivotTable in the UI has all columns to work with (similar as in DOC). 

TODO:
* Migrate to scnfo, water, etc.
"""

"""
TODO: Generate this same info from an instance of a ScnfoScenarioDbManager.
Avoid defining the same info again.
But this can be used when there is no ScenarioDbManager.
"""
scnfo_input_tables:List[ScenarioTableSchema]= [
    ScenarioTableSchema(
        table_name = 'TimePeriod',
        index_columns = ['timePeriodSeq'],
        value_columns = [],
        foreign_tables = [],
    ),
    ScenarioTableSchema(
        table_name = 'Demand',
        index_columns = ['customerName', 'locationName', 'productName', 'timePeriodSeq'],
        value_columns =[],
        foreign_tables = [
            ForeignKeySchema(
                table_name = 'Location',
                foreign_keys = ['locationName']
            ),
            ForeignKeySchema(
                table_name = 'Product',
                foreign_keys = ['productName']
            ),
        ],
    ),
    ScenarioTableSchema(
        table_name = 'Product',
        index_columns = ['productName'],
        value_columns = [],
        foreign_tables = [],
    ),
    ScenarioTableSchema(
        table_name = 'RecipeProperties',
        index_columns = ['productName', 'timePeriodSeq', 'lineName', 'recipeId'],
        value_columns = [],
        foreign_tables= [],
    ),
    ScenarioTableSchema(
        table_name = 'Line',
        index_columns = ['lineName'],
        value_columns = [],
        foreign_tables = [],
    ),
    ScenarioTableSchema(
        table_name = 'Plant',
        index_columns = ['plantName'],
        value_columns = [],
        foreign_tables = [],
    ),
    ScenarioTableSchema(
        table_name = 'Location',
        index_columns = ['locationName'],
        value_columns = [],
        foreign_tables = [],
    ),
    ScenarioTableSchema(
        table_name = 'WIP',
        index_columns = ['productName', 'locationName', 'timePeriodSeq'],
        value_columns = [],
        foreign_tables = [],
    ),
    ScenarioTableSchema(
        table_name = 'Warehouse',
        index_columns = ['warehouseName'],
        value_columns = [],
        foreign_tables = [],
    ),
    ScenarioTableSchema(
        table_name = 'WarehouseProperties',
        index_columns = ['warehouseName', 'productName', 'timePeriodSeq'],
        value_columns = [],
        foreign_tables = [],
    ),
    ScenarioTableSchema(
        table_name = 'ShippingMode',
        index_columns = ['shippingModeName'],
        value_columns = [],
        foreign_tables = [],
    ),
    ScenarioTableSchema(
        table_name = 'ShippingLane',
        index_columns = ['originLocationName', 'destinationLocationName', 'shippingMode'],
        value_columns = [],
        foreign_tables = [],
    ),
    ScenarioTableSchema(
        table_name = 'ShippingLaneProperties',
        index_columns = ['originLocationName', 'destinationLocationName', 'shippingMode','productName'],
        value_columns = [],
        foreign_tables = [],
    ),
    ScenarioTableSchema(
        table_name = 'PlannedProductionActivity',
        index_columns = ['planId', 'productName', 'timePeriodSeq', 'lineName', 'recipeId'],
        value_columns = [],
        foreign_tables = [],
    ),
    ScenarioTableSchema(
        table_name = 'StochasticScenario',
        index_columns = ['stochasticScenarioId'],
        value_columns = [],
        foreign_tables = [],
    ),
]

scnfo_output_tables: List[ScenarioTableSchema]= [
    ScenarioTableSchema(
        table_name = 'ProductionActivity',
        index_columns = ['productName', 'timePeriodSeq', 'lineName', 'recipeId'],
        value_columns = [],
        foreign_tables = [],
    ),
    ScenarioTableSchema(
        table_name = 'PlantInventory',
        index_columns = ['productName', 'locationName', 'timePeriodSeq'],
        value_columns = [],
        foreign_tables = [],
    ),
    ScenarioTableSchema(
        'DemandInventory',
        index_columns = ['productName', 'locationName', 'timePeriodSeq'],
        value_columns = [],
        foreign_tables = [],
    ),
    ScenarioTableSchema(
        'WarehouseInventory',
        index_columns = ['productName', 'locationName', 'timePeriodSeq'],
        value_columns = [],
        foreign_tables = [],
    ),
    ScenarioTableSchema(
        table_name = 'TransportationActivity',
        index_columns = ['originLocationName','destinationLocationName','shippingMode', 'productName', 'timePeriodSeq'],
        value_columns = [],
        foreign_tables = [],
    ),
    ScenarioTableSchema(
        table_name = 'LineUtilization',
        index_columns = ['lineName', 'timePeriodSeq'],
        value_columns = [],
        foreign_tables = [],
    ),
    ScenarioTableSchema(
        table_name = 'SupplyMap',
        index_columns = ['locationName'],
        value_columns = [],
        foreign_tables = [],
    ),
    ScenarioTableSchema(
        table_name = 'DemandMap',
        index_columns = ['locationName'],
        value_columns = [],
        foreign_tables = [],
    ),
    ScenarioTableSchema(
        table_name = 'DemandSupplyMap',
        index_columns = ['locationName'],
        value_columns = [],
        foreign_tables = [],
    ),
    ScenarioTableSchema(
        table_name = 'BusinessKpis',
        index_columns = ['kpi'],
        value_columns = [],
        foreign_tables = [],
    ),
    ScenarioTableSchema(
        table_name = 'kpis',
        index_columns = ['NAME'],
        value_columns = [],
        foreign_tables = [],
    ),
    ScenarioTableSchema(
        table_name = 'ProductionActivityStochastic',
        index_columns = ['stochasticScenarioId','productName','timePeriodSeq','lineName','recipeId'],
        value_columns = [],
        foreign_tables = [],
    ),
    ScenarioTableSchema(
        table_name = 'PlantInventoryStochastic',
        index_columns = ['stochasticScenarioId','productName','locationName','timePeriodSeq'],
        value_columns = [],
        foreign_tables = [],
    ),
    ScenarioTableSchema(
        table_name = 'WarehouseInventoryStochastic',
        index_columns = ['stochasticScenarioId','productName','locationName','timePeriodSeq'],
        value_columns = [],
        foreign_tables = [],
    ),
    ScenarioTableSchema(
        table_name = 'DemandInventoryStochastic',
        index_columns = ['stochasticScenarioId','productName','locationName','timePeriodSeq'],
        value_columns = [],
        foreign_tables = [],
    ),
    ScenarioTableSchema(
        table_name = 'TransportationActivityStochastic',
        index_columns = ['stochasticScenarioId','originLocationName','destinationLocationName','shippingMode','productName','timePeriodSeq'],
        value_columns = [],
        foreign_tables = [],
    ),
]

SCNFO_SCHEMA:Dict[str, ScenarioTableSchema] = {t.table_name : t for t in (scnfo_input_tables + scnfo_output_tables)}

# print(scnfo_schema)
# print(scnfo_schema['Demand'].index_columns)

scnfo_input_pivots:List[PivotTableConfig]= [
    PivotTableConfig(
        table_name='Location',
        rows=[],
        cols=['state'],
        vals=[],
        rendererName='Stacked Column Chart',
        aggregatorName='Count'
    ),
    PivotTableConfig(
        table_name='Plant',
        rows=[],
        cols=[],
        vals=[],
        rendererName='Table',
        aggregatorName='Count'
    ),
    PivotTableConfig(
        table_name='TimePeriod',
        rows=[],
        cols=[],
        vals=[],
        rendererName='Table',
        aggregatorName='Count'
    ),
    PivotTableConfig(
        table_name='Line',
        rows=['country', 'state'],
        cols=[],
        vals=[],
        rendererName='Table',
        aggregatorName='Count'
    ),
    PivotTableConfig(
        table_name='Product',
        rows=['subgroupID'],
        cols=['groupID'],
        vals=[],
        rendererName='Stacked Column Chart',
        aggregatorName='Count'
    ),
    PivotTableConfig(
        table_name='Demand',
        rows=['productName'],
        cols=['timePeriodSeq'],
        vals=['quantity'],
        rendererName='Stacked Column Chart',
        aggregatorName='Sum'
    ),
]

scnfo_output_pivots = [
    PivotTableConfig(
        table_name='ProductionActivity',
        rows=['lineName'],
        cols=['timePeriodSeq'],
        vals=['line_capacity_utilization'],
        rendererName='Table Heatmap',
        aggregatorName='Sum'
    ),
    PivotTableConfig(
        table_name='PlantInventory',
        rows=['locationName','productName'],
        cols=['timePeriodSeq'],
        vals=['xPlantInvSol'],
        rendererName='Table Heatmap',
        aggregatorName='Sum'
    ),
    PivotTableConfig(
        table_name='DemandInventory',
        rows=['locationName','productName'],
        cols=['timePeriodSeq'],
        vals=['xBacklogSol'],
        rendererName='Stacked Column Chart',
        aggregatorName='Sum'
    ),
    PivotTableConfig(
        table_name='LineUtilization',
        rows=['lineName'],
        cols=['timePeriodSeq'],
        vals=['utilization'],
        rendererName='Table Heatmap',
        aggregatorName='Sum'
    ),

]

SCNFO_PIVOT_CONFIG:Dict[str, PivotTableConfig] = {t.table_name : t for t in (scnfo_input_pivots + scnfo_output_pivots)}
