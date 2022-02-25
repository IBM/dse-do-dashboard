# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import List, Optional, Dict

import pandas as pd
import dash
from dash.exceptions import PreventUpdate

from dse_do_dashboard.main_pages.main_page import MainPage
from dash.dependencies import Input, Output, State
from dash import dcc, html
import dash_bootstrap_components as dbc
import pprint
from dash import dash_table

from dse_do_dashboard.main_pages.prepare_data_page import PrepareDataPage
from dse_do_dashboard.utils.dash_common_utils import get_data_table_card_children, get_pivot_table_card_children, \
    diff_dashtable_mi, ScenarioTableSchema, table_type
from dse_do_dashboard.utils.scenariodbmanager_update import DbCellUpdate


class PrepareDataPageEdit(PrepareDataPage):
    """Includes feature to edit input tables.
    Use instead of `PrepareDataPage`.
    Do not combine in same app: will cause duplicate callbacks."""
    def __init__(self, dash_app):
        self.data_table_id = 'input_data_table'
        super().__init__(dash_app,
                         page_name='Prepare Data',
                         page_id='prepare-data',
                         url='prepare-data',
                         )

    def get_layout(self, scenario_name: str = None, reference_scenario_name: str = None, multi_scenario_names: List[str] = None):
        input_tables = self.dash_app.get_input_table_names()
        layout = html.Div([
            dcc.Store(id="current_table_name"),

            self.get_input_table_selection_card(),

            dbc.Card([
                # dbc.CardHeader('Input Table'),
                dbc.CardBody(id='input_data_table_card', style={'width': '79vw'},
                             children=get_data_table_card_children(df=pd.DataFrame(), table_name='None', editable=True, data_table_id=self.data_table_id)  # We need to initialize a DataTable, otherwise issues with registering callbacks
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

    def update_data_and_pivot_input_table_callback(self, scenario_name, table_name, diff_store_data=None):
        """Body for the Dash callback.
        Usage::
            @app.callback([Output('input_data_table_card', 'children'),
            Output('input_pivot_table_card', 'children')],
            [Input('top_menu_scenarios_drpdwn', 'value'),
            Input('input_table_drpdwn', 'value')])
            def update_data_and_pivot_input_table(scenario_name, table_name):
                data_table_children, pivot_table_children = DA.update_data_and_pivot_input_table_callback(scenario_name, table_name)
                return [data_table_children, pivot_table_children]

        TODO: share parts with parent
        """
        # print(f"update_data_and_pivot_input_table for {table_name} in {scenario_name}")
        input_table_names = [table_name]
        pm = self.dash_app.get_plotly_manager(scenario_name, input_table_names, [])
        dm = pm.dm
        df = self.dash_app.get_table_by_name(dm=dm, table_name=table_name, index=False, expand=False)
        table_schema = self.dash_app.get_table_schema(table_name)
        pivot_table_config = self.dash_app.get_pivot_table_config(table_name)
        data_table_children = self.get_data_table_card_children(df, table_name, table_schema, editable=True, data_table_id=self.data_table_id, diff_store_data=diff_store_data)
        pivot_table_children = get_pivot_table_card_children(df, scenario_name, table_name, pivot_table_config)
        return data_table_children, pivot_table_children

    def get_data_table_card_children(self, df, table_name:str, table_schema: Optional[ScenarioTableSchema] = None,
                                     editable: bool = False, data_table_id:str=None, diff_store_data=None):
        return [
            dbc.CardHeader(
                table_name
                # title=table_name,
                # fullscreen=True
            ),
            self.get_data_table(df, table_schema, editable, data_table_id, diff_store_data)
        ]

    def get_data_table(self, df, table_schema: Optional[ScenarioTableSchema] = None, editable: bool = False, data_table_id=None, diff_store_data=None) -> dash_table.DataTable:
        """
        Generates a DataTable for a DataFrame. For use in 'Prepare Data' and 'Explore Solution' pages.
        :param df:
        :param table_schema:
        :return:
        """
        if data_table_id is None:
            data_table_id = 'my_data_table'
        index_columns = []
        if table_schema is not None:
            # print(f"prepare_data_page_edit - get_data_table table_schema.index_columns={table_schema.index_columns}")
            if len(table_schema.index_columns) > 0:
                df = df.set_index(table_schema.index_columns).reset_index()  # ensures all index columns are first
            index_columns = table_schema.index_columns
        return dash_table.DataTable(
            id=data_table_id,
            data=df.to_dict('records'),
            columns=[
                {'name': i, 'id': i, 'type': table_type(df[i])}
                for i in df.columns
            ],
            fixed_rows={'headers': True},
            editable=editable,
            # fixed_columns={'headers': False, 'data': 0}, # Does NOT create a horizontal scroll bar
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            style_cell={
                'textOverflow': 'ellipsis',  # See https://dash.plotly.com/datatable/width to control column-name width
                'maxWidth': 0,               # Needs to be here for the 'ellipsis' option to work
                'overflow' : 'hidden',
                'font_family': 'sans-serif',
                'font_size': '12px',
                'textAlign': 'left'},
            style_table={
                'maxHeight': '400px',
                'overflowY': 'scroll'
            },
            style_header={
                'if': {
                    'column_id': index_columns
                },
                # 'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            style_data_conditional=([
                {
                    'if': {
                        'column_id': index_columns
                    },
                    'fontWeight': 'bold',
                    # 'backgroundColor': '#0074D9',
                    # 'color': 'white'
                },
                # {
                #     'if': {
                #         'row_index': 2,
                #         'column_id': 'size'
                #     },
                #     'backgroundColor': '#d62728'
                # },
            ] + self.get_table_style_data_conditional_cell_edit(diff_store_data)
            ))

    def get_table_style_data_conditional_cell_edit(self, diff_store_data=None) -> List[Dict]:
        """Return a list of dicts with conditional cell style. For each cell that has been edited.
        Partly works:
        - The coloring works, but
        - The table needs to be refreshed/regenerated to get the color filtering active.
        That refresh is not happening currently. Need to see how it can be triggered
        That refresh will reset the edits in the table
        So one would need to re-apply the changes from the store.
        Seems like a lot of work for this feature.
        """
        # print(f"get_table_style_data_conditional_cell_edit diff_store_data = {diff_store_data}")
        if diff_store_data is None:
            return []
        cell_edits = []
        for l in diff_store_data.values():
            for diff in l:
                cell_edits.append({
                    'if': {
                        'row_index': diff['row_idx'],
                        'column_id': diff['column_name']
                    },
                    'backgroundColor': '#d62728'
                })
        return cell_edits


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
        # print("Set dash callbacks for PrepareDataPageEdit")
        # super().set_dash_callbacks()
        app = self.dash_app.app

        @app.callback([Output('input_data_table_card', 'children'),
                       Output('input_pivot_table_card', 'children')],
                      [Input('top_menu_scenarios_drpdwn', 'value'),
                       Input('input_table_drpdwn', 'value')],
                      State("my_data_table_diff_store", "data"))
        def update_data_and_pivot_input_table_edit(scenario_name:str, table_name:str, diff_store_data):
            data_table_children, pivot_table_children = self.update_data_and_pivot_input_table_callback(scenario_name, table_name, diff_store_data)
            return [data_table_children, pivot_table_children]

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

        # print("Set dash callbacks for PrepareDataPageEdit.capture_and_commit_edits")
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
                # print(f"Not triggered. diff_store_data = {diff_store_data}")
                # raise PreventUpdate
                # Attempt to enable Commit button if there are changes pending in the diff-store after a 'Refresh' button click
                # Note that the value of the change in the table has been lost due to the refresh, but not the Store
                # So the diff can still be committed, but doesn't properly show in the table
                if diff_store_data is None:
                    raise PreventUpdate
                else:
                    return diff_store_data, False

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
