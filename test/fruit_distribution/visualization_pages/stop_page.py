# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import List

from plotly.graph_objs import Figure
from dash import html, dcc, Output, Input, State
import dash_daq as daq
import dash_bootstrap_components as dbc
from dse_do_dashboard.do_dash_app import DoDashApp
from dse_do_dashboard.visualization_pages.plotly_1_column_visualization_page import Plotly1ColumnVisualizationPage
from dse_do_utils.plotlymanager import PlotlyManager
from dse_do_dashboard.visualization_pages.visualization_page import VisualizationPage


class StopPage(VisualizationPage):
    def __init__(self, dash_app: DoDashApp):
        super().__init__(dash_app=dash_app,
                         page_name='Stop',
                         page_id='stop_tab',
                         url='stop',
                         input_table_names=[],
                         # input_table_names=['*'],
                         output_table_names=[],
                         )

    def get_layout_children(self, pm: PlotlyManager) -> List:
        layout_children = [
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
                id="collapse",
                is_open=False,
            ),
        ]
        return layout_children

    def set_dash_callbacks(self):
        app = self.dash_app.app

        # @app.callback(
        #     Output("collapse", "is_open"),
        #     [Input("collapse_stop_server_button", "n_clicks")],
        #     [State("collapse", "is_open")],
        # )
        # def toggle_collapse(n, is_open):
        #     if n:
        #         return not is_open
        #     return is_open
        #
        # @app.callback(
        #     Output('stop_server_button_output', 'children'),
        #     Input('stop_server_button', 'n_clicks'),
        #     prevent_initial_call=True
        # )
        # def update_output(n_clicks):
        #     self.dash_app.shutdown()
        #     return 'The stop button has been clicked {} times.'.format(n_clicks)


