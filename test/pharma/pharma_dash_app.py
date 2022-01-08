from typing import Dict, List

from pharma.visualization_pages.capacity_page import CapacityPage
from pharma.visualization_pages.demand_fulfillment_page import DemandFulfillmentPage
from pharma.visualization_pages.demand_fulfillment_scroll_page import DemandFulfillmentScrollPage
from pharma.visualization_pages.demand_page import DemandPage
from pharma.visualization_pages.inventory_dos_page import InventoryDosPage
from pharma.visualization_pages.inventory_page import InventoryPage
from pharma.visualization_pages.kpi_page import KpiPage
from pharma.visualization_pages.maps_page import MapsPage
from pharma.visualization_pages.planned_production_page import PlannedProductionPage
from pharma.visualization_pages.production_page import ProductionPage
from pharma.visualization_pages.supply_page import SupplyPage
from pharma.visualization_pages.transportation_page import TransportationPage
from pharma.visualization_pages.utilization_page import UtilizationPage
from dse_do_dashboard.do_dash_app import DoDashApp
from dse_do_dashboard.utils.dash_common_utils import PivotTableConfig, ScenarioTableSchema, ForeignKeySchema
from supply_chain.pharma.pharmadatamanager import PharmaDataManager
from supply_chain.pharma.pharmaplotlymanager import PharmaPlotlyManager
from supply_chain.pharma.pharmascenariodbtables import PharmaScenarioDbManager

"""
How-To create a DO Dashboard:
1. Subclass DoDashApp
2. In the `__init__()`, specify:
   - visualization_pages: a list of instances of subclasses of VisualizationPage.
   - logo_file_name (optional) - Needs to be located in the Dash `assets` folder
   - database_manager_class (required) - Subclass of ScenarioDbManager
   - data_manager_class (required) - Subclass of DataManager
   - plotly_manager_class (required) - Subclass of PlotlyManager
3. Specify pivot-table configurations and table-schemas by overriding the methods:
   - get_pivot_table_configs (optional)
   - get_table_schemas (optional)
4. Create instance of DoDashApp-subclass and specify:
   - db_credentials (required)
   - schema (basically required)
   - cache_config (optional)
"""

class PharmaDashApp(DoDashApp):
    def __init__(self, db_credentials: Dict, schema: str = None, db_echo: bool = False, cache_config: Dict = None,
                 port: int = 8050, dash_debug: bool = False, host_env: str = None):
        visualization_pages = [
            KpiPage(self),
            DemandPage(self),
            CapacityPage(self),
            ProductionPage(self),
            PlannedProductionPage(self),
            SupplyPage(self),
            DemandFulfillmentPage(self),
            DemandFulfillmentScrollPage(self),
            InventoryPage(self),
            InventoryDosPage(self),
            UtilizationPage(self),
            TransportationPage(self),
            MapsPage(self),
        ]
        logo_file_name = "IBM.png"

        database_manager_class = PharmaScenarioDbManager
        data_manager_class = PharmaDataManager
        plotly_manager_class = PharmaPlotlyManager
        super().__init__(db_credentials, schema,
                         db_echo = db_echo,
                         logo_file_name=logo_file_name,
                         cache_config=cache_config,
                         visualization_pages = visualization_pages,
                         database_manager_class=database_manager_class,
                         data_manager_class=data_manager_class,
                         plotly_manager_class=plotly_manager_class,
                         port=port, dash_debug=dash_debug, host_env=host_env)

    def get_pivot_table_configs(self) -> Dict[str, PivotTableConfig]:
        input_pivots: List[PivotTableConfig] = [
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
        output_pivots = [
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
        pivot_table_configs: Dict[str, PivotTableConfig] = {t.table_name : t for t in (input_pivots + output_pivots)}
        return pivot_table_configs

    def get_table_schemas(self) -> Dict[str, ScenarioTableSchema]:
        input_tables: List[ScenarioTableSchema] = [
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

        output_tables: List[ScenarioTableSchema]= [
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

        table_schemas: Dict[str, ScenarioTableSchema] = {t.table_name : t for t in (input_tables + output_tables)}
        return table_schemas