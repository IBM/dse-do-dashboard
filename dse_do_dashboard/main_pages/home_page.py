# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
from typing import List

from dse_do_dashboard.main_pages.main_page import MainPage
from dash import dcc, html, Output, Input, State
import dash_daq as daq
import dash_bootstrap_components as dbc


class HomePage(MainPage):
    def __init__(self, dash_app):
        super().__init__(dash_app,
                         page_name='Home',
                         page_id='home',
                         url='',
                         )

    def get_layout(self, scenario_name: str = None, reference_scenario_name: str = None, multi_scenario_names: List[str] = None):
        scenarios_df = self.dash_app.read_scenarios_table_from_db_cached().reset_index()  # SCDB2.get_scenarios_df().reset_index()
        layout = html.Div([

            dbc.Card([
                dbc.CardHeader(html.Div("Reference Scenario", style={'width': '28vw'})),
                dbc.CardBody([
                    # dbc.CardHeader(html.Div("Reference Scenario", style={'width': '28vw'})),
                    dcc.Dropdown(
                        id='reference_scenario',
                        options=[
                            {'label': i, 'value': i}
                            for i in scenarios_df.scenario_name
                        ],  style = {'width': '28vw'})
                ])
            ], style = {'width': '30vw'}),

            dbc.Card([
                dbc.CardBody(
                    # id='scenario_table_card',
                    [dbc.CardHeader(html.Div("Scenarios", style={'width': '80vw'})),
                     html.Div(id="scenario_table_div", style={'width': '78vw'})]
                ),
            ], style={'width': '80vw'}),

            dbc.Card([
                dbc.CardBody(
                    [
                        dbc.Button(
                            "Show 'Stop Server' Button",
                            id="collapse_stop_server_button",
                            className="mb-3",
                            color="primary",
                            n_clicks=0,
                        ),
                        dbc.Collapse(
                            dbc.Card(dbc.CardBody([
                                daq.StopButton(
                                    id='stop_server_button',
                                    label=f'Stop the Dash server. '
                                          f'Will release the port number {self.dash_app.port}.',
                                    n_clicks=0
                                ),
                                html.Div(id='stop_server_button_output')
                            ])),
                            id="collapse_stop_server_button_state",
                            is_open=False,
                        ),
                    ]
                ),
            ], style={'width': '80vw'}),

        ])
        return layout

    def set_dash_callbacks(self):
        app = self.dash_app.app

        @app.callback(
            Output("collapse_stop_server_button_state", "is_open"),
            [Input("collapse_stop_server_button", "n_clicks")],
            [State("collapse_stop_server_button_state", "is_open")],
        )
        def toggle_collapse(n, is_open):
            if n:
                return not is_open
            return is_open

        @app.callback(
            Output('stop_server_button_output', 'children'),
            Input('stop_server_button', 'n_clicks'),
            prevent_initial_call=True
        )
        def update_output(n_clicks):
            self.dash_app.shutdown()
            return 'The stop button has been clicked {} times.'.format(n_clicks)