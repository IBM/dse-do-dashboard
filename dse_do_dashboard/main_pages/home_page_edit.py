# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import ast
import base64
import io
import os
import pathlib
import tempfile
import zipfile

import flask
import pandas as pd
from dash.exceptions import PreventUpdate
import dash
from dse_do_utils import ScenarioManager

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
    - Download Scenario(s)
    - Upload Scenario(s)
    """
    def __init__(self, dash_app):
        super().__init__(dash_app,
                         page_name='Home',
                         page_id='home',
                         url='',
                         )

    def get_layout(self):
        scenarios_df = self.dash_app.read_scenarios_table_from_db_cached()  #.reset_index()  # SCDB2.get_scenarios_df().reset_index()

        layout = html.Div([

            dbc.Card([
                dbc.CardHeader(html.Div("Reference Scenario", style={'width': '28vw'})),
                dbc.CardBody([
                    # dbc.CardHeader(html.Div("Reference Scenario", style={'width': '28vw'})),
                    dcc.Dropdown(
                        id='reference_scenario_drpdwn',
                        options=[
                            {'label': i, 'value': i}
                            # for i in scenarios_df.reset_index().scenario_name
                            for i in scenarios_df.index
                        ],  style = {'width': '28vw'})
                ])
            ], #style = {'width': '30vw'}
            ),

            dbc.Card([
                dbc.CardHeader(html.Div("Reference Scenarios", style={'width': '28vw'})),
                dbc.CardBody([
                    # dbc.CardHeader(html.Div("Reference Scenario", style={'width': '28vw'})),
                    dcc.Checklist(
                        id='reference_scenarios_checklist',
                        options=[
                            {'label': i, 'value': i}
                            # for i in scenarios_df.reset_index().scenario_name
                            for i in scenarios_df.index
                        ],
                        value=[],
                        labelStyle={'display': 'block'},
                        # style={"overflow":"auto"}
                        # style = {'width': '28vw'}
                    )
                ])
            ], #style = {'width': '30vw'}
            ),

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
            ], # style={'width': '80vw'}
            ),

            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            html.P("Download all scenarios in a .zip archive. May take a long time."),
                            html.Hr(),
                            dbc.Button(
                                "Download all scenarios",
                                id="download_scenarios_button",
                                className="mb-3",
                                color="primary",
                                n_clicks=0,
                            ),
                            dcc.Download(id='download_scenarios_download'),
                        ],
                        title="Download All Scenarios",
                    ),

                    dbc.AccordionItem(
                        [
                            html.P("Select or drop one or more .xlsx or one .zip (with multiple .xlsx)"),
                            html.Hr(),
                            dcc.Upload(
                                id='upload_scenario', # 'upload-data',
                                children=html.Div([
                                    'Drag and Drop or ',
                                    html.A('Select Files')
                                ]),
                                style={
                                    'width': '100%',
                                    'height': '60px',
                                    'lineHeight': '60px',
                                    'borderWidth': '1px',
                                    'borderStyle': 'dashed',
                                    'borderRadius': '5px',
                                    'textAlign': 'center',
                                    'margin': '10px'
                                },
                                # Allow multiple files to be uploaded
                                multiple=True
                            ),
                            html.Div(id='output_data_upload'),
                        ],
                        title="Upload Scenarios",
                    ),

                    dbc.AccordionItem(
                        [
                            daq.StopButton(
                                id='stop_server_button',
                                label=f'Stop the Dash server. '
                                      f'Will release the port number {self.dash_app.port}.',
                                n_clicks=0
                            ),
                            html.Div(id='stop_server_button_output')
                        ],
                        title="Stop Server",
                    ),
                ],
                start_collapsed=True,
            ),

            # dbc.Card([
            #     dbc.CardBody(
            #         [
            #             dbc.Button(
            #                 "Show 'Stop Server' Button",
            #                 id="collapse_stop_server_button",
            #                 className="mb-3",
            #                 color="primary",
            #                 n_clicks=0,
            #             ),
            #             dbc.Collapse(
            #                 dbc.Card(dbc.CardBody([
            #                     # daq.StopButton(
            #                     #     id='stop_server_button',
            #                     #     label=f'Stop the Dash server. '
            #                     #           f'Will release the port number {self.dash_app.port}.',
            #                     #     n_clicks=0
            #                     # ),
            #                     html.Div(id='stop_server_button_output')
            #                 ])),
            #                 id="collapse_stop_server_button_state",
            #                 is_open=False,
            #             ),
            #         ]
            #     ),
            # ], style={'width': '80vw'}),

        ])
        return layout

    def get_scenario_operations_table(self, scenarios_df, ):
        """Create a layout which allows a user to select an operation on a scenario: duplicate, rename, delete"""
        layout = []
        # for scenario_name in scenarios_df.reset_index().scenario_name:
        for scenario_name in scenarios_df.index:
            layout.append(
                dbc.Card(dbc.Row([
                    dbc.Col(self.get_scenario_edit_dropdown(scenario_name, scenarios_df), width=1),
                    dbc.Col(scenario_name),])),
            )
        # layout.extend([
        #     dbc.Button(
        #         "Download all scenarios",
        #         id="download_scenarios_button",
        #         className="mb-3",
        #         color="primary",
        #         n_clicks=0,
        #     ),
        #     dcc.Download(id='download_scenarios_download'),
        # ]
        # )
            # break
        return layout

    def get_scenario_edit_dropdown(self, scenario_name, scenarios_df):
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
                        self.get_scenario_duplicate_modal_dialog(scenario_name, scenarios_df),
                        dbc.DropdownMenuItem(
                            "Download",
                            id = {'type':'download_scenario_mi', 'index': scenario_name},
                            n_clicks=0
                        ),
                        dcc.Download(id={'type':'download_scenario_download', 'index': scenario_name}),
                        # html.A(id={'type':'download_scenario_link', 'index': scenario_name},
                        #        children='Download File'
                        #        ),
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

    def get_scenario_duplicate_modal_dialog(self, scenario_name: str, scenarios_df=None):
        new_scenario_name = self.dash_app.dbm._find_free_duplicate_scenario_name(scenario_name, scenarios_df)
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

    def parse_scenario_upload_contents_callback(self, contents, filename, date):
        """Called for each uploaded scenario"""
        content_type, content_string = contents.split(',')
        print(f"Upload file. filename={filename}, content_type={content_type}")
        decoded = base64.b64decode(content_string)
        # root, file_extension = os.path.splitext(filename)
        file_extension = pathlib.Path(filename).suffix
        scenario_name = pathlib.Path(filename).stem

        print(f"scenario_name = {scenario_name}, extension = {file_extension}")
        try:
            if file_extension == '.xlsx':
                # pass
                # Assume that the user uploaded an excel file
                # df = pd.read_excel(io.BytesIO(decoded))
                xl = pd.ExcelFile(io.BytesIO(decoded))
                # Read data from Excel
                inputs, outputs = ScenarioManager.load_data_from_excel_s(xl)
                # s = f"inputs = {inputs.keys()}, outputs = {outputs.keys()}"
                # print(s)
                print("Input tables: {}".format(", ".join(inputs.keys())))
                print("Output tables: {}".format(", ".join(outputs.keys())))
                self.dash_app.dbm.replace_scenario_in_db(scenario_name=scenario_name, inputs=inputs, outputs=outputs)
                child = html.Div([
                    html.P(f"Uploaded scenario: '{scenario_name}' from '{filename}'"),
                    html.P(f"Input tables: {', '.join(inputs.keys())}"),
                    html.P(f"Output tables: {', '.join(outputs.keys())}"),
                ])
                return child
            elif file_extension == '.zip':
                zip_file = zipfile.ZipFile(io.BytesIO(decoded))
                # unzip_results = [html.P(f"Support for zip archives (of .xslx) is pending: {filename}")]
                unzip_results = []
                for info in zip_file.infolist():
                    scenario_name = pathlib.Path(info.filename).stem
                    file_extension = pathlib.Path(info.filename).suffix
                    if file_extension == '.xlsx':
                        print(f"file in zip : {info.filename}")
                        filecontents = zip_file.read(info)
                        xl = pd.ExcelFile(filecontents)
                        inputs, outputs = ScenarioManager.load_data_from_excel_s(xl)
                        print("Input tables: {}".format(", ".join(inputs.keys())))
                        print("Output tables: {}".format(", ".join(outputs.keys())))
                        self.dash_app.dbm.replace_scenario_in_db(scenario_name=scenario_name, inputs=inputs, outputs=outputs)  #
                        unzip_results.append(html.P(f"Uploaded scenario: '{scenario_name}' from '{info.filename}'"),)
                    else:
                        unzip_results.append(html.P(f"File: '{info.filename}' is not a .xlsx. Skipped."),)
                child = html.Div(unzip_results)
                return child
            else:
                return html.P(f"Unsupported file type: {filename}")
        except Exception as e:
            print(e)
            return html.Div([
                f'There was an error processing this file: {e}'
            ])

        return html.P(f"Uploaded scenario {filename}")

    def set_dash_callbacks(self):
        app = self.dash_app.app

        #############################################################################
        # Scenario operations callbacks
        #############################################################################
        @app.callback(Output('output_data_upload', 'children'),
                      Input('upload_scenario', 'contents'),
                      State('upload_scenario', 'filename'),
                      State('upload_scenario', 'last_modified'))
        def update_output(list_of_contents, list_of_names, list_of_dates):
            """Supports uploading a set of scenarios"""
            if list_of_contents is not None:
                children = [
                    # f"{n}, {d}" for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)
                    self.parse_scenario_upload_contents_callback(c, n, d) for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)
                ]
                return children


        @app.callback([
            Output('download_scenarios_button', 'n_clicks'),
            Output('download_scenarios_download', 'data'),
            ],
            Input('download_scenarios_button', 'n_clicks'),
            prevent_initial_call=True
        )
        def download_scenarios_callback(n_clicks):
            """Download all scenarios in a zip file.
            TODO: download selected set of scenarios
            """
            print("Download all scenarios")
            scenarios_df = self.dash_app.read_scenarios_table_from_db_cached()
            data = None
            with tempfile.TemporaryDirectory() as tmpdir:
                zip_filepath = os.path.join(tmpdir, 'scenarios.zip')
                with zipfile.ZipFile(zip_filepath, 'w') as zipMe:
                    for scenario_name in scenarios_df.index:
                        print(f"Download scenario {scenario_name}")
                        inputs, outputs = self.dash_app.dbm.read_scenario_from_db(scenario_name)
                        filename = f'{scenario_name}.xlsx'
                        filepath = os.path.join(tmpdir, filename)
                        with pd.ExcelWriter(filepath) as writer:
                            ScenarioManager.write_data_to_excel_s(writer, inputs=inputs, outputs=outputs)
                            writer.save()
                            zipMe.write(filepath, arcname=filename, compress_type=zipfile.ZIP_DEFLATED)
                data = dcc.send_file(zip_filepath)

            return 0, data

        @app.callback([
            Output({'type': 'download_scenario_mi', 'index': MATCH}, 'n_clicks'),
            Output({'type': 'download_scenario_download', 'index': MATCH}, 'data'),
            ],
            Input({'type': 'download_scenario_mi', 'index': MATCH}, 'n_clicks'),
            State({'type': 'download_scenario_mi', 'index': MATCH}, 'id'),
            prevent_initial_call=True
            )
        def download_scenario_callback(n_clicks, id):
            """We need the `n_clicks` as input. Only the `id` will not be triggered when a user selects the menu option.
            See https://community.plotly.com/t/excel-writer-to-dcc-download/54132/5 for use of tempfile.TemporaryDirectory()
            """
            scenario_name = id['index']
            print(f"Download scenario {scenario_name}")
            # df = pd.DataFrame({'dropdown_value': [1, 2, 3]})
            # relative_filename = os.path.join(
            #     'downloads',
            #     '{}-download.xlsx'.format(scenario_name)
            # )
            # absolute_filename = os.path.join(os.getcwd(), relative_filename)
            # writer = pd.ExcelWriter(absolute_filename)
            # df.to_excel(writer, 'Sheet1')
            # writer.save()
            # href = './{}'.format(relative_filename)

            multi_threaded = False  # Enabling multi-threading does NOT result in speedup. In fact for small scenarios it is slower!
            inputs, outputs = self.dash_app.dbm.read_scenario_from_db(scenario_name, multi_threaded)
            #TODO: inputs include a scenario table. Remove.

            data = None
            with tempfile.TemporaryDirectory() as tmpdir:
                filename = f'{scenario_name}.xlsx'
                filepath = os.path.join(tmpdir, filename)
                with pd.ExcelWriter(filepath) as writer:
                    ScenarioManager.write_data_to_excel_s(writer, inputs=inputs, outputs=outputs)
                    writer.save()
                    data = dcc.send_file(filepath)

            return 0, data

        # @app.server.route('/downloads/<path:path>')
        # def serve_static(path):
        #     root_dir = os.getcwd()
        #     return flask.send_from_directory(
        #         os.path.join(root_dir, 'downloads'), path
        #     )

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

        # @app.callback(
        #     Output({'type': 'duplicate_scenario_mi', 'index': MATCH}, 'n_clicks'),
        #     Input({'type': 'duplicate_scenario_mi', 'index': MATCH}, 'n_clicks'),
        #     State({'type': 'duplicate_scenario_mi', 'index': MATCH}, 'id'),
        #     prevent_initial_call=True
        # )
        # def duplicate_scenario_callback(n_clicks, id):
        #     """We need the `n_clicks` as input. Only the `id` will not be triggered when a user selects the menu option."""
        #     scenario_name = id['index']
        #     print(f"Duplicate scenario {scenario_name}")
        #     raise PreventUpdate
        #     return 0
        #
        # @app.callback(
        #     Output({'type': 'rename_scenario_mi', 'index': MATCH}, 'n_clicks'),
        #     Input({'type': 'rename_scenario_mi', 'index': MATCH}, 'n_clicks'),
        #     State({'type': 'rename_scenario_mi', 'index': MATCH}, 'id'),
        #     prevent_initial_call=True
        # )
        # def rename_scenario_callback(n_clicks, id):
        #     """We need the `n_clicks` as input. Only the `id` will not be triggered when a user selects the menu option."""
        #     scenario_name = id['index']
        #     print(f"Rename scenario {scenario_name}")
        #     raise PreventUpdate
        #     return 0
        #
        # @app.callback(
        #     Output({'type': 'delete_scenario_mi', 'index': MATCH}, 'n_clicks'),
        #     Input({'type': 'delete_scenario_mi', 'index': MATCH}, 'n_clicks'),
        #     State({'type': 'delete_scenario_mi', 'index': MATCH}, 'id'),
        #     prevent_initial_call=True
        # )
        # def delete_scenario_callback(n_clicks, id):
        #     """We need the `n_clicks` as input. Only the `id` will not be triggered when a user selects the menu option."""
        #     scenario_name = id['index']
        #     print(f"Delete scenario {scenario_name}")
        #     raise PreventUpdate
        #     return 0

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

        ##############################################################################
        #  Select Reference Scenarios
        ##############################################################################
        @app.callback(
            Output('reference_scenario_name_store', 'data'),
            Input('reference_scenario_drpdwn', 'value'),
        )
        def store_reference_scenario(reference_scenario_name):
            # print(f"Selected ref scenario = {reference_scenario_name}")
            return reference_scenario_name

        @app.callback(
            Output('multi_scenario_names_store', 'data'),
            Input('reference_scenarios_checklist', 'value'),
        )
        def store_multi_scenario_names(multi_scenario_names):
            # print(f"Multi scenario names = {multi_scenario_names}")
            return multi_scenario_names