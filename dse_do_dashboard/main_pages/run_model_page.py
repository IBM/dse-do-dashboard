# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import time
from typing import List

from dse_do_dashboard.main_pages.main_page import MainPage
from dash import dcc, html, Output, Input, State
import dash_bootstrap_components as dbc

# import diskcache
# from dash.long_callback import DiskcacheLongCallbackManager
# cache = diskcache.Cache("./cache")
# long_callback_manager = DiskcacheLongCallbackManager(cache)

class RunModelPage(MainPage):
    def __init__(self, dash_app):
        super().__init__(dash_app,
                         page_name='Run Model',
                         page_id='run-model',
                         url='run-model',
                         )

    def get_layout(self, scenario_name: str = None, reference_scenario_name: str = None, multi_scenario_names: List[str] = None):
        layout = html.Div([

            dbc.Button('Run Model', id='run_model', n_clicks=0, color="primary", className="me-1"),
            # html.Button('Run Model', id='run_model', n_clicks=0),

            html.Div(id='container_button_basic',
                     children='Enter a value and press submit'),

            # ddk.Block(
            #     width=30,
            #     children=ddk.ControlCard(
            #         width=100,
            #         children=[
            #             ddk.ControlItem(
            #                 # label='xxx',
            #                 children=dcc.Dropdown(
            #                     id='scenarios',
            #                     options=[
            #                         {'label': i, 'value': i}
            #                         for i in names
            #                     ],
            #                     # value=scenarios_df.scenarioName[0]
            #                 )
            #             ),
            #         ]
            #
            #     )
            # ),

        ])
        return layout

    # @app.callback(
    #         Output('container-button-basic', 'children'),
    #         [Input('run_model', 'n_clicks')])
    def run_model_callback(self, n_clicks, scenario_name):
        """Callback for pressing `run-model` button
        Usage:
        1. On index.py add::

            @app.callback(
                    Output('container-button-basic', 'children'),
                    [Input('run_model', 'n_clicks')])
            def run_model_callback(self, n_clicks):
                DA.run_model_callback(n_clicks)

        2. On DashApp add method

            def run_model_callback(self, n_clicks):
                self.get_run_model_page().run_model_callback(n_clicks)
        """
        # self.dash_app.tmp_run_notebook(scenario_name)  # HACK!!!!!!!
        return f"The button has been clicked {n_clicks} times for {scenario_name}"

    def set_dash_callbacks(self):
        """Define Dash callbacks for this page

        Will be called to register any callbacks
        :return:
        """
        app = self.dash_app.app

        @app.callback(Output('container_button_basic', 'children'),
                      [Input('run_model', 'n_clicks')],
                      State('top_menu_scenarios_drpdwn', 'value'),
                      manager=self.dash_app.long_callback_manager,
                      prevent_initial_call=True
        )
        def run_model_callback(n_clicks, scenario_name):
            # time.sleep(2.0)
            return self.run_model_callback(n_clicks, scenario_name)

