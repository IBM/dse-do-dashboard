# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Common functions for generating Dash components
"""
from typing import Optional, NamedTuple, List, Dict
import pandas as pd

import dash_bootstrap_components as l
from dash import html
# import dash_html_components as html
import dash_pivottable
from dash import dash_table
import dash_bootstrap_components as dbc


##########################################################################
#  Generic Schema NamedTuple classes
##########################################################################
from dash.dash_table.Format import Format


class ForeignKeySchema(NamedTuple):
    table_name: str
    foreign_keys: List[str]


class ScenarioTableSchema(NamedTuple):
    table_name: str
    index_columns: List[str]
    value_columns: List[str]
    foreign_tables: List[ForeignKeySchema]


class PivotTableConfig(NamedTuple):
    table_name: str
    rows: List[str]
    cols: List[str]
    vals: List[str]
    rendererName: str
    aggregatorName: str

##########################################################################
#  VisualizationPage classes
##########################################################################
# class VisualizationPageConfig(NamedTuple):
#     """Specification of visualization pages/tabs.
#     """
#     page_name: str  # As used as the menu/tab name in the UI
#     page_id: str  # The Tab.value when using Tabs
#     module_name: str  # name of the Python module
#     url: str  # Part of the url string
#     input_table_names: List[str]  # Names of input tables used in page
#     output_table_names:List[str]  # Names of output tables used in page

##########################################################################
#  Functions
##########################################################################

def table_type(df_column):
    # Note - this only works with Pandas >= 1.0.0

    # if sys.version_info < (3, 0):  # Pandas 1.0.0 does not support Python 2
    #     return 'any'

    if isinstance(df_column.dtype, pd.DatetimeTZDtype):
        return 'datetime',
    elif (isinstance(df_column.dtype, pd.StringDtype) or
          isinstance(df_column.dtype, pd.BooleanDtype) or
          isinstance(df_column.dtype, pd.CategoricalDtype) or
          isinstance(df_column.dtype, pd.PeriodDtype)):
        return 'text'
    elif (isinstance(df_column.dtype, pd.SparseDtype) or
          isinstance(df_column.dtype, pd.IntervalDtype) or
          isinstance(df_column.dtype, pd.Int8Dtype) or
          isinstance(df_column.dtype, pd.Int16Dtype) or
          isinstance(df_column.dtype, pd.Int32Dtype) or
          isinstance(df_column.dtype, pd.Int64Dtype)):
        return 'numeric'
    else:
        return 'any'


def get_data_table(df, table_schema: Optional[ScenarioTableSchema] = None, editable: bool = False, data_table_id=None) -> dash_table.DataTable:
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
        if len(table_schema.index_columns) > 0:
            df = df.set_index(table_schema.index_columns).reset_index()  # ensures all index columns are first
        index_columns = table_schema.index_columns
    return dash_table.DataTable(
        id=data_table_id,
        data=df.to_dict('records'),
        columns=[
            {'name': i, 'id': i, 'type': table_type(df[i])}  # TODO: format 'thousands' separator with: 'format':Format().group(True) or ,  'format': Format(group=',', precision=0)
            for i in df.columns
        ],
        fixed_rows={'headers': True},
        editable=editable,
        virtualization=True,
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
            'maxHeight': '800px',
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
            }
        ]),
    )

def get_editable_data_table(df, table_schema: Optional[ScenarioTableSchema]=None) -> dash_table.DataTable:
    """
    Generates an editable DataTable for a DataFrame. For use in 'Prepare Data' page.
    :param df:
    :param table_schema:
    :return:
    """
    index_columns = []
    if table_schema is not None:
        df = df.set_index(table_schema.index_columns).reset_index()  # ensures all index columns are first
        index_columns = table_schema.index_columns
    return dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[
            {'name': i, 'id': i, 'type': table_type(df[i])}
            for i in df.columns
        ],
        fixed_rows={'headers': True},
        # page_size=20,
        editable=True,
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
            }
        ]),
    )

def get_pivot_table(df, scenario_name, table_name, pivot_config) -> dash_pivottable.PivotTable:
    """
    Generates a PivotTable for a DataFrame. For use in 'Prepare Data' and 'Explore Solution' pages.
    :param df:
    :param scenario_name:
    :param table_name:
    :return:
    """
    if pivot_config is None:
        pivot = dash_pivottable.PivotTable(
            id=f"pivot-{scenario_name}-{table_name}",
            data=df.to_dict('records'),  # What is difference between rows and records?
            # cols=['timePeriodSeq'],
            colOrder="key_a_to_z",
            # rows=['lineName'],
            rowOrder="key_a_to_z",
            rendererName="Table",
            aggregatorName="Sum",
        # vals=["line_capacity_utilization"],
        # valueFilter={'Day of Week': {'Thursday': False}}
        )
    else:
        # print(pivot_config)
        pivot = dash_pivottable.PivotTable(
            id=f"pivot-{scenario_name}-{table_name}",
            data=df.to_dict('records'),  # What is difference between rows and records?
            cols = pivot_config.cols,
            colOrder="key_a_to_z",
            rows = pivot_config.rows,
            rowOrder="key_a_to_z",
            rendererName=pivot_config.rendererName,
            aggregatorName=pivot_config.aggregatorName,
            vals=pivot_config.vals,
            # valueFilter={'Day of Week': {'Thursday': False}}
        )
    return pivot


def get_data_table_card_children(df, table_name:str, table_schema: Optional[ScenarioTableSchema] = None,
                                 editable: bool = False, data_table_id:str=None):
    return [
        dbc.CardHeader(
            table_name
            # title=table_name,
            # fullscreen=True
        ),
        get_data_table(df, table_schema, editable, data_table_id)
    ]


def get_pivot_table_card_children(df, scenario_name, table_name, pivot_config: Optional[PivotTableConfig]=None):
    return [
        dbc.CardHeader(
            table_name
            # title=table_name,
            # fullscreen=True
        ),
        get_pivot_table(df, scenario_name, table_name, pivot_config)
    ]

#####################################
import functools
# import plotly.express as px
import plotly.graph_objects as go
import traceback

def plotly_figure_exception_handler(f):
    # type: (Callable[..., Any]) -> Callable[..., Any]
    """
    A function wrapper/decorator for catching all exceptions on methods that generate a Plotly Figure.
    Returns a default Figure in case of an exception
    """
    @functools.wraps(f)
    def inner(self, *args, **kwargs):
        # type: (*Any, **Any) -> Any

        # TODO: only handle exception in 'deployed' Dash app, so that we can use the regular Dash exception handling in the UI for debugging.
        # If in 'deployed' mode: 
        # return f(self, *args, **kwargs)

        try:
            return f(self, *args, **kwargs)
        except Exception as ex:
            # print(ex)
            print(f"Exception handled by utils.dash_common_utils.plotly_figure_exception_handler decorator:")
            traceback.print_exc()
            # fig = px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])
            fig = go.Figure(data=[go.Table(header=dict(values=[f'Exception in {f.__name__}']),
                 cells=dict(values=[[traceback.format_exc()]]))
                     ])
            return fig

    return inner


################################
# def diff_dashtable(data, data_previous, row_id_name=None) -> List[Dict]:
#     """Generate a diff of Dash DataTable data.
#
#     From: https://community.plotly.com/t/detecting-changed-cell-in-editable-datatable/26219/4
#     Modified from: https://community.plotly.com/t/detecting-changed-cell-in-editable-datatable/26219/2
#
#     Parameters
#     ----------
#     data: DataTable property (https://dash.plot.ly/datatable/reference)
#         The contents of the table (list of dicts)
#     data_previous: DataTable property
#         The previous state of `data` (list of dicts).
#
#     Returns
#     -------
#     A list of dictionaries in form of [{row_id_name:, column_name:, current_value:,
#         previous_value:}]
#     """
#     df, df_previous = pd.DataFrame(data=data), pd.DataFrame(data_previous)
#
#     if row_id_name is not None:
#         # If using something other than the index for row id's, set it here
#         for _df in [df, df_previous]:
#
#             # Why do this?  Guess just to be sure?
#             assert row_id_name in _df.columns
#
#             _df = _df.set_index(row_id_name)
#     else:
#         row_id_name = "index"
#
#     # Pandas/Numpy says NaN != NaN, so we cannot simply compare the dataframes.  Instead we can either replace the
#     # NaNs with some unique value (which is fastest for very small arrays, but doesn't scale well) or we can do
#     # (from https://stackoverflow.com/a/19322739/5394584):
#     # Mask of elements that have changed, as a dataframe.  Each element indicates True if df!=df_prev
#     df_mask = ~((df == df_previous) | ((df != df) & (df_previous != df_previous)))
#
#     # ...and keep only rows that include a changed value
#     df_mask = df_mask.loc[df_mask.any(axis=1)]
#
#     changes = []
#
#     # This feels like a place I could speed this up if needed
#     for idx, row in df_mask.iterrows():
#         row_id = row.name
#
#         # Act only on columns that had a change
#         row = row[row.eq(True)]
#
#         for change in row.iteritems():
#
#             changes.append(
#                 {
#                     row_id_name: row_id,
#                     "column_name": change[0],
#                     "current_value": df.at[row_id, change[0]],
#                     "previous_value": df_previous.at[row_id, change[0]],
#                 }
#             )
#
#     return changes

def diff_dashtable_mi(data, data_previous, index_columns: List[str] = None,
                      table_name: str = None, scenario_name: str = None) -> List[Dict]:
    """Generate a diff of Dash DataTable data.
    Allow for multi-index tables.

    Based on idea in: https://community.plotly.com/t/detecting-changed-cell-in-editable-datatable/26219/4
    Modified from: https://community.plotly.com/t/detecting-changed-cell-in-editable-datatable/26219/2

    Parameters
    ----------
    data: DataTable property (https://dash.plot.ly/datatable/reference)
        The contents of the table (list of dicts)
    data_previous: DataTable property
        The previous state of `data` (list of dicts).

    Returns
    -------
    A list of dictionaries in form of [{row_id_name:, column_name:, current_value:,
        previous_value:}]
        :param data: data from DataTable
        :param data_previous: data_previous from DataTable
        :param index_columns: names of the index/primary-key columns
        :param table_name: name of table
        :param scenario_name: name of scenario
        :returns changes: A list of dictionaries in form of [{row_idx:, column_name:, current_value:,
        previous_value:, row_index:, table_name:, scenario_name:}]
    """
    df, df_previous = pd.DataFrame(data=data), pd.DataFrame(data_previous)
    # df, df_previous = data=data, data_previous

    if index_columns is not None and len(index_columns) > 0:
        assert len(index_columns) > 0
        assert all(index_column in df.columns for index_column in index_columns)
        df.set_index(index_columns, verify_integrity=True)  # Just to test?
        df_previous.set_index(index_columns, verify_integrity=True) # Just to test?
    else:
        # Grab all columns
        index_columns = df.columns

    # Pandas/Numpy says NaN != NaN, so we cannot simply compare the dataframes.  Instead we can either replace the
    # NaNs with some unique value (which is fastest for very small arrays, but doesn't scale well) or we can do
    # (from https://stackoverflow.com/a/19322739/5394584):
    # Mask of elements that have changed, as a dataframe.  Each element indicates True if df!=df_prev
    df_mask = ~((df == df_previous) | ((df != df) & (df_previous != df_previous)))

    # ...and keep only rows that include a changed value
    df_mask = df_mask.loc[df_mask.any(axis=1)]

    changes = []
    # This feels like a place I could speed this up if needed
    for idx, row in df_mask.iterrows():
        row_id = row.name

        # Act only on columns that had a change
        row = row[row.eq(True)]

        #         print(f"row={row}")
        # for change in row.iteritems():  # Deprecated in Pandas 2.0
        for change in row.items():
            change = {
                "row_idx": row_id,
                "column_name": change[0],
                "current_value": df.at[row_id, change[0]],
                "previous_value": df_previous.at[row_id, change[0]],
            }
            if index_columns is not None:
                change['row_index'] = [{'column': i, 'value': df_previous.at[row_id, i]} for i in index_columns]
            if table_name is not None:
                change['table_name'] = table_name
            if scenario_name is not None:
                change['scenario_name'] = scenario_name
            changes.append(change)

    return changes


