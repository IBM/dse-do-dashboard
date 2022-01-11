# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import pandas as pd
from dash.exceptions import PreventUpdate

from dse_do_dashboard.main_pages.main_page import MainPage
from dash.dependencies import Input, Output, State
from dash import dcc, html
import dash_bootstrap_components as dbc
import pprint

from dse_do_dashboard.utils.dash_common_utils import get_data_table_card_children, get_pivot_table_card_children


class PrepareDataPage(MainPage):
    def __init__(self, dash_app,
                 page_name: str = 'Prepare Data',
                 page_id: str = 'prepare-data',
                 url: str = 'prepare-data'):
        super().__init__(dash_app,
                         page_name=page_name,
                         page_id=page_id,
                         url=url,
                         )

    def get_layout(self):
        # input_tables = self.dash_app.get_input_table_names()
        layout = html.Div([
            self.get_input_table_selection_card(),
            # dbc.Card([
            #     dbc.CardHeader('Input Table', style= {'fullscreen':True}),
            #     dbc.CardBody(
            #         dcc.Dropdown(id='input_table_drpdwn',
            #                      options=[ {'label': i, 'value': i}
            #                                for i in input_tables],
            #                      value=input_tables[0],
            #                      style = {'width': '75vw','height':'2vw'},
            #                      ),
            #     ),
            # ], style = {'width': '80vw'}),

            dbc.Card([
                # dbc.CardHeader('Input Table'),
                dbc.CardBody(id='input_data_table_card', style={'width': '79vw'} ),
                html.Div(id="input_data_table_div"),
            ], style={'width': '80vw'}),

            # dbc.Card([
            #
            #     dbc.CardBody(id = 'input_pivot_table_card',style = {'width': '79vw'}),
            #     html.Div(id="input_pivot_table_div"),
            # ], style = {'width': '80vw'})
            self.get_pivot_table_card(),

        ])
        return layout

    def get_input_table_selection_card(self):
        input_tables = self.dash_app.get_input_table_names()
        card = dbc.Card([
            dbc.CardHeader('Input Table', style={'fullscreen': True}),
            dbc.CardBody(
                dcc.Dropdown(id='input_table_drpdwn',
                             options=[ {'label': i, 'value': i}
                                       for i in input_tables],
                             value=input_tables[0],
                             style = {'width': '75vw', 'height': '2vw'},
                             ),
            ),
        ], style={'width': '80vw'})
        return card

    def get_pivot_table_card(self):
        card = dbc.Card([
            dbc.CardBody(id='input_pivot_table_card', style={'width': '79vw'}),
            html.Div(id="input_pivot_table_div"),
        ], style={'width': '80vw'})
        return card


    def update_data_and_pivot_input_table_callback(self, scenario_name, table_name):
        """Body for the Dash callback.

        Usage::

            @app.callback([Output('input_data_table_card', 'children'),
            Output('input_pivot_table_card', 'children')],
            [Input('top_menu_scenarios_drpdwn', 'value'),
            Input('input_table_drpdwn', 'value')])
            def update_data_and_pivot_input_table(scenario_name, table_name):
                data_table_children, pivot_table_children = DA.update_data_and_pivot_input_table_callback(scenario_name, table_name)
                return [data_table_children, pivot_table_children]

        """
        # print(f"update_data_and_pivot_input_table for {table_name} in {scenario_name}")
        input_table_names = [table_name]
        pm = self.dash_app.get_plotly_manager(scenario_name, input_table_names, [])
        dm = pm.dm
        df = self.dash_app.get_table_by_name(dm=dm, table_name=table_name, index=False, expand=False)
        table_schema = self.dash_app.get_table_schema(table_name)
        pivot_table_config = self.dash_app.get_pivot_table_config(table_name)
        data_table_children = get_data_table_card_children(df, table_name, table_schema, editable=True)
        pivot_table_children = get_pivot_table_card_children(df, scenario_name, table_name, pivot_table_config)
        return data_table_children, pivot_table_children


    def set_dash_callbacks(self):
        """Define Dash callbacks for this page

        Will be called to register any callbacks
        :return:
        """
        app = self.dash_app.app

        @app.callback([Output('input_data_table_card', 'children'),
                       Output('input_pivot_table_card', 'children')],
                      [Input('top_menu_scenarios_drpdwn', 'value'),
                       Input('input_table_drpdwn', 'value')])
        def update_data_and_pivot_input_table(scenario_name:str, table_name:str):
            data_table_children, pivot_table_children = self.update_data_and_pivot_input_table_callback(scenario_name, table_name)
            return [data_table_children, pivot_table_children]

