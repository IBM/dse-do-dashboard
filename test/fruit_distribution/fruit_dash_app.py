# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Dict, List
from dash import html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
from dse_do_dashboard.do_dash_app import DoDashApp
from dse_do_dashboard.main_pages.explore_solution_page import ExploreSolutionPage
from dse_do_dashboard.main_pages.home_page import HomePage
from dse_do_dashboard.main_pages.main_page import MainPage
from dse_do_dashboard.main_pages.prepare_data_page import PrepareDataPage
from dse_do_dashboard.main_pages.prepare_data_page_edit import PrepareDataPageEdit
from dse_do_dashboard.main_pages.run_model_page import RunModelPage
from dse_do_dashboard.main_pages.visualization_tabs_page import VisualizationTabsPage
from dse_do_dashboard.utils.dash_common_utils import PivotTableConfig, ScenarioTableSchema, ForeignKeySchema

# from .visualization_pages.kpi_page import KpiPage
from fruit_distribution.visualization_pages.kpi_page import KpiPage
from visualization_pages.demand_page import DemandPage

from fruit.fruitdatamanager import FruitDataManager
from fruit.fruitplotlymanager import FruitPlotlyManager
from fruit.fruitdbmanager import FruitScenarioDbManager
from visualization_pages.stop_page import StopPage

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

class FruitDashApp(DoDashApp):
    def __init__(self, db_credentials: Dict, schema: str = None, cache_config: Dict = None,
                 port: int = 8050, debug: bool = False, host_env: str = None):
        visualization_pages = [
            KpiPage(self),
            DemandPage(self),
            # StopPage(self),
        ]
        logo_file_name = "logistics.jpg"

        database_manager_class = FruitScenarioDbManager
        data_manager_class = FruitDataManager
        plotly_manager_class = FruitPlotlyManager
        super().__init__(db_credentials, schema,
                         logo_file_name=logo_file_name,
                         cache_config=cache_config,
                         visualization_pages = visualization_pages,
                         database_manager_class=database_manager_class,
                         data_manager_class=data_manager_class,
                         plotly_manager_class=plotly_manager_class,
                         port=port, debug=debug, host_env=host_env)


    def create_main_pages(self) -> List[MainPage]:
        """Creates the ordered list of main pages for the DO app.
        Can be overridden to replace by subclasses (not typical).
        """
        main_pages = [
            HomePage(self),
            # PrepareDataPage(self),
            PrepareDataPageEdit(self),
            RunModelPage(self),
            ExploreSolutionPage(self),
            VisualizationTabsPage(self)
        ]
        return main_pages

    # def shutdown(self):
    #     from flask import request
    #     func = request.environ.get('werkzeug.server.shutdown')
    #     if func is None:
    #         raise RuntimeError('Not running with the Werkzeug Server')
    #     func()

    def get_pivot_table_configs(self) -> Dict[str, PivotTableConfig]:
        input_pivots: List[PivotTableConfig] = [
            # PivotTableConfig(
            #     table_name='Location',
            #     rows=[],
            #     cols=['state'],
            #     vals=[],
            #     rendererName='Stacked Column Chart',
            #     aggregatorName='Count'
            # ),
            # PivotTableConfig(
            #     table_name='Plant',
            #     rows=[],
            #     cols=[],
            #     vals=[],
            #     rendererName='Table',
            #     aggregatorName='Count'
            # ),
        ]
        output_pivots = [
            # This is nonsense! TODO: properly configure!
            # PivotTableConfig(
            #     table_name='TruckLoadsOutput',
            #     rows=['TruckId'],
            #     cols=['PlantId'],
            #     vals=['loadSeq'],
            #     rendererName='Table Heatmap',
            #     aggregatorName='Sum'
            # ),
            PivotTableConfig(
                table_name='kpis',
                rows=['NAME'],
                cols=[],
                vals=['VALUE'],
                rendererName='Grouped Column Chart',
                aggregatorName='Sum'
            ),
        ]
        pivot_table_configs: Dict[str, PivotTableConfig] = {t.table_name : t for t in (input_pivots + output_pivots)}
        return pivot_table_configs


