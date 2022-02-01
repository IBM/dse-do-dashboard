# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
from typing import List
from dash import html
# from dse_do_dashboard.do_dash_app import DoDashApp
from dse_do_dashboard.main_pages.not_found import NotFoundPage
from dse_do_utils.plotlymanager import PlotlyManager


class VisualizationPage(ABC):
    """Abstract class

    Subclass should override/implement:
    * get_layout_children(self)
    """
    def __init__(self, dash_app, page_name:str='Default', page_id:str='default', url:str='default',
                 input_table_names: List[str] = [], output_table_names: List[str] = [],
                 enable_reference_scenario: bool = False,
                 enable_multi_scenario: bool = False):
        """
        Best practice to specify the minimal set of input and output tables.
        Loading less tables speeds of the response time of the dashboard.
        Shortcut to load all (input or output) tables: ['*']

        Args:
            dash_app (DoDashApp)
            page_name (str): Name of page in UI
            page_id (str): Internal unique ID
            url (str): url name
            input_table_names (List[str]): list of input table names required loading by the combined visualizations on this page. Or ['*'] for all input tables.
            output_table_names (List[str]): list of output table names required loading by the combined visualizations on this page. Or ['*'] for all output tables.
            enable_reference_scenario (bool): if True and if reference_scenario_name not None, will load the reference scenario and add a ref_dm dataManager to the PlotlyManager
            enable_multi_scenario (bool): if True and if there are more than 1 scenarios to compare in multi_scenario_names, will load multiple scenarios (including the currently selected) in ms_inputs and ms_outputs of the PlotlyManager
        TODO:
        * dash_app: DoDashApp. Due to circular imports, cannot specify type!
        """
        self.dash_app = dash_app
        self.page_name = page_name  # As shown in UI
        self.page_id = page_id  # Used for Dash pattern-matching callback
        self.url = url  # URL, i.e. web address: `host:port/visualization/url`

        self.input_table_names = input_table_names  # Names of input tables required for any of the plots in this page
        self.output_table_names = output_table_names  # Names of output tables required for any of the plots in this page
        self.enable_reference_scenario = enable_reference_scenario
        self.enable_multi_scenario = enable_multi_scenario
        # if len(input_table_names) == 1 and input_table_names[0] == '*':
        #     self.input_table_names = dash_app.get_input_table_names()
        # else:
        #     self.input_table_names = input_table_names  # Names of input tables required for any of the plots in this page

    def get_layout(self, scenario_name: str,
                   reference_scenario_name: str = None, multi_scenario_names: List[str] = None):
        """Returns layout of visualization page.
        TODO:
        * We are NOT using pattern-matching callback anynore, so the `id` of the Div is no long relevant
        * Do we need 2 Divs? (This is what worked so far)
        """
        layout = html.Div([
            html.Div(
                id={
                    'type': 'tab_layout',
                    'index': self.page_id
                },
                children=self.get_layout_children(self.get_plotly_manager(scenario_name,
                                                                          reference_scenario_name=reference_scenario_name,
                                                                          multi_scenario_names=multi_scenario_names,
                                                                          enable_reference_scenario=self.enable_reference_scenario,
                                                                          enable_multi_scenario=self.enable_multi_scenario))
            )
        ])
        return layout

    @abstractmethod
    def get_layout_children(self, pm: PlotlyManager) -> List:
        """Abstract method. To be overridden.
        Create a list of components that will be added as children of a Div.
        Use dbc.Row and dbc.Column to create a layout.
        Embed each Plotly figure in a dcc.Graph, within a dbc.Card.

        Args:
            pm (PlotlyManager): PlotlyManager subclass instantiated with the specified in- and output tables for this VisualizationPage

        Typical usage::

            def get_layout_children(self, pm: PlotlyManager):
                layout_children = [

                    dbc.Row(
                        dbc.Col(
                            dbc.Card([
                                dbc.CardBody(
                                    dcc.Graph(
                                        figure=pm.create_my_plotly_figure(),
                                    )
                                )
                            ])
                        )
                    ),
                ]
                return layout_children

        """
        layout = NotFoundPage().get_layout("Default Visualization Page. Need to override the `get_layout_children` method.")
        return layout

    def get_input_table_names(self) -> List[str]:
        """Return the specified table-names.
        Does the 'pattern-matching' based on the '*' option to include all tables.
        Can only be done dynamically (i.e. not in the constructor), because the self.dash_app.dbm might not have been initialized properly
        :return:
        """
        if len(self.input_table_names) == 1 and self.input_table_names[0] == '*':
            input_table_names = self.dash_app.get_input_table_names()
        else:
            input_table_names = self.input_table_names
        return input_table_names

    def get_output_table_names(self) -> List[str]:
        """Return the specified table-names.
        Does the 'pattern-matching' based on the '*' option to include all tables.
        :return:
        """
        if len(self.output_table_names) == 1 and self.output_table_names[0] == '*':
            output_table_names = self.dash_app.get_output_table_names()
        else:
            output_table_names = self.output_table_names
        return output_table_names

    def get_plotly_manager(self, scenario_name: str, reference_scenario_name: str = None, multi_scenario_names: List[str] = None,
                           enable_reference_scenario: bool = False,
                           enable_multi_scenario: bool = False):
        # reference_scenario_name = None
        # multi_scenario_names = None
        return self.dash_app.get_plotly_manager(scenario_name,
                                                self.get_input_table_names(),
                                                self.get_output_table_names(),
                                                reference_scenario_name=reference_scenario_name,
                                                multi_scenario_names=multi_scenario_names,
                                                enable_reference_scenario=enable_reference_scenario,
                                                enable_multi_scenario=enable_multi_scenario
                                                )

    def set_dash_callbacks(self):
        """Define Dash callbacks for this page.
        Will be called to register any callbacks.

        For the annotation `@app.callback`, get `app` from `app = self.dash_app.app`.

        :return:

        Usage::

            def set_dash_callbacks(self):
                app = self.dash_app.app

                @app.callback(Output('container_button_basic', 'children'),
                              [Input('run_model', 'n_clicks')])
                def run_model_callback(n_clicks):
                    return self.run_model_callback(n_clicks)

        """
        app = self.dash_app.app
        pass