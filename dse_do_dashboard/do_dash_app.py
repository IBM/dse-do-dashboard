# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import time
from typing import Dict, List, Optional

import pandas as pd

from dse_do_dashboard.main_pages.home_page_edit import HomePageEdit
from dse_do_dashboard.main_pages.prepare_data_page_edit import PrepareDataPageEdit
from dse_do_dashboard.utils.domodelrunner import DoModelRunner, DoModelRunnerConfig
from dse_do_utils import DataManager
from dse_do_utils.scenariodbmanager import ScenarioDbManager, DatabaseType

from dse_do_dashboard.dash_app import DashApp, HostEnvironment
from dash import dcc, html, Output, Input, State
import dash_bootstrap_components as dbc

from dse_do_dashboard.main_pages.explore_solution_page import ExploreSolutionPage
from dse_do_dashboard.main_pages.home_page import HomePage
from dse_do_dashboard.main_pages.main_page import MainPage
from dse_do_dashboard.main_pages.not_found import NotFoundPage
from dse_do_dashboard.main_pages.prepare_data_page import PrepareDataPage
from dse_do_dashboard.main_pages.run_model_page import RunModelPage
from dse_do_dashboard.main_pages.visualization_tabs_page import VisualizationTabsPage
from dse_do_dashboard.utils.dash_common_utils import ScenarioTableSchema, PivotTableConfig
from dse_do_utils.plotlymanager import PlotlyManager
from dse_do_dashboard.visualization_pages.visualization_page import VisualizationPage



class DoDashApp(DashApp):
    """Abstract class.
    Note that currently the difference between DashApp and DoDashApp is fairly arbitrary.
    It will start to make some sense once there are different frameworks for DashApp, i.e. peers of DoDashApp.

    How-To create a DO Dashboard:
    1. Subclass DoDashApp
    2. In the `__init__()`, specify:
       - logo_file_name (optional)
       - database_manager_class (required)
       - data_manager_class (required)
       - plotly_manager_class (required)
    3. Specify pivot-table configurations and table-schemas by overriding the methods:
       - get_pivot_table_configs (optional)
       - get_table_schemas (optional)
    4. Create instance of DoDashApp-subclass and specify:
       - db_credentials (required)
       - schema (basically required)
       - cache_config (optional)
    """
    def __init__(self, db_credentials: Dict,
                 schema: Optional[str] = None,
                 db_echo: Optional[bool] = False,
                 logo_file_name: Optional[str] = 'IBM.png',
                 navbar_brand_name: Optional[str] = 'Dashboard',
                 cache_config: Optional[Dict]= {},
                 visualization_pages: Optional[List[VisualizationPage]]= [],
                 database_manager_class=None,
                 data_manager_class=None,
                 plotly_manager_class=None,
                 port: Optional[int] = 8050,
                 dash_debug: Optional[bool] = False,
                 host_env: Optional[HostEnvironment] = None,
                 bootstrap_theme=dbc.themes.BOOTSTRAP,
                 bootstrap_figure_template:str="bootstrap",
                 enable_long_running_callbacks: bool = False,
                 db_type: DatabaseType = DatabaseType.DB2,
                 db_manager_kwargs: Dict = {},
                 ):
        """Create a Dashboard app.

        :param db_credentials: Database connection credentials.
        :param schema: Name of DB schema. If it doesn't exist, will create it automatically.
        :param logo_file_name: Name of image for logo.
        Must be in `./assets` folder (where '.' is the directory of the `index.py` file that starts the app.
        :param cache_config: Flask cache configuration. By default will use in-memory caching for 1 hour.
        :param visualization_pages: List of classes that represent the visualization pages.
        :param database_manager_class: class of the ScenarioDbManager.
        Alternatively, override the method `create_database_manager_instance`.
        :param data_manager_class: class of the DataManager.
        Either specify the `data_manager_class` and the `plotly_manager_class` or override the method `get_plotly_manager`
        :param plotly_manager_class: class of the PlotlyManager.
        Either specify the `data_manager_class` and the `plotly_manager_class` or override the method `get_plotly_manager`
        :param port: Port for DashApp. Default = 8050.
        :param dash_debug: If true, runs dash app server in debug mode.
        :param host_env: If HostEnvironment.CPD402, will use the ws_applications import make_link to
        generate a requests_pathname_prefix for the Dash app. For use with custom environment in CPD v4.0.02.
        The alternative (None of HostEnvironment.Local) runs the Dash app regularly.
        :param enable_long_running_callbacks. Default = True. Enables the use of Dash long-running callbacks for model runs. If False, it only allows for in-line runs.
        """
        self.db_credentials = db_credentials
        self.schema = schema
        self.db_echo = db_echo
        self.db_type = db_type
        self.db_manager_kwargs = db_manager_kwargs
        self.database_manager_class = database_manager_class
        # assert issubclass(self.database_manager_class, ScenarioDbManager)
        self.dbm = self.create_database_manager_instance()

        # Initialize main pages:
        self.main_pages = self.create_main_pages()
        # MainPage quick access by URL:
        self.main_pages_dict_by_url_page_name: Dict[str, MainPage] = {
            vp.url: vp for vp in
            self.main_pages}

        # self.home_page = HomePage(self)
        # self.prepare_data_page = PrepareDataPage(self)
        # self.run_model_page = RunModelPage(self)
        # self.explore_solution_page = ExploreSolutionPage(self)
        # self.visualization_tabs_page = VisualizationTabsPage(self)

        self.visualization_pages: List[VisualizationPage] = visualization_pages
        # VisualizationPage quick access by URL:
        self.visualization_pages_dict_by_url_page_name: Dict[str, VisualizationPage] = {
            f"visualization/{vp.url}": vp for vp in
            self.visualization_pages}

        self.table_pivot_configs = self.get_pivot_table_configs() # table_pivot_config
        self.table_schemas = self.get_table_schemas()

        self.data_manager_class = data_manager_class
        self.plotly_manager_class = plotly_manager_class
        # assert issubclass(self.data_manager_class, DataManager)
        # assert issubclass(self.plotly_manager_class, PlotlyManager)

        if cache_config is None:
            # This default should typically apply to any non-deployment platform
            cache_config = {
                'CACHE_TYPE': 'SimpleCache',
                'CACHE_DEFAULT_TIMEOUT': 3600  # in seconds, i.e. 1 hour
            }

        self.read_scenario_table_from_db_callback = None  # For Flask caching
        self.read_scenarios_table_from_db_callback = None # For Flask caching

        self.job_queue: List[DoModelRunner] = []  # TODO: migrate to Store. Using global variables is dangerous



        super().__init__(logo_file_name=logo_file_name, navbar_brand_name=navbar_brand_name,
                         cache_config=cache_config, port=port,
                         dash_debug=dash_debug, host_env=host_env,
                         bootstrap_theme=bootstrap_theme, bootstrap_figure_template=bootstrap_figure_template,
                         enable_long_running_callbacks=enable_long_running_callbacks,)

    def create_database_manager_instance(self) -> ScenarioDbManager:
        """Create an instance of a ScenarioDbManager.
        The default implementation uses the database_manager_class from the constructor.
        Optionally, override this method."""
        if self.database_manager_class is not None and self.db_credentials is not None:
            print(f"Connecting to {self.db_type} at {self.db_credentials['host']}, schema = {self.schema}")
            dbm = self.database_manager_class(credentials=self.db_credentials,
                                              schema=self.schema, echo=self.db_echo, db_type = self.db_type,
                                              **self.db_manager_kwargs)
        else:
            print("Error: either specifiy `database_manager_class`, `db_credentials` and `schema`, or override `create_database_manager_instance`.")
        return dbm

    def get_app_stores(self) -> List[dcc.Store]:
        """Add global dcc.Stores"""
        stores = [
            # For reference scenario(s):
            # TODO
        ]
        if self.enable_long_running_callbacks:
            stores.extend([
                # For long-running callbacks for model runs:
                dcc.Store(id='lrc_job_trigger_store'),
                dcc.Store(id='lrc_job_log_store'),
                dcc.Store(id='lrc_job_queue_data_store'),
            ])
        return stores

    def create_main_pages(self) -> List[MainPage]:
        """Creates the ordered list of main pages for the DO app.
        Can be overridden to replace by subclasses (not typical).
        """
        main_pages = [
            HomePageEdit(self),
            PrepareDataPageEdit(self),
            RunModelPage(self),
            ExploreSolutionPage(self),
            VisualizationTabsPage(self)
        ]
        return main_pages

    def get_sidebar(self):
        """Creates the sidebar."""
        sidebar_style = {
            "position": "fixed",
            "top": self.header_height,
            "left": 0,
            "bottom": self.footer_height,
            "width": self.sidebar_width,
            "padding": "1rem 1rem",
        }

        visualization_menu_children = [
            dbc.DropdownMenuItem(
                vp.page_name,
                href=self.app.get_relative_path(f'/visualization/{vp.url}')
            ) for vp in self.visualization_pages
        ]

        # Create links for main pages:
        main_page_nav_links: List[dbc.NavLink] = [
            dbc.NavLink(
                href=self.app.get_relative_path(f'/{mp.url}'),
                children=mp.page_name
            )
            for mp in self.main_pages
        ]

        # Add Visualization pages:
        main_page_nav_links.extend([
            dbc.Button(
                "Visualization Pages",
                outline=True,
                id='visualization_pages_collapse_button',
                className='mb-3',
                n_clicks=0,
                # href=self.app.get_relative_path('/visualization'),
                # active=True,
                color='primary',

            ),
            dbc.Collapse(
                children = visualization_menu_children,
                id="visualization_pages_collapse_menu",
                is_open=True,
                navbar=True,
            ),
        ]
        )

        sidebar = html.Div([
            html.Hr(),
            dbc.Nav(main_page_nav_links #+ [

                # dbc.NavLink(
                #     href=self.app.get_relative_path('/'),
                #     children='Home'
                # ),
                # dbc.NavLink(
                #     href=self.app.get_relative_path('/prepare-data'),
                #     children='Prepare Data'
                # ),
                # dbc.NavLink(
                #     href=self.app.get_relative_path('/run-model'),
                #     children='Run Model'
                # ),
                # dbc.NavLink(
                #     href=self.app.get_relative_path('/explore-solution'),
                #     children='Explore Solution'
                # ),

                # dbc.Button(
                #     "Visualization",
                #     outline=True,
                #     id='collapse-button',
                #     className='mb-3',
                #     n_clicks=0,
                #     href=self.app.get_relative_path('/visualization'),
                #     # active=True,
                #     color='primary',
                #
                # ),

                # dbc.Collapse(
                #     children = visualization_menu_children,
                #     id="collapse",
                #     is_open=True,
                #     navbar=True,
                # ),

            # ]
            , vertical=True, pills=True,)
        ], style=sidebar_style)
        return sidebar

    def refresh_scenarios_dash_callback(self, current_scenario_name: str):
        """Reads the currently selected scenario-name. Reloads the scenario names from DB.
        If the currently selected scenario is valid, this will be maintained as the selected value.
        """
        print(f"Scenario refresh button. Reload scenario table. Clears cache. current-scenario={current_scenario_name}")
        self.cache.init_app(self.app.server, config=self.cache_config)
        # with app.app_context():
        self.cache.clear()

        # scenarios_df = get_scenarios_df_cached_proc().reset_index()
        scenarios_df = self.read_scenarios_table_from_db_cached().reset_index()
        if scenarios_df.shape[0] > 0:
            if current_scenario_name in list(scenarios_df.scenario_name):
                initial_scenario_name = current_scenario_name
            else:
                initial_scenario_name = scenarios_df.scenario_name[0]
        else:
            initial_scenario_name = None
        options = [
            {'label': i, 'value': i}
            for i in scenarios_df.scenario_name
        ]
        return options, initial_scenario_name

    ########################################################################################
    # DB caching callbacks
    ########################################################################################
    # Scenarios table
    def set_scenarios_table_read_callback(self, scenarios_table_read_callback=None):
        """Sets a callback function to read the scenario table from the DB.
        """
        self.read_scenarios_table_from_db_callback = scenarios_table_read_callback

    def read_scenarios_table_from_db_cached(self) -> pd.DataFrame:
        """For use with Flask caching. Default implementation.
        In case no caching has been configured. Simply calls the regular method `get_scenarios_df`.

        For caching:
        1. Specify a callback procedure in `read_scenarios_table_from_db_callback` that uses a hard-coded version of a ScenarioDbManager,
        which in turn calls the regular method `get_scenarios_df`
        """
        # df = self.dbm.read_scenarios_table_from_db_cached()
        # df = get_scenarios_df_cached_proc()

        if self.read_scenarios_table_from_db_callback is not None:
            df = self.read_scenarios_table_from_db_callback()  # NOT a method!
        else:
            df = self.dbm.get_scenarios_df()
        return df

    def get_scenarios_df(self):
        return self.dbm.get_scenarios_df()

    ########################################################################################
    # Scenario table
    def set_table_read_callback(self, table_read_callback=None):
        """Sets a callback function to read a table from a scenario.
        """
        #     print(f"Set callback to {table_read_callback}")
        self.read_scenario_table_from_db_callback = table_read_callback

    def read_scenario_table_from_db_cached(self, scenario_name: str, scenario_table_name: str) -> pd.DataFrame:
        """For use with Flask caching. Default implementation.
        In case no caching has been configured. Simply calls the regular method `read_scenario_table_from_db`.

        For caching:
        1. Specify a callback procedure in `read_scenario_table_from_db_callback` that uses a hard-coded version of a ScenarioDbManager,
        which in turn calls the regular method `read_scenario_table_from_db`
        """
        # 1. Override this method and call a procedure that uses a hard-coded version of a ScenarioDbManager,
        # which in turn calls the regular method `read_scenario_table_from_db`

        # return self.read_scenario_table_from_db(scenario_name, scenario_table_name)
        if self.read_scenario_table_from_db_callback is not None:
            df = self.read_scenario_table_from_db_callback(scenario_name, scenario_table_name)  # NOT a method!
        else:
            df = self.dbm.read_scenario_table_from_db(scenario_name, scenario_table_name)
        return df

    def read_scenario_tables_from_db_cached(self, scenario_name: str,
                                            input_table_names: List[str] = None,
                                            output_table_names: List[str] = None):
        """For use with Flask caching. Loads data for selected input and output tables.
        Same as `read_scenario_tables_from_db`, but calls `read_scenario_table_from_db_cached`.
        Is called from dse_do_dashboard.DoDashApp to create the PlotlyManager."""

        if input_table_names is None:
            # input_table_names = list(self.dbm.input_db_tables.keys())  # This is not consistent with implementation in ScenarioDbManager! Replace by empty list
            input_table_names = []
            if 'Scenario' in input_table_names: input_table_names.remove('Scenario')  # Remove the scenario table
        if output_table_names is None:  # load all tables by default
            output_table_names = self.dbm.output_db_tables.keys()

        # VT 2022-09-12: Only read tables that exist in schema:
        # TODO: test and enable this code to handle optional tables in DB, like the Warehouse, WarehouseProperties, etc
        # input_table_names_in_schema = []
        # for input_table_name in input_table_names:
        #     if input_table_name in self.dbm.input_db_tables.keys():
        #         input_table_names_in_schema.append(input_table_name)
        #     else:
        #         print(f"Warning: DODashApp.read_scenario_tables_from_db_cached: input table {input_table_name} not in schema. Table not read.")
        #
        # output_table_names_in_schema = []
        # for output_table_name in output_table_names:
        #     if output_table_name in self.dbm.output_db_tables.keys():
        #         output_table_names_in_schema.append(output_table_name)
        #     else:
        #         print(f"Warning: DODashApp.read_scenario_tables_from_db_cached: output table {output_table_name} not in schema. Table not read.")

        inputs = {}
        for scenario_table_name in input_table_names:
            # print(f"read input table {scenario_table_name}")
            # TODO: skip scenario_table_name if not in schema
            if scenario_table_name in self.dbm.input_db_tables.keys():
                inputs[scenario_table_name] = self.read_scenario_table_from_db_cached(scenario_name, scenario_table_name)

        outputs = {}
        for scenario_table_name in output_table_names:
            # print(f"read output table {scenario_table_name}")
            if scenario_table_name in self.dbm.output_db_tables.keys():
                outputs[scenario_table_name] = self.read_scenario_table_from_db_cached(scenario_name, scenario_table_name)
        return inputs, outputs

    ########################################################################################
    # End DB caching callbacks
    ########################################################################################

    def display_content_callback(self, pathname: str, scenario_name: str,
                                 reference_scenario_name: str = None, multi_scenario_names: List[str] = None):
        """Callback for main content area. Will update the content area.
        Will need to be called through callback in index.py, where `DA` is the instance of the DashApp.

        Usage::

            @app.callback(Output('content', 'children'), [Input('url', 'pathname')])
            def display_content(pathname):
                return DA.display_content_callback()

        """
        page_name = self.app.strip_relative_path(pathname)
        # if not page_name:  # None or ''
        #     return self.get_home_page().get_layout()
        # elif page_name == 'prepare-data':
        #     return self.get_prepare_data_page().get_layout()
        # elif page_name == 'run-model':
        #     return self.get_run_model_page().get_layout()
        # elif page_name == 'explore-solution':
        #     return self.get_explore_solution_page().get_layout()
        # elif page_name == 'visualization':
        #     return self.get_visualization_tabs_page().get_layout()
        if page_name in self.main_pages_dict_by_url_page_name:
            page = self.main_pages_dict_by_url_page_name[page_name]
            layout = page.get_layout(scenario_name, reference_scenario_name, multi_scenario_names)
        elif page_name in self.visualization_pages_dict_by_url_page_name:
            vp = self.visualization_pages_dict_by_url_page_name[page_name]
            layout = vp.get_layout(scenario_name, reference_scenario_name, multi_scenario_names)
        else:
            layout = self.get_not_found_page().get_layout(f"Page '{pathname}' not found")
        return layout

    def get_not_found_page(self) -> NotFoundPage:
        return NotFoundPage(self)

    ###########################################################################################################
    #
    ###########################################################################################################

    def get_plotly_manager(self, scenario_name: str,
                           input_table_names: List[str] = None,
                           output_table_names: List[str] = None,
                           reference_scenario_name: str = None,  # TODO: support single reference scenario
                           multi_scenario_names: List[str] = None,
                           enable_reference_scenario: bool = False,
                           enable_multi_scenario: bool = False) -> PlotlyManager:
        """Creates the PlotlyManager based on the plotly_manager_class and the data_manager_class.
        Loads data for selected input and output tables from the DB, creates a DataManager and embeds into a PlotlyManager.

        :param scenario_name: Name of scenario.
        :param input_table_names: List of input table names to load. Use ['*'] for all input tables.
        :param output_table_names: List of output table names to load. Use ['*'] for all output tables.
        :return: A PlotlyManager, or None if plotly_manager_class and the data_manager_class have not been defined.
        """
        if self.data_manager_class is not None and self.plotly_manager_class is not None:
            inputs, outputs = self.read_scenario_tables_from_db_cached(scenario_name, input_table_names, output_table_names)
            dm = self.data_manager_class(inputs, outputs)
            dm.prepare_data_frames()
            pm = self.plotly_manager_class(dm)

            # print(f"get_plotly_manager. Input tables = {input_table_names}")
            if enable_reference_scenario and reference_scenario_name is not None:
                inputs, outputs = self.read_scenario_tables_from_db_cached(reference_scenario_name, input_table_names, output_table_names)
                ref_dm = self.data_manager_class(inputs, outputs)
                ref_dm.prepare_data_frames()
                pm.ref_dm = ref_dm  # TODO: add to pm via constructor
            else:
                pm.ref_dm = None

            if enable_multi_scenario and multi_scenario_names is not None:
                # TODO: this is not (yet) cached. Add caching.
                ms_inputs, ms_outputs = self.dbm.read_multi_scenario_tables_from_db(multi_scenario_names, input_table_names, output_table_names)
                # TODO: for now just add as properties of the pm, since the dm is for one scenario. Maybe we'll need a `MultiScenarioDataManager`?
                pm.ms_inputs = ms_inputs
                pm.ms_outputs = ms_outputs
            else:
                pm.ms_inputs = None
                pm.ms_outputs = None
        else:
            print("Error: either specify the `data_manager_class` and the `plotly_manager_class` or override the method `get_plotly_manager`.")
            pm = None
        return pm

    def get_input_table_names(self) -> List[str]:
        """Return list of valid table names based on self.input_db_tables"""
        names = list(self.dbm.input_db_tables.keys())
        if 'Scenario' in names: names.remove('Scenario')
        return names

    def get_output_table_names(self) -> List[str]:
        """Return list of valid table names based on self.input_db_tables"""
        names = list(self.dbm.output_db_tables.keys())
        return names

    def get_pivot_table_config(self, table_name) -> Optional[PivotTableConfig]:
        """Get the PivotTableConfig for this table, or None if it doesn't exist."""
        pivot_config = (self.table_pivot_configs[table_name] if table_name in self.table_pivot_configs else None)
        return pivot_config

    def get_table_by_name(self, dm: DataManager,
                          table_name: str,
                          index: Optional[bool] = False,
                          expand: Optional[bool] = False) -> Optional[pd.DataFrame]:
        """Return input or output table by name.

        :param dm: The DataManager.
        :param table_name: can be the name of an input or an output table
        :param index: index the DataFrame based on the primary keys on the ScenarioTableSchema of this table.
        :param expand: join tables from foreign-keys. This is NOT tested. Leave False for now.
        :return: A DataFrame, or None of not found.

        TODO: validate that the `expand` option works
        """
        df = dm.get_raw_table_by_name(table_name)
        if df is not None:
            if expand:
                if table_name in self.table_schemas:
                    for fkt in self.table_schemas[table_name].foreign_tables:
                        foreign_df = self.get_table_by_name(fkt.table_name, expand=True)
                        if foreign_df is not None:
                            df = pd.merge(df, foreign_df, on=fkt.foreign_keys, how='inner')
                        else:
                            print(f"Error: could not find foreign-key table {fkt.table_name}")
            if index:
                if table_name in self.table_schemas:
                    df = df.set_index(self.table_schemas[table_name].index_columns, verify_integrity=True)
        return df

    def get_table_schema(self, table_name: str) -> Optional[ScenarioTableSchema]:
        table_schema = None
        # print(f"get_table_schema - {self.table_schemas}")
        if self.table_schemas is not None and table_name in self.table_schemas:
            table_schema = self.table_schemas[table_name]
        return table_schema

    # def get_table_schemas(self) -> Dict[str, ScenarioTableSchema]:
    #     """Optionally can be overridden to specify table schemas.
    #     By default, doesn't specify table schemas."""
    #     input_tables: List[ScenarioTableSchema] = [
    #     ]
    #     output_tables: List[ScenarioTableSchema] = [
    #     ]
    #     table_schemas: Dict[str, ScenarioTableSchema] = {t.table_name: t for t in (input_tables + output_tables)}
    #     return table_schemas

    def get_table_schemas(self) -> Dict[str, ScenarioTableSchema]:
        """This method will automatically extract the table-schemas from ScenarioDbManager.
        Note that only works if the schema is explicitly defined, not when the class AutoScenarioDbTable is used.
        TODO:
        * value_columns are currently NOT populated because the DoDashApp doesn't use them
        * foreign_tables are NOT populated yet. Is not that trivial due to different names in DB and Scenario.
        Also, this feature needs testing in DODashApp
        """
        tss = []
        for table_name, table in self.dbm.db_tables.items():
            if table_name != 'Scenario':
                index_columns = []
                value_columns = []
                for column in table.columns_metadata:
                    # print(column.primary_key)
                    # print(column.name)
                    # if column.name != 'scenario_name' :
                    if column.name not in ['scenario_seq', 'scenario_name']:  # Works in both designs
                        if column.primary_key:
                            index_columns.append(column.name)
                        else:
                            value_columns.append(column.name)
                for fk in table.constraints_metadata:
                    pass
                ts = ScenarioTableSchema(
                    table_name = table_name,
                    index_columns = index_columns,
                    value_columns = [],  # value_columns,
                    foreign_tables = [],
                )
                tss.append(ts)
        table_schemas: Dict[str, ScenarioTableSchema] = {t.table_name: t for t in tss}
        return table_schemas

    def get_pivot_table_configs(self) -> Dict[str, PivotTableConfig]:
        """Optionally can be overridden to specify pivot table configurations.
        By default, doesn't specify configurations"""
        input_pivots: List[PivotTableConfig]= [
        ]
        output_pivots = [
        ]
        pivot_table_configs: Dict[str, PivotTableConfig] = {t.table_name: t for t in (input_pivots + output_pivots)}
        return pivot_table_configs

    ###################################################################################################
    #  Set Dash callbacks programmatically
    ###################################################################################################

    def set_cache_callbacks(self):
        """Define the procedures that will be cached.
        Notes:
        * The cached procedure can contain a reference to `self`, i.e. the current DoDashApp!
        * No need to hard-code
        """
        super().set_cache_callbacks()
        cache = self.cache
        print("Initializing the cache")

        @cache.memoize()
        def read_scenario_table_from_db_cached_proc(scenario_name: str, scenario_table_name: str) -> pd.DataFrame:
            """To be cached. Keys are 'clean' strings: scenario name and table"""
            df = self.dbm.read_scenario_table_from_db(scenario_name, scenario_table_name)
            print(f"DB read {scenario_name} - {scenario_table_name} - {df.shape[0]} rows")
            return df
        self.set_table_read_callback(read_scenario_table_from_db_cached_proc)

        @cache.memoize()
        def get_scenarios_df_cached_proc() -> pd.DataFrame:
            print(f"DB read scenario table")
            df = self.dbm.get_scenarios_df()
            return df
        self.set_scenarios_table_read_callback(get_scenarios_df_cached_proc)

    def set_dash_callbacks(self):
        """Define Dash callbacks programatically.
        Note that the callback procedure can contain a reference to `self`, i.e. the current DoDashApp!
        """
        super().set_dash_callbacks()

        for main_page in self.main_pages:
            main_page.set_dash_callbacks()

        for vp in self.visualization_pages:
            vp.set_dash_callbacks()

        # Set any globally defined callbacks
        app = self.app

        @app.callback(
            Output("visualization_pages_collapse_menu", "is_open"),
            [Input("visualization_pages_collapse_button", "n_clicks")],
            [State("visualization_pages_collapse_menu", "is_open")],
            )
        def toggle_collapse(n, is_open):
            if n:
                return not is_open
            return is_open

        if self.enable_long_running_callbacks:
            app = self.app
            runner_config_dict = {config.runner_id: config for config in self.get_do_model_runner_configs()}
            @app.long_callback(
                output=Output('lrc_job_log_store', 'data'),
                inputs=(
                        Input('lrc_job_trigger_store', 'data'),
                ),
                progress=Output('lrc_job_queue_data_store', 'data'), # Global store
                progress_default=[],
                prevent_initial_call=True,
            )
            def run_model_long_callback(
                    set_progress,
                    n_clicks,
            ):
                print(f"n_clicks = {n_clicks}")
                trigger = n_clicks
                if trigger is None:
                    return "None"
                scenario_name = n_clicks['scenario_name']
                do_model_class_name = n_clicks['do_model_class_name']
                print(f"RunModelPage2.run_model_callback_LRC model = {do_model_class_name}")
                if do_model_class_name == 'None':
                    return "None"
                progress_dict = {'scenario': scenario_name, 'model': do_model_class_name, 'run_status': 'initializing'}
                set_progress([progress_dict])
                # time.sleep(1)

                progress_dict['run_status'] = 'running'
                set_progress([progress_dict])

                runner_class = runner_config_dict[do_model_class_name].runner_class
                runner = runner_class(scenario_name)
                runner.run()

                print("set_progress")
                progress_dict['run_status'] = 'done'
                set_progress([progress_dict])

                # time.sleep(4)

                log = f"Run {do_model_class_name} with scenario {scenario_name}\n" \
                      "Log: \n" \
                      f"{runner.log}"
                return log

    def get_do_model_runner_configs(self) -> List[DoModelRunnerConfig]:
        """Returns the model runners for the 'Run Model' page.
        Needs to be overridden.
        """
        configs = []
        return configs