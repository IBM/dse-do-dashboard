# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import List

import pandas as pd
import dash
from dash.exceptions import PreventUpdate

from dse_do_dashboard.main_pages.main_page import MainPage
from dash.dependencies import Input, Output, State
from dash import dcc, html
import dash_bootstrap_components as dbc
import pprint

from dse_do_dashboard.main_pages.prepare_data_page import PrepareDataPage
from dse_do_dashboard.utils.dash_common_utils import get_data_table_card_children, get_pivot_table_card_children, \
    diff_dashtable_mi, ScenarioTableSchema
from dse_do_dashboard.utils.scenariodbmanager_update import DbCellUpdate


class PrepareDataPageEdit(PrepareDataPage):
    """Use instead of `PrepareDataPage`.
    Do not combine in same app: will cause duplicate callbacks."""
    def __init__(self, dash_app):
        self.data_table_id = 'input_data_table'
        super().__init__(dash_app,
                         page_name='Prepare Data(*)',
                         page_id='prepare-data',
                         url='prepare-data',
                         )

    def get_layout(self):
        input_tables = self.dash_app.get_input_table_names()
        layout = html.Div([
            dcc.Store(id="current_table_name"),

            self.get_input_table_selection_card(),

            dbc.Card([
                # dbc.CardHeader('Input Table'),
                dbc.CardBody(id='input_data_table_card', style={'width': '79vw'},
                             children=get_data_table_card_children(df=pd.DataFrame(), table_name='None', data_table_id=self.data_table_id)  # We need to initialize a DataTable, otherwise issues with registering callbacks
                             ),

                html.Button("No table updates", id="commit_changes_button", disabled=True),
                html.Div(id="input_data_table_div"),
                dcc.Store(id="my_data_table_diff_store"), # Stores all changes
                html.Div(id="my_data_table_data_diff"),  # Show the difference
                html.Div(id="my_data_table_output")
            ], style = {'width': '80vw'}),

            self.get_pivot_table_card(),
        ])
        return layout

    def get_db_cell_updates(self, diff_store_data, ) -> List[DbCellUpdate]:
        """Get the changes in the diff store as DbCellUpdate.
        Note: from Python 3.7, a Dict maintains the order in which items are added. So no need to sort by time.
        TODO: can we store the NamedTuple `DbCellUpdate` directly in the store? Saves us from converting from Dict.
        """
        db_cell_updates: List[DbCellUpdate] = []
        for ts, diffs in diff_store_data.items():  # Potentially multiple changes in the value
            for diff in diffs:
                db_cell_update = DbCellUpdate(
                    scenario_name=diff['scenario_name'],
                    table_name=diff['table_name'],
                    row_index=diff['row_index'],  # e.g. [{'column': 'col1', 'value': 1}, {'column': 'col2', 'value': 'pear'}]
                    column_name=diff['column_name'],
                    current_value=diff['current_value'],
                    previous_value=diff['previous_value'],
                    row_idx=diff['row_idx'],
                )
                db_cell_updates.append(db_cell_update)
        return db_cell_updates

    def capture_diffs_callback(self, ts, data, data_previous, diff_store_data, table_name: str, scenario_name: str):
        """Capture diffs and store in my_data_table_diff_store."""
        if ts is None:
            raise PreventUpdate
        diff_store_data = diff_store_data or {}
        index_columns = None
        table_schema: ScenarioTableSchema = self.dash_app.get_table_schema(table_name)
        if table_schema is not None:
            index_columns = table_schema.index_columns
        diff_store_data[ts] = diff_dashtable_mi(data, data_previous, index_columns=index_columns, table_name=table_name, scenario_name=scenario_name)
        return diff_store_data

    def commit_changes_to_db_callback(self, n_clicks, diff_store_data):
        if n_clicks is None:
            raise PreventUpdate
        if diff_store_data is None:
            raise PreventUpdate
        if diff_store_data:
            dt_changes = []
            for ts, v in diff_store_data.items():
                dt_changes.append(f"* {v} {ts}")
            # for v in diff_store_data.values():
            #     dt_changes.append(f"* {v}")
            output = [dcc.Markdown(change) for change in dt_changes]
        else:
            output = "No Changes to DataTable"

        db_cell_updates = self.get_db_cell_updates(diff_store_data)
        self.dash_app.dbm.update_cell_changes_in_db(db_cell_updates)

        return output

    def set_dash_callbacks(self):
        """Define Dash callbacks for this page

        Will be called to register any callbacks
        :return:
        """
        super().set_dash_callbacks()
        app = self.dash_app.app

        @app.callback([Output('commit_changes_button', 'style'),
                       Output('commit_changes_button', 'children')
                       ],
                      Input("my_data_table_diff_store", "data"))
        def change_button_style(data):
            if data is None:
                raise PreventUpdate

            white_button_style = {'background-color': 'white',
                                  'color': 'black',
                                  # 'height': '50px',
                                  # 'width': '100px',
                                  # 'margin-top': '50px',
                                  # 'margin-left': '50px'
                                  }

            red_button_style = {'background-color': 'red',
                                'color': 'white',
                                # 'height': '50px',
                                # 'width': '100px',
                                # 'margin-top': '50px',
                                # 'margin-left': '50px'
                                }

            if len(data) > 0:
                return red_button_style, f"Commit {len(data)} changes to DB"
            else:
                return white_button_style, "No changes to commit"

        @app.callback(
            [
             Output("my_data_table_diff_store", "data"),
             Output('commit_changes_button', 'disabled')],
            [Input(self.data_table_id, "data_timestamp"),
             Input("commit_changes_button", "n_clicks")],
            [
                State(self.data_table_id, "data"),
                State(self.data_table_id, "data_previous"),
                State("my_data_table_diff_store", "data"),
                State("input_table_drpdwn", "value"),
                State('top_menu_scenarios_drpdwn', 'value'),
            ],
        )
        def capture_and_commit_edits(ts, n_clicks, data, data_previous, diff_store_data, table_name: str, scenario_name: str):
            """Combined callback for either editing cells in the DataTable, or pressing the commit button.
            Editing a cell detects and stores changes in the diff store.
            The commit button performs updates in the DB and clears the diff store.
            """
            ctx = dash.callback_context
            if not ctx.triggered:
                raise PreventUpdate
            triggered_component_id = ctx.triggered[0]['prop_id'].split('.')[0]

            if triggered_component_id == self.data_table_id:
                # print("Triggered by a table edit")
                diff_store_data = self.capture_diffs_callback(ts,data, data_previous, diff_store_data, table_name, scenario_name)
                commit_button_disabled = False
            elif triggered_component_id == 'commit_changes_button':
                # print("Triggered by commit button")
                output = self.commit_changes_to_db_callback(n_clicks, diff_store_data)
                diff_store_data = {}  # Clear diff store
                commit_button_disabled = True
            else:
                print(f"Triggered by unknown component {triggered_component_id}")
                raise PreventUpdate

            return diff_store_data, commit_button_disabled


        # @app.callback(
        #     [Output("my_data_table_diff_store", "data"),
        #      Output('commit_changes_button', 'disabled')],
        #     [Input("my_data_table", "data_timestamp")],
        #     [
        #         State("my_data_table", "data"),
        #         State("my_data_table", "data_previous"),
        #         State("my_data_table_diff_store", "data"),
        #         State("input_table_drpdwn", "value"),
        #         State('top_menu_scenarios_drpdwn', 'value'),
        #     ],
        # )
        # def capture_diffs(ts, data, data_previous, diff_store_data, table_name: str, scenario_name: str):
        #     """Capture diffs and store in my_data_table_diff_store."""
        #     if ts is None:
        #         raise PreventUpdate
        #     diff_store_data = diff_store_data or {}
        #     index_columns = None
        #     table_schema: ScenarioTableSchema = self.dash_app.get_table_schema(table_name)
        #     if table_schema is not None:
        #         index_columns = table_schema.index_columns
        #     diff_store_data[ts] = diff_dashtable_mi(data, data_previous, index_columns=index_columns, table_name=table_name, scenario_name=scenario_name)
        #     return diff_store_data, False

        # @app.callback(
        #     Output("my_data_table_data_diff", "children"),
        #     # Output("my_data_table_diff_store", "data"),
        #     [Input("commit_changes_button", "n_clicks")],
        #     [State("my_data_table_diff_store", "data")],
        # )
        # def update_output(n_clicks, diff_store_data):
        #     if n_clicks is None:
        #         raise PreventUpdate
        #     if diff_store_data is None:
        #         raise PreventUpdate
        #     if diff_store_data:
        #         dt_changes = []
        #         for ts, v in diff_store_data.items():
        #             dt_changes.append(f"* {v} {ts}")
        #         # for v in diff_store_data.values():
        #         #     dt_changes.append(f"* {v}")
        #         output = [dcc.Markdown(change) for change in dt_changes]
        #     else:
        #         output = "No Changes to DataTable"
        #
        #     db_cell_updates = self.get_db_cell_updates(diff_store_data)
        #     self.dash_app.dbm.update_cell_changes_in_db(db_cell_updates)
        #
        #     diff_store_data = {}
        #
        #     return output #, diff_store_data

###########################################################################
# Test to use the dcc.Location to stor the table name as a html variable
# Disadvantage/problem is that a change to the url causes a page-reload
###########################################################################
        # @app.callback(Output("my_data_table_data_diff", "children"),
        #               Input('url', 'search'))
        # def test_url_vars(search):
        #     print(f"test_url_vars = {search}")
        #     return "Test"
        #
        # @app.callback(Output('url', 'search'),
        #               Input('input_table_drpdwn', 'value'),
        #               prevent_initial_call=True)
        # def test_url_vars_output(table_name):
        #     return f"?table={table_name}"

##################################################################################
# Test using a dcc.Store to store the table_name, so switching scenarios keeps the same table
# Not straightforward: the callback update_data_and_pivot_input_table would have to do a context test to see which input triggered the callback
# Also, not sure the store gets retained when switching scenarios
# (surprisingly, that DOES seem to be the case for the diff-store!)
##################################################################################
        # @app.callback(Output('current_table_name', 'data'),
        #               Input('input_table_drpdwn', 'value'))
        # def store_table_name(table_name):
        #     return table_name
        #
        # @app.callback(Output("my_data_table_data_diff", "children"),
        #               Input('current_table_name', 'data'))
        # def test_table_name(data):
        #     return data
