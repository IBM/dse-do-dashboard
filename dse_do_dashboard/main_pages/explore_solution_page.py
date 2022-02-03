# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
from typing import Optional

from dash.exceptions import PreventUpdate

from dse_do_dashboard.main_pages.main_page import MainPage
from dash.dependencies import Input, Output
from dash import dcc, html
import dash_bootstrap_components as dbc

from dse_do_dashboard.utils.dash_common_utils import get_data_table_card_children, get_pivot_table_card_children


class ExploreSolutionPage(MainPage):
    def __init__(self, dash_app):
        super().__init__(dash_app,
                         page_name='Explore Solution',
                         page_id='explore-solution',
                         url='explore-solution',
                         )

    def get_layout(self):
        output_tables = self.dash_app.get_output_table_names()
        layout = html.Div([

            dbc.Card([
                dbc.CardHeader('Output Table', style= {'fullscreen': True}),
                dbc.CardBody(
                    dcc.Dropdown(id='output_table_drpdwn',
                                 options=[ {'label': i, 'value': i}
                                           for i in output_tables],
                                 value=(output_tables[0] if len(output_tables) > 0 else None),  # In case there are no output tables
                                 style = {'width': '75vw','height': '2vw'},
                                 ),
                ),
            ], style = {'width': '80vw'}),

            dbc.Card([
                # dbc.CardHeader('Input Table'),
                dbc.CardBody(id = 'output_data_table_card',style = {'width': '79vw'} ),
                html.Div(id="output_data_table_div")
            ], style = {'width': '80vw'}),

            dbc.Card([

                dbc.CardBody(id = 'output_pivot_table_card',style = {'width': '79vw'}),
                html.Div(id="output_pivot_table_div"),
            ], style = {'width': '80vw'})

        ])
        return layout


    def update_data_and_pivot_output_table_callback(self, scenario_name, table_name: Optional[str]):
        """Body for the Dash callback.

        :param table_name (str): name of selected table. Can be None if no tables.

        Usage::

            @app.callback([Output('output_data_table_card', 'children'),
               # Output('output_pivot_table_div', 'children'),
               Output('output_pivot_table_card', 'children'),
               ],
              [Input('top_menu_scenarios_drpdwn', 'value'),
               Input('output_table_drpdwn', 'value')])
            def update_data_and_pivot_output_table(scenario_name, table_name):
                data_table_children, pivot_table_children = DA.update_data_and_pivot_output_table_callback(scenario_name, table_name)
                return [data_table_children, pivot_table_children]

        """
        if table_name is None:
            # In case there are no output tables
            raise PreventUpdate
        output_table_names = [table_name]
        pm = self.dash_app.get_plotly_manager(scenario_name, [], output_table_names)
        dm = pm.dm
        df = dm.outputs[table_name]
        table_schema = self.dash_app.get_table_schema(table_name)
        pivot_table_config = self.dash_app.get_pivot_table_config(table_name)
        data_table_children = get_data_table_card_children(df, table_name, table_schema)
        pivot_table_children = get_pivot_table_card_children(df, scenario_name, table_name, pivot_table_config)
        return data_table_children, pivot_table_children


    def set_dash_callbacks(self):
        """Define Dash callbacks for this page

        Will be called to register any callbacks
        :return:
        """
        app = self.dash_app.app

        @app.callback([Output('output_data_table_card', 'children'),
                       Output('output_pivot_table_card', 'children'),
                       ],
                      [Input('top_menu_scenarios_drpdwn', 'value'),
                       Input('output_table_drpdwn', 'value')])
        def update_data_and_pivot_output_table(scenario_name, table_name):
            data_table_children, pivot_table_children = self.update_data_and_pivot_output_table_callback(scenario_name, table_name)
            return [data_table_children, pivot_table_children]