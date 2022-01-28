# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import time

from dse_do_dashboard.main_pages.main_page import MainPage
from dash import dcc, html, Output, Input
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

    def get_layout(self):
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
    def run_model_callback(self, n_clicks):
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
        return f"The button has been clicked {n_clicks} times"

    def set_dash_callbacks(self):
        """Define Dash callbacks for this page

        Will be called to register any callbacks
        :return:
        """
        app = self.dash_app.app

        @app.callback(Output('container_button_basic', 'children'),
                      [Input('run_model', 'n_clicks')],
                      manager=self.dash_app.long_callback_manager,
        )
        def run_model_callback(n_clicks):
            time.sleep(2.0)
            return self.run_model_callback(n_clicks)

