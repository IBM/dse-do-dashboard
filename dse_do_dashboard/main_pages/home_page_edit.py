# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import ast

from dash.exceptions import PreventUpdate
import dash

from dse_do_dashboard.main_pages.main_page import MainPage
from dash import dcc, html, Output, Input, State, ALL, MATCH
import dash_daq as daq
import dash_bootstrap_components as dbc


class HomePageEdit(MainPage):
    """
    Includes:
    - Duplicate Scenario
    - Rename Scenario
    - Delete Scenario
    """
    def __init__(self, dash_app):
        super().__init__(dash_app,
                         page_name='Home',
                         page_id='home',
                         url='',
                         )

    def get_layout(self):
        scenarios_df = self.dash_app.read_scenarios_table_from_db_cached().reset_index()  # SCDB2.get_scenarios_df().reset_index()

        # rename_scenario_modal = html.Div(
        #     [
        #         dbc.Button("Rename Scenario", id="open"),
        #         # dbc.Modal(
        #         #     [
        #         #         dbc.ModalHeader("Rename Scenario"),
        #         #         dbc.ModalBody("BODY OF MODAL"),
        #         #         dbc.ModalFooter([
        #         #             dbc.Button("Rename", id="rename", className="ml-auto"),
        #         #             # dbc.Button("Cancel", id="cancel", className="ml-auto")
        #         #             dbc.Button("Close", id="close", className="ml-auto"),
        #         #         ]),
        #         #     ],
        #         #     id="modal",
        #         # ),
        #     ]
        # )

        layout = html.Div([
            # rename_scenario_modal,

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
                dbc.CardHeader(html.Div("Scenarios", style={'width': '80vw'})),
                dbc.CardBody(
                    # id='scenario_table_card',
                    [
                     # html.Div(id="scenario_table_div", style={'width': '78vw'},
                     #          ),
                     html.Div(children=self.get_scenario_operations_table(scenarios_df)),
                     ]
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

    def get_scenario_operations_table(self, scenarios_df):
        """Create a layout which allows a user to select an operation on a scenario: duplicate, rename, delete"""
        layout = []
        for scenario_name in scenarios_df.scenario_name:
            layout.append(
                dbc.Card(dbc.Row([
                    dbc.Col(self.get_scenario_edit_dropdown(scenario_name), width=1),
                    dbc.Col(scenario_name),])),
            )
            # break
        return layout

    def get_scenario_edit_dropdown(self, scenario_name):
        dropdown = html.Div(
            [
                dbc.DropdownMenu(
                    [
                        dbc.DropdownMenuItem(
                            "Duplicate",
                            id = {'type':'duplicate_scenario_mi', 'index': scenario_name},
                            n_clicks=0,
                        ),
                        self.get_scenario_rename_modal_dialog(scenario_name),
                        dbc.DropdownMenuItem(
                            "Rename",
                            id = {'type':'rename_scenario_mi', 'index': scenario_name},
                            n_clicks=0
                        ),
                        self.get_scenario_duplicate_modal_dialog(scenario_name),
                        dbc.DropdownMenuItem(divider=True),
                        dbc.DropdownMenuItem(
                            "Delete",
                            id = {'type':'delete_scenario_mi', 'index': scenario_name},
                            n_clicks=0
                        ),
                        self.get_scenario_delete_modal_dialog(scenario_name),
                    ],
                    label="...",
                    size="sm",
                ),
                # html.P(id="item_clicks", className="mt-3"),
            ]
        )
        return dropdown

    def get_scenario_rename_modal_dialog(self, scenario_name: str):
        modal = dbc.Modal(
                    [
                        dbc.ModalHeader("Rename Scenario"),
                        dbc.ModalBody(f"New scenario name for '{scenario_name}'"),
                        dbc.Input(
                            id = {'type':'rename_scenario_modal_input', 'index': scenario_name},
                            value=scenario_name, type="text"),
                        dbc.ModalFooter([
                            dbc.Button("Cancel",
                                       id = {'type':'rename_scenario_modal_cancel', 'index': scenario_name},
                                       className="ml-auto"),
                            dbc.Button("Rename",
                                       id = {'type':'rename_scenario_modal_rename', 'index': scenario_name},
                                       className="ml-auto"),
                        ]),
                    ],
                    id = {'type':'rename_scenario_modal', 'index': scenario_name},
                )
        return modal

    def get_scenario_duplicate_modal_dialog(self, scenario_name: str):
        new_scenario_name = self.dash_app.dbm._find_free_duplicate_scenario_name(scenario_name)
        modal = dbc.Modal(
            [
                dbc.ModalHeader("Duplicate Scenario"),
                dbc.ModalBody(f"Name for the duplicate of the scenario '{scenario_name}':"),
                dbc.Input(
                    id = {'type':'duplicate_scenario_modal_input', 'index': scenario_name},
                    value=new_scenario_name, type="text"),
                dbc.ModalFooter([
                    dbc.Button("Cancel",
                               id = {'type':'duplicate_scenario_modal_cancel', 'index': scenario_name},
                               className="ml-auto"),
                    dbc.Button("Duplicate",
                               id = {'type':'duplicate_scenario_modal_rename', 'index': scenario_name},
                               className="ml-auto"),
                ]),
            ],
            id = {'type':'duplicate_scenario_modal', 'index': scenario_name},
        )
        return modal

    def get_scenario_delete_modal_dialog(self, scenario_name: str):
        modal = dbc.Modal(
            [
                dbc.ModalHeader("Delete Scenario"),
                dbc.ModalBody(f"Delete the scenario '{scenario_name}':"),
                dbc.ModalFooter([
                    dbc.Button("Cancel",
                               id = {'type':'delete_scenario_modal_cancel', 'index': scenario_name},
                               className="ml-auto"),
                    dbc.Button("Delete",
                               id = {'type':'delete_scenario_modal_rename', 'index': scenario_name},
                               className="ml-auto"),
                ]),
            ],
            id = {'type':'delete_scenario_modal', 'index': scenario_name},
        )
        return modal

    def set_dash_callbacks(self):
        app = self.dash_app.app

        #############################################################################
        # Scenario operations callbacks
        #############################################################################
        @app.callback(
            Output({'type': 'delete_scenario_modal', 'index': MATCH}, "is_open"),
            [
                Input({'type': 'delete_scenario_mi', 'index': MATCH}, 'n_clicks'),
                Input({'type': 'delete_scenario_modal_cancel', 'index': MATCH}, "n_clicks"),
                Input({'type': 'delete_scenario_modal_rename', 'index': MATCH}, "n_clicks"),
            ],
            [State({'type': 'delete_scenario_modal', 'index': MATCH}, "is_open"),
             # State({'type': 'delete_scenario_modal_input', 'index': MATCH}, "value")
             ],
        )
        def toggle_delete_modal(n1, n2, n3, is_open):
            """

            """
            ctx = dash.callback_context
            if not ctx.triggered:
                raise PreventUpdate

            if n1 or n2 or n3:
                # print(f"Rename modal: {new_scenario_name}")
                # print(f"ctx.triggered[0] = {ctx.triggered[0]}")
                triggered_component_id_str = ctx.triggered[0]['prop_id'].split('.')[0]  # This returns a STRING representation of the pattern-matching id
                # print(f"Rename context id = {triggered_component_id}")
                triggered_component_id_dict = ast.literal_eval(triggered_component_id_str)  # Convert the string to a Dict to get the type.
                ctx_type = triggered_component_id_dict['type']
                current_scenario_name = triggered_component_id_dict['index']
                # print(f"Rename context type = {ctx_type}")

                if ctx_type == 'delete_scenario_modal_rename':
                    print(f"Deleting scenario from {current_scenario_name}")
                    self.dash_app.dbm.delete_scenario_from_db(current_scenario_name)

                return not is_open
            return is_open

        @app.callback(
            Output({'type': 'duplicate_scenario_modal', 'index': MATCH}, "is_open"),
            [
                Input({'type': 'duplicate_scenario_mi', 'index': MATCH}, 'n_clicks'),
                Input({'type': 'duplicate_scenario_modal_cancel', 'index': MATCH}, "n_clicks"),
                Input({'type': 'duplicate_scenario_modal_rename', 'index': MATCH}, "n_clicks"),
            ],
            [State({'type': 'duplicate_scenario_modal', 'index': MATCH}, "is_open"),
             State({'type': 'duplicate_scenario_modal_input', 'index': MATCH}, "value")
             ],
        )
        def toggle_duplicate_modal(n1, n2, n3, is_open, new_scenario_name):
            """
            TODO: replace by a duplicate + delete
            """
            ctx = dash.callback_context
            if not ctx.triggered:
                raise PreventUpdate

            if n1 or n2 or n3:
                # print(f"Rename modal: {new_scenario_name}")
                # print(f"ctx.triggered[0] = {ctx.triggered[0]}")
                triggered_component_id_str = ctx.triggered[0]['prop_id'].split('.')[0]  # This returns a STRING representation of the pattern-matching id
                # print(f"Rename context id = {triggered_component_id}")
                triggered_component_id_dict = ast.literal_eval(triggered_component_id_str)  # Convert the string to a Dict to get the type.
                ctx_type = triggered_component_id_dict['type']
                current_scenario_name = triggered_component_id_dict['index']
                # print(f"Rename context type = {ctx_type}")

                if ctx_type == 'duplicate_scenario_modal_rename':
                    if new_scenario_name != current_scenario_name:
                        print(f"Duplicating scenario from {current_scenario_name} to {new_scenario_name}")
                        self.dash_app.dbm.duplicate_scenario_in_db(current_scenario_name, new_scenario_name)

                return not is_open
            return is_open

        @app.callback(
            Output({'type': 'rename_scenario_modal', 'index': MATCH}, "is_open"),
            [
             Input({'type': 'rename_scenario_mi', 'index': MATCH}, 'n_clicks'),
             Input({'type': 'rename_scenario_modal_cancel', 'index': MATCH}, "n_clicks"),
             Input({'type': 'rename_scenario_modal_rename', 'index': MATCH}, "n_clicks"),
             ],
            [State({'type': 'rename_scenario_modal', 'index': MATCH}, "is_open"),
             State({'type': 'rename_scenario_modal_input', 'index': MATCH}, "value")
             ],
                )
        def toggle_rename_modal(n1, n2, n3, is_open, new_scenario_name):
            """
            TODO: trigger reload of scenario table and update of UI
            If `rename_scenario_modal_rename` then do the rename
            """
            ctx = dash.callback_context
            if not ctx.triggered:
                raise PreventUpdate

            if n1 or n2 or n3:
                # print(f"Rename modal: {new_scenario_name}")
                # print(f"ctx.triggered[0] = {ctx.triggered[0]}")
                triggered_component_id_str = ctx.triggered[0]['prop_id'].split('.')[0]  # This returns a STRING representation of the pattern-matching id
                # print(f"Rename context id = {triggered_component_id}")
                triggered_component_id_dict = ast.literal_eval(triggered_component_id_str)  # Convert the string to a Dict to get the type.
                ctx_type = triggered_component_id_dict['type']
                current_scenario_name = triggered_component_id_dict['index']
                # print(f"Rename context type = {ctx_type}")

                if ctx_type == 'rename_scenario_modal_rename':
                    if new_scenario_name != current_scenario_name:
                        print(f"Renaming scenario from {current_scenario_name} to {new_scenario_name}")
                        self.dash_app.dbm.rename_scenario_in_db(current_scenario_name, new_scenario_name)

                return not is_open
            return is_open

        @app.callback(
            Output({'type': 'duplicate_scenario_mi', 'index': MATCH}, 'n_clicks'),
            Input({'type': 'duplicate_scenario_mi', 'index': MATCH}, 'n_clicks'),
            State({'type': 'duplicate_scenario_mi', 'index': MATCH}, 'id'),
            prevent_initial_call=True
        )
        def duplicate_scenario_callback(n_clicks, id):
            """We need the `n_clicks` as input. Only the `id` will not be triggered when a user selects the menu option."""
            scenario_name = id['index']
            print(f"Duplicate scenario {scenario_name}")
            raise PreventUpdate
            return 0

        @app.callback(
            Output({'type': 'rename_scenario_mi', 'index': MATCH}, 'n_clicks'),
            Input({'type': 'rename_scenario_mi', 'index': MATCH}, 'n_clicks'),
            State({'type': 'rename_scenario_mi', 'index': MATCH}, 'id'),
            prevent_initial_call=True
        )
        def rename_scenario_callback(n_clicks, id):
            """We need the `n_clicks` as input. Only the `id` will not be triggered when a user selects the menu option."""
            scenario_name = id['index']
            print(f"Rename scenario {scenario_name}")
            raise PreventUpdate
            return 0

        @app.callback(
            Output({'type': 'delete_scenario_mi', 'index': MATCH}, 'n_clicks'),
            Input({'type': 'delete_scenario_mi', 'index': MATCH}, 'n_clicks'),
            State({'type': 'delete_scenario_mi', 'index': MATCH}, 'id'),
            prevent_initial_call=True
        )
        def delete_scenario_callback(n_clicks, id):
            """We need the `n_clicks` as input. Only the `id` will not be triggered when a user selects the menu option."""
            scenario_name = id['index']
            print(f"Delete scenario {scenario_name}")
            raise PreventUpdate
            return 0

        #############################################################################
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